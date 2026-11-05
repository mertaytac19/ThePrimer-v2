# 60–90 saniyelik demo video planı

**0–10 sn:** The Primer v2 açılışı; Oyun Modu seçilir, ONNX durum etiketi gösterilir.

**10–30 sn:** Aynı sahnede seçim, değişiklik sayısı, karar süresi ve ilk seçim–onay süresi geliştirme panelinde gösterilir. Gerçek modelden gelen olasılık açıklanır.

**30–45 sn:** Yavaş/kararsız oyuncu davranışıyla sahne başlatılır. Model yüksek olasılık üretiyorsa onay öncesi bağlamsal ipucu görünür. Her durumda gerçek çıktı kullanılır; zorla yüzde üretmeyin.

**45–60 sn:** Yeniden başlanır, hızlı/az hata yapan oyuncu davranışı gösterilir. Model düşük olasılık veriyorsa otomatik ipucu gizli kalır. Model aynı kararı veriyorsa farklı gerçek veri örnekleri deneyin, videoyu manipüle etmeyin.

**60–75 sn:** Veri Toplama Modu: ipucu olmadan karar ve bağımsız yardım ihtiyacı sorusu gösterilir, CSV indirilir.

**75–90 sn:** Python Oracle ile Cypress `<1e-4` parite testi sonucu ve çalışan yayın linkleri gösterilir; yalnız gerçek test sonucu ekran kaydı alınır.

Bu belge **video değildir**. Ekran kaydını kullanıcı alıp herkese açık bir bağlantıyla teslim etmelidir.
