from __future__ import annotations
import argparse
import json
import math
import shutil
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import ColorInterp, Resampling
from rasterio.features import geometry_mask
from rasterio.transform import array_bounds, from_bounds
from rasterio.warp import reproject, transform_bounds, transform_geom

ROOT = Path(__file__).resolve().parents[1]
INDEX_BANDS = {
    'NDVI': (5, 4),
    'NDWI': (3, 5),
    'NDBI': (6, 5),
}
INDEX_CMAPS = {
    'NDVI': 'RdYlGn',
    'NDWI': 'BrBG',
    'NDBI': 'PuOr_r',
}
INDEX_DESCRIPTIONS = {
    'NDVI': 'NDVI = (B5 − B4) / (B5 + B4). Wyższe wartości zwykle wskazują roślinność.',
    'NDWI': 'NDWI = (B3 − B5) / (B3 + B5). Wskaźnik wykorzystuje kanał zielony i NIR do rozpoznawania wody i wilgotnych obszarów.',
    'NDBI': 'NDBI = (B6 − B5) / (B6 + B5). Wyższe wartości mogą wskazywać obszary zabudowane lub odsłoniętą powierzchnię.',
}
COMPOSITES = {
    'RGB': (4, 3, 2),
    'CIR': (5, 4, 3),
}
COMPOSITE_DESCRIPTIONS = {
    'RGB': 'RGB — kompozycja barw naturalnych B4/B3/B2.',
    'CIR': 'CIR — Color Infrared, kompozycja B5/B4/B3; roślinność jest widoczna w czerwonych tonach.',
}
NS = {'e': 'http://espa.cr.usgs.gov/v2'}

def read_metadata(scene: Path) -> dict:
    """Obsługuje dostarczony produkt Landsat Collection 1 ESPA."""
    files = list(scene.glob('*.xml'))
    if len(files) != 1:
        raise ValueError('Oczekiwano dokładnie jednego pliku ESPA XML.')
    root = ET.parse(files[0]).getroot()
    product = root.findtext('e:global_metadata/e:product_id', namespaces=NS)
    if not product or '_01_' not in product:
        raise ValueError(
            'To ćwiczenie obsługuje wyłącznie Landsat Collection 1 z pixel_qa.'
        )
    bands = {}
    for band in root.findall('e:bands/e:band', NS):
        name = band.attrib['name']
        valid = band.find('e:valid_range', NS)
        bands[name] = {
            'file': band.findtext('e:file_name', namespaces=NS),
            'scale': float(band.get('scale_factor', 1)),
            'offset': float(band.get('add_offset', 0)),
            'fill': float(band.get('fill_value', -9999)),
            'valid_min': float(valid.get('min')) if valid is not None else None,
            'valid_max': float(valid.get('max')) if valid is not None else None,
        }
    return {
        'product': product,
        'date': root.findtext('e:global_metadata/e:acquisition_date', namespaces=NS),
        'bands': bands,
    }

def quality_mask(qa: np.ndarray, saturation: np.ndarray) -> np.ndarray:
    """True = dobry piksel C1; woda pozostaje ważna."""
    bad_bits = (1 << 0) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 10)
    bad = (qa & bad_bits) != 0
    bad |= ((qa >> 6) & 3) == 3
    bad |= ((qa >> 8) & 3) == 3
    bad |= (saturation & (1 | sum(1 << b for b in range(2, 7)))) != 0
    return ~bad

