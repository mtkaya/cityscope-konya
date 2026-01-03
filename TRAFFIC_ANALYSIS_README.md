# 🛰️ Trafik Yoğunluğu Analizi - Uydu Görüntüleri

Bu modül, Sentinel Hub uydu görüntülerinden YOLO modeli kullanarak gerçek zamanlı trafik yoğunluğu analizi yapar.

## 🎯 Özellikler

- **Otomatik Uydu Görüntü Toplama**: Sentinel Hub API ile saatlik uydu görüntüsü alımı
- **AI Tabanlı Araç Tespiti**: YOLOv8 modeli ile araç sayısı ve tür tespiti
- **Trafik Yoğunluğu Skoru**: 0-100 arası yoğunluk skoru hesaplama
- **Zamanlanmış Analiz**: Her saat otomatik analiz çalışması
- **Manuel Tetikleme**: API üzerinden istediğiniz zaman analiz başlatma
- **Özel Alan Analizi**: Belirlediğiniz koordinatlar için analiz

## 🏗️ Mimari

```
┌─────────────────┐
│  Sentinel Hub   │ ← Uydu görüntüsü (saatte bir)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Image Service  │ → Görüntü işleme ve önbellek
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLO Service   │ → Araç tespiti (YOLOv8)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Database       │ → Sonuçları kaydet
│  (SQLite/PG)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  REST API       │ → Frontend'e veri sun
└─────────────────┘
```

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 2. Sentinel Hub Hesabı Oluştur

