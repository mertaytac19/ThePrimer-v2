# Hocaya anlatım rehberi — The Primer v2

## 30 saniyelik anlatım

“Yazılım mühendisliği konulu sekiz karar sahnesi geliştirdik. Oyuncunun önceki hata sayısını, karar süresini, seçim değiştirmesini, sahne zorluğunu ve ilk seçim–onay süresini ölçüyoruz. Bu beş özelliği küçük lojistik regresyon modeline veriyoruz. Model ONNX formatına dönüştürülüp tarayıcıda çalışıyor ve gerektiğinde onay öncesi ipucu sunuyor. Python Oracle ile web çıktısının aynı girdi için `1e-4` tolerans içinde eşleşmesini diferansiyel testle; önceki oyun akışlarının bozulmamasını Cypress regresyon testleriyle doğrulamayı hedefliyoruz.”

## Kavramlar

- **Development:** Gerçek kullanıcı verisi + eğitim + önceden belirlenmiş F1 kabul kapısı.
- **Deployment:** HF modeli commit'e sabitleme, sürüm/rollback ve yayın stratejisi.
- **Inference:** Eğitimden çıkan modelin yeni oyuncu özellikleriyle olasılık üretmesi.
- **ONNX:** sklearn ile eğitilen modeli JS/Python gibi farklı ortamlarda kullanmaya yarayan taşınabilir biçim.
- **Test kahini (oracle):** Beklenen sonucu hesaplayan referans Python uygulaması; onun da doğruluğu kontrol edilir.
- **Diferansiyel test:** Aynı girişte Python ve tarayıcı modeli olasılıklarının farkının `<0.0001` olması.
- **Regresyon testi:** Yapay zekâ eklendiğinde oyun başlangıcı, sahne geçişi, iki final ve yeniden başlatmanın bozulmaması.
- **Karakterizasyon testi:** Eski sürümün gözlenen davranışını kaydederek yeni sürümle kıyaslama.
- **Verification / Validation:** Ürün gereksinimlere uygun mu / Kullanıcının gerçek öğrenme ihtiyacını karşılıyor mu?
- **3V:** Velocity (hız), Validation (doğrulama), Versioning (sürümleme).
- **Shadow:** Yeni model karar verir ama gerçek oyuncu deneyimini etkilemez.
- **Canary:** Yeni model önce küçük bir gruba açılır.
- **Rollback:** Sorun olursa önceki doğrulanmış model commit'ine dönülür.

## Hoca ne sorabilir?

**“Model ne öğreniyor?”** Kullanıcının *kendi bildirdiği* yardım ihtiyacı ile beş davranış özelliği arasındaki ilişkiyi. Oyun doğru/yanlışını değil.

**“Hatanız ve çözümünüz?”** Önceki kodda karar sonucu hata sayacına erken ekleniyordu; bu veri sızıntısına yol açıyordu. Artık tahmin girdisinde sadece önceki hatalar var.

**“F1 niye 1.0?”** Eski rapor beş sentetik satırla hesaplanmıştı; gerçek geçerleme kabul edilemez. Yeni kod bunu `demo_unverified` olarak ayırıyor, üretim için 15 gerçek oturum istiyor.

**“Parite nasıl kanıtlanır?”** Python sklearn Oracle beş referans olasılığını `parite.json` dosyasına yazar; gerçek browser ONNX aynı girişlere tahmin yapar, Cypress farkın `<1e-4` olduğunu doğrular. Python içinde iki sonucu karşılaştırmak web paritesi değildir.

**“Zayıf noktalar?”** Veri azlığı, etiketlerin öz bildirimle gelmesi, aynı kişiden çok oturum, modelin karar esnasındaki ara özelliklerle eğitimin final özelliklerinin dağılım farkı. Kodun geçerli çalışması oyuncuya fayda kanıtı değildir.
