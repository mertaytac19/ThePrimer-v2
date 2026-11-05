# The Primer v2 — Hata Avcısı

**Yazılım Testi dersi / deneysel makine öğrenmesi projesi.** Sekiz teknik görev içeren, oyuncu davranışlarını ölçen ve küçük bir ONNX modelinin yardım ihtiyacı tahminiyle uyarlanabilir ipuçları gösteren Türkçe web oyunu.

> **Önemli durum (4 Kasım 2026):** ZIP'teki mevcut model yalnızca **5 sentetik kayıtla** eğitilmiş *deneysel demonstrasyondur*. Henüz **15 gerçek oturum yoktur**; gerçek veri değerlendirmesi, canlı Hugging Face yayını, gerçek Chromium parite testi ve son kullanıcı demo videosu tamamlanmadan proje “tam teslim” değildir. Model kartı ve config bu durumu açıkça işaretler.


## 1. Hızlı kurulum — 3 komut

Python 3.10 veya 3.11 ve Node.js LTS yüklü olmalı. Proje kökünde PowerShell açın. Python sanal ortamınız zaten varsa etkinleştirin (`.\.venv\Scripts\Activate.ps1`). Kurulum:

```powershell
python -m pip install -r requirements.txt
npm install
npm start
```

Chrome'da **http://127.0.0.1:8080/web/** adresini açın. Modelin JavaScript runtime kütüphanesi jsDelivr'den indirilir, ilk açılışta internet gerekir. İndirilemiyorsa oyun modelsiz çalışır; sahte tahmin üretmez. `npm start` açık kalsın. Terminali kapatmak için Ctrl+C.

> `python -m venv .venv` yeni ortam oluşturmak, ardından `.\.venv\Scripts\Activate.ps1` ile etkinleştirmek isterseniz kurulum öncesinde yapabilirsiniz.

## 2. Oyun modu ve veri toplama modu

- **Oyun modu:** 8 teknik karar, senaryo, birden fazla son; seçim değişikliği ve bekleme süresi ölçülür. ONNX modeli uygun gördüğünde karar *onaylanmadan önce* bağlamsal ipucu gösterebilir. Oyuncunun elle istediği ipucu ayrı olarak işaretlenir. Model yoksa oyun devam eder.
- **Veri Toplama Modu:** Katılımcıya girişte bilgi verilir. **AI ipucu gösterilmez** ve her onaylanan kararın ardından “yardıma ihtiyaç duydun mu?” sorulur. Bağımsız öz bildirim etiketi CSV'ye kaydedilir. `CSV indir` ile dosyayı kullanıcı kendi bilgisayarına kaydeder. Otomatik uzak gönderim yoktur.

Ölçüm sözlüğü `data/SOZLUK.md` içinde. Karar süresi sahne açılışından onaylanana kadar, tereddüt süresi ilk seçimden onaya kadar. Tereddüt gerçek psikolojik durumun kesin ölçümü değildir. `onceki_hata_sayisi`, **mevcut karar sonuçlanmadan önceki** hata sayısıdır.

## 3. En az 15 gerçek oturum toplama