1. [Sentinel Hub](https://www.sentinel-hub.com/) sitesine git
2. Ücretsiz hesap oluştur (trial 1 ay)
3. Dashboard'dan OAuth credentials oluştur
4. Client ID ve Client Secret'i kopyala

### 3. Environment Variables Ayarla

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
SENTINEL_CLIENT_ID=your_actual_client_id
SENTINEL_CLIENT_SECRET=your_actual_client_secret
```

### 4. YOLO Modelini İndir

İlk çalıştırmada model otomatik indirilecek. Manuel indirmek için:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## 📡 API Endpoints

### Trafik Yoğunluğu Verileri

#### En Son Veriler
```http
GET /traffic/density/latest?limit=100
```

**Response:**
```json
[
  {
    "id": 1,
    "latitude": "37.8716",
    "longitude": "32.4851",
    "density_score": 65,
    "vehicle_count": 324,
    "analyzed_at": "2025-01-03T10:00:00Z",
    "satellite_image_id": "konya_sentinel_20250103_100000"
  }
]
```

#### Belirli Alan İçin Veriler
```http
GET /traffic/density/area?min_lon=32.4351&min_lat=37.8216&max_lon=32.5351&max_lat=37.9216&hours=24
```

### Uydu Görüntüleri

#### İşlenmiş Görüntü Listesi
```http
GET /traffic/satellite/images?limit=10&status=completed
```

**Response:**
```json
[
  {
    "id": 1,
    "image_id": "konya_sentinel_20250103_100000",
    "bbox": "[32.4351, 37.8216, 32.5351, 37.9216]",
    "capture_time": "2025-01-03T10:00:00Z",
    "processed_at": "2025-01-03T10:05:00Z",
    "processing_status": "completed",
    "vehicle_detections": 324
  }
]
```

### Analiz Tetikleme

#### Manuel Analiz Başlat
```http
POST /traffic/analyze/trigger
```

**Response:**
```json
{
  "status": "started",
  "message": "Traffic analysis has been triggered and will run in the background"
}
```

#### Özel Alan Analizi
```http
POST /traffic/analyze/custom?min_lon=32.45&min_lat=37.85&max_lon=32.50&max_lat=37.90
```

**Response:**
```json
{
  "status": "started",
  "message": "Analyzing area: [32.45, 37.85, 32.50, 37.90]",
  "bbox": [32.45, 37.85, 32.50, 37.90]
}
```

### İstatistikler

#### Özet İstatistikler
```http
GET /traffic/stats/summary?hours=24
```

**Response:**
```json
{
  "time_range_hours": 24,
  "total_records": 24,
  "avg_density_score": 58.5,
  "max_density_score": 89,
  "min_density_score": 23,
  "total_vehicles_detected": 7824,
  "avg_vehicles_per_area": 326
}
```

## ⚙️ Konfigürasyon

### YOLO Model Seçimi

Model boyutu ve hız/doğruluk dengesi:

| Model | Boyut | Hız | Doğruluk | Kullanım |
|-------|-------|-----|----------|----------|
| yolov8n | 6 MB | ⚡⚡⚡ | ⭐⭐ | Gerçek zamanlı, düşük kaynak |
| yolov8s | 22 MB | ⚡⚡ | ⭐⭐⭐ | Dengeli |
| yolov8m | 52 MB | ⚡ | ⭐⭐⭐⭐ | Yüksek doğruluk |
| yolov8l | 87 MB | 🐌 | ⭐⭐⭐⭐⭐ | Maksimum doğruluk |

Varsayılan: `yolov8n.pt` (hız için)

Değiştirmek için `backend/app/services/yolo_service.py`:
```python
VehicleDetectionService(model_name="yolov8s.pt")
```

### Analiz Sıklığı

Varsayılan: Her 1 saat

Değiştirmek için `backend/app/services/scheduler.py`:
```python
trigger=IntervalTrigger(hours=2)  # 2 saatte bir
# veya
trigger=IntervalTrigger(minutes=30)  # 30 dakikada bir
```

### Uydu Görüntü Çözünürlüğü

Varsayılan: 10 metre/piksel

Değiştirmek için `backend/app/services/sentinel_service.py`:
```python
resolution=5  # 5 metre/piksel (daha detaylı ama daha yavaş)
```

## 🧪 Test

### Manuel Test

```bash
# API'yi başlat
cd backend
uvicorn app.main:app --reload

# Başka terminalde test et
curl http://localhost:8000/traffic/analyze/trigger -X POST
```

### Python ile Test

```python
import requests

# Analiz tetikle
response = requests.post("http://localhost:8000/traffic/analyze/trigger")
print(response.json())

# Sonuçları kontrol et (5 dakika sonra)
response = requests.get("http://localhost:8000/traffic/density/latest?limit=1")
print(response.json())
```

## 📊 Database Şeması

### `traffic_density` Tablosu
```sql
CREATE TABLE traffic_density (
    id INTEGER PRIMARY KEY,
    latitude VARCHAR,
    longitude VARCHAR,
    density_score INTEGER,  -- 0-100
    vehicle_count INTEGER,
    analyzed_at DATETIME,
    satellite_image_id VARCHAR
);
```

### `satellite_images` Tablosu
```sql
CREATE TABLE satellite_images (
    id INTEGER PRIMARY KEY,
    image_id VARCHAR UNIQUE,
    bbox VARCHAR,
    capture_time DATETIME,
    processed_at DATETIME,
    processing_status VARCHAR,  -- pending, processing, completed, failed
    vehicle_detections INTEGER
);
```

## 🐛 Troubleshooting

### Sentinel Hub Hatası
```
ValueError: Sentinel Hub credentials not found
```

**Çözüm**: `.env` dosyasında credentials'ları kontrol edin.

### YOLO İndirme Hatası
```
Error downloading YOLO model
```

**Çözüm**:
```bash
# Manuel indir
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
# Model dosyasını projeye kopyala
```

### Scheduler Başlamıyor
```
Warning: Could not start scheduler
```

**Çözüm**: Credentials eksik olabilir. API yine de çalışır, manual tetikleme kullanın.

### Düşük Tespit Doğruluğu

- Daha büyük model kullanın (`yolov8m` veya `yolov8l`)
- Görüntü çözünürlüğünü artırın (`resolution=5`)
- Confidence threshold'u düşürün (varsayılan: 0.25)

## 💡 Kullanım Örnkleri

### Örnek 1: Rush Hour Analizi
```python
# Sabah 8-9 arası trafik yoğunluğunu analiz et
response = requests.get(
    "http://localhost:8000/traffic/stats/summary",
    params={"hours": 1}
)
data = response.json()
print(f"Ortalama yoğunluk: {data['avg_density_score']}/100")
```

### Örnek 2: Şehir Merkezi Trafik Haritası
```python
# Konya merkez için grid analizi
response = requests.post(
    "http://localhost:8000/traffic/analyze/custom",
    params={
        "min_lon": 32.4351,
        "min_lat": 37.8216,
        "max_lon": 32.5351,
        "max_lat": 37.9216
    }
)
```

### Örnek 3: Haftalık Trend Analizi
```python
# Son 7 günün verilerini al
response = requests.get(
    "http://localhost:8000/traffic/density/latest",
    params={"limit": 168}  # 7 gün * 24 saat
)
data = response.json()

# Ortalama hesapla
avg_by_hour = {}
for record in data:
    hour = datetime.fromisoformat(record['analyzed_at']).hour
    if hour not in avg_by_hour:
        avg_by_hour[hour] = []
    avg_by_hour[hour].append(record['density_score'])

for hour, scores in avg_by_hour.items():
    print(f"Saat {hour:02d}: Ort. yoğunluk {sum(scores)/len(scores):.1f}")
```

## 🚀 Production Deployment

### 1. Resource Requirements
- RAM: Minimum 4GB (YOLO model için)
- Disk: 2GB (model + görüntü cache)
- CPU: 2+ cores önerilir

### 2. Optimizasyon
```bash
# Batch processing için
# yolo_service.py'de batch inference kullan
model.predict(images_batch, batch=True)
```

### 3. Monitoring
```bash
# Log dosyalarını izle
tail -f logs/traffic_analysis.log
```

## 📝 Lisans

MIT License - CityScope Konya Projesi

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Commit edin
4. Push edin
5. Pull Request açın

## 📧 İletişim

Sorularınız için: GitHub Issues
