# Analiza Wielowarstwowa Krakowa: CIR & NDBI 🌍🛰️

Projekt przedstawia interaktywną aplikację webową (WebGIS) do analizy pokrycia terenu w Krakowie. Aplikacja wykorzystuje dane satelitarne (pasma bliskiej i krótkofalowej podczerwieni) do obliczenia oraz wizualizacji wskaźników środowiskowych i urbanistycznych.

## 📌 Funkcjonalności
* **Obliczanie wskaźników satelitarnych:** Skrypty w Pythonie obliczające wskaźnik zabudowy (NDBI) ze zdefiniowaną inżynierską paletą barw oraz przezroczystością tła.
* **Przetwarzanie danych przestrzennych (GDAL):** Konwersja surowych plików `.tif` na optymalne kafelki mapowe (TMS) pozwalające na płynne renderowanie w przeglądarce.
* **Interaktywna mapa (Leaflet):** Aplikacja webowa wyposażona w:
  * Suwak porównawczy (Side-by-Side) zestawiający zdjęcia w barwach rzeczywistych z wybranym wskaźnikiem.
  * Przełącznik warstw pozwalający na płynną zmianę między analizą roślinności (CIR) a analizą betonu i zabudowy (NDBI).
  * Skalę mapy oraz czytelne legendy kolorystyczne.

## 🛠️ Technologie
* **Języki i narzędzia:** Python (Jupyter Notebook), HTML5, CSS3, JavaScript.
* **Biblioteki Python:** `rasterio`, `numpy`, `matplotlib`.
* **Przetwarzanie GIS:** `GDAL` (`gdal2tiles`).
* **Front-end GIS:** `Leaflet`, `leaflet-side-by-side`.

## 🚀 Przebieg pracy (Workflow)

### 1. Generowanie wskaźników (Python)
Wirtualne środowisko musi posiadać zainstalowane biblioteki przestrzenne. Uruchomienie skryptu `Obliczenia.ipynb` pobiera surowe pasma satelitarne, nakłada na nie palety barw i generuje pliki `.tif` z przezroczystym tłem (maskowanie wartości NoData).

### 2. Generowanie kafelków mapowych (Terminal / OSGeo4W)
Pliki wynikowe cięte są na lekkie kafelki (zoom 8-11), np. dla warstwy NDBI:
```bash
python -m gdal2tiles -z 8-11 -s EPSG:32634 -k Krakow_NDBI_RGB.tif ndbi_tiles
