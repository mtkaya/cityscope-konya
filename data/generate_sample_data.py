"""
CityScope Konya - Örnek Veri Üreteci
====================================
Gerçekçi örnek veriler oluşturur.
Gerçek veriler Konya Büyükşehir Belediyesi Kent Bilgi Sistemi'nden alınacaktır.
"""

import json
import random
import math
from datetime import datetime

# Konya merkez koordinatları
KONYA_CENTER = {"lat": 37.8746, "lon": 32.4932}

# Önemli noktalar (gerçek koordinatlar)
LANDMARKS = {
    "mevlana_muzesi": {"lat": 37.8707, "lon": 32.5044, "name": "Mevlana Müzesi", "type": "tourism"},
    "alaaddin_tepesi": {"lat": 37.8746, "lon": 32.4891, "name": "Alaaddin Tepesi", "type": "park"},
    "karatay_medresesi": {"lat": 37.8732, "lon": 32.4985, "name": "Karatay Medresesi", "type": "tourism"},
    "selcuklu_belediyesi": {"lat": 37.8812, "lon": 32.4756, "name": "Selçuklu Belediyesi", "type": "government"},
    "konya_garı": {"lat": 37.8698, "lon": 32.4847, "name": "Konya Garı", "type": "transport"},
    "meram_bagları": {"lat": 37.8456, "lon": 32.4623, "name": "Meram Bağları", "type": "nature"},
    "kentpark": {"lat": 37.8889, "lon": 32.4534, "name": "Kent Park", "type": "park"},
    "selcuk_universitesi": {"lat": 37.8634, "lon": 32.4156, "name": "Selçuk Üniversitesi", "type": "education"}
}

# Mahalle verileri (gerçek mahalleler)
MAHALLELER = [
    {"name": "Mevlana", "center": (37.8707, 32.5044), "density": "high", "type": "historic"},
    {"name": "Karatay", "center": (37.8732, 32.4985), "density": "high", "type": "historic"},
    {"name": "Selçuklu", "center": (37.8812, 32.4756), "density": "medium", "type": "residential"},
    {"name": "Meram", "center": (37.8456, 32.4623), "density": "low", "type": "green"},
    {"name": "Bosna Hersek", "center": (37.8923, 32.4812), "density": "medium", "type": "residential"},
    {"name": "Yazır", "center": (37.8534, 32.5123), "density": "medium", "type": "mixed"},
    {"name": "Horozluhan", "center": (37.8789, 32.5234), "density": "high", "type": "commercial"},
    {"name": "Fevzi Çakmak", "center": (37.8645, 32.4567), "density": "medium", "type": "residential"}
]

def generate_buildings():
    """Örnek bina verileri oluştur"""
    buildings = {
        "type": "FeatureCollection",
        "name": "konya_buildings",
        "features": []
    }
    
    building_types = ["residential", "commercial", "industrial", "public", "mixed"]
    
    for mahalle in MAHALLELER:
        # Her mahalle için farklı sayıda bina
        num_buildings = {"high": 150, "medium": 80, "low": 40}[mahalle["density"]]
        
        for i in range(num_buildings):
            # Mahalle merkezine göre rastgele konum
            lat = mahalle["center"][0] + random.gauss(0, 0.008)
            lon = mahalle["center"][1] + random.gauss(0, 0.008)
            
            # Bina boyutu (metre)
            width = random.randint(10, 40)
            height = random.randint(10, 40)
            floors = random.choices([1, 2, 3, 4, 5, 6, 8, 10, 15], 
                                   weights=[10, 15, 20, 20, 15, 10, 5, 3, 2])[0]
            
            # Basit dikdörtgen polygon
            half_w = width / 111000 / 2
            half_h = height / 111000 / 2
            
            polygon = [
                [lon - half_w, lat - half_h],
                [lon + half_w, lat - half_h],
                [lon + half_w, lat + half_h],
                [lon - half_w, lat + half_h],
                [lon - half_w, lat - half_h]
            ]
            
            building_type = "historic" if mahalle["type"] == "historic" else random.choice(building_types)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "id": f"bld_{mahalle['name']}_{i}",
                    "mahalle": mahalle["name"],
                    "type": building_type,
                    "floors": floors,
                    "height": floors * 3,  # metre
                    "year_built": random.randint(1960, 2023),
                    "area": width * height,
                    "population_estimate": floors * random.randint(2, 8) if building_type == "residential" else 0
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon]
                }
            }
            buildings["features"].append(feature)
    
    return buildings

