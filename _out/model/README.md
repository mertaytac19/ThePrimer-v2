# The Primer v2 — Model Kartı

**Durum:** `demo_unverified`.

## Amaç
Küçük lojistik regresyon modeli, oyuncunun bildirdiği yardım ihtiyacı etiketini oyun davranışlarından tahmin eder.

## Veri
Eğitim satırı: 120. Bağımsız gerçek oturum sayısı: 0. Kaynak: data/oturumlar.csv.

## Ölçüm
Oturum bazlı veri ayrımı; üretim kabul koşulu F1 ≥ 0.65. Metrikler: `{"accuracy": 0.78125, "precision": 0.730769, "recall": 1.0, "f1": 0.844444, "confusion_matrix": [[6, 7], [0, 19]], "train_rows": 88, "test_rows": 32, "train_sessions": 11, "test_sessions": 4, "evaluation_type": "demo_session_split_synthetic_eval"}`. ONNX–sklearn maksimum fark: 8.21575746e-08.

## Sınırlamalar
Bu bir sağlık/eğitim başarısı tanısı değildir; öz bildirim yanıltıcı olabilir, az veriyle genelleme güvenilir değildir. Karar verme sırasında alınan ara özellikler ile eğitimdeki final-özellik dağılımı farklılık gösterebilir.

## Kullanılmaması gereken durumlar
Kritik güvenlik, sağlık, disiplin ve öğrenci puanlama kararlarında kullanılmamalıdır.
