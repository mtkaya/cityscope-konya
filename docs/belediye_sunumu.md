# CityScope Konya
## Konya Büyükşehir Belediyesi için Kentsel Simülasyon Platformu

---

## 📋 Yönetici Özeti

CityScope Konya, MIT Media Lab tarafından geliştirilen ve dünya genelinde 50'den fazla şehirde kullanılan CityScope platformunun Konya'ya uyarlanmış versiyonudur. Platform, kentsel planlama kararlarının **veri odaklı**, **görsel** ve **interaktif** bir şekilde değerlendirilmesini sağlar.

### Temel Değer Önerisi

| Geleneksel Planlama | CityScope ile Planlama |
|---------------------|------------------------|
| Statik haritalar ve raporlar | İnteraktif 3D görselleştirme |
| Uzman odaklı karar alma | Paydaş katılımlı süreç |
| Sonuçları önceden görememe | Gerçek zamanlı simülasyon |
| Parçalı veri sistemleri | Entegre veri platformu |

---

## 🎯 Proje Hedefleri

### Kısa Vadeli (6 ay)
- ✅ Konya merkez için pilot uygulama
- ✅ Kent Bilgi Sistemi veri entegrasyonu
- ✅ Temel göstergelerin (yürünebilirlik, yoğunluk) hesaplanması
- ⏳ Belediye personeli eğitimi

### Orta Vadeli (1 yıl)
- Tüm Konya metropoliten alanına genişleme
- Ulaşım simülasyonu (tramvay, otobüs)
- Vatandaş katılım modülü
- Akıllı Şehirler Portalı entegrasyonu

### Uzun Vadeli (2-3 yıl)
- Deprem risk analizi entegrasyonu
- İklim değişikliği senaryoları
- Yapay zeka destekli tahminler
- Diğer Anadolu şehirlerine ölçekleme

---

## 💡 Kullanım Senaryoları

### 1. İmar Planı Değerlendirme
Yeni imar planlarının nüfus yoğunluğu, trafik ve yeşil alan üzerindeki etkilerini önceden görün.

**Örnek**: Mevlana çevresinde kat artışı yapıldığında:
- Nüfus yoğunluğu: +35%
- Yürünebilirlik skoru: -12 puan
- Trafik yükü: +40%

### 2. Ulaşım Planlaması
Yeni tramvay hatlarının ve otobüs güzergahlarının erişilebilirlik üzerindeki etkisi.

**Örnek**: Selçuklu-Meram tramvay hattı:
- 15 dakika erişim alanı: +25%
- Etkilenen nüfus: 180,000 kişi
- Tahmini yolcu sayısı: 45,000/gün

### 3. Kentsel Dönüşüm
Dönüşüm alanlarında farklı yoğunluk senaryolarını karşılaştırın.

### 4. Afet Hazırlık
Deprem sonrası toplanma alanları ve tahliye güzergahları analizi.

### 5. Vatandaş Katılımı
Mahalle toplantılarında interaktif planlama oturumları.

---

## 🔧 Teknik Altyapı

### Mevcut Kent Bilgi Sistemi ile Entegrasyon

```
┌─────────────────────────────────────────────────────────┐
│                    CityScope Konya                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │  CityScopeJS │   │   CityIO     │   │   Modüller   │ │
│  │  (Frontend)  │◄──│   (API)      │◄──│  (Analiz)    │ │
│  └──────────────┘   └──────────────┘   └──────────────┘ │
│         ▲                  ▲                  ▲         │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────┐
│         ▼                  ▼                  ▼         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │  Bina        │   │  ADNKS       │   │  KOSKİ       │ │
│  │  Envanteri   │   │  Nüfus       │   │  Altyapı     │ │
│  └──────────────┘   └──────────────┘   └──────────────┘ │
│                                                          │
│            Konya Kent Bilgi Sistemi                      │
└─────────────────────────────────────────────────────────┘
```

### Veri Akışı

1. **Girdi Verileri**: KBS'den bina, nüfus, altyapı verileri
2. **İşleme**: CityIO API'si ile veri standardizasyonu
3. **Analiz**: Modüller ile gösterge hesaplama
4. **Görselleştirme**: Web arayüzünde interaktif sunum

---

## 📊 Gösterge Paneli

### Temel Metrikler

