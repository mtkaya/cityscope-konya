"""
Konya Yol Ağı Oluşturucu
========================
Konya'nın ana cadde ve bulvarlarını içeren detaylı yol ağı oluşturur.
"""

import json
import numpy as np
from shapely.geometry import LineString, mapping

# Konya merkez koordinatları
KONYA_CENTER = [32.4932, 37.8746]  # lon, lat
KONYA_BBOX = {
    'west': 32.40,
    'east': 32.58,
    'south': 37.83,
    'north': 37.92
}

# Konya'nın gerçek ana yolları
KONYA_MAJOR_ROADS = [
    # Ana Bulvarlar - Doğu-Batı
    {
        'name': 'Mevlana Caddesi',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 50,
        'coords': [[32.45, 37.875], [32.55, 37.875]]
    },
    {
        'name': 'Alaaddin Bulvarı',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 50,
        'coords': [[32.46, 37.87], [32.54, 37.87]]
    },
    {
        'name': 'Ankara Caddesi',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 60,
        'coords': [[32.44, 37.88], [32.56, 37.88]]
    },
    {
        'name': 'İstanbul Caddesi',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 60,
        'coords': [[32.44, 37.89], [32.54, 37.89]]
    },
    {
        'name': 'Adana Caddesi',
        'type': 'primary',
        'lanes': 3,
        'speed_limit': 50,
        'coords': [[32.46, 37.86], [32.54, 37.86]]
    },

    # Ana Bulvarlar - Kuzey-Güney
    {
        'name': 'Beyhekim Caddesi',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 50,
        'coords': [[32.48, 37.84], [32.48, 37.90]]
    },
    {
        'name': 'Nalçacı Caddesi',
        'type': 'primary',
        'lanes': 3,
        'speed_limit': 50,
        'coords': [[32.50, 37.85], [32.50, 37.89]]
    },
    {
        'name': 'Fatih Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.49, 37.86], [32.49, 37.88]]
    },
    {
        'name': 'Şerafettin Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.51, 37.85], [32.51, 37.89]]
    },

    # Çevre Yolu
    {
        'name': 'Konya Çevreyolu',
        'type': 'motorway',
        'lanes': 6,
        'speed_limit': 110,
        'coords': [
            [32.42, 37.84], [32.43, 37.83], [32.45, 37.83],
            [32.55, 37.83], [32.57, 37.84], [32.58, 37.86],
            [32.58, 37.90], [32.57, 37.91], [32.54, 37.91],
            [32.45, 37.91], [32.43, 37.90], [32.42, 37.88],
            [32.42, 37.84]
        ]
    },

    # Selçuklu İlçesi
    {
        'name': 'Yeni İstanbul Caddesi',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 60,
        'coords': [[32.50, 37.86], [32.57, 37.86]]
    },
    {
        'name': 'Büyükkayacık Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 50,
        'coords': [[32.52, 37.85], [32.52, 37.89]]
    },

    # Karatay İlçesi
    {
        'name': 'Karatay Caddesi',
        'type': 'primary',
        'lanes': 3,
        'speed_limit': 50,
        'coords': [[32.45, 37.85], [32.50, 37.85]]
    },
    {
        'name': 'Yazır Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.44, 37.87], [32.48, 37.87]]
    },

    # Meram İlçesi
    {
        'name': 'Meram Yolu',
        'type': 'primary',
        'lanes': 4,
        'speed_limit': 60,
        'coords': [[32.47, 37.84], [32.47, 37.87]]
    },
    {
        'name': 'Armağan Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.46, 37.84], [32.46, 37.87]]
    },

    # Diğer Önemli Caddeler
    {
        'name': 'Feritpaşa Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.485, 37.865], [32.485, 37.885]]
    },
    {
        'name': 'Hükümet Caddesi',
        'type': 'secondary',
        'lanes': 2,
        'speed_limit': 40,
        'coords': [[32.475, 37.87], [32.505, 37.87]]
    },
    {
        'name': 'Aziziye Caddesi',
        'type': 'tertiary',
        'lanes': 2,
        'speed_limit': 30,
        'coords': [[32.490, 37.872], [32.495, 37.872]]
    },
]

def interpolate_coords(coords, points_per_segment=5):
    """Koordinatlar arasında düzgün geçişler oluştur"""
    if len(coords) < 2:
        return coords

    interpolated = []
    for i in range(len(coords) - 1):
        start = coords[i]
        end = coords[i + 1]

        for j in range(points_per_segment):
            t = j / points_per_segment
            lon = start[0] + t * (end[0] - start[0])
            lat = start[1] + t * (end[1] - start[1])
            interpolated.append([lon, lat])

    interpolated.append(coords[-1])
    return interpolated

def create_secondary_roads(bbox, num_roads=50):
    """Ara sokaklar oluştur"""
    roads = []

    for i in range(num_roads):
        # Rastgele yön (0: doğu-batı, 1: kuzey-güney)
        direction = np.random.choice([0, 1])

        if direction == 0:  # Doğu-Batı
            lat = np.random.uniform(bbox['south'], bbox['north'])
            lon_start = np.random.uniform(bbox['west'], bbox['west'] + 0.05)
            lon_end = np.random.uniform(bbox['east'] - 0.05, bbox['east'])

            coords = [[lon_start, lat], [lon_end, lat]]
            road_type = 'residential'
            lanes = 1
            speed_limit = 30
        else:  # Kuzey-Güney
            lon = np.random.uniform(bbox['west'], bbox['east'])
            lat_start = np.random.uniform(bbox['south'], bbox['south'] + 0.02)
            lat_end = np.random.uniform(bbox['north'] - 0.02, bbox['north'])

            coords = [[lon, lat_start], [lon, lat_end]]
            road_type = 'residential'
            lanes = 1
            speed_limit = 30

        roads.append({
            'name': f'Sokak {i+1}',
            'type': road_type,
            'lanes': lanes,
            'speed_limit': speed_limit,
            'coords': coords
        })

    return roads

def generate_road_network():
    """Tam yol ağını oluştur"""

    print("🛣️  Konya yol ağı oluşturuluyor...")

    # Ana yollar
    all_roads = KONYA_MAJOR_ROADS.copy()
    print(f"   ✓ {len(all_roads)} ana yol")

    # Ara sokaklar ekle
    secondary_roads = create_secondary_roads(KONYA_BBOX, num_roads=100)
    all_roads.extend(secondary_roads)
    print(f"   ✓ {len(secondary_roads)} ara sokak eklendi")

    # GeoJSON oluştur
    features = []
    for idx, road in enumerate(all_roads):
        # Koordinatları interpolate et
        coords = interpolate_coords(road['coords'], points_per_segment=3)

        feature = {
            "type": "Feature",
            "properties": {
                "id": f"road_{idx}",
                "name": road['name'],
                "type": road['type'],
                "lanes": road['lanes'],
                "speed_limit": road['speed_limit']
            },
            "geometry": mapping(LineString(coords))
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "name": "konya_roads_detailed",
        "features": features
    }

    return geojson

if __name__ == "__main__":
    # Yol ağını oluştur
    road_network = generate_road_network()

    # Dosyaya kaydet
    output_file = 'data/konya_roads_detailed.geojson'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(road_network, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(road_network['features'])} yol segmenti oluşturuldu")
    print(f"📁 Dosya: {output_file}")

    # İstatistikler
    road_types = {}
    for feature in road_network['features']:
        road_type = feature['properties']['type']
        road_types[road_type] = road_types.get(road_type, 0) + 1

    print("\n📊 Yol Tipleri:")
    for road_type, count in sorted(road_types.items()):
        print(f"   • {road_type}: {count}")