def generate_pois():
    """Örnek POI verileri oluştur"""
    pois = {
        "type": "FeatureCollection",
        "name": "konya_pois",
        "features": []
    }
    
    poi_categories = {
        "education": ["Okul", "Üniversite", "Kütüphane", "Kreş", "Dershane"],
        "health": ["Hastane", "Sağlık Ocağı", "Eczane", "Klinik"],
        "commerce": ["Market", "AVM", "Mağaza", "Pazar"],
        "religion": ["Cami", "Türbe"],
        "transport": ["Otobüs Durağı", "Tramvay Durağı", "Taksi Durağı", "Otopark"],
        "recreation": ["Park", "Spor Salonu", "Kafe", "Restoran"],
        "government": ["Belediye", "Kaymakamlık", "PTT", "Nüfus Müdürlüğü"]
    }
    
    # Landmark'ları ekle
    for key, landmark in LANDMARKS.items():
        feature = {
            "type": "Feature",
            "properties": {
                "id": key,
                "name": landmark["name"],
                "category": landmark["type"],
                "is_landmark": True,
                "importance": "high"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [landmark["lon"], landmark["lat"]]
            }
        }
        pois["features"].append(feature)
    
    # Her mahalle için POI'ler
    poi_id = 0
    for mahalle in MAHALLELER:
        for category, names in poi_categories.items():
            # Kategori başına 2-8 POI
            num_pois = random.randint(2, 8)
            
            for _ in range(num_pois):
                lat = mahalle["center"][0] + random.gauss(0, 0.006)
                lon = mahalle["center"][1] + random.gauss(0, 0.006)
                
                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": f"poi_{poi_id}",
                        "name": f"{random.choice(names)} - {mahalle['name']}",
                        "category": category,
                        "mahalle": mahalle["name"],
                        "is_landmark": False,
                        "importance": random.choice(["low", "medium", "high"])
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                }
                pois["features"].append(feature)
                poi_id += 1
    
    return pois

def generate_grid(cell_size=200):
    """CityScope grid oluştur"""
    grid = {
        "type": "FeatureCollection",
        "name": "konya_grid",
        "features": []
    }
    
    # Konya merkez etrafında grid
    min_lat, max_lat = 37.84, 37.92
    min_lon, max_lon = 32.44, 32.54
    
    cell_deg = cell_size / 111000  # derece cinsinden
    
    cell_id = 0
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            # Hücre için rastgele göstergeler
            # Merkeze yakınlık
            dist_to_center = math.sqrt((lat - KONYA_CENTER["lat"])**2 + (lon - KONYA_CENTER["lon"])**2)
            centrality = max(0, 1 - dist_to_center * 20)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "id": cell_id,
                    "row": int((lat - min_lat) / cell_deg),
                    "col": int((lon - min_lon) / cell_deg),
                    # Göstergeler
                    "building_density": random.uniform(0.1, 0.9) * (0.5 + centrality * 0.5),
                    "population_density": random.uniform(50, 500) * (0.3 + centrality * 0.7),
                    "poi_count": int(random.uniform(0, 20) * (0.4 + centrality * 0.6)),
                    "green_ratio": random.uniform(0.05, 0.4) * (1.2 - centrality * 0.5),
                    "walkability": random.uniform(40, 95) * (0.6 + centrality * 0.4),
                    "accessibility": random.uniform(30, 100) * (0.5 + centrality * 0.5),
                    "land_use": random.choice(["residential", "commercial", "mixed", "industrial", "green"])
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon, lat],
                        [lon + cell_deg, lat],
                        [lon + cell_deg, lat + cell_deg],
                        [lon, lat + cell_deg],
                        [lon, lat]
                    ]]
                }
            }
            grid["features"].append(feature)
            cell_id += 1
            lon += cell_deg
        lat += cell_deg
    
    return grid

def generate_roads():
    """Örnek yol ağı verileri"""
    roads = {
        "type": "FeatureCollection",
        "name": "konya_roads",
        "features": []
    }
    
    # Ana arterler
    main_roads = [
        {"name": "Mevlana Caddesi", "type": "primary", "points": [
            [32.48, 37.87], [32.50, 37.87], [32.52, 37.87]
        ]},
        {"name": "Alaaddin Bulvarı", "type": "primary", "points": [
            [32.49, 37.86], [32.49, 37.87], [32.49, 37.88], [32.49, 37.89]
        ]},
        {"name": "Ankara Yolu", "type": "trunk", "points": [
            [32.44, 37.88], [32.48, 37.88], [32.52, 37.88]
        ]},
        {"name": "Konya-Antalya Yolu", "type": "trunk", "points": [
            [32.46, 37.84], [32.48, 37.86], [32.50, 37.88]
        ]}
    ]
    
    road_id = 0
    for road in main_roads:
        feature = {
            "type": "Feature",
            "properties": {
                "id": f"road_{road_id}",
                "name": road["name"],
                "type": road["type"],
                "lanes": 4 if road["type"] == "trunk" else 2,
                "speed_limit": 70 if road["type"] == "trunk" else 50
            },
            "geometry": {
                "type": "LineString",
                "coordinates": road["points"]
            }
        }
        roads["features"].append(feature)
        road_id += 1
    
    # Rastgele sokaklar
    for mahalle in MAHALLELER:
        for i in range(10):
            start_lat = mahalle["center"][0] + random.uniform(-0.01, 0.01)
            start_lon = mahalle["center"][1] + random.uniform(-0.01, 0.01)
            
            # Rastgele yön ve uzunluk
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(0.002, 0.008)
            
            end_lat = start_lat + length * math.sin(angle)
            end_lon = start_lon + length * math.cos(angle)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "id": f"road_{road_id}",
                    "name": f"Sokak {road_id}",
                    "type": random.choice(["residential", "tertiary", "secondary"]),
                    "lanes": random.choice([1, 2]),
                    "speed_limit": 30
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
                }
            }
            roads["features"].append(feature)
            road_id += 1
    
    return roads

