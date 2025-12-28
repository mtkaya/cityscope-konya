# 🏠 CityScope Konya - Lokal Kurulum Rehberi

Bu rehber, projeyi kendi bilgisayarınızda çalıştırmanız için gerekli adımları içerir.

## 📋 Gereksinimler

Sisteminizde aşağıdaki yazılımların yüklü olması gerekiyor:

- Python 3.8 veya üzeri
- Node.js 16 veya üzeri (frontend için)
- Git

## 🚀 Hızlı Başlangıç

### Windows Kullanıcıları

```powershell
# 1. Projeyi indirin
git clone https://github.com/mtkaya/cityscope-konya.git
cd cityscope-konya

# 2. Python sanal ortamı oluşturun (önerilen)
python -m venv venv
venv\Scripts\activate

# 3. Python bağımlılıklarını kurun
pip install -r requirements.txt

# 4. Frontend build edin
cd frontend
npm install
npm run build
cd ..

# 5. Sunucuyu başlatın
python backend\server.py
```

Tarayıcınızda açın: **http://localhost:5555**

---

### Mac/Linux Kullanıcıları

```bash
# 1. Projeyi indirin
git clone https://github.com/mtkaya/cityscope-konya.git
cd cityscope-konya

# 2. Python sanal ortamı oluşturun (önerilen)
python3 -m venv venv
source venv/bin/activate

# 3. Python bağımlılıklarını kurun
pip install -r requirements.txt

# 4. Frontend build edin
cd frontend
npm install
npm run build
cd ..

# 5. Sunucuyu başlatın
python backend/server.py
```

Tarayıcınızda açın: **http://localhost:5555**

---

## 🐳 Docker ile Kurulum (En Kolay)

Eğer Docker Desktop yüklüyse:

```bash
# 1. Projeyi indirin
git clone https://github.com/mtkaya/cityscope-konya.git
cd cityscope-konya

# 2. Docker Compose ile başlatın
docker-compose up --build

# Arka planda çalıştırmak için:
docker-compose up -d --build
```

Tarayıcınızda açın: **http://localhost:5555**

Durdurmak için:
```bash
docker-compose down
```

---

## 🛠️ Geliştirme Modu

Frontend üzerinde geliştirme yapacaksanız:

```bash
# Terminal 1 - Backend
python backend/server.py

# Terminal 2 - Frontend (Hot Reload)
cd frontend
npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:5555

---

## 🔧 Sorun Giderme

### Python Bağımlılıkları Kurulamıyor

**Windows'ta gdal hatası:**
```powershell
# Önce wheel dosyasını indirin:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
pip install GDAL-3.x.x-cp3xx-cp3xx-win_amd64.whl
pip install -r requirements.txt
```

**Mac'te gdal hatası:**
```bash
brew install gdal
pip install -r requirements.txt
```

### Port 5555 Kullanımda

Backend'in portunu değiştirmek için `backend/server.py` dosyasındaki son satırı düzenleyin:

```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

### Frontend Build Hataları

TypeScript hatalarını atlayıp build yapın:
```bash
cd frontend
npx vite build
```

---

## 📊 Veri Dosyaları

İlk çalıştırmada otomatik olarak örnek veriler yüklenir:

- `data/konya_buildings.geojson` - 810 bina
- `data/konya_pois.geojson` - 271 POI
- `data/konya_grid.geojson` - 2,520 grid hücresi

---

## 🌐 API Kullanımı

Sunucu başladığında aşağıdaki endpointler kullanılabilir:

```bash
# Tablo listesi
curl http://localhost:5555/api/tables/list

# Konya verilerini al
curl http://localhost:5555/api/table/konya

# Grid verilerini al
curl http://localhost:5555/api/table/konya/geogrid

# Göstergeleri al
curl http://localhost:5555/api/table/konya/indicators
```

---

## 📞 Yardım

Sorun yaşarsanız:

1. GitHub Issues: https://github.com/mtkaya/cityscope-konya/issues
2. README.md dosyasını kontrol edin
3. Python ve Node.js versiyonlarınızı kontrol edin

---

## ✅ Başarılı Kurulum Kontrolü

Sunucu başladığında şu mesajları görmelisiniz:

```
============================================================
🏙️  CityScope Konya - CityIO Server
============================================================

📊 Konya tablosu yükleniyor...
   ✓ Tablo yüklendi: konya
   • Binalar: 810
   • POI'ler: 271
   • Grid hücreleri: 2520

🚀 Server başlatılıyor: http://localhost:5555
============================================================
```

**Başarılar! 🎉**
