# Veri sözlüğü — `data/oturumlar.csv`

| Sütun | Açıklama | Tip | Birim / aralık |
|---|---|---|---|
| `session_id` | Her oynayışta rastgele oluşan anonim oturum kimliği. Bir oturumun sekiz satırında aynı ID bulunur. | string | UUID; kişisel bilgi değildir |
| `karar_suresi_sn` | Sahnenin açılmasından kararın onaylanmasına kadar süre | float | saniye, ≥0 |
| `onceki_hata_sayisi` | **Mevcut karar öncesindeki** toplam yanlış teknik karar | int | ≥0 |
| `karar_degistirme_sayisi` | İlk seçimi saymadan başka seçeneğe geçiş sayısı | int | ≥0 |
| `sahne_zorlugu` | İlgili teknik görevin sabit zorluğu | int | 1–5 |
| `tereddut_suresi_sn` | İlk seçimden karar onayına kadar geçen süre (psikolojik tereddüdün kesin ölçümü değil) | float | saniye, 0..karar_suresi_sn |
| `yardim_etkisi` | Model hedefi: “Bu karar sırasında yardıma ihtiyaç duydun mu?” öz bildirimi | int | 0=hayır, 1=evet |
| `kaynak` | Kaydın kaynağı | string | `gercek` / `synthetic` |

**Etiket edinimi:** Veri Toplama Modunda otomatik ipucu verilmez, kullanıcı kararını onayladıktan sonra bağımsız öz bildirim sorusu yanıtlar. Etiket oyun içi doğru/yanlış kararından ve AI tahmininden hesaplanmaz. İndirilen CSV'ler dosya bazında birleştirilir; aynı oturum kimliği farklı satırlarda yinelenebilir, farklı oturum sayısı distinct ID sayısıdır.

**Gizlilik:** İsim, e-posta, IP, konum, cihaz kimliği veya hastalık bilgileri kaydedilmez. Katılımcı izin vermediği veriler paylaşılmamalıdır.
