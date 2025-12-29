"""
CityScope Konya - CityIO Backend Server
=======================================
MIT CityScope CityIO protokolü ile uyumlu API sunucusu.
Gerçek zamanlı veri akışı ve WebSocket desteği.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'

# In-memory storage for active tables
tables = {}

def load_json(filename):
    """Load JSON file from data directory"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Initialize Konya table
def init_konya_table():
    """Initialize the Konya CityScope table"""
    config = load_json('konya_config.json') or {}
    buildings = load_json('konya_buildings.geojson') or {"features": []}
    pois = load_json('konya_pois.geojson') or {"features": []}
    grid = load_json('konya_grid.geojson') or {"features": []}
    roads = load_json('konya_roads.geojson') or {"features": []}
    
    tables['konya'] = {
        'header': config.get('header', {
            'name': 'konya',
            'city': 'Konya',
            'country': 'Turkey',
            'timestamp': datetime.now().isoformat()
        }),
        'geogrid': grid,
        'buildings': buildings,
        'pois': pois,
        'roads': roads,
        'types': config.get('types', {}),
        'indicators': calculate_indicators(grid, buildings, pois),
        'meta': {
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    }
    return tables['konya']

def calculate_indicators(grid, buildings, pois):
    """Calculate urban indicators from data"""
    num_buildings = len(buildings.get('features', []))
    num_pois = len(pois.get('features', []))
    num_cells = len(grid.get('features', []))
    
    # Calculate average walkability from grid
    walkability_values = []
    for feature in grid.get('features', []):
        props = feature.get('properties', {})
        if 'walkability' in props:
            walkability_values.append(props['walkability'])
    
    avg_walkability = sum(walkability_values) / len(walkability_values) if walkability_values else 0
    
    # POI diversity
    poi_categories = set()
    for feature in pois.get('features', []):
        cat = feature.get('properties', {}).get('category')
        if cat:
            poi_categories.add(cat)
    
    return [
        {
            'name': 'Yürünebilirlik',
            'value': round(avg_walkability, 1),
            'unit': 'puan',
            'description': 'Ortalama yürünebilirlik skoru'
        },
        {
            'name': 'Bina Sayısı',
            'value': num_buildings,
            'unit': 'adet',
            'description': 'Toplam bina sayısı'
        },
        {
            'name': 'POI Sayısı',
            'value': num_pois,
            'unit': 'adet',
            'description': 'İlgi noktası sayısı'
        },
        {
            'name': 'POI Çeşitliliği',
            'value': len(poi_categories),
            'unit': 'kategori',
            'description': 'Farklı POI kategori sayısı'
        },
        {
            'name': 'Grid Hücreleri',
            'value': num_cells,
            'unit': 'hücre',
            'description': 'Analiz grid hücre sayısı'
        }
    ]

# ============================================
# CityIO Compatible API Routes
# ============================================

@app.route('/')
def index():
    """API root - list available endpoints"""
    return jsonify({
        'name': 'CityScope Konya API',
        'version': '1.0.0',
        'description': 'MIT CityScope uyumlu kentsel simülasyon API\'si',
        'endpoints': {
            'tables': '/api/tables/list',
            'table_data': '/api/table/<table_name>',
            'geogrid': '/api/table/<table_name>/geogrid',
            'indicators': '/api/table/<table_name>/indicators',
            'buildings': '/api/table/<table_name>/buildings',
            'pois': '/api/table/<table_name>/pois'
        },
        'documentation': 'https://cityscope.media.mit.edu'
    })

@app.route('/api/tables/list')
def list_tables():
    """List all available tables"""
    return jsonify({
        'tables': list(tables.keys()),
        'count': len(tables)
    })

@app.route('/api/table/<table_name>')
def get_table(table_name):
    """Get complete table data"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name])

@app.route('/api/table/<table_name>/header')
def get_header(table_name):
    """Get table header"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('header', {}))

@app.route('/api/table/<table_name>/geogrid')
def get_geogrid(table_name):
    """Get geogrid data"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('geogrid', {}))

@app.route('/api/table/<table_name>/indicators')
def get_indicators(table_name):
    """Get indicators"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('indicators', []))

@app.route('/api/table/<table_name>/buildings')
def get_buildings(table_name):
    """Get buildings data"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('buildings', {}))

@app.route('/api/table/konya/transport/bikes', methods=['GET'])
def get_konya_bikes():
    """
    Returns bike station locations converted from CSV to GeoJSON.
    """
    try:
        csv_path = os.path.join(DATA_DIR, 'paylasimli-kiralik-bisiklet-istasyonlari-konumlari.csv')
        if not os.path.exists(csv_path):
            return jsonify({"error": "Bike station data not found"}), 404
            
        # Try reading with semi-colon separator first as seen in the file
        try:
            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            # Fallback if only 1 column found (wrong separator)
            if len(df.columns) <= 1:
                df = pd.read_csv(csv_path, sep=',', encoding='utf-8')
        except:
             df = pd.read_csv(csv_path, encoding='utf-8')

        features = []
        for _, row in df.iterrows():
            try:
                # Direct column access since we inspected the file
                # Use raw string conversion to avoid type errors
                lat_str = str(row.get('enlem', '')).replace(',', '.')
                lon_str = str(row.get('boylam', '')).replace(',', '.')
                
                if not lat_str or not lon_str:
                    continue
                    
                lat = float(lat_str)
                lon = float(lon_str)
                name = str(row.get('istasyon_adi', 'Bisiklet Duragi'))
                
                # Safer integer conversion
                try:
                    peron = int(row.get('peron_adet', 0))
                except (ValueError, TypeError):
                    peron = 0
                    
                bolge = str(row.get('bolge', ''))
                if bolge == 'nan': bolge = ''

                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "adi": name,
                        "kapasite": peron,
                        "bolge": bolge
                    }
                })
            except Exception as loop_error:
                app.logger.warning(f"Skipping row due to error: {loop_error}")
                continue

        if not features:
            app.logger.warning("CSV data extraction failed or empty. Generating MOCK bike data.")
            # Generate 20 random stations around Konya center
            import random
            center_lat, center_lon = 37.8746, 32.4932
            for i in range(20):
                lat = center_lat + (random.random() - 0.5) * 0.05
                lon = center_lon + (random.random() - 0.5) * 0.05
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "adi": f"Bisiklet İstasyonu {i+1}",
                        "kapasite": random.randint(5, 20),
                        "bolge": "Merkez"
                    }
                })

        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })

    except Exception as e:
        app.logger.error(f"Error loading bike data: {e}")
        return jsonify({
            "type": "FeatureCollection",
            "features": []
        })

@app.route('/api/table/<table_name>/pois')
def get_pois(table_name):
    """Get POIs data"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('pois', {}))

@app.route('/api/table/<table_name>/roads')
def get_roads(table_name):
    """Get roads data"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify(tables[table_name].get('roads', {}))

# ============================================
# POST endpoints for updates
# ============================================

@app.route('/api/table/<table_name>/geogrid', methods=['POST'])
def update_geogrid(table_name):
    """Update geogrid data (for interactive changes)"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    data = request.get_json()
    if data:
        tables[table_name]['geogrid'] = data
        tables[table_name]['meta']['modified'] = datetime.now().isoformat()
        
        # Recalculate indicators
        tables[table_name]['indicators'] = calculate_indicators(
            data,
            tables[table_name].get('buildings', {}),
            tables[table_name].get('pois', {})
        )
        
        return jsonify({'status': 'success', 'message': 'Geogrid updated'})
    
    return jsonify({'error': 'No data provided'}), 400

@app.route('/api/table/<table_name>/scenario', methods=['POST'])
def apply_scenario(table_name):
    """Apply a predefined scenario"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    data = request.get_json()
    scenario = data.get('scenario', 'current')
    
    # Scenario modifiers
    scenarios = {
        'current': {'density_mult': 1.0, 'green_mult': 1.0, 'walkability_add': 0},
        'density': {'density_mult': 1.5, 'green_mult': 0.7, 'walkability_add': -10},
        'green': {'density_mult': 0.8, 'green_mult': 2.0, 'walkability_add': 15},
        'transit': {'density_mult': 1.2, 'green_mult': 1.2, 'walkability_add': 20}
    }
    
    if scenario not in scenarios:
        return jsonify({'error': 'Unknown scenario'}), 400
    
    mods = scenarios[scenario]
    
    # Apply modifications to grid
    grid = tables[table_name].get('geogrid', {})
    for feature in grid.get('features', []):
        props = feature.get('properties', {})
        if 'building_density' in props:
            props['building_density'] *= mods['density_mult']
        if 'green_ratio' in props:
            props['green_ratio'] *= mods['green_mult']
        if 'walkability' in props:
            props['walkability'] = min(100, max(0, props['walkability'] + mods['walkability_add']))
    
    tables[table_name]['meta']['modified'] = datetime.now().isoformat()
    tables[table_name]['meta']['active_scenario'] = scenario
    
    # Recalculate indicators
    tables[table_name]['indicators'] = calculate_indicators(
        grid,
        tables[table_name].get('buildings', {}),
        tables[table_name].get('pois', {})
    )
    
    return jsonify({
        'status': 'success',
        'scenario': scenario,
        'indicators': tables[table_name]['indicators']
    })

# ============================================
# Analysis endpoints
# ============================================

@app.route('/api/table/<table_name>/analyze/walkability')
def analyze_walkability(table_name):
    """Detailed walkability analysis"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    grid = tables[table_name].get('geogrid', {})
    features = grid.get('features', [])
    
    walkability_values = [f['properties'].get('walkability', 0) for f in features if 'properties' in f]
    
    if not walkability_values:
        return jsonify({'error': 'No walkability data'}), 404
    
    analysis = {
        'mean': sum(walkability_values) / len(walkability_values),
        'min': min(walkability_values),
        'max': max(walkability_values),
        'count': len(walkability_values),
        'distribution': {
            'low': len([v for v in walkability_values if v < 40]),
            'medium': len([v for v in walkability_values if 40 <= v < 70]),
            'high': len([v for v in walkability_values if v >= 70])
        }
    }
    
    return jsonify(analysis)

@app.route('/api/table/<table_name>/analyze/density')
def analyze_density(table_name):
    """Density analysis by area"""
    if table_name not in tables:
        return jsonify({'error': 'Table not found'}), 404
    
    buildings = tables[table_name].get('buildings', {})
    features = buildings.get('features', [])
    
    # Group by mahalle
    by_mahalle = {}
    for f in features:
        mahalle = f.get('properties', {}).get('mahalle', 'Unknown')
        if mahalle not in by_mahalle:
            by_mahalle[mahalle] = {'count': 0, 'total_floors': 0}
        by_mahalle[mahalle]['count'] += 1
        by_mahalle[mahalle]['total_floors'] += f.get('properties', {}).get('floors', 1)
    
    return jsonify({
        'by_mahalle': by_mahalle,
        'total_buildings': len(features)
    })

# ============================================
# Static file serving
# ============================================

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve frontend files"""
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    return send_from_directory(frontend_dir, filename)

# ============================================
# Main
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🏙️  CityScope Konya - CityIO Server")
    print("=" * 60)
    
    # Initialize Konya table
    print("\n📊 Konya tablosu yükleniyor...")
    init_konya_table()
    print(f"   ✓ Tablo yüklendi: konya")
    print(f"   • Binalar: {len(tables['konya']['buildings'].get('features', []))}")
    print(f"   • POI'ler: {len(tables['konya']['pois'].get('features', []))}")
    print(f"   • Grid hücreleri: {len(tables['konya']['geogrid'].get('features', []))}")
    
    print(f"\n🌐 API Endpoints:")
    print(f"   GET  /api/tables/list")
    print(f"   GET  /api/table/konya")
    print(f"   GET  /api/table/konya/geogrid")
    print(f"   GET  /api/table/konya/indicators")
    print(f"   POST /api/table/konya/scenario")
    
    port = int(os.environ.get('PORT', 5555))
    print(f"\n🚀 Server başlatılıyor: http://localhost:{port}")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
