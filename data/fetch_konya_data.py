"""
CityScope Konya - Veri Toplama Modülü
=====================================
Bu script Konya'nın OpenStreetMap verilerini çeker ve CityScope formatına dönüştürür.
"""

import osmnx as ox
import geopandas as gpd
import pandas as pd
import json
import numpy as np
from shapely.geometry import box, Point, Polygon
import warnings
warnings.filterwarnings('ignore')

# Konya merkez koordinatları
KONYA_CENTER = (37.8746, 32.4932)  # lat, lon
KONYA_BBOX = {
    'north': 37.92,
    'south': 37.83,
    'east': 32.58,
    'west': 32.40
}

def fetch_buildings(place="Konya, Turkey", bbox=None):
    """Konya binalarını çek"""
    print("📦 Binalar çekiliyor...")
    try:
        if bbox:
            buildings = ox.features_from_bbox(
                bbox=bbox,
                tags={'building': True}
            )
        else:
            buildings = ox.features_from_place(place, tags={'building': True})
        
        # Sadece polygon geometrileri al
        buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        print(f"   ✓ {len(buildings)} bina bulundu")
        return buildings
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return gpd.GeoDataFrame()

def fetch_roads(place="Konya, Turkey", bbox=None):
    """Konya yol ağını çek"""
    print("🛣️  Yollar çekiliyor...")
    try:
        if bbox:
            G = ox.graph_from_bbox(bbox=bbox, network_type='drive')
        else:
            G = ox.graph_from_place(place, network_type='drive')
        
        # Graph'ı GeoDataFrame'e çevir
        edges = ox.graph_to_gdfs(G, nodes=False)
        print(f"   ✓ {len(edges)} yol segmenti bulundu")
        return edges
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return gpd.GeoDataFrame()

def fetch_pois(place="Konya, Turkey", bbox=None):
    """Konya POI'lerini çek (okul, hastane, park, market vb.)"""
    print("📍 İlgi noktaları çekiliyor...")
    
    poi_tags = {
        'amenity': ['hospital', 'clinic', 'school', 'university', 'kindergarten',
                   'restaurant', 'cafe', 'bank', 'pharmacy', 'mosque', 'library',
                   'police', 'fire_station', 'bus_station'],
        'shop': ['supermarket', 'mall', 'convenience'],
        'leisure': ['park', 'playground', 'sports_centre', 'stadium'],
        'tourism': ['museum', 'monument', 'hotel']
    }
    
    all_pois = []
    
    for tag_key, tag_values in poi_tags.items():
        try:
            if bbox:
                pois = ox.features_from_bbox(
                    bbox=bbox,
                    tags={tag_key: tag_values}
                )
            else:
                pois = ox.features_from_place(place, tags={tag_key: tag_values})
            
            if len(pois) > 0:
                pois['poi_type'] = tag_key
                all_pois.append(pois)
        except:
            continue
    
    if all_pois:
        combined = pd.concat(all_pois, ignore_index=True)
        # GeoDataFrame olarak döndür
        combined = gpd.GeoDataFrame(combined, geometry='geometry')
        print(f"   ✓ {len(combined)} POI bulundu")
        return combined
    
    return gpd.GeoDataFrame()