1. Gönüllü arkadaşlarınıza Veri Toplama Modu'nu açtırın; giriş/şifre, isim, e-posta veya cihaz kimliği istemeyin. **3 kişinin 5'er ayrı oyun oturumu** gibi en az 15 gerçek oyun oturumu toplayın.
2. Her oynayış sonunda `CSV indir` deyin. Her oynayış yeni, rastgele bir `session_id` alır. Bu dosyaları `data/collected/` klasörüne koyun. **Sentetik testler gerçek oturum sayılmaz.**
3. Aşağıdaki komutla birleştirin (birleşmeden önce var olan CSV'nin `.bak` yedeği alınır):

```powershell
python scripts/merge_sessions.py "data/collected/*.csv"
```

Gerçek oturumların sayısını program raporlar. Veri için etiketler oyuncunun kendi öz bildirimi olan 0/1'dir; oyunda doğru/yanlış cevap ile otomatik üretilmez.

## 4. Model eğitme ve kabul kapısı

```powershell
python train.py
```

Üretim eğitimi **yalnızca 15 veya daha fazla gerçek, farklı oturum** varsa ilerler. Train/test ayrımı **oturum bazlı** yapılır, iki tarafta da her iki sınıf olmalıdır. Önceden `spec.md` içinde yazan pozitif sınıf F1 kabul eşiği **≥0.65**. Başarı eşiği sağlanmazsa yeni model **yayınlanmaz ve önceki model korunur**. Kabul edilirse gerçek oturumlarla yeniden eğitilen son model `_out/model/` klasörüne yazılır; sklearn→ONNX paritesi `<1e-4` olarak doğrulanır. Çıktılar: `model.onnx`, `config.json`, `model.joblib` (sadece Python oracle), `README.md` (model kartı).

Yalnız **demonstrasyon** için `python train.py --demo` kullanılabilir; config içinde açıkça `demo_unverified` yazılır, rapor başarı puanı üretilmez. Demo sonucu gerçek performans anlamına gelmez.

## 5. Testleri çalıştırma

```powershell
python scripts/create_parite.py
python -m pytest tests/ -v -rs
npm run test:e2e
```

Cypress testlerinden önce **ayrı bir terminalde** `npm start` açık olmalıdır. Chrome/Chromium yüklemeleri internete bağlı olabilir. `cypress/e2e/game.cy.js` oyun/regresyon ve veri toplama akışını; `cypress/e2e/parite.cy.js` ise **gerçek tarayıcı ONNX çıktısını** `tests/parite.json` içindeki sklearn/Python oracle referanslarıyla karşılaştırır. Her bir fark `<1e-4` olmalıdır. Model yüklenmediyse web parite testi geçemez; atlanmaz.

`tests/parite.py` Python ONNX ve sklearn arasında ayrıca test yapar. `scripts/compare_parite.py` **iki Python sonucunu** karşılaştırır; bu **web/Python testi değildir**. `tests/parite.json` üretim modeli her değiştiğinde yeniden oluşturulmalıdır.

## 6. Yayın / teslim dosyaları

Yerelde çalışan projenin aynısını statik sunucuya yüklemek yerine küçük dağıtım paketi oluşturun:

```powershell
python scripts/build_site.py
```

`dist/` içinde web dosyaları ve sadece `model.onnx` + `config.json` vardır. `dist` içeriğini GitHub Pages (`gh-pages` dalı) veya benzeri statik barındırmaya yükleyebilirsiniz. ONNX Runtime tarayıcıda çalışır; kullanıcı davranışı sunucuya gönderilmez. Üretim modeliyle çalışırken tüm dosyaları yeniden oluşturun.

Hugging Face'te ücretsiz public model reposu açın ve yalnızca `model.onnx`, `config.json`, `README.md` yükleyin. **Yayın için gerekli hesap yetkisi kullanıcıya aittir.** Gerçek commit hash alındıktan sonra bağlantıyı şu biçimde sabitleyin: `https://huggingface.co/<kullanici>/<repo>/resolve/<commit>/model.onnx`.

Teslim formuna GitHub repo, Hugging Face commit'li model linki, canlı web linki ve **60–90 saniyelik gerçek demo video** bağlantısı gerekir. Hepsi gizli pencerede erişilebilir olmalı. Ödevin teslim tarihi: **6 Kasım 2026 23:59**.

## 7. Mimari, sınırlar ve kaynaklar

`train.py` (Development) → `model.onnx + config.json` (taşınabilir model sözleşmesi) → Hugging Face public sürümlü repo (Deployment) → `onnxruntime-web` tarayıcıda (Inference). Python referans Oracle ve Cypress web sonucu diferansiyel test edilir; tüm hikâye akışı regresyon testinden geçirilir.

Sınırlamalar: Öz bildirim etiketi kusurlu olabilir; oturum sayısı/genel örnek sayısı azsa güvenilirlik sınırlıdır; model, final karar süreleriyle eğitildiği hâlde oyun sırasında *ara* davranışları değerlendirebilir (dağılım kayması). Model çıktısı eğitimsel rehberdir, kritik karar vermek için uygun değildir. Python ve web arasındaki sayısal farklar `<1e-4` toleransta değerlendirilecektir.

Başlangıç örneği / kaynak: https://github.com/seyyah/huggingface-hello-web. Dersin referansları: Amershi vd. (2019), *Software Engineering for Machine Learning*; Shankar vd. (2022), *Operationalizing Machine Learning*; Mitchell vd. (2019), *Model Cards for Model Reporting*; Breck vd. (2017), *The ML Test Score*. `huggingface-hello-web/` kaynak örneği ayrı korunmuştur.

## 8. Yapay zekâ aracı kullanım beyanı

- Antigravity, ilk oyun arayüzünün ve model entegrasyonunun oluşturulmasında kullanıldı.
- Önceki agent çıktılarındaki kopya kod, eksik veri toplama, karşılaştırma iddiaları ve bozuk `package.json` insan gözetimiyle yeniden inceletildi.
- Sonraki aşamada ChatGPT ile yeni çalışma kopyasında oyun davranışları, veri kaydı, eğitim kapısı, Cypress testleri ve dokümantasyon taslakları geliştirildi.
- Kaynak kodun gerçek kullanıcı testleri, 15 gönüllü oturumun toplanması, üretim ONNX karşılaştırması, yayın bağlantıları ve video insan tarafından ayrıca kontrol edilmelidir; gerçekleşmeyen aşamalar tamamlandı olarak beyan edilmez.
