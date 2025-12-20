# 🏙️ CityScope Konya

**MIT CityScope Protokolü ile Uyumlu Kentsel Simülasyon Platformu**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

---

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Veri Kaynakları](#-veri-kaynakları)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## 🌟 Genel Bakış

CityScope Konya, MIT Media Lab City Science Group tarafından geliştirilen CityScope platformunun Konya şehri için özelleştirilmiş versiyonudur. Platform, kentsel planlama kararlarının görselleştirilmesi, simülasyonu ve paydaş katılımını destekler.

### Neden CityScope?

- **Veri Odaklı Kararlar**: Kentsel müdahalelerin etkilerini önceden görün
- **Paydaş Katılımı**: Vatandaş, belediye ve uzmanlar arasında ortak dil
- **Gerçek Zamanlı Simülasyon**: Farklı senaryoları anında karşılaştırın
- **Açık Kaynak**: Tamamen özelleştirilebilir ve genişletilebilir

---

## ✨ Özellikler

### 🗺️ Görselleştirme
- 2D/3D interaktif harita (Deck.gl + MapLibre)
- Bina, POI, yol ve arazi kullanım katmanları
- Isı haritaları ve gösterge panelleri
- Gece/gündüz modları

### 📊 Analiz Modülleri
- **Yürünebilirlik Analizi**: 15 dakikalık şehir metrikleri
- **Nüfus Yoğunluğu**: Demografik dağılım
- **Erişilebilirlik**: Toplu taşıma ve yaya erişimi
- **Yeşil Alan Oranı**: Çevresel göstergeler

### 🎮 Senaryolar
- **Mevcut Durum**: Güncel kentsel yapı
- **Yoğunluk Artışı**: Dikey büyüme senaryosu
- **Yeşil Dönüşüm**: Sürdürülebilir şehir
- **Ulaşım Odaklı**: Transit-oriented development

### 🔌 Entegrasyonlar
- Konya Kent Bilgi Sistemi uyumlu
- ADNKS-GIS protokol desteği
- OpenStreetMap veri entegrasyonu
- CityIO API uyumluluğu

---

## 🚀 Kurulum

### Gereksinimler

```bash
# Python 3.8+
python --version

# Node.js 16+ (opsiyonel, geliştirme için)
node --version
```

### Hızlı Başlangıç

```bash
# 1. Repo'yu klonla
git clone https://github.com/mtkaya/cityscope-konya.git
cd cityscope-konya

# 2. Python bağımlılıklarını kur
pip install -r requirements.txt

# 3. Örnek verileri oluştur
python data/generate_sample_data.py

# 4. Backend sunucuyu başlat
python backend/server.py

# 5. Tarayıcıda aç
open http://localhost:5000/frontend/index.html
```

### Docker ile Kurulum

```bash
# Docker image oluştur
docker build -t cityscope-konya .

# Container başlat
docker run -d -p 5000:5000 cityscope-konya

### Docker Compose ile Çalıştırma

```bash
# Servisi başlat
docker-compose up -d --build

# Logları izle
docker-compose logs -f
```
```

---

## 💻 Kullanım

### Web Arayüzü

1. Tarayıcıda `http://localhost:5000/frontend/index.html` adresini açın
2. Sol panelden katmanları açıp kapatın
3. Üst menüden senaryo seçin
4. Harita üzerinde tıklayarak detay görün

### Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| `B` | Binalar katmanı |
| `P` | POI katmanı |
| `G` | Grid katmanı |
| `R` | Yollar katmanı |
| `3` | 3D görünüm |
| `N` | Gece modu |
| `H` | Ana görünüme dön |

### API Kullanımı

```python
import requests

# Tablo listesi
response = requests.get('http://localhost:5000/api/tables/list')
print(response.json())

# Konya verileri
response = requests.get('http://localhost:5000/api/table/konya')
data = response.json()

# Senaryo uygula
response = requests.post(
    'http://localhost:5000/api/table/konya/scenario',
    json={'scenario': 'green'}
)
```

---

## 📚 API Dokümantasyonu

### Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/tables/list` | Mevcut tabloları listele |
| GET | `/api/table/{name}` | Tablo verilerini al |
| GET | `/api/table/{name}/geogrid` | Grid verilerini al |
| GET | `/api/table/{name}/indicators` | Göstergeleri al |
| GET | `/api/table/{name}/buildings` | Bina verilerini al |
| GET | `/api/table/{name}/pois` | POI verilerini al |
| POST | `/api/table/{name}/geogrid` | Grid güncelle |
| POST | `/api/table/{name}/scenario` | Senaryo uygula |

### Veri Formatları

#### GeoGrid Feature
```json
{
  "type": "Feature",
  "properties": {
    "id": 1,
    "walkability": 72.5,
    "building_density": 0.65,
    "green_ratio": 0.18,
    "land_use": "residential"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[lon, lat], ...]]
  }
}
```

#### Indicator
```json
{
  "name": "Yürünebilirlik",
  "value": 72.5,
  "unit": "puan",
  "description": "Ortalama yürünebilirlik skoru"
}
```

---

## 📁 Veri Kaynakları

### Mevcut Veriler

| Dosya | İçerik | Kaynak |
|-------|--------|--------|
| `konya_buildings.geojson` | Bina footprint'leri | Örnek veri |
| `konya_pois.geojson` | İlgi noktaları | Örnek veri |
| `konya_roads.geojson` | Yol ağı | Örnek veri |
| `konya_grid.geojson` | Analiz gridi | Hesaplanmış |
| `konya_config.json` | Tablo konfigürasyonu | Sistem |

### Gerçek Veri Entegrasyonu

Konya Büyükşehir Belediyesi Kent Bilgi Sistemi'nden alınabilecek veriler:

1. **Bina Envanteri**: Kat sayısı, yapı tipi, yaş
2. **Nüfus Verileri**: ADNKS entegrasyonu
3. **İmar Planları**: Arazi kullanım zonları
4. **Altyapı**: KOSKİ, MEDAŞ, Gaznet
5. **Ulaşım**: Tramvay, otobüs hatları

### Veri Toplama

```bash
# OpenStreetMap verilerini çek (network gerekli)
python data/fetch_konya_data.py

# Belediye verilerini dönüştür
python data/convert_kbs_data.py --input belediye_data.shp
```

---

## 🏗️ Proje Yapısı

```
cityscope-konya/
├── frontend/
│   ├── index.html          # Ana uygulama
│   └── assets/             # Statik dosyalar
├── backend/
│   ├── server.py           # Flask API sunucusu
│   └── modules/            # Analiz modülleri
├── data/
│   ├── konya_buildings.geojson
│   ├── konya_pois.geojson
│   ├── konya_grid.geojson
│   ├── konya_roads.geojson
│   ├── konya_config.json
│   ├── generate_sample_data.py
│   └── fetch_konya_data.py
├── docs/
│   ├── belediye_sunumu.md
│   └── teknik_dokumantasyon.md
├── modules/
│   ├── walkability/
│   ├── mobility/
│   └── indicators/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Repo'yu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

### Geliştirme Fikirleri

- [ ] Trafik simülasyonu (SUMO entegrasyonu)
- [ ] Gürültü haritalaması
- [ ] Enerji tüketim analizi
- [ ] Deprem risk haritası
- [ ] Mobil uygulama
- [ ] AR/VR desteği

---

## 📞 İletişim

- **Proje**: [GitHub Issues](https://github.com/mtkaya/cityscope-konya/issues)
- **MIT CityScope**: [cityscope.media.mit.edu](https://cityscope.media.mit.edu)
- **Konya KBS**: kentbilgisistemi@konya.bel.tr

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🙏 Teşekkürler

- [MIT Media Lab City Science Group](https://www.media.mit.edu/groups/city-science/overview/)
- [Konya Büyükşehir Belediyesi](https://www.konya.bel.tr)
- [OpenStreetMap Contributors](https://www.openstreetmap.org)

---

<p align="center">
  <strong>🏙️ Konya için Akıllı Şehir Çözümleri</strong><br>
  <em>Veri Odaklı • Katılımcı • Sürdürülebilir</em>
</p>
