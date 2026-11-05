# RELEASE — The Primer v2

## v2.0 (aday sürüm, 4 Kasım 2026)

- Sekiz teknik karar ve iki farklı final; ipucu isteği ve adaptif destek.
- Karar süresi, ilk seçim–onay aralığı, seçim değişikliği ve *önceki* hata sayısı.
- Gönüllü Veri Toplama Modu, bağımsız yardım ihtiyacı öz bildirim etiketi, CSV indirme ve birleştirme betiği.
- ONNX browser inference; model yoksa açık hata/fallback, rastgele yüzdeler yok.
- Gerçek oturum asgari sınırı, oturum bazlı train/test ayırma, F1 kapısı ve katı ONNX doğrulaması.
- Python parity oracle, Cypress web parity + regresyon test dosyaları, demo ve belge altyapısı.

**Yayın durumu:** YEREL ADAY. GitHub commit ID: **henüz yok**. Hugging Face commit ID: **henüz yok**. Canlı dağıtım: **henüz yapılmadı**. Gönderimdeki model **demo_unverified** ve 5 sentetik kayıtla eğitilmiştir; üretim modeli değildir. Gerçek yayın yapılmış gibi beyan etmeyin.

## Yayın/rollback prosedürü

1. En az 15 gerçek oturum ve iki hedef sınıf toplandıktan sonra `python train.py` çalıştırın. F1≥0.65 ve `<1e-4` ONNX doğrulaması başarısızsa yeni model oluşturmayın.
2. `python scripts/create_parite.py` ile referansları üretin ve tüm Python+Cypress testlerini çalıştırın.
3. Başarılı modelin `model.onnx`, `config.json`, `README.md` dosyalarını public Hugging Face model reposuna yükleyin ve commit hash'i belgeleyin.
4. Aynı doğrulanmış modelle `python scripts/build_site.py` çalıştırın; web uygulamasını yayınlayın, tarayıcı konsolunu ve gerçek kullanıcı akışlarını kontrol edin.
5. Problem olursa önceki doğrulanmış Hugging Face commit'inden `model.onnx` ve `config.json`'u birlikte geri yükleyip statik paketi yeniden yayınlayın. `_out/model_previous/` yerel son başarılı sürüm için yedektir; commit ID olmadan `main`'e bağımlı kalmayın.

## Güvenli dağıtım planı (henüz uygulanmadı)

- **Shadow (%0 etki):** Yeni modelin kararlarını mevcut modelin kararlarını değiştirmeden karşılaştır; aynı girdilerde olasılık/parite sapmasını, hataları ve gecikmeleri gözle.
- **Canary (%5):** Gönüllü ilk kullanıcı kitlesine yeni modelin rehberlik davranışını aç; hata ve geri alma ölçütlerini kontrol et.
- **Progressive rollout:** %25 → %50 → %100; önceki aşamada hata oranı artmamalı; sorun görülürse eski commit'e rollback.
- **Rollback kriterleri (öneri):** ONNX yükleme başarısızlığı, fark ≥1e-4, kritik UX regresyonu ya da kabul edilemeyen hata oranı. Bu değerler gerçek kullanıcı sonuçlarıyla yeniden değerlendirilir.

## Mimari ödünleşim (trade-off)

| Seçenek | İnternet ve gecikme | Kişisel/oyun verisi | Model gizliliği | Maliyet / bakım |
|---|---|---|---|---|
| Tarayıcı onnxruntime-web (**seçildi**) | İlk JS+model indirirken ağ, sonrasında inference yerel | Girdi cihazda kalır | Model istemciye iner ve görülebilir | Statik, düşük maliyet; model yayınlaması gerekir |
| Mobil cihaz içi ONNX | Uygulama yükleme sırasında ağ, ardından çevrimdışı çalışabilir | Cihaz dışına çıkmaz | APK içinden model çıkarılabilir | Android/iOS bakım ve paketleme gerekir |
| Sunucu FastAPI / Rails | Her istekte ağ, ağ gecikmesi | Tahmin girdileri sunucuya ulaşır; KVKK sorumluluğu artar | Dosya istemciye verilmez ama API üzerinden tersine mühendislik riski vardır | Barındırma, ölçekleme ve güvenlik bakımı gerekir |

Bu seçimin amacı cihazda çıkarım ve gizlilik. Tarayıcının ilk model/JS indirmesi internete bağlıdır, tamamen çevrimdışı kullanım iddiası yoktur.
