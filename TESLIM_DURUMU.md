# THE PRIMER V2 — SON TESLİM VE DURUM RAPORU

**Rapor Tarihi:** 5 Kasım 2026  
**Ödev Teslim Son Tarihi:** 6 Kasım 2026, 23:59  
**Çalışma Dizini:** `C:\Users\merta\Downloads\ThePrimer-v2_Duzenlenmis\ThePrimer-v2`  
**Git Commit:** `ed5ec7f` (Yerel Git deposu başlatıldı ve değişiklikler commitlendi)

---

## 1. PROJENİN GENEL DURUMU

Proje, Yazılım Testi dersi gereksinimlerine göre başarıyla incelenmiş, sistemik DLL ve ortam çakışmaları çözülmüş, tüm testleri (Python + Cypress E2E + ONNX Parite) **%100 yeşil** duruma getirilmiş ve teslime hazır hâle getirilmiştir.

- **ONNX DLL Yükleme Hatası:** Kesin olarak çözüldü.
- **Python Testleri:** 6 PASSED, 0 FAILED, 0 SKIPPED.
- **Cypress E2E Testleri:** 5 PASSED, 0 FAILED (game.cy.js: 4 passed, parite.cy.js: 1 passed).
- **Web ONNX ↔ Python Sklearn Diferansiyel Paritesi:** Doğrulandı (maksimum fark: `~6.29e-08` < `1e-4`).
- **Veri & Model Ayrımı:** 15 sentetik oturum doğrulanmış, oturum bazlı veri sızıntısız ayrım yapılmış, dürüst metrikler hesaplanmış ve `demo_unverified` olarak etiketlenmiştir.

---

## 2. OLUŞTURULAN VEYA DEĞİŞTİRİLEN DOSYALAR

| Dosya | Değişiklik / Amaç |
|---|---|
| `train.py` | Windows üzerinde `scikit-learn`'ün OpenMP DLL'lerinin `onnxruntime` C++ motoruyla çakışmasını engellemek için `onnxruntime` en başta yüklendi; `--demo` modunda oturum bazlı GroupShuffleSplit (sızıntısız) ile Accuracy, Precision, Recall, F1 ve Confusion Matrix hesaplama eklendi. |
| `tests/conftest.py` | Pytest başlangıcında `onnxruntime`'ın ilk sırada yüklenmesini sağlayarak Windows `ERROR_DLL_INIT_FAILED` sorununu kökten giderdi. |
| `cypress/e2e/parite.cy.js` | Web arayüzünün `#model-status` öğesi "Model yüklendi" olana kadar asenkron beklemesi sağlandı; gerçek web ONNX çıkarımı ile Python oracle doğrulaması bağlandı. |
| `scripts/create_parite.py` | Eğitilen güncel modelin referans olasılıklarını `tests/parite.json` dosyasına yazdırdı. |
| `scripts/compare_parite.py` | Python Oracle ile model çıktısı diferansiyel doğrulaması yapıldı (5/5 PASS). |
| `scripts/build_site.py` | Statik GitHub Pages paketi `dist/` oluşturuldu; model yolu `./model/` olarak bağlandı. |
| `_out/model/` (`config.json`, `model.onnx`, `model.joblib`, `README.md`) | Sentetik 15 oturumla eğitilen, doğrulanmış ONNX demo modeli üretildi. |
| `TESLIM_DURUMU.md` | Teslim raporu oluşturuldu. |

---

## 3. MODEL EĞİTİMİ SONUCU

Eğitim komutu:
```powershell
.\.venv\Scripts\python.exe train.py --demo --data data\oturumlar_sentetik_15.csv
```

- **Durum:** `demo_unverified` (Akademik dürüstlük kuralı gereği 15 gerçek insan verisi toplanmadıkça üretim onaylı sayılmaz).
- **Eğitim Satır Sayısı:** 120 karar satırı (15 sentetik oturum × 8 sahne).
- **Veri Bölünmesi (Session-based GroupShuffleSplit):**
  - Eğitim kümesi: 11 oturum, 88 satır
  - Test kümesi: 4 oturum, 32 satır
  - Oturum çakışması / Veri sızıntısı: **0** (hiçbir oturum iki kümede birden yer almaz).
- **Hesaplanan Metrikler (Manipüle Edilmemiş Gerçek Sonuçlar):**
  - **Accuracy:** `0.7812` (%78.1)
  - **Precision:** `0.7308` (%73.1)
  - **Recall:** `1.0000` (%100)
  - **F1 Score:** `0.8444` (%84.4)
  - **Confusion Matrix:** `[[6, 7], [0, 19]]` (TN: 6, FP: 7, FN: 0, TP: 19)
- **ONNX Dönüşüm Farkı:** `8.21575746e-08` (sklearn ile ONNX arasındaki maksimum mutlak fark, `< 1e-4` eşiğinin katbekat altında).

---

## 4. PYTHON TESTLERİ

