"""Jednorazowe przygotowanie paczki z oryginalnych danych projektu.
Wymaga rasterio i fiona. Nie jest częścią obowiązkowej ścieżki studenta.
"""
from pathlib import Path
import json, shutil, hashlib
import fiona
import rasterio
from rasterio.warp import transform_geom
from rasterio.windows import from_bounds, Window
ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parent / 'Landsat8'
OUT = ROOT / 'data' / 'scene'
OUT.mkdir(parents=True, exist_ok=True)
with fiona.open(ORIGINAL / 'vector/krakow_krakowskie.shp') as src:
    features = [dict(f['geometry']) for f in src]
    bounds = src.bounds
    # Brak PRJ w źródle. Układ odtworzony z pokrycia z istniejącym clipped GeoTIFF.
    source_crs = 'EPSG:32634'
geo = {'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Obszar z projektu','crs_provenance':'EPSG:32634 inferred from original clipped rasters; source .prj missing'},'geometry':transform_geom(source_crs, 'EPSG:4326', g)} for g in features]}
(ROOT / 'data/aoi.geojson').write_text(json.dumps(geo,ensure_ascii=False), encoding='utf-8')
files = [*sum([list((ORIGINAL/'LC08').glob(f'*sr_band{i}.tif')) for i in range(2,7)],[]),*list((ORIGINAL/'LC08').glob('*pixel_qa.tif')),*list((ORIGINAL/'LC08').glob('*radsat_qa.tif'))]
manifest = {'source_scene':'LC08_L1TP_188025_20130807_20170503_01_T1','acquisition_date':'2013-08-07','collection':1,'source': 'Dane istniejącego projektu NASA/Landsat8, USGS/EROS','subset':'Prostokąt granicy obszaru, zachowana rozdzielczość 30 m i oryginalne DN. Przycięcie do wielokąta wykonuje student. XML zachowuje metadane pełnej sceny; rozmiary i transformację wycinka odczytujemy z GeoTIFF.','boundary_crs_assumption':'Oryginalny SHP nie ma PRJ ani DBF. EPSG:32634 odtworzono przez zgodność zasięgu ze znajdującymi się w projekcie rastrami clipped. GeoJSON zapisano w EPSG:4326. Nie jest to nowo pozyskana oficjalna granica administracyjna.','files':[]}
for p in files:
    with rasterio.open(p) as src:
        w=from_bounds(*bounds,src.transform)
        import math
        left,top=math.floor(w.col_off),math.floor(w.row_off)
        w=Window(left,top,math.ceil(w.col_off+w.width)-left,math.ceil(w.row_off+w.height)-top)
        data=src.read(window=w)
        profile=src.profile.copy()
        profile.update(width=int(w.width),height=int(w.height),transform=src.window_transform(w),compress='deflate',tiled=True)
        dest=OUT/p.name
        with rasterio.open(dest,'w',**profile) as dst: dst.write(data)
    manifest['files'].append({'path':'scene/'+p.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
for p in (ORIGINAL/'LC08').glob('*.xml'): shutil.copy2(p,OUT/p.name)
(ROOT/'data/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Przygotowano',len(files),'rastrów',data.shape)