| Gösterge | Açıklama | Veri Kaynağı |
|----------|----------|--------------|
| Yürünebilirlik | 15 dk içinde erişilebilen hizmet sayısı | POI + Yol ağı |
| Nüfus Yoğunluğu | km² başına düşen kişi sayısı | ADNKS |
| Yeşil Alan Oranı | Yeşil alan / Toplam alan | İmar planı |
| Erişilebilirlik | Toplu taşıma erişim skoru | Ulaşım verileri |
| Bina Yoğunluğu | Emsal (KAKS) değeri | Bina envanteri |

### Senaryo Karşılaştırma

| Senaryo | Yürünebilirlik | Nüfus | Yeşil | Erişim |
|---------|----------------|-------|-------|--------|
| Mevcut | 72 | 8.4K | 18% | 84 |
| Yoğunluk+ | 65 | 12.1K | 12% | 78 |
| Yeşil Dönüşüm | 85 | 7.2K | 35% | 88 |
| Ulaşım Odaklı | 88 | 9.8K | 22% | 95 |

---

## 💰 Maliyet ve Kaynak Analizi

### Uygulama Maliyetleri

| Kalem | Tutar (TL) | Açıklama |
|-------|------------|----------|
| Yazılım Geliştirme | - | Açık kaynak, ücretsiz |
| Sunucu Altyapısı | 50,000/yıl | Bulut veya yerinde |
| Veri Entegrasyonu | 150,000 | Tek seferlik |
| Eğitim | 30,000 | Personel eğitimi |
| Bakım | 40,000/yıl | Teknik destek |
| **Toplam (İlk Yıl)** | **270,000** | |
| **Toplam (Sonraki)** | **90,000/yıl** | |

### Potansiyel Faydalar

- Planlama süreçlerinde %30 zaman tasarrufu
- Veri odaklı kararlarla maliyet optimizasyonu
- Vatandaş katılımı ile sosyal kabul artışı
- Akıllı Şehirler sıralamasında yükseliş

---

## 🗓️ Uygulama Takvimi

### Faz 1: Hazırlık (Ay 1-2)
- [x] Teknik gereksinim analizi
- [x] Örnek veri seti oluşturma
- [x] Prototip geliştirme
- [ ] Paydaş görüşmeleri

### Faz 2: Pilot (Ay 3-6)
- [ ] Mevlana bölgesi pilot uygulaması
- [ ] KBS veri entegrasyonu
- [ ] Personel eğitimi
- [ ] Kullanıcı geri bildirimleri

### Faz 3: Genişleme (Ay 7-12)
- [ ] Tüm merkez ilçelere genişleme
- [ ] Ek modül geliştirme (ulaşım, enerji)
- [ ] Vatandaş arayüzü
- [ ] Performans optimizasyonu

---

## 🌍 Referans Projeler

CityScope dünya genelinde başarıyla uygulanmıştır:

| Şehir | Proje | Odak |
|-------|-------|------|
| Hamburg, Almanya | Finding Places | Mülteci yerleşimi |
| Andorra | CityScope Andorra | Turizm ve trafik |
| Boston, ABD | Volpe | Kentsel dönüşüm |
| Roma, İtalya | 15 Minute City | Erişilebilirlik |
| Kharkiv, Ukrayna | Masterplan | Yeniden yapılanma |

---

## 📞 İletişim ve Sonraki Adımlar

### Önerilen Aksiyonlar

1. **Teknik değerlendirme toplantısı** - KBS ekibi ile
2. **Pilot bölge belirleme** - İmar Dairesi ile
3. **Veri paylaşım protokolü** - Hukuk birimi ile
4. **Bütçe planlaması** - Mali hizmetler ile

### İletişim

- **Proje Koordinatörü**: [Ad Soyad]
- **E-posta**: proje@konya.bel.tr
- **MIT CityScope**: cityio.media.mit.edu

---

## 📎 Ekler

- Ek A: Teknik Dokümantasyon
- Ek B: API Referansı
- Ek C: Veri Sözlüğü
- Ek D: Ekran Görüntüleri

---

<div align="center">

**CityScope Konya**

*Veri Odaklı Şehir Planlaması için Açık Platform*

MIT Media Lab City Science Group | Konya Büyükşehir Belediyesi

</div>