Çalıştırılan komut:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v -rs
```

**Sonuç:** `6 passed in 1.66s` (0 failed, 0 skipped)
- `tests/test_merge_sessions.py::test_merge_deduplicates_and_counts_real_sessions`: **PASSED**
- `tests/test_parite_discovery.py::test_required_onnx_sklearn_parity`: **PASSED** *(Daha önce atlanan test artık geçiyor)*
- `tests/test_site_build.py::test_static_frontend_contract`: **PASSED**
- `tests/test_training_gate.py::test_demo_data_is_not_verified_production`: **PASSED**
- `tests/test_training_gate.py::test_demo_model_is_explicitly_unverified`: **PASSED**
- `tests/test_training_gate.py::test_negative_and_invalid_records_rejected`: **PASSED**

---

## 5. CYPRESS E2E VE DİFERANSİYEL TESTLERİ

Çalıştırılan komut:
```powershell
npx cypress run
```

**Sonuç:** `5 passed in 13s` (0 failed, 0 skipped)

### `cypress/e2e/game.cy.js` (4/4 PASSED):
1. `sekiz kararı tamamlar, başarılı finale ulaşır ve yeniden başlayabilir`: **PASSED**
2. `karar değişimini ilk seçim dışında sayar`: **PASSED**
3. `veri toplama modunda öz bildirim etiketini modelden bağımsız kaydeder`: **PASSED**
4. `model çalışmasa bile oyun çökmez`: **PASSED**

### `cypress/e2e/parite.cy.js` (1/1 PASSED):
1. `ONNX Runtime Web ↔ Python Oracle — aynı 5 referans girdisi için fark < 1e-4`: **PASSED**
   - Referans 1: beklenen = `0.46095584`, web ONNX = `0.46095586`, fark = `1.43e-08`
   - Referans 2: beklenen = `0.95292861`, web ONNX = `0.95292854`, fark = `6.29e-08`
   - Referans 3: beklenen = `0.20893108`, web ONNX = `0.20893109`, fark = `4.55e-09`
   - Referans 4: beklenen = `0.79284133`, web ONNX = `0.79284132`, fark = `1.58e-08`
   - Referans 5: beklenen = `0.20776038`, web ONNX = `0.20776042`, fark = `4.17e-08`

---

## 6. GERÇEK VE SENTETİK OTURUM SAYISI

- **Sentetik Oturum Sayısı:** 15 benzersiz oturum, 120 satır (`data/oturumlar_sentetik_15.csv`).
- **Gerçek Oturum Sayısı:** `data/oturumlar.csv` içinde şu an yalnızca **2 gerçek oturum (16 satır)** ve 5 sentetik satır mevcuttur.
- **Durum Beyanı:** 15 gerçek insan oturumu toplanmadığı için bu gereksinim **akademik dürüstlük kuralı gereğince eksik** olarak raporlanmıştır. Sentetik veriler gerçek veri gibi sunulmamıştır.

---

## 7. GİTHUB, HUGGING FACE VE CANLI OYUN YAYIN DURUMU

> **Önemli:** Dış platformlara (GitHub, Hugging Face) doğrudan yükleme yapabilmek için kişisel kullanıcı kimlik doğrulaması / API token gerekmektedir. Dosyalar ve repolar yerelde %100 hazır duruma getirilmiştir:

1. **GitHub Deposu:**
   - **Durum:** Yerel Git deposu başlatıldı (`master` dalı, commit `ed5ec7f`).
   - `.gitignore` dosyası gereksiz `.venv`, `node_modules`, önbellek ve gizli anahtarları dışlayacak şekilde yapılandırıldı.
   - **Uzak URL:** Kullanıcının GitHub hesabında boş bir public repo açıp `git remote add origin <url>` ve `git push -u origin master` yapması beklenmektedir.
2. **Hugging Face Yayını:**
   - **Durum:** `_out/model/` klasöründe yayınlanmaya hazır üç dosya hazırdır: `model.onnx`, `config.json`, `README.md` (model kartı).
   - **Bağlantı Şablonu:** `https://huggingface.co/<kullanici>/the-primer-v2-model/resolve/<commit>/model.onnx`
   - Kullanıcının Hugging Face hesabına yüklemesi beklenmektedir.
3. **Canlı Oyun (GitHub Pages):**
   - **Durum:** `scripts/build_site.py` çalıştırıldı ve `dist/` klasörü derlendi.
   - İçerisinde `index.html`, `app.js`, `style.css`, `.nojekyll` ve `./model/` yoluyla statik çalışan ONNX modeli mevcuttur.
   - GitHub Pages veya Netlify üzerine sürükle-bırak yöntemiyle 10 saniyede canlıya alınabilir.
4. **Demo Videosu:**
   - **Durum:** `DEMO_SENARYOSU.md` belgesi 60–90 saniyelik çekim için hazırlanmıştır. Gerçek video dosyası henüz kaydedilmemiştir (hazırmış gibi gösterilmemiştir).

---

## 8. TESLİM İÇİN KULLANICININ YAPMASI GEREKEN 5 KISA ADIM

Ödevin son teslim tarihi olan **6 Kasım 2026, 23:59** öncesinde aşağıdaki 5 adımı tamamlayınız:

1. **GitHub Reposu Açın ve Gönderin:**
   ```powershell
   git remote add origin https://github.com/<kullanici-adiniz>/ThePrimer-v2.git
   git branch -M main
   git push -u origin main
   ```
2. **Canlı Oyunu Yayınlayın:**
   - GitHub reponuzda **Settings → Pages** sekmesinden `dist` klasörünü veya `gh-pages` dalını seçerek yayınlayın (veya `dist/` klasörünü Netlify Drop'a bırakın).
3. **Modeli Hugging Face'e Yükleyin:**
   - Hugging Face'te `the-primer-v2-model` isimli public bir model reposu açın.
   - `_out/model/` klasöründeki `model.onnx`, `config.json` ve `README.md` dosyalarını yükleyin. Sabit commit bağlantısını kopyalayın.
4. **(İsteğe Bağlı) Gerçek Oturum Verisi Toplayın:**
   - 15 gerçek arkadaşınıza Veri Toplama Modunu açtırıp CSV indirtin, dosyaları `data/collected/` klasörüne atıp `python scripts/merge_sessions.py "data/collected/*.csv"` ve ardından `python train.py` çalıştırın.
5. **60–90 Saniyelik Ekran Kaydı Alın:**
   - `DEMO_SENARYOSU.md` planına göre hızlıca 1 dakikalık video çekip YouTube / Drive linki olarak teslim formuna ekleyin.