def load_scene(data_dir: Path = ROOT / 'data') -> dict:
    """Czyta scenę, AOI, maskę jakości i reflektancję kanałów B2–B6."""
    data_dir = Path(data_dir)
    meta = read_metadata(data_dir / 'scene')
    aoi = json.loads((data_dir / 'aoi.geojson').read_text(encoding='utf-8'))
    raw = {}
    profile = None
    required_keys = [*(f'sr_band{i}' for i in range(2, 7)), 'pixel_qa', 'radsat_qa']
    for key in required_keys:
        with rasterio.open(data_dir / 'scene' / meta['bands'][key]['file']) as src:
            if profile is None:
                profile = src.profile.copy()
            elif (
                src.crs != profile['crs']
                or src.transform != profile['transform']
                or src.width != profile['width']
                or src.height != profile['height']
            ):
                raise ValueError(f'Niezgodna siatka rastra: {key}')
            raw[key] = src.read(1)
    geoms = [
        transform_geom('EPSG:4326', profile['crs'], feature['geometry'])
        for feature in aoi['features']
    ]
    inside = geometry_mask(
        geoms,
        out_shape=raw['pixel_qa'].shape,
        transform=profile['transform'],
        invert=True,
    )
    if not inside.any():
        raise ValueError('Granica nie przecina sceny. Sprawdź CRS i zasięg.')
    quality = quality_mask(raw['pixel_qa'], raw['radsat_qa'])
    valid = inside & quality
    for band_number in range(2, 7):
        band_meta = meta['bands'][f'sr_band{band_number}']
        values = raw[f'sr_band{band_number}']
        valid &= values != band_meta['fill']
        valid &= values >= band_meta['valid_min']
        valid &= values <= band_meta['valid_max']
    if not valid.any():
        raise ValueError('Po maskowaniu nie pozostały ważne piksele.')
    reflectance = {}
    for band_number in range(2, 7):
        band_meta = meta['bands'][f'sr_band{band_number}']
        values = raw[f'sr_band{band_number}'].astype('float32')
        values = values * band_meta['scale'] + band_meta['offset']
        reflectance[band_number] = np.where(valid, values, np.nan)
    return {
        'metadata': meta,
        'profile': profile,
        'raw': raw,
        'inside': inside,
        'valid': valid,
        'quality': quality,
        'reflectance': reflectance,
        'aoi': aoi,
    }

