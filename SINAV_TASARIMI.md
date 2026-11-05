# Sizinle Uyumlanan Sınav — Bir Sayfalık Klasik Vize Tasarımı

**Senaryo:** The Primer v2'de çalışan sklearn modeli ve tarayıcı ONNX modeli, beş aynı girdi için yardım olasılığı üretir. Python oracle sonucu `0.63120`, web sonucu `0.63126` çıktığında test başarılıdır. Yeni sürüm devreye alındıktan sonra daha önce çalışan bir sahnenin son ekranı açılmaz. Ayrıca model bütün testleri geçmesine rağmen oyuncular, ipucunun yararsız olduğunu bildiriyor.

**Soru (20 dakika, 20 puan):**
1. Python ve web çıktılarını hangi test türüyle karşılaştırırsınız? Tolerans `<1e-4` ise verilen örneğin sonucunu hesaplayıp gerekçelendirin. (5 p)
2. Python tarafı için “test kahini (oracle)” nasıl seçilir? İkinci bir algoritma yazmadan referansın kendisinin yanlış olabileceği iki durumu söyleyin. (4 p)
3. Önceki sürümün gözlenen davranışlarını korumak için karakterizasyon testi, önceki akışların bozulmasını yakalamak için regresyon testi örnekleri yazın. (4 p)
4. “Kod gereksinimi karşılıyor mu?” ile “oyuncu gerçekten öğrenebiliyor mu?” sorularını doğrulama (verification) ve geçerleme (validation) olarak ayırın. (4 p)
5. Model güncellemesini doğrudan %100 kullanıcıya vermek yerine ne yaparsınız ve neden? (3 p)

**Beklenen kavramlar:** Diferansiyel/parite testi, oracle, mutlak fark = 0.00006, hata toleransı, karakterizasyon testi, E2E regresyon, verification–validation farkı, canary ve rollback.

**Çeldiriciler:** “Sayılar birebir eşit olmalı”, “Python oracle yanılmaz”, “Yüksek F1 oyuncunun öğrendiğini kanıtlar”, “Yeni model başarılıysa eski testlere gerek yok”, “testten geçen ürünü herkese aniden açabiliriz”.

**Notlandırma:** Terim ezberi değil, ölçülebilir karar ve doğru gerekçe puanlanır.