def fetch_landuse(place="Konya, Turkey", bbox=None):
    """Arazi kullanım verilerini çek"""
    print("🏞️  Arazi kullanımı çekiliyor...")
    try:
        landuse_tags = {
            'landuse': ['residential', 'commercial', 'industrial', 'retail', 
                       'farmland', 'forest', 'meadow', 'recreation_ground']
        }
        
        if bbox:
            landuse = ox.features_from_bbox(bbox=bbox, tags=landuse_tags)
        else:
            landuse = ox.features_from_place(place, tags=landuse_tags)
        
        landuse = landuse[landuse.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        print(f"   ✓ {len(landuse)} arazi parcası bulundu")
        return landuse
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return gpd.GeoDataFrame()

def create_grid(bbox, cell_size=100):
    """CityScope için grid oluştur (metre cinsinden)"""
    print(f"📐 {cell_size}m grid oluşturuluyor...")
    
    # Bbox'ı metre cinsine çevir (UTM Zone 36N - Konya için)
    minx, miny, maxx, maxy = bbox['west'], bbox['south'], bbox['east'], bbox['north']
    
    # Basit grid oluştur
    x_coords = np.arange(minx, maxx, cell_size / 111000)  # derece cinsinden yaklaşık
    y_coords = np.arange(miny, maxy, cell_size / 111000)
    
    cells = []
    cell_id = 0
    
    for x in x_coords:
        for y in y_coords:
            cell = {
                'id': cell_id,
                'geometry': box(x, y, x + cell_size/111000, y + cell_size/111000),
                'center_lon': x + (cell_size/111000)/2,
                'center_lat': y + (cell_size/111000)/2
            }
            cells.append(cell)
            cell_id += 1
    
    grid = gpd.GeoDataFrame(cells, crs="EPSG:4326")
    print(f"   ✓ {len(grid)} hücre oluşturuldu")
    return grid

def calculate_indicators(grid, buildings, pois, roads):
    """Her grid hücresi için kentsel göstergeler hesapla"""
    print("📊 Göstergeler hesaplanıyor...")
    
    indicators = []
    
    for idx, cell in grid.iterrows():
        cell_geom = cell.geometry
        
        # Bina yoğunluğu
        if len(buildings) > 0:
            buildings_in_cell = buildings[buildings.geometry.intersects(cell_geom)]
            building_count = len(buildings_in_cell)
            building_area = buildings_in_cell.geometry.area.sum() if building_count > 0 else 0
        else:
            building_count = 0
            building_area = 0
        
        # POI çeşitliliği
        if len(pois) > 0:
            pois_in_cell = pois[pois.geometry.intersects(cell_geom)]
            poi_count = len(pois_in_cell)
            poi_diversity = pois_in_cell['poi_type'].nunique() if poi_count > 0 else 0
        else:
            poi_count = 0
            poi_diversity = 0
        
        # Yol yoğunluğu
        if len(roads) > 0:
            roads_in_cell = roads[roads.geometry.intersects(cell_geom)]
            road_length = roads_in_cell.geometry.length.sum() if len(roads_in_cell) > 0 else 0
        else:
            road_length = 0
        
        indicators.append({
            'cell_id': cell['id'],
            'building_count': building_count,
            'building_density': building_area * 1000000,  # normalize
            'poi_count': poi_count,
            'poi_diversity': poi_diversity,
            'road_density': road_length * 100000,  # normalize
            'walkability_score': min(100, (poi_diversity * 20 + min(building_count, 5) * 10))
        })
    
    indicators_df = pd.DataFrame(indicators)
    grid = grid.merge(indicators_df, left_on='id', right_on='cell_id')
    print("   ✓ Göstergeler hesaplandı")
    return grid

def export_to_geojson(gdf, filename):
    """GeoDataFrame'i GeoJSON olarak kaydet"""
    if len(gdf) > 0:
        # CRS'i ayarla
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        gdf.to_file(filename, driver='GeoJSON')
        print(f"   💾 {filename} kaydedildi")

def export_to_cityscope_format(grid, buildings, pois):
    """CityIO formatında JSON oluştur"""
    print("🔄 CityScope formatına dönüştürülüyor...")
    
    cityscope_data = {
        "header": {
            "name": "konya",
            "spatial": {
                "latitude": KONYA_CENTER[0],
                "longitude": KONYA_CENTER[1],
                "physical_longitude": KONYA_CENTER[1],
                "physical_latitude": KONYA_CENTER[0],
                "cellSize": 100,
                "rotation": 0,
                "nrows": 50,
                "ncols": 50
            },
            "owner": {
                "name": "CityScope Konya",
                "institute": "Konya Büyükşehir Belediyesi"
            }
        },
        "geogrid": {
            "type": "FeatureCollection",
            "features": []
        },
        "indicators": []
    }
    
    # Grid hücrelerini ekle
    for idx, row in grid.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row.geometry.__geo_interface__,
            "properties": {
                "id": int(row['id']),
                "building_count": int(row.get('building_count', 0)),
                "poi_count": int(row.get('poi_count', 0)),
                "walkability": float(row.get('walkability_score', 0))
            }
        }
        cityscope_data["geogrid"]["features"].append(feature)
    
    # Göstergeleri ekle
    cityscope_data["indicators"] = [
        {"name": "Bina Yoğunluğu", "value": float(grid['building_density'].mean())},
        {"name": "POI Çeşitliliği", "value": float(grid['poi_diversity'].mean())},
        {"name": "Yürünebilirlik", "value": float(grid['walkability_score'].mean())},
        {"name": "Yol Yoğunluğu", "value": float(grid['road_density'].mean())}
    ]
    
    return cityscope_data

def main():
    print("=" * 60)
    print("🏙️  CityScope Konya - Veri Toplama")
    print("=" * 60)
    
    # Daha küçük bir alan için (Mevlana çevresi - pilot bölge)
    pilot_bbox = (37.85, 37.89, 32.46, 32.52)  # south, north, west, east
    
    print("\n📍 Pilot Bölge: Konya Merkez (Mevlana Çevresi)")
    print(f"   Koordinatlar: {pilot_bbox}\n")
    
    # Verileri çek
    buildings = fetch_buildings(bbox=pilot_bbox)
    roads = fetch_roads(bbox=pilot_bbox)
    pois = fetch_pois(bbox=pilot_bbox)
    landuse = fetch_landuse(bbox=pilot_bbox)
    
    # Grid oluştur
    bbox_dict = {
        'south': pilot_bbox[0],
        'north': pilot_bbox[1],
        'west': pilot_bbox[2],
        'east': pilot_bbox[3]
    }
    grid = create_grid(bbox_dict, cell_size=200)  # 200m hücreler
    
    # Göstergeleri hesapla
    if len(buildings) > 0 or len(pois) > 0:
        grid = calculate_indicators(grid, buildings, pois, roads)
    
    # Dosyaları kaydet
    print("\n💾 Veriler kaydediliyor...")
    export_to_geojson(buildings, '/home/claude/cityscope-konya/data/konya_buildings.geojson')
    export_to_geojson(roads, '/home/claude/cityscope-konya/data/konya_roads.geojson')
    export_to_geojson(pois, '/home/claude/cityscope-konya/data/konya_pois.geojson')
    export_to_geojson(grid, '/home/claude/cityscope-konya/data/konya_grid.geojson')
    
    # CityScope formatı
    cityscope_data = export_to_cityscope_format(grid, buildings, pois)
    with open('/home/claude/cityscope-konya/data/konya_cityscope.json', 'w', encoding='utf-8') as f:
        json.dump(cityscope_data, f, ensure_ascii=False, indent=2)
    print("   💾 konya_cityscope.json kaydedildi")
    
    print("\n" + "=" * 60)
    print("✅ Veri toplama tamamlandı!")
    print("=" * 60)
    
    # Özet
    print(f"\n📊 Özet:")
    print(f"   • Binalar: {len(buildings)}")
    print(f"   • Yollar: {len(roads)}")
    print(f"   • POI'ler: {len(pois)}")
    print(f"   • Grid hücreleri: {len(grid)}")
    
    return buildings, roads, pois, grid

if __name__ == "__main__":
    buildings, roads, pois, grid = main()
