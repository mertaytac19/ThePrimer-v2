# Spec — The Primer v2: Hata Avcısı

## Problem, hedef ve girdi sözleşmesi

Yazılım mühendisliği oyununda kullanıcının yardıma ihtiyaç duyduğunu **öz bildirime göre** öngören küçük bir model geliştirilir. Sınıflar: `0 = yardıma ihtiyacım yok`, `1 = yardıma ihtiyacım var`.

Önceden belirlenmiş sıra ve tip (her biri `float32` ONNX girdisi):

1. `karar_suresi_sn` — sahne gösteriminden karar onayına kadar saniye
2. `onceki_hata_sayisi` — **mevcut karar verilmeden önceki** hatalı teknik karar sayısı
3. `karar_degistirme_sayisi` — ilk seçim sayılmaksızın farklı seçeneğe geçiş sayısı
4. `sahne_zorlugu` — 1–5 arası zorluk
5. `tereddut_suresi_sn` — ilk seçimden kararı onaylamaya kadar saniye (psikolojik tanı değil)

Hedef: `yardim_etkisi` (0/1; oyuncunun onay sonrasında, AI ipucu verilmeden önceki öz bildirimi). Veri sözlüğü: `data/SOZLUK.md`.

## Ürün özellikleri

- Sekiz anlamlı teknik karar; doğru/yanlış geri bildirimi, iki final, yeniden oynama.
- Gönüllü Normal Oyun ve Veri Toplama Modu. Model yüksek olasılık ürettiğinde sahne **karar kesinleşmeden önce** bağlamsal destek önerilir. Oyuncu manuel ipucu isteyebilir; bu yapay zekâ kararı olarak gösterilmez.
- Model yoksa oyun çalışır, tahmin uydurulmaz ve anlaşılır uyarı verilir.
- Her kararın öz bildirimi, rastgele `session_id` ve `kaynak=gercek` sütunuyla CSV'ye kaydedilir. Kimlik, e-posta, cihaz kimliği, konum toplanmaz.
- Tercihler, veri indirilmedikçe yalnızca tarayıcının geçici belleğindedir.
- Geliştirici paneli model durumunu, girdi sırasını ve gerçek tahminleri gösterir.

## Model kabul eşiği (eğitimden önce ilan edilmiş)

- **Pozitif sınıf F1 ≥ 0.65**. Minimum **15 gerçek, farklı oturum**. Train/test ayrımı `session_id` üzerinde yapılır; aynı oturum iki tarafta bulunamaz; her tarafta iki sınıf olmalıdır.
- Yalnız sentetik veri için `--demo` etiketli prototip üretilir; metrik doğrulanmış üretim skoru değildir.
- Kabul eşiğini geçmeyen model veya ONNX ile sklearn arasında `max(abs(p_onnx-p_sklearn)) >= 1e-4` fark üreten model yayınlanmaz; eski model korunur.
- Web–Python diferansiyel testi: `tests/parite.json` içinde gerçek sklearn Oracle'ın beş referans olasılığı; Chromium'daki gerçek ONNX Runtime Web ile her biri **`<1e-4`** olmalı.
- Dağıtım adımları: commit'e sabit HF repo, Shadow/Canary/Progressive/Rollback senaryoları (`RELEASE.md`).

## Üç yeni kabul örneği

1. **Zorlanan oyuncu:** Yüksek olasılık verdiği bilinen gerçek bir referans girdi oyunda karar onaylanmadan önce işlenirse bağlamsal destek gösterilir. Aynı karar sonrası önceden alınmış öz bildirim hedefiyle test edilir. (Modelin her yavaş oyuncuya otomatik olarak yüksek olasılık vereceği iddia edilmez.)
2. **Rahat ilerleyen oyuncu:** Düşük olasılık verdiği doğrulanan referans girdide otomatik ipucu açılmaz; kullanıcı manuel isteği ayrı işaretlenir.
3. **Model yok:** CDN veya model dosyası erişilemezse oyun bozulmaz; sonuç sahnesine ilerlenebilir ve sahte olasılık sunulmaz.

## Sınırlar / geçerleme

Yükleme süresi ağdan etkilenir, sabit 2 saniyelik garanti yoktur. Geçerli teknik sonucun üretilmesi (verification), oyuncunun gerçekten daha iyi öğrendiği anlamına gelmez (validation); bunu ayrı kullanıcı değerlendirmeleriyle incelemek gerekir. Kısıtlı gerçek veri ve ara karar anındaki dağılım kayması önemli risklerdir.