def generate_cityscope_config():
    """CityIO uyumlu konfigürasyon"""
    config = {
        "header": {
            "name": "konya",
            "city": "Konya",
            "country": "Turkey",
            "timestamp": datetime.now().isoformat(),
            "spatial": {
                "latitude": KONYA_CENTER["lat"],
                "longitude": KONYA_CENTER["lon"],
                "rotation": 0,
                "cellSize": 200,
                "nrows": 40,
                "ncols": 50
            },
            "owner": {
                "name": "CityScope Konya",
                "institute": "Konya Büyükşehir Belediyesi",
                "contact": "kentbilgisistemi@konya.bel.tr"
            },
            "block": ["type", "height", "density", "walkability"]
        },
        "types": {
            "residential": {"color": [100, 150, 200], "height": 15, "description": "Konut Alanı"},
            "commercial": {"color": [200, 100, 100], "height": 20, "description": "Ticari Alan"},
            "mixed": {"color": [150, 100, 200], "height": 25, "description": "Karma Kullanım"},
            "industrial": {"color": [100, 100, 100], "height": 10, "description": "Sanayi Alanı"},
            "green": {"color": [100, 200, 100], "height": 2, "description": "Yeşil Alan"},
            "historic": {"color": [200, 150, 100], "height": 12, "description": "Tarihi Alan"}
        },
        "indicators": [
            {"name": "Nüfus Yoğunluğu", "viz_type": "heatmap", "unit": "kişi/km²"},
            {"name": "Yürünebilirlik", "viz_type": "bar", "unit": "puan"},
            {"name": "Yeşil Alan Oranı", "viz_type": "pie", "unit": "%"},
            {"name": "Erişilebilirlik", "viz_type": "radar", "unit": "puan"},
            {"name": "Bina Yoğunluğu", "viz_type": "heatmap", "unit": "m²/m²"}
        ]
    }
    return config

def main():
    print("=" * 60)
    print("🏙️  CityScope Konya - Örnek Veri Üreteci")
    print("=" * 60)
    
    # Verileri oluştur
    print("\n📦 Binalar oluşturuluyor...")
    buildings = generate_buildings()
    print(f"   ✓ {len(buildings['features'])} bina oluşturuldu")
    
    print("\n📍 POI'ler oluşturuluyor...")
    pois = generate_pois()
    print(f"   ✓ {len(pois['features'])} POI oluşturuldu")
    
    print("\n🛣️  Yollar oluşturuluyor...")
    roads = generate_roads()
    print(f"   ✓ {len(roads['features'])} yol segmenti oluşturuldu")
    
    print("\n📐 Grid oluşturuluyor...")
    grid = generate_grid(cell_size=200)
    print(f"   ✓ {len(grid['features'])} grid hücresi oluşturuldu")
    
    print("\n⚙️  Konfigürasyon oluşturuluyor...")
    config = generate_cityscope_config()
    
    # Dosyaları kaydet
    print("\n💾 Dosyalar kaydediliyor...")
    
    import os
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(f"{data_dir}/konya_buildings.geojson", 'w', encoding='utf-8') as f:
        json.dump(buildings, f, ensure_ascii=False, indent=2)
    print("   ✓ konya_buildings.geojson")
    
    with open(f"{data_dir}/konya_pois.geojson", 'w', encoding='utf-8') as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)
    print("   ✓ konya_pois.geojson")
    
    with open(f"{data_dir}/konya_roads.geojson", 'w', encoding='utf-8') as f:
        json.dump(roads, f, ensure_ascii=False, indent=2)
    print("   ✓ konya_roads.geojson")
    
    with open(f"{data_dir}/konya_grid.geojson", 'w', encoding='utf-8') as f:
        json.dump(grid, f, ensure_ascii=False, indent=2)
    print("   ✓ konya_grid.geojson")
    
    with open(f"{data_dir}/konya_config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("   ✓ konya_config.json")
    
    print("\n" + "=" * 60)
    print("✅ Veri üretimi tamamlandı!")
    print("=" * 60)
    
    return buildings, pois, roads, grid, config

if __name__ == "__main__":
    main()
