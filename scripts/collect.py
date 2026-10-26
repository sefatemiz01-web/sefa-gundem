"""Python 3.12+ standart kütüphane; pip, ücretli AI veya X API gerekmez.
Kurulum: python scripts/collect.py. Zamanlama: .github/workflows/daily.yml.
JSON arşivi kalıcı statik veri deposudur. X doğrulanmış hesap/erişim olmadan kapalıdır.
"""
import concurrent.futures, datetime as dt, email.utils, hashlib, html, json, os, re
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dist/data'
TR=dt.timezone(dt.timedelta(hours=3))
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',s or ''))).strip()
def safe_url(s): return s if urllib.parse.urlparse(s or '').scheme in ('http','https') else ''
def read(path,default): return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,path)
def tokens(s): return set(re.findall(r'\w+',s.lower()))-{'bir','ve','ile','için','son','dakika','haber'}
def similar(a,b):
    if a['url']==b['url']: return True
    if abs((dt.datetime.fromisoformat(a['published'])-dt.datetime.fromisoformat(b['published'])).total_seconds())>129600: return False
    x,y=tokens(a['title']),tokens(b['title'])
    return len(x&y)>=5 and len(x&y)/max(1,len(x|y))>=.78

def parse_feed(raw,feed,now):
    items=[]
    for node in ET.fromstring(raw).findall('.//item'):
        title,url=clean(node.findtext('title')),safe_url(node.findtext('link'))
        try:
            published=email.utils.parsedate_to_datetime(node.findtext('pubDate') or '')
            if published.tzinfo is None: published=published.replace(tzinfo=dt.timezone.utc)
            published=published.astimezone(TR)
        except (ValueError,TypeError,OverflowError): continue
        if not title or not url or published>now+dt.timedelta(minutes=10) or published<now-dt.timedelta(days=7): continue
        src=node.find('source'); source=clean(src.text) if src is not None else feed['name']
        category=feed['category']
        combined=(title+' '+clean(node.findtext('description'))).lower()
        # Siyasi haberler korunur; spor/yaşam gibi kapsam dışı RSS kayıtları ayıklanır.
        political=bool(re.search(r'cumhurbaşkan|bakan|tbmm|meclis|parti|seçim|hükümet|erdoğan|özdağ|bütçe|enflasyon|merkez bank|siyasi|diplomasi|savaş|ateşkes|ordu|başkan|belediye|soruşturma|mahkeme',combined))
        if not feed.get('google'):
            if '/spor/' in url and not political: continue
            if '/dunya/' in url: category='dunya'
            elif '/haber/' in url and not any(v in url for v in ('/gundem/','/turkiye/','/ekonomi/')) and not political: continue
            elif 'bbc.' in url and not political: continue
        if feed.get('google') and category=='turkiye' and not political and not re.search(r'ekonomi|güvenlik|deprem|afet',combined): continue
        if source and title.endswith(' - '+source): title=title[:-len(source)-3]
        description=clean(node.findtext('description')) if not feed.get('google') else ''
        sentences=re.split(r'(?<=[.!?])\s+',description)
        # Kaynak metninden en fazla dört cümle/75 kelime. Eksik cümle uydurulmaz.
        summary=' '.join(' '.join(sentences[:4]).split()[:75])
        image=''
        for child in node.iter():
            tag=child.tag.split('}')[-1]
            if tag in ('thumbnail','content','enclosure') and (child.attrib.get('type','').startswith('image/') or tag in ('thumbnail','content')):
                image=safe_url(child.attrib.get('url',''))
                if image: break
        if not image:
            match=re.search(r'<img[^>]+src=[\"\']([^\"\']+)',node.findtext('description') or '')
            if match: image=safe_url(html.unescape(match[1]))
        items.append({'id':hashlib.sha256(url.encode()).hexdigest()[:20],'title':title,'url':url,'published':published.isoformat(),'source':source or feed['name'],'summary':summary,'summaryLimited':len(sentences)<3 or not summary,'image':image,'categories':[category],'sources':[{'name':source or feed['name'],'url':url}],'xUrl':None})
    return items

def fetch_feed(feed,now):
    try:
        request=urllib.request.Request(feed['url'],headers={'User-Agent':'SefaTemizGundem/1.0 RSS Reader'})
        with urllib.request.urlopen(request,timeout=25) as response: raw=response.read(4000001)
        if len(raw)>4000000: raise ValueError('Akış boyutu sınırı')
        items=parse_feed(raw,feed,now)
        return items,{'name':feed['name'],'url':feed['url'],'ok':True,'count':len(items)}
    except Exception as exc: return [],{'name':feed['name'],'url':feed['url'],'ok':False,'error':str(exc)[:200]}

def merge(items):
    groups=[]
    for item in sorted(items,key=lambda i:i['published'],reverse=True):
        old=next((g for g in groups if similar(g,item)),None)
        if old is None: groups.append(item); continue
        old['categories']=sorted(set(old['categories']+item['categories']))
        for source in item['sources']:
            if source not in old['sources']: old['sources'].append(source)
        if len(item['summary'])>len(old['summary']): old['summary'],old['summaryLimited']=item['summary'],item['summaryLimited']
        old['image']=old['image'] or item['image']
    return groups

def main():
    config=read(ROOT/'config.json',{}); now=dt.datetime.now(TR); feeds=list(config['feeds'])
    for category,queries in config['queries'].items():
        for query in queries:
            url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query+' when:1d','hl':'tr','gl':'TR','ceid':'TR:tr'})
            feeds.append({'category':category,'name':'Google Haberler · '+query,'url':url,'google':True})
    items,health=[],[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for batch,status in pool.map(lambda f:fetch_feed(f,now),feeds): items.extend(batch); health.append(status)
    fresh=[i for i in items if dt.datetime.fromisoformat(i['published'])>=now-dt.timedelta(hours=24)]
    if not fresh:
        write(DATA/'health.json',{'attemptedAt':now.isoformat(),'feeds':health,'ok':False})
        raise SystemExit('Güncel haber alınamadı; son iyi arşiv korundu.')
    date=now.date().isoformat(); previous=read(DATA/f'{date}.json',{'items':[]})
    bulletin={'date':date,'updatedAt':now.isoformat(),'feeds':health,'items':merge(fresh+previous['items']),'xEnabled':False}
    write(DATA/f'{date}.json',bulletin)
    dates=sorted([p.stem for p in DATA.glob('????-??-??.json')],reverse=True)
    write(DATA/'index.json',{'dates':dates,'latest':date,'updatedAt':now.isoformat()})
    write(DATA/'health.json',{'attemptedAt':now.isoformat(),'feeds':health,'ok':True})
    print(f'{date}: {len(bulletin["items"])} kart; {sum(s["ok"] for s in health)}/{len(health)} akış erişilebilir')
if __name__=='__main__': main()
