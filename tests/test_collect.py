import datetime as dt, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import parse_feed, merge, safe_url
class CollectorTests(unittest.TestCase):
    def test_feed_rejects_script_and_bad_date(self):
        xml=b'<rss><channel><item><title>Bad</title><link>javascript:alert(1)</link><pubDate>Mon, 26 Oct 2026 08:00:00 GMT</pubDate></item><item><title>No date</title><link>https://example.com/a</link></item></channel></rss>'
        self.assertEqual(parse_feed(xml,{'name':'test','category':'turkiye'},dt.datetime(2026,10,26,13,tzinfo=dt.timezone.utc)),[])
    def test_duplicate_preserves_categories_and_sources(self):
        a={'title':'Meclis bütçe görüşmelerine bugün yeni komisyon toplantısıyla başladı','url':'https://a.test/1','published':'2026-10-26T13:00:00+03:00','categories':['turkiye'],'sources':[{'name':'A','url':'https://a.test/1'}],'summary':'','summaryLimited':True,'image':''}
        b={**a,'url':'https://b.test/2','categories':['zafer'],'sources':[{'name':'B','url':'https://b.test/2'}]}
        result=merge([a,b]);self.assertEqual(len(result),1);self.assertEqual(len(result[0]['sources']),2);self.assertEqual(set(result[0]['categories']),{'turkiye','zafer'})
    def test_different_claims_not_merged(self):
        a={'title':'Parti başkanı bütçe teklifine destek verdi','url':'https://a.test','published':'2026-10-26T13:00:00+03:00'}
        b={**a,'title':'Parti başkanı bütçe teklifine karşı çıktı','url':'https://b.test'}
        from collect import similar
        self.assertFalse(similar(a,b))
    def test_url_safety(self): self.assertEqual(safe_url('javascript:alert(1)'), '')
if __name__=='__main__': unittest.main()
