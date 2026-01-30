# Log Analaizi ve Tespit Sistemi

Bu proje, siber güvenlik farkındalığı oluşturmak amacıyla geliştirilmiş; sistem loglarını kural tabanlı analiz eden ve gerçek zamanlı izleme yapan bir SIEM prototipidir.

## Kurulum ve Çalıştırma
Projeyi Docker üzerinden ayağa kaldırmak için:

```bash
docker-compose up --build
İnteraktif modda çalıştırmak için:
docker compose run -it log-analyzer