def normalized_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Oblicza znormalizowaną różnicę bez sztucznego obcinania wartości."""
    a = np.asarray(a, dtype='float32')
    b = np.asarray(b, dtype='float32')
    out = np.full(np.broadcast_shapes(a.shape, b.shape), np.nan, dtype='float32')
    denominator = a + b
    valid = np.isfinite(a) & np.isfinite(b) & (np.abs(denominator) > 1e-6)
    np.divide(a - b, denominator, out=out, where=valid)
    return out

def calculate_indices(reflectance: dict) -> dict:
    return {
        name: normalized_difference(reflectance[a], reflectance[b])
        for name, (a, b) in INDEX_BANDS.items()
    }

def stretch_composite(reflectance: dict, bands: tuple[int, int, int]) -> np.ndarray:
    """Tworzy kompozycję RGB z niezależnym rozciągnięciem 2–98 percentyla."""
    channels = []
    for band_number in bands:
        values = reflectance[band_number]
        lo, hi = np.nanpercentile(values, (2, 98))
        scaled = np.clip((values - lo) / max(hi - lo, 1e-6), 0, 1)
        channels.append((np.nan_to_num(scaled) * 255).astype('uint8'))
    alpha = (np.isfinite(reflectance[bands[0]]) * 255).astype('uint8')
    return np.dstack([*channels, alpha])

def index_rgba(array: np.ndarray, name: str) -> np.ndarray:
    rgba = matplotlib.colormaps[INDEX_CMAPS[name]](
        np.clip((array + 1) / 2, 0, 1),
        bytes=True,
    )
    rgba[..., 3] = np.isfinite(array) * 255
    return rgba

def write_geotiff(path: Path, data: np.ndarray, profile: dict, rgba: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    output_profile = profile.copy()
    if rgba:
        data = np.moveaxis(data, -1, 0)
        output_profile.update(
            count=4,
            dtype='uint8',
            nodata=None,
            photometric='RGB',
        )
    else:
        data = np.where(np.isfinite(data), data, -9999).astype('float32')[None]
        output_profile.update(count=1, dtype='float32', nodata=-9999)
        output_profile.pop('photometric', None)
    output_profile.update(driver='GTiff', compress='deflate', tiled=True)
    with rasterio.open(path, 'w', **output_profile) as dst:
        dst.write(data)
        if rgba:
            dst.colorinterp = (
                ColorInterp.red,
                ColorInterp.green,
                ColorInterp.blue,
                ColorInterp.alpha,
            )
        else:
            dst.set_band_description(1, path.stem)
            dst.update_tags(
                meaning='normalized difference; no numeric clipping; NoData=-9999'
            )

def xyz_tiles(
    rgba_tif: Path,
    target: Path,
    minzoom: int = 9,
    maxzoom: int = 12,
) -> int:
    """Tworzy lokalne kafelki XYZ 256 px w EPSG:3857."""
    if not 0 <= minzoom <= maxzoom <= 15:
        raise ValueError('W ćwiczeniu dozwolone 0 <= minzoom <= maxzoom <= 15.')
    radius = 20037508.342789244
    count = 0
    with rasterio.open(rgba_tif) as src:
        west, south, east, north = transform_bounds(
            src.crs,
            'EPSG:3857',
            *src.bounds,
            densify_pts=21,
        )
        for z in range(minzoom, maxzoom + 1):
            n = 2 ** z
            span = 2 * radius / n
            x0 = max(0, math.floor((west + radius) / span))
            x1 = min(n - 1, math.floor((east + radius) / span))
            y0 = max(0, math.floor((radius - north) / span))
            y1 = min(n - 1, math.floor((radius - south) / span))
            for x in range(x0, x1 + 1):
                folder = target / str(z) / str(x)
                folder.mkdir(parents=True, exist_ok=True)
                for y in range(y0, y1 + 1):
                    dst = np.zeros((4, 256, 256), dtype='uint8')
                    bounds = (
                        x * span - radius,
                        radius - (y + 1) * span,
                        (x + 1) * span - radius,
                        radius - y * span,
                    )
                    reproject(
                        source=rasterio.band(src, [1, 2, 3, 4]),
                        destination=dst,
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=from_bounds(*bounds, 256, 256),
                        dst_crs='EPSG:3857',
                        resampling=Resampling.nearest,
                        src_alpha=4,
                        dst_alpha=4,
                    )
                    Image.fromarray(np.moveaxis(dst, 0, -1)).save(folder / f'{y}.png')
                    count += 1
    return count

def make_figures(scene: dict, indices: dict, composites: dict, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 15,
        'figure.facecolor': 'white',
    })
    extent = array_bounds(
        scene['profile']['height'],
        scene['profile']['width'],
        scene['profile']['transform'],
    )
    west, south, east, north = extent
    extent_km = [west / 1000, east / 1000, south / 1000, north / 1000]
    def plot(array, title, filename, cmap=None, limits=None, label=None):
        fig, ax = plt.subplots(figsize=(8.8, 6.2), layout='constrained')
        image = ax.imshow(
            array,
            extent=extent_km,
            cmap=cmap,
            **({'vmin': limits[0], 'vmax': limits[1]} if limits else {}),
        )
        ax.set(
            title=title,
            xlabel='Easting [km], EPSG:32634',
            ylabel='Northing [km]',
        )
        if cmap:
            fig.colorbar(image, ax=ax, shrink=.8, label=label or '')
        fig.savefig(out / filename, dpi=155)
        plt.close(fig)
    for name, (bands, image) in composites.items(): plot(image, f'Landsat 8 • {name} • {scene["metadata"]["date"]}', f'{name.lower()}.png')
    band5 = scene['raw']['sr_band5'].astype(float)
    band5[band5 == scene['metadata']['bands']['sr_band5']['fill']] = np.nan
    plot(band5, 'Kanał B5 przed maskowaniem', 'band5_dn.png', 'gray', (0, 6000), 'DN')
    plot(
        scene['reflectance'][5],
        'B5: reflektancja po masce jakości i granicy',
        'band5_masked.png',
        'gray',
        (0, .6),
        'Reflektancja',
    )
    quality = np.where(~scene['inside'], np.nan, np.where(scene['valid'], 1, 0))
    plot(
        quality,
        'Maska: 1 = ważny piksel, 0 = odrzucony',
        'quality.png',
        'RdYlGn',
        (0, 1),
        'Ważność',
    )
    for name, array in indices.items():
        plot(
            array,
            f'{name} • {scene["metadata"]["date"]}',
            f'{name.lower()}.png',
            INDEX_CMAPS[name],
            (-1, 1),
            'Wartość wskaźnika',
        )
    fig, axs = plt.subplots(1, len(indices), figsize=(12.5, 3.8), layout='constrained')
    if len(indices) == 1: axs = [axs]
    for ax, (name, array) in zip(axs, indices.items()):
        ax.hist(array[np.isfinite(array)], bins=60, range=(-1, 1), color='#167f83')
        ax.set(title=name, xlabel='Wartość', ylabel='Liczba pikseli')
    fig.savefig(out / 'histograms.png', dpi=155)
    plt.close(fig)

def build_layer_catalog(indices: dict, composites: dict) -> dict:
    """Tworzy jeden katalog warstw używany przez generator i przez JavaScript."""
    catalog = {}
    for name in composites:
        catalog[name] = {
            'type': 'composite',
            'description': COMPOSITE_DESCRIPTIONS[name],
            'legend': False,
            'folder': name,
        }
    for name in indices:
        catalog[name] = {
            'type': 'index',
            'description': INDEX_DESCRIPTIONS[name],
            'legend': True,
            'folder': name,
            'ramp': [
                '#'+''.join(
                    f'{value:02x}'
                    for value in matplotlib.colormaps[INDEX_CMAPS[name]](
                        float(t),
                        bytes=True,
                    )[:3]
                )
                for t in np.linspace(0, 1, 9)
            ],
        }
    return catalog

def export_results(
    scene: dict,
    indices: dict,
    composites: dict,
    output_dir: Path = ROOT / 'outputs',
    minzoom: int = 9,
    maxzoom: int = 12,
) -> dict:
    start = time.perf_counter()
    output_dir = Path(output_dir)
    raster_dir = output_dir / 'rasters'
    figure_dir = output_dir / 'figures'
    site = output_dir / 'site'
    for path in (raster_dir, figure_dir, site):
        path.mkdir(parents=True, exist_ok=True)
    summary = {
        'product': scene['metadata']['product'],
        'date': scene['metadata']['date'],
        'shape': [scene['profile']['height'], scene['profile']['width']],
        'crs': str(scene['profile']['crs']),
        'inside_pixels': int(scene['inside'].sum()),
        'valid_pixels': int(scene['valid'].sum()),
        'indices': {},
        'composites': list(composites),
        'tiles': {},
        'minzoom': minzoom,
        'maxzoom': maxzoom,
    }
    for name, array in indices.items():
        finite = array[np.isfinite(array)]
        summary['indices'][name] = {
            'count': int(finite.size),
            'min': float(finite.min()),
            'max': float(finite.max()),
            'mean': float(finite.mean()),
            'median': float(np.median(finite)),
            'outside_minus1_plus1': int((np.abs(finite) > 1).sum()),
        }
        write_geotiff(raster_dir / f'{name}.tif', array, scene['profile'])

    layers = {}
    for name, (bands, image) in composites.items(): layers[name] = image
    for name, array in indices.items(): layers[name] = index_rgba(array, name)
    for name, rgba in layers.items():
        display_tif = raster_dir / f'{name}_display.tif'
        write_geotiff(display_tif, rgba, scene['profile'], rgba=True)
        summary['tiles'][name] = xyz_tiles(
            display_tif,
            site / 'tiles' / name,
            minzoom,
            maxzoom,
        )
    make_figures(scene, indices, composites, figure_dir)
    vendor_source = Path(__file__).parent / 'vendor'
    if vendor_source.exists(): shutil.copytree(vendor_source, site / 'vendor', dirs_exist_ok=True)
    else: raise FileNotFoundError(f'Brak katalogu Leaflet: {vendor_source}')
    (site / 'aoi.geojson').write_text(
        json.dumps(scene['aoi'], ensure_ascii=False),
        encoding='utf-8',
    )
    bounds = array_bounds(
        scene['profile']['height'],
        scene['profile']['width'],
        scene['profile']['transform'],
    )
    west, south, east, north = transform_bounds(
        scene['profile']['crs'],
        'EPSG:4326',
        *bounds,
    )
    catalog = build_layer_catalog(indices, composites)
    config = {
        'bounds': [[south, west], [north, east]],
        'minzoom': minzoom,
        'maxzoom': maxzoom,
        'date': summary['date'],
        'layers': catalog,
        'layer_order': list(catalog),
    }
    template_path = Path(__file__).parent / 'map_template.html'
    template = template_path.read_text(encoding='utf-8')
    (site / 'index.html').write_text(
        template.replace('__MAP_CONFIG__', json.dumps(config, ensure_ascii=False)),
        encoding='utf-8',
    )
    summary['export_seconds'] = round(time.perf_counter() - start, 2)
    summary_text = json.dumps(summary, indent=2, ensure_ascii=False)
    (output_dir / 'summary.json').write_text(summary_text, encoding='utf-8')
    (site / 'summary.json').write_text(summary_text, encoding='utf-8')
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'data')
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs')
    parser.add_argument('--minzoom', type=int, default=9)
    parser.add_argument('--maxzoom', type=int, default=12)
    args = parser.parse_args()
    scene = load_scene(args.data)
    indices = calculate_indices(scene['reflectance'])
    composites = {
        name: (bands, stretch_composite(scene['reflectance'], bands))
        for name, bands in COMPOSITES.items()
    }
    result = export_results(
        scene,
        indices,
        composites,
        args.output,
        args.minzoom,
        args.maxzoom,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        'Podgląd: python -m http.server 8000 --bind 127.0.0.1 '
        f'--directory {Path(args.output) / "site"}'
    )

if __name__ == '__main__':
    main()