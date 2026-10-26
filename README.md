# SEFA TEMİZ | GÜNDEM

Gündemi tek noktadan takip edin.

## Yerelde çalıştırma
Python 3.12+ ile depo kökünde:

    python scripts/collect.py
    python -m unittest discover -s tests
    python -m http.server 8080 --directory dist

http://localhost:8080 adresini açın. Node, npm paketi, veritabanı sunucusu veya AI anahtarı gerekmez. `dist/` doğrudan statik barındırmaya hazırdır. Dosyayı çift tıklamak yerine HTTP sunucusu kullanın.

## Ücretsiz otomasyon ve herkese açık yayın
1. Bu klasörün içeriğini (gizli `.github` dahil) size ait **public** bir GitHub deposuna yükleyin. `.openai` yalnızca Sites yayını içindir; GitHub Pages için gerekmez.
2. Settings > Pages > Build and deployment > Source: **GitHub Actions**.
3. Actions > Günlük bülten > Run workflow. Gerekirse Actions erişimini ve workflow yazma iznini açın. Depoda branch koruması bot push'una izin vermelidir.
4. İş akışı önce test eder, haberleri toplar, arşivi commit eder ve `dist` dizinini Pages'e yayınlar. Pages adresi iş akışının deploy çıktısındadır. Şifre veya ziyaretçi üyeliği yoktur.
5. Günlük cron `0 10 * * *`: 10.00 UTC / Türkiye 13.00. GitHub zamanlaması yoğunlukta gecikebilir; kesin 13.00 garantisi vermez. İnaktif public depolarda zamanlama durdurulabilir; Actions durumunu izleyin. Daha sıkı zamanlama gerekirse aynı komutu çalıştıran harici cron sonraki aşamadır.

## Dış bağlantılar / kalan işler
- **GitHub deposu, Pages ve Actions henüz bağlanmadı.** Workflow dosyası hazır; günlük otomasyon şu anda canlı değildir. Bu sohbetten bir Pages hesabı oluşturulmadı.
- Sites yayını ilk arşivin görüntüsüdür. GitHub Actions Sites deposuna kendiliğinden erişmez. Sürekli güncelleme için yukarıdaki Pages yolunu kullanın veya Sites için ayrı yetkili veri yazıcısı ekleyin.
- **Ayrı veritabanı gerekmiyor.** `dist/data/YYYY-MM-DD.json` günlük bültenleri, `index.json` arşiv dizinini tutar; Git geçmişi yedektir. İlk kurulumdan önceki günler geriye dönük doldurulmaz.
- **X bağlantısı yok.** Üç kişinin kullanıcı adları doğrulanamadığı için `config.json` içinde null / verified:false bırakıldı. İsimden kullanıcı adı tahmin edilmez. Kimliği resmi web sitesinden/kişinin doğrulanabilir kendi bağlantısından doğrulayın ve kanıt URL'sini kaydedin. Ancak erişim koşulları uygunsa ayrı X bağlayıcısı ekleyin; ücretli API zorunlu değildir, ilk sürüm haberlerle çalışır.
- Özel takip, isimleri tırnak içinde tarar. Aynı isimli kişiler için yanlış eşleşme ihtimali vardır; kişi kimliği haberden kontrol edilmelidir.
- Alan adı isteğe bağlıdır; satın alma gerekmez. GitHub ücretsiz planlarının güncel kullanım sınırları sağlayıcının koşullarına tabidir.

## Haberler, kapsam ve sınırlar
Türkiye için hükümet, TBMM, seçim, parti ve ekonomi sorguları ayrı yürür. Zafer Partisi, Ümit Özdağ ve yönetim/faaliyet/iddia/eleştiri sorguları birlikte yürür; duygu veya siyasi görüş filtresi uygulanmaz. RSS ve arama sağlayıcısının kapsamadığı bir gelişmenin yakalanması garanti edilemez. Yeni kaynaklar `config.json` içinde eklenir.

Benzer başlıklarda sözcük örtüşmesi ve 36 saatlik zaman penceresi kullanılır; kaynak bağlantıları tek kartta korunur. Bu anlamsal analiz değildir; farklı yazılmış aynı haber ayrı kalabilir. Yanlış birleştirmeleri azaltmak için eşik yüksektir.

Özetler kaynak RSS açıklamasından en fazla 4 cümle / 75 kelimelik kısa alıntılardır. Kaynak yeterli metin verirse 3–4 cümle gösterilir. **Google Haberler RSS genellikle haber gövdesi sağlamaz: bu kartlarda 3–4 cümlelik özet yoktur.** Metin uydurulmaz ve karta uyarı konur. Tam ve tutarlı 3–4 cümle için izinli tam metin kaynakları veya ek bir açık kaynak metin çıkarma katmanı gerekir. Paywall ve erişim engeli aşılmaz.

RSS görseli varsa gösterilir, yoksa yerel ST yer tutucu kullanılır. Google RSS bağlantıları Google Haberler üzerinden kaynak habere yönlendirir; doğrudan yayınevi URL'si her akışta sağlanmaz. Yayın zamanı kaynağa aittir, derleme zamanı ayrıca gösterilir. Bülten son 24 saatlik pencereyi kapsar; 13.00 sonrası haberler sonraki bültene girer. İlk toplama kurulum anında yapıldı.

Her akış ayrı hata yalıtımıyla okunur. Tam başarısızlık eski bülteni silmez, görev hata koduyla biter. Kısmi erişim sorunları arayüzde görünür. `health.json` son deneme raporudur. Ücretli AI, analiz düğmesi veya istemcide toplama yoktur. Kullanıcıya açık yazma uç noktası ve gizli anahtar yoktur.
