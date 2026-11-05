# Veri toplama klasörü

Oyunun Veri Toplama Modu ile indirilen `oturum-*.csv` dosyalarını buraya kopyalayın. Dosyalar gönüllü katılımcıların gerçek oturumlarından oluşmalı; sentetik test oturumlarını gerçek veri olarak eklemeyin. Sonra proje kökünde:

```powershell
python scripts/merge_sessions.py "data/collected/*.csv"
```

Oturum sayısı farklı `session_id` değerlerinden hesaplanır. Katılımcıların isim veya e-postalarını yazmayın.
