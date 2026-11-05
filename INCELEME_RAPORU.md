# ZIP inceleme / düzeltme raporu — 4 Kasım 2026

## Yüklenen orijinalde saptanan sorunlar

- `package.json` sonunda fazladan virgül olduğundan geçerli JSON değildi.
- `requirements.txt` içinde ONNX sürümü iki kez yazılıydı.
- `train.py`: model tahmini için kritik kontrol `onnxruntime` DLL hatasında atlanıyordu; kabul eşiğine bağlı üretim yayın kapısı 5 sentetik kayıtla güvenilir değildi; oturum bazında ayırma yapılmıyordu; kodda dönüşten sonraki ulaşılamayan tekrarlar vardı.
- `web/app.js`: güncel kararda yapılan hatanın **önceki hata sayısına** dahil edilmesi sızıntı oluşturuyordu. Oyun, gerçek veri toplama ve bağımsız hedef etiketi kaydetme özelliğine sahip değildi.
- `data/oturumlar.csv`: 5 satır tamamen sentetik, gerçek oturum 0.
- Web ile Python parite karşılaştırmasının otomatik gerçek Chromium sürümü yoktu; Python→Python sonucu web testi olarak raporlanmıştı.
- Teslim için README, RELEASE, SINAV_TASARIMI, video senaryosu ve dağıtılabilir statik site dosyaları eksikti.

## Eklenen / düzeltilenler

- Anlaşılır modern Türkçe 8 sahne + 2 final; karar onayı, seçim değiştirme ve tereddüt ölçümleri; gerçek ONNX inference, destek davranışı ve model hatasında fallback.
- Açık rızaya dayalı Veri Toplama Modu, bağımsız 0/1 öz bildirimi, CSV indirme, CSV birleştirme; 15 farklı gerçek oturum sayımı.
- Üretim eğitimi için oturum bazlı ayrım, 15 gerçek oturum zorunluluğu, F1≥0.65 kapısı, ONNX ↔ sklearn paritesi, fail durumunda eski modeli koruma.
- Kullanılabilir `package.json`, Cypress E2E oyun/regresyon ve Web↔Python Oracle parite testleri, 5 Python birim/regresyon testi.
- README, RELEASE (Shadow/Canary/Rollback/trade-off), spec, data dictionary, model kartı, vize tasarımı, demo ve proje anlatımı.
- `scripts/build_site.py` ile yalnızca gerekli frontend+ONNX dosyalarından `dist/` statik web paketi.
- Başlangıç `huggingface-hello-web/` örneği korunmuştur; `.venv`, cache ve node_modules ZIP'e alınmamıştır.

## Gerçekten gerçekleştirilen kontroller

- `python -m pytest tests/ -q -rs`: **5 passed, 1 skipped**. Atlanan test gerçek Python ONNX paritesidir; bu ortamda `onnxruntime` paketi bulunmuyor.
- `node --check web/app.js`: sözdizimi geçti.
- `node --check cypress/e2e/game.cy.js`, `node --check cypress/e2e/parite.cy.js`: sözdizimleri geçti.
- `python scripts/build_site.py`: `dist/` oluşturuldu.

## Henüz doğrulanmamış / kullanıcı tarafından tamamlanması gerekenler

1. **Gerçek veri:** 15 gerçek oturum yok; örnek CSV sentetik. Oturumları topla ve `merge_sessions.py` ile birleştir.
2. **Üretim modeli:** Gerçek veri ile `python train.py`; F1 kapısı ve ONNX Runtime doğrulaması gerçek Windows ortamında geçmeli.
3. **Gerçek tarayıcı testi:** Bu çalışma ortamında tarayıcı yerel URL'leri yönetimsel olarak engelleniyor, ayrıca `onnxruntime` Python paketi yüklenemedi. Bu yüzden yeni sürümün gerçek ONNX ve Cypress testleri burada başarıyla koşturulamadı. Windows'ta `npm start` + `npm run test:e2e` ve `python -m pytest tests -v -rs` çalıştırılmalı.
4. **Yayın:** GitHub repo ve Hugging Face public model reposu henüz açılmadı; commit'e sabit URL yok. `RELEASE.md` gerçek commit hash ile güncellenmeli.
5. **Demo:** Gerçek 60–90 saniyelik ekran kaydı ve erişilebilir bağlantı kullanıcı tarafından hazırlanmalı.

**Özet:** Düzenlenmiş, test altyapısı ve veri toplama özellikleri eklenmiş çalışma kopyasıdır. Bu ZIP'i “100 puan garanti / tüm testler geçti” diye sunmayın; listelenen insan adımları ve gerçek browser testleri tamamlanmalıdır.
