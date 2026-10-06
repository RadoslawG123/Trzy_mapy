"""Buduje konspekt PDF i treść prezentacji z wyników tego samego uruchomienia."""
from pathlib import Path
import json, html, textwrap
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'materials';OUT.mkdir(exist_ok=True)
S=json.loads((ROOT/'outputs/summary.json').read_text())
FIG=ROOT/'outputs/figures'
FONT=Path('/System/Library/Fonts/Supplemental')
# DejaVu Sans jest alternatywą na Linux.
if (FONT/'Arial.ttf').exists():
 fonts=[('Lab','Arial.ttf'),('LabBold','Arial Bold.ttf'),('LabMono','Courier New.ttf')]
 for n,f in fonts: pdfmetrics.registerFont(TTFont(n,str(FONT/f)))
else:
 for n,f in [('Lab','DejaVuSans.ttf'),('LabBold','DejaVuSans-Bold.ttf'),('LabMono','DejaVuSansMono.ttf')]:
  pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Lab',normal='Lab',bold='LabBold',italic='Lab',boldItalic='LabBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyPL',fontName='Lab',fontSize=10.5,leading=15,spaceAfter=9,textColor=HexColor('#243d48')))
styles.add(ParagraphStyle(name='TitlePL',fontName='LabBold',fontSize=25,leading=30,spaceAfter=16,textColor=HexColor('#123e4a')))
styles.add(ParagraphStyle(name='SubPL',fontName='LabBold',fontSize=13,leading=18,spaceBefore=12,spaceAfter=7,textColor=HexColor('#147f82')))
styles.add(ParagraphStyle(name='SmallPL',fontName='Lab',fontSize=8.5,leading=12,spaceAfter=6,textColor=HexColor('#49626b')))
styles.add(ParagraphStyle(name='CodePL',fontName='LabMono',fontSize=9,leading=12.5,spaceBefore=5,spaceAfter=12,backColor=HexColor('#edf3f3'),borderPadding=8))
story=[]
def p(t,style='BodyPL'): story.append(Paragraph(t.replace('–','-').replace('—','-').replace('‑','-'),styles[style]))
def title(t): p(t,'TitlePL')
def sub(t): p(t,'SubPL')
def code(t):
 # Długie komendy łamiemy ręcznie, aby można było je skopiować z Markdown.
 story.append(Preformatted(t.strip(),styles['CodePL']))
def pic(name,w=470):
 from PIL import Image as PILImage
 path=FIG/name
 with PILImage.open(path) as im: iw,ih=im.size
 story.append(Image(str(path),width=w,height=w*ih/iw))
 story.append(Spacer(1,8))
def table(rows,widths):
 data=[[Paragraph(html.escape(str(v)),styles['SmallPL']) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e2eeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,HexColor('#147f82')),('LINEBELOW',(0,1),(-1,-1),.35,HexColor('#d7e3e3'))]))
 story.append(t);story.append(Spacer(1,8))
def page(): story.append(PageBreak())

title('Landsat 8\n<br/>Analiza i publikacja mapy WWW')
p('Konspekt laboratoryjny • 90 minut','SubPL')
p('Scena z 7 sierpnia 2013 r. • Kraków i okolice')
pic('rgb.png',470)
p('Obliczenia w Pythonie, bez QGIS. Jedna paczka danych, jeden notatnik, kompletna strona do przesłania przez SSH/SCP.')
p('Materiały towarzyszą wykładowi 90 minut. Zakres obowiązkowy obejmuje Landsat 8. IBIS nie należy do zadania.','SmallPL')
p('Wersja materiałów: 30.09.2026. Dane: USGS/EROS, istniejący projekt NASA/Landsat8. Pierwotny kod: credit S. Moliński.','SmallPL')
page();title('1. Cel i przebieg zajęć')
p('Po zakończeniu ćwiczenia student potrafi odczytać georeferencję, zastosować skalowanie i maskę jakości, obliczyć wskaźniki spektralne oraz udostępnić mapę na swoim koncie UNIX AGH.')
table([['Czas','Czynność','Wynik'],['0–10 min','Środowisko i kernel','Notatnik gotowy do pracy'],['10–25 min','Dane i georeferencja','Kanały, CRS i podgląd'],['25–40 min','Skalowanie i maskowanie','Reflektancja i ważne piksele'],['40–55 min','Wskaźniki','NDVI, NDBI, MNDWI'],['55–70 min','Eksport i mapa','GeoTIFF i strona lokalna'],['70–85 min','SSH/SCP','Strona na serwerze'],['85–90 min','Sprawdzenie i oddanie','URL i trzy wnioski']],[72,185,218])
sub('Przed laboratorium')
p('Zainstaluj Python 3.12 i zależności. Pobierz całą paczkę LABOLATORIUM. Aktywuj konto UNIX, sprawdź login i VPN AGH. Instalacja oraz zakładanie konta nie mieszczą się w 90 minutach zajęć.')
sub('Co przygotowano')
p('Dane stanowią wycinek sceny o rozdzielczości 30 m, bez ponownego próbkowania. Notatnik zawiera działające przykłady i miejsca na własne interpretacje. Obliczenia można powtórzyć jednym poleceniem Pythona.')
sub('Co oddajesz')
p('Notatnik z wynikami, rzeczywisty adres opublikowanej mapy i trzy wnioski interpretacyjne. Każdy wniosek odnosi się do konkretnego obszaru oraz jednego wskaźnika.')
page();title('2. Pliki i przygotowanie środowiska')
table([['Katalog / plik','Znaczenie'],['data/scene','B2–B6, pixel_qa, radsat_qa i XML'],['data/aoi.geojson','Granica obszaru w EPSG:4326'],['data/manifest.json','Pochodzenie danych i założenia'],['src/landsat_lab.py','Wspólny kod obliczeń i eksportu'],['notebooks/*.ipynb','Notatnik wykonywany podczas zajęć'],['outputs/site','Kompletna strona do publikacji'],['docs/polecenia_iterm.md','Polecenia do kopiowania do terminala']],[165,310])
p('W iTerm przejdź do katalogu LABOLATORIUM. Ścieżka zależy od miejsca zapisania paczki. Poniższy przykład odpowiada projektowi prowadzącego:')
code('''cd "/Users/owerko/PycharmProjects/NASA/LABOLATORIUM"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --sys-prefix \\
  --name landsat-lab --display-name "Python (Landsat LAB)"
python -m jupyterlab notebooks/landsat_od_danych_do_www.ipynb''')
p('Wybierz kernel Python (Landsat LAB). Pliku .venv nie przenosimy na inne komputery. W nowym terminalu ponownie aktywuj środowisko.','SmallPL')
page();title('3. Pierwsze uruchomienie notatnika')
p('Otwórz notatnik landsat_od_danych_do_www.ipynb. Uruchamiaj komórki od góry przez Shift+Enter. Tekst wyjaśnia sens operacji, a komórki kodu wykonują obliczenia.')
sub('Ścieżka względna zamiast ścieżki autora')
code('''from pathlib import Path
ROOT = Path.cwd()
# Notatnik automatycznie szuka src/landsat_lab.py
# także w katalogach nadrzędnych.
DATA = ROOT / "data"
OUT = ROOT / "outputs"''')
p('Powyższy przykład ilustruje łączenie ścieżek. Wykonaj pełną komórkę inicjalizacji w notatniku, która znajdzie ROOT także wtedy, gdy katalogiem bieżącym jest notebooks.')
sub('Punkt kontrolny')
p('Oczekiwany komunikat: „Dane wejściowe kompletne”. Program powinien znaleźć siedem plików TIFF. Odczyt źródłowych danych nie wymaga internetu.')
sub('Restart i powtarzalność')
p('Polecenie Restart Kernel and Run All Cells odtwarza wszystkie lokalne wyniki. Nie wykonuje SSH ani SCP. W normalnej pracy nie uruchamiaj losowych komórek po zmianie konfiguracji, ponieważ pamięć kernela może zawierać stare dane.')
sub('Gdy wystąpi błąd')
p('ModuleNotFoundError oznacza zwykle niewłaściwy kernel. FileNotFoundError wymaga sprawdzenia struktury paczki. Nie zmieniaj ścieżek na ścieżki z komputera prowadzącego, jeśli pliki leżą u Ciebie gdzie indziej.')
page();title('4. Dane Landsat i kanały')
p('Scena LC08_L1TP_188025_20130807_20170503_01_T1 pochodzi z 7 sierpnia 2013 r. W paczce znajdują się produkty Surface Reflectance Collection 1. Nazwa sceny zawiera identyfikator produktu poziomu 1, ale pliki sr_band i metadane XML opisują reflektancję powierzchniową.')
table([['Kanał','Zakres / rola','Użycie'],['B2','Niebieski','Kompozycja RGB'],['B3','Zielony','RGB, MNDWI'],['B4','Czerwony','RGB, NDVI'],['B5','NIR','NDVI, NDBI'],['B6','SWIR1','NDBI, MNDWI'],['pixel_qa','Bity jakości C1','Maskowanie'],['radsat_qa','Bity nasycenia','Odrzucenie nasyconych pikseli']],[65,180,230])
code('''scene = load_scene(DATA)
print(scene["metadata"]["date"])
print(scene["profile"]["crs"])
print(scene["profile"]["height"], scene["profile"]["width"])''')
p('Punkt kontrolny: 2013-08-07, EPSG:32634, 1583 × 1982. Metadane XML zachowują rozmiar pełnej sceny; rzeczywiste rozmiary wycinka czytamy z TIFF. Nie utożsamiaj starej sceny z aktualnym stanem zabudowy.')
page();title('5. Georeferencja i obszar analizy')
p('Raster ma układ WGS 84 / UTM zone 34N, EPSG:32634. Jego współrzędne są wyrażone w metrach. GeoJSON zapisuje długość i szerokość geograficzną w stopniach. Przed maskowaniem program przelicza granicę do układu rastra.')
code('''from rasterio.warp import transform_geom
from rasterio.features import geometry_mask
geoms = [transform_geom("EPSG:4326", profile["crs"],
                        f["geometry"])
         for f in scene["aoi"]["features"]]
inside = geometry_mask(geoms,
    out_shape=(profile["height"], profile["width"]),
    transform=profile["transform"], invert=True)''')
p('Przypisanie CRS nie przelicza współrzędnych. Reprojekcja przelicza je między układami. Zastosowanie stopni jako metrów spowodowałoby pusty wynik albo błędne położenie granicy.')
sub('Jawne założenie dotyczące granicy')
p('Oryginalny SHP nie miał plików PRJ ani DBF. EPSG:32634 odtworzono z dopasowania zasięgu do istniejących rastrów clipped. Zapisano geometrię jako GeoJSON i opisano pochodzenie w manifest.json. Granica służy ćwiczeniu; nie stanowi nowo zweryfikowanego urzędowego zbioru granic.')
sub('Przycięcie')
p('Dostarczone dane obejmują prostokąt wokół granicy, aby skrócić odczyt. Student wykonuje maskowanie wielokątem w Pythonie. Piksele poza wielokątem stają się NaN, a przy eksporcie otrzymują NoData. Kryterium włączenia piksela opiera się na jego środku (all_touched=False).')
p(f'Punkt kontrolny: w granicy znajduje się {S["inside_pixels"]:,} pikseli.'.replace(',',' '))
page();title('6. Skala, offset i wartości DN')
p('Surowe DN są całkowitoliczbowym zapisem reflektancji. Skala w XML dla kanałów sr_band wynosi 0.0001. Brak add_offset w tym produkcie oznacza offset 0.')
code('''rho = DN * scale_factor + add_offset
# Nasza scena:
rho = 6000 * 0.0001 + 0
# rho = 0.6''')
p('Ten sam wzór nie oznacza tych samych parametrów dla każdego produktu. USGS podaje dla reflektancji Collection 2 skalę 0.0000275 i offset -0.2. Nie wolno przenosić maski QA ani parametrów C1 na C2. Kod ćwiczenia odrzuca nieobsługiwaną kolekcję.')
pic('band5_dn.png',440)
p('Dla każdego kanału kod czyta scale_factor, fill_value i valid_range z XML. W tym zestawie XML dopuszcza DN od -2000 do 16000. Nie zastępuj tego zakresu arbitralną regułą „wszystko poniżej zera jest błędem”.','SmallPL')
page();title('7. Maska jakości i NoData')
p('Maska łączy granicę obszaru, informacje pixel_qa, nasycenie oraz zakresy poprawnych DN. Wspólna maska B2–B6 pozwala porównywać wskaźniki na tym samym zbiorze pikseli.')
table([['Warunek C1','Decyzja w ćwiczeniu'],['Fill, cień chmur, śnieg, chmura, teren zasłonięty','Odrzucamy'],['Wysoka pewność chmur / cirrus','Odrzucamy'],['Nasycenie B2–B6 lub data fill w radsat_qa','Odrzucamy'],['Flaga wody','Pozostawiamy'],['DN poza zakresem XML lub równy fill','Odrzucamy']],[275,200])
pic('quality.png',410)
p(f'Ważne piksele: {S["valid_pixels"]:,}. Odrzucone w granicy: {S["inside_pixels"]-S["valid_pixels"]}. Zwróć uwagę, że białe tło poza granicą nie jest chmurą.'.replace(',',' '),'SmallPL')
page();title('8. Obraz po przygotowaniu')
pic('band5_masked.png',470)
p('Po zastosowaniu masek ważne piksele zawierają reflektancję, a pozostałe NaN. Funkcja obliczająca wskaźnik pomija NaN i zabezpiecza dzielenie przez mianownik bliski zeru.')
code('''a = scene["reflectance"][5]
print(np.isfinite(a).sum())
# NaN nie jest zerem:
print(np.isfinite(np.nan))  # False
print(np.isfinite(0.0))     # True''')
p('Pytanie kontrolne: dlaczego zastąpienie każdej wartości 0 przez NaN zmieniłoby statystyki? Wskaźnik równy 0 może oznaczać równe sygnały obu kanałów i pozostaje poprawną obserwacją.')
page();title('9. NDVI krok po kroku')
p('<b>NDVI = (B5 - B4) / (B5 + B4).</b> Kanał NIR porównujemy z czerwonym. Przykład dydaktyczny: (0.6 - 0.2) / (0.6 + 0.2) = 0.5.')
code('''nir = scene["reflectance"][5]
red = scene["reflectance"][4]
denominator = nir + red
ndvi = np.full(nir.shape, np.nan, dtype="float32")
np.divide(nir - red, denominator, out=ndvi,
    where=np.isfinite(nir) & np.isfinite(red)
          & (np.abs(denominator) > 1e-6))''')
pic('ndvi.png',410)
p('Wyższe NDVI często odpowiada roślinności. Interpretacja zależy od pokrycia terenu, sezonu i jakości danych. Wskaźnik nie identyfikuje gatunku ani nie stanowi samodzielnej miary zdrowia roślin.','SmallPL')
page();title('10. NDBI i niejednoznaczność zabudowy')
p('<b>NDBI = (B6 - B5) / (B6 + B5).</b> Porównujemy SWIR1 z NIR. Przykład dydaktyczny: (0.35 - 0.20) / (0.35 + 0.20) = 0.273.')
code('''ndbi = normalized_difference(
    scene["reflectance"][6], scene["reflectance"][5])''')
pic('ndbi.png',460)
p('Dodatnie wartości mogą wspierać identyfikację zabudowy, ale pojawiają się również na odsłoniętej glebie. Porównaj jasny obszar z RGB i NDVI, zanim nazwiesz go zabudową. Nie obliczaj „powierzchni miasta” wyłącznie z NDBI > 0.')
page();title('11. MNDWI i rozpoznawanie wody')
p('<b>MNDWI = (B3 - B6) / (B3 + B6).</b> Porównujemy kanał zielony z SWIR1. Przykład dydaktyczny: (0.12 - 0.02) / (0.12 + 0.02) = 0.714.')
code('''mndwi = normalized_difference(
    scene["reflectance"][3], scene["reflectance"][6])''')
pic('mndwi.png',460)
p('Dodatni wynik wspiera rozpoznanie otwartej wody. Sprawdź kontekst przestrzenny i RGB. W poprzednim kodzie ten wzór nazywano NDWI. NDWI McFeetersa wykorzystuje zielony i NIR, dlatego wzór B3/B6 nazywamy tutaj MNDWI.')
page();title('12. Rzeczywiste wyniki i interpretacja')
rows=[['Wskaźnik','Średnia','Mediana','Poza [-1,1]']]
for name,v in S['indices'].items():rows.append([name,f'{v["mean"]:.4f}',f'{v["median"]:.4f}',v['outside_minus1_plus1']])
table(rows,[105,120,120,130])
p('Statystyki pochodzą z dostarczonego wycinka, wspólnej maski i bieżącego kodu. Drobne różnice ostatnich cyfr mogą zależeć od wersji bibliotek. Dane nie są przykładami syntetycznymi.')
pic('histograms.png',475)
sub('Wartości spoza zakresu')
p('Przy ujemnej reflektancji znormalizowana różnica może przekroczyć [-1,1]. Takie wartości raportujemy i zachowujemy w wynikach liczbowych. Nie obcinamy ich automatycznie do granic. Kolory na mapie mają stały zakres [-1,1].')
sub('Ćwiczenie')
p('Zmień próg NDVI z 0.5 na 0.3. Porównaj odsetki ważnych pikseli. Wyjaśnij, dlaczego te odsetki nie są zweryfikowanymi udziałami roślinności. Wskaż trzy konkretne obszary na mapie i zapisz trzy krótkie wnioski.')
page();title('13. GeoTIFF i kontrola eksportu')
p('Wynik analityczny ma typ float32, CRS i transformację zgodne z wejściem. NaN zapisujemy jako NoData = -9999. Wynik prezentacyjny zawiera cztery kanały uint8: czerwony, zielony, niebieski i alfa.')
table([['Plik','Przeznaczenie'],['NDVI.tif, NDBI.tif, MNDWI.tif','Analiza liczbowa, dalsze obliczenia'],['*_display.tif','Kolorowa prezentacja RGBA'],['figures/*.png','Ilustracje w materiałach'],['site/tiles/*','Kafelki mapy WWW']],[240,235])
code('''summary = export_results(scene, indices, OUT,
                         minzoom=9, maxzoom=12)
with rasterio.open(OUT / "rasters/NDVI.tif") as src:
    restored = src.read(1, masked=True).filled(np.nan)
    np.testing.assert_allclose(restored, ndvi,
                               equal_nan=True)
    assert src.crs == profile["crs"]
    assert src.transform == profile["transform"]''')
p('Punkt kontrolny: test odczytu potwierdza zgodność wartości i georeferencji. Zwykły PNG z wykresem nie zastępuje GeoTIFF, ponieważ nie niesie tej samej georeferencji ani oryginalnych wartości.')
page();title('14. Kafelki i mapa internetowa')
p('Generator używa Rasterio z poziomu Pythona. Reprojektuje kolorowy raster do EPSG:3857 i zapisuje PNG 256 × 256 w układzie XYZ. Nie uruchamia programów gdal_translate, gdalwarp ani gdal2tiles.')
code('''site/
  index.html
  aoi.geojson
  summary.json
  vendor/
    leaflet.js
    leaflet.css
  tiles/
    NDVI/9/x/y.png
    NDBI/...
    MNDWI/...
    RGB/...''')
p('x i y powyżej oznaczają numery kafelków. W XYZ numer y rośnie na południe. Odwrócenie osi, typowe dla pomylenia XYZ z TMS, spowoduje złą lokalizację warstwy. Szablon mapy ustawia tms=False.')
p(f'Dla tego obszaru zakres 9–12 daje {sum(S["tiles"].values())} kafelków: po {S["tiles"]["NDVI"]} dla każdej z czterech warstw. Zoom powyżej 12 jedynie powiększa istniejące kafelki.')
sub('Kolory i przezroczystość')
p('Kolory wskaźników mają wspólny zakres -1 do 1. Kanał alfa ukrywa NoData. Kafelki stosują najbliższego sąsiada, aby nie mieszać kolorów przy granicy maski. Do nowych analiz wracamy do float32 GeoTIFF, a nie do kolorów PNG.')
sub('Co wymaga internetu')
p('Leaflet i kafelki wynikowe są dołączone. Jedynie podkład OpenStreetMap jest pobierany z internetu. Jego współczesna treść może różnić się od sceny z 2013 r.')
page();title('15. Podgląd lokalny')
pic('map_web.png',400)
p('W nowym lokalnym terminalu przejdź do LABOLATORIUM, aktywuj środowisko i uruchom serwer:')
code('''source .venv/bin/activate
python -m http.server 8000 --bind 127.0.0.1 \\
  --directory outputs/site''')
p('Otwórz <b>http://127.0.0.1:8000/</b>. Nie otwieraj index.html przez file://. Serwer pozostaje uruchomiony do Ctrl+C. Jeśli port jest zajęty, wybierz 8001.')
sub('Lista kontroli przed publikacją')
p('1. Przełącz NDVI, NDBI, MNDWI i RGB.<br/>2. Sprawdź aktualizację opisu i legendy.<br/>3. Zmień przezroczystość warstwy.<br/>4. Powiększ i przesuń mapę.<br/>5. Wróć przyciskiem „Cały obszar”.<br/>6. Otwórz statystyki obliczeń.')
sub('Błędny kolor lub białe tło')
p('Sprawdź, czy oglądasz obszar z ważnymi pikselami. Puste miejsce poza granicą jest oczekiwane. Gdy brakuje całej warstwy, sprawdź istnienie katalogu tiles i błędy 404. Gdy brakuje tylko podkładu, sprawdź internet.')
page();title('16. SSH: konto i połączenie')
p('Do SSH i SCP potrzebujesz sieci AGH lub VPN. Strony na student.agh.edu.pl są dostępne w sieci uczelni/VPN. Host SSH i adres WWW nie zawsze są identyczne. Źródło: CRI AGH [5].')
table([['Konto','SSH','WWW'],['Student','student.agh.edu.pl','student.agh.edu.pl/~login'],['Pracownik / doktorant','galaxy.agh.edu.pl','home.agh.edu.pl/~login']],[130,170,175])
p('W nowym lokalnym terminalu ustaw wariant studencki (składnia zsh w iTerm):')
code('''read "AGH_LOGIN?Podaj login UNIX AGH: "
AGH_HOST="student.agh.edu.pl"
AGH_WEB="https://student.agh.edu.pl"
ssh "${AGH_LOGIN}@${AGH_HOST}"''')
p('W bash użyj read -r -p "Podaj login UNIX AGH: " AGH_LOGIN. Login nie zawiera części @student. Zweryfikuj klucz hosta zgodnie z informacją administratora. Hasło wpisywane w terminalu nie jest widoczne.')
p('Po zalogowaniu jesteś na serwerze. Wykonaj:')
code('''pwd
ls -ld "$HOME" public_html
exit''')
p('Brak public_html przy pierwszym logowaniu jest normalny. Polecenie exit przywraca lokalną sesję. Nie wklejaj hasła do notatnika ani pliku Markdown.')
page();title('17. SCP: przesłanie strony')
p('Wszystkie poniższe polecenia wykonuj lokalnie, z katalogu LABOLATORIUM. Nowa nazwa podkatalogu chroni istniejącą główną stronę przed przypadkowym nadpisaniem.')
code('''AGH_FOLDER="landsat-$(date +%Y%m%d-%H%M%S)"
ssh "${AGH_LOGIN}@${AGH_HOST}" \\
  "mkdir -p public_html/${AGH_FOLDER} && \\
   chmod 755 public_html public_html/${AGH_FOLDER}"
scp -r outputs/site/. \\
  "${AGH_LOGIN}@${AGH_HOST}:public_html/${AGH_FOLDER}/"''')
p('SCP przesyła zawartość site, w tym wszystkie kafelki i bibliotekę Leaflet. Nie wysyłaj .venv ani surowych scen. Sama obecność index.html nie wystarcza.')
code('''ssh "${AGH_LOGIN}@${AGH_HOST}" \\
  "find public_html/${AGH_FOLDER} -type d \\
     -exec chmod 755 {} + && \\
   find public_html/${AGH_FOLDER} -type f \\
     -exec chmod 644 {} +"''')
p('Katalogi potrzebują prawa przejścia, a pliki prawa odczytu przez serwer WWW. Ustawienia dotyczą tylko katalogu publikacji i public_html. Nie używaj chmod -R 777.')
sub('Wariant prowadzącego')
code('''AGH_LOGIN="owerko"
AGH_HOST="galaxy.agh.edu.pl"
AGH_WEB="https://home.agh.edu.pl"''')
p('Wariant prowadzącego ustaw zamiast wariantu studenckiego, przed wykonaniem publikacji. Zmienna AGH_FOLDER pozostaje nazwą osobnego podkatalogu; głównego index.html nie zastępujemy.')
page();title('18. Weryfikacja strony zdalnej')
code('''AGH_URL="${AGH_WEB}/~${AGH_LOGIN}/${AGH_FOLDER}/"
printf '%s\\n' "$AGH_URL"
curl -I "$AGH_URL"
open "$AGH_URL"''')
p('open działa na macOS. Na innym systemie otwórz wypisany adres ręcznie. Oczekuj odpowiedzi 200 lub przekierowania prowadzącego do 200. Następnie sprawdź w przeglądarce wszystkie warstwy i kafelki.')
code('''ssh "${AGH_LOGIN}@${AGH_HOST}" \\
  "test -f public_html/${AGH_FOLDER}/index.html && \\
   find public_html/${AGH_FOLDER}/tiles \\
     -name '*.png' | wc -l"''')
p(f'Oczekiwana liczba PNG w nowym katalogu: {sum(S["tiles"].values())}. Jeśli jest mniejsza, powtórz SCP i sprawdź komunikaty przesyłania. Jeśli większa, sprawdź, czy katalog zawiera wyniki wcześniejszych prób.')
sub('403 Forbidden')
p('Sprawdź uprawnienia 755 dla katalogów, 644 dla plików. Niektóre konfiguracje wymagają prawa przejścia przez katalog domowy. Po sprawdzeniu ustawień konta możesz nadać wyłącznie to prawo:')
code('''ssh "${AGH_LOGIN}@${AGH_HOST}" 'chmod o+x "$HOME"' ''')
sub('Brak dostępu do konta')
p('Zachowaj outputs/site i uzgodnij z prowadzącym dokończenie publikacji. Nie wpisuj wymyślonego URL. Instrukcja jest przygotowana zgodnie z dokumentacją AGH, ale sprawdzenie konta wymaga rzeczywistego logowania właściciela.')
page();title('19. Typowe błędy i diagnoza')
table([['Objaw','Najpierw sprawdź'],['ImportError / ModuleNotFoundError','Aktywne .venv i wybrany kernel Jupyter.'],['Brak rastra','Paczka data/scene i bieżący katalog.'],['Niezgodna siatka','CRS, transformacja i wymiary wszystkich kanałów.'],['Brak przecięcia granicy','Współrzędne GeoJSON i reprojekcja do UTM.'],['Wynik tylko NaN','Maska QA, fill_value i zgodność produktu C1.'],['NDVI ponad 1','Ujemna reflektancja, mianownik i piksele QA. Nie obcinaj bez diagnozy.'],['Strona bez kafelków','Przesłanie całego site, ścieżki względne, wielkość liter.'],['Mapa odwrócona przestrzennie','Pomylenie TMS i XYZ; tutaj tms=False.'],['SSH timeout','Sieć AGH/VPN i poprawny host.'],['Permission denied','Login UNIX, aktywność konta i hasło UNIX.'],['404 / 403','Adres i index.html / prawa odczytu i przejścia.'],['Zajęty port 8000','Inny port, np. 8001, i zgodny adres przeglądarki.']],[170,305])
p('Nie zmieniaj wielu parametrów jednocześnie. Zachowaj pełny komunikat błędu, wskaż komórkę i sprawdź ostatni poprawny punkt kontrolny. To pozwala odróżnić błąd danych od błędu środowiska.','SmallPL')
page();title('20. Zadanie i kryteria zaliczenia')
p('Oddaj zapisany notatnik z wykonanymi komórkami. W sekcji „Moje wyniki” wpisz rzeczywisty adres mapy oraz trzy wnioski. Każdy wniosek powinien odnosić się do wskazanego miejsca, a nie tylko do definicji wskaźnika.')
table([['Element','Punkty','Warunek'],['Obliczenia i QA','4','Poprawne kanały, skala, NoData, georeferencja'],['Mapa','2','Warstwy, legenda, przezroczystość'],['Publikacja','2','Działający URL i komplet kafelków'],['Interpretacja','2','Trzy obserwacje i ograniczenia']],[125,55,295])
sub('Przykład formy odpowiedzi')
p('„W obszarze wskazanym współrzędnymi … obserwuję wysokie NDVI i zieloną strukturę na RGB. Wspiera to interpretację roślinności dla daty 2013-08-07.” Uzupełnij miejsce na podstawie własnej mapy; nie przepisuj tego zdania bez wskazania obiektu.')
sub('Pytania końcowe')
p('1. Dlaczego 0 nie jest NoData?<br/>2. Dlaczego dodatni NDBI nie wystarcza do rozpoznania zabudowy?<br/>3. Czym różni się GeoTIFF od kolorowego PNG?<br/>4. Dlaczego SSH dla home.agh.edu.pl używa innego hosta?<br/>5. Czy zoom 17 poprawia rozdzielczość Landsat?')
sub('Dla chętnych')
p('Oblicz NDWI B3/B5 i porównaj go z MNDWI. Następnie zmniejsz maxzoom do 11 i zapisz do osobnego katalogu. Porównaj rozmiar publikacji i czytelność.')
page();title('21. Źródła i odtwarzalność')
refs=[('1. Dane i parametry','USGS/EROS, ESPA XML dostarczonej sceny. Skala, zakresy DN i bity QA w data/scene/*.xml. Manifest opisuje przygotowanie wycinka i założenie CRS granicy.'),('2. USGS: NDVI','https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index'),('3. USGS: skala i offset','https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products'),('4. Wskaźniki NDBI i MNDWI','Zha, Gao, Ni (2003): doi.org/10.1080/01431160210144570. Xu (2006): doi.org/10.1080/01431160600589179.'),('5. CRI AGH: konta UNIX','https://cri.agh.edu.pl/uslugi/konta-unix (sprawdzono 30.09.2026).'),('6. Rasterio','https://rasterio.readthedocs.io/en/stable/topics/reproject.html'),('7. Leaflet 1.9.4','https://leafletjs.com/reference.html. Licencja biblioteki w src/vendor/LICENSE-Leaflet.txt.'),('8. Projekt źródłowy','NASA/Landsat8, pierwotny credit: S. Moliński. Pakiet zachowuje plik LICENSE projektu. IBIS pominięto.')]
for h,t in refs:sub(h);p(html.escape(t),'SmallPL')
p('requirements.txt utrwala wersje środowiska użytego do sprawdzenia ćwiczenia. summary.json zapisuje parametry i wyniki. tools/build_notebook.py odtwarza notatnik źródłowy, a tools/build_materials.py konspekt i treść slajdów.','SmallPL')

def footer(c,doc):
 c.saveState();c.setStrokeColor(HexColor('#d4e1e2'));c.line(48,42,547,42)
 c.setFont('Lab',8);c.setFillColor(HexColor('#49626b'))
 c.drawString(48,28,'LANDSAT 8  /  LABORATORIUM 90 MIN')
 c.drawRightString(547,28,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(OUT/'konspekt_landsat.pdf'),pagesize=(595.276,841.89),rightMargin=60,leftMargin=60,topMargin=48,bottomMargin=58,title='Landsat 8: konspekt laboratoryjny',author='Materiały dydaktyczne projektu NASA',pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('PDF gotowy')

# Treść slajdów: czas w minutach, tekst, uwagi prowadzącego i źródła.
slides=[]
def slide(title,minutes,body='',image=None,notes='',kind='text',source='Dane projektu NASA/Landsat8 i kod LABOLATORIUM/src/landsat_lab.py'):
 slides.append(dict(title=title,minutes=minutes,body=body,image=image,notes=notes,kind=kind,source=source))
slide('Landsat 8\nAnaliza i publikacja mapy',2,'Wykład 90 minut\nLaboratorium 90 minut\nKraków i okolice, 7 sierpnia 2013',kind='cover',notes='Przedstaw efekt zajęć: obliczenia w Pythonie i mapa na koncie AGH. Zapowiedz, że to analiza wskaźników, nie model uczenia maszynowego. Uczestnicy powinni znać podstawy tablic NumPy. IBIS pozostaje poza zakresem.')
slide('Efekt końcowy ćwiczenia',5,'NDVI, NDBI i MNDWI w jednej mapie\nGeoTIFF do dalszej analizy\nPublikacja na koncie UNIX AGH',notes='Otwórz przygotowaną stronę lokalnie. Przełącz cztery warstwy, pokaż legendę i przezroczystość. Wyjaśnij, że notatnik odtwarza te same wyniki. Zapytaj studentów, czy sam kolor mapy wystarczy do określenia pokrycia terenu. Zarezerwuj dwie minuty na odpowiedzi.')
slide('Scena i paczka danych',4,'2013-08-07, Collection 1 Surface Reflectance\n1583 × 1982 piksele, rozdzielczość 30 m\nB2–B6, pixel_qa, radsat_qa i XML',notes='Pokaż nazwy plików. Zwróć uwagę na sr_band i identyfikator L1TP w nazwie sceny. Dane zostały wycięte prostokątem bez resamplingu. XML opisuje pełną scenę, ale georeferencję wycinka czytamy z TIFF. Nie pobieramy archiwalnej Collection 1 na zajęciach, ponieważ używamy dostarczonych danych.')
slide('Kanały użyte w ćwiczeniu',4,'B2  niebieski\nB3  zielony\nB4  czerwony\nB5  NIR\nB6  SWIR1',kind='bands',notes='Powiąż kanały z RGB i wzorami wskaźników. Zapytaj, dlaczego RGB nie pokazuje wszystkiego, co rejestruje satelita. Nie myl numeracji pasm Landsat 8 z Landsat 5. Kanał B5 jest bliską podczerwienią, nie kanałem termalnym.')
slide('Georeferencja rastra',4,'EPSG:32634: metry w układzie UTM\nTransformacja wiąże wiersz i kolumnę z położeniem\nGeoJSON granicy: EPSG:4326',notes='Wyjaśnij znaczenie CRS i transformacji afinicznej. Jeden piksel ma 30 m. Przypisanie CRS to interpretacja istniejących liczb, reprojekcja to przeliczenie. Brak PRJ w oryginale został jawnie uzupełniony na podstawie zgodności ze starymi rastrami clipped; nie przedstawiaj tej granicy jako zweryfikowanej urzędowej geometrii.')
slide('Przycięcie do granicy',4,'Prostokąt ogranicza koszt odczytu\nMaska wielokąta wyznacza obszar analizy\nPoza granicą zapisujemy brak danych',image='band5_dn.png',notes='Pokaż prostokątny obraz B5. Omów odczyt tylko niezbędnej części sceny. Następnie transform_geom przelicza granicę, a geometry_mask tworzy maskę środków pikseli. Zmiana all_touched może zmienić liczbę pikseli na granicy.',kind='image')
slide('Skalowanie reflektancji',4,'ρ = DN × skala + offset\n6000 × 0.0001 = 0.6\nParametry pochodzą z XML',notes='Przelicz przykład na tablicy. W tej scenie add_offset nie występuje, więc przyjmujemy 0. C2 ma inne parametry, w tym offset. Nie opisuj 10000 jako maksimum wszystkich pikseli. XML dopuszcza wartości ujemne. Zapytaj, kiedy wspólna skala skraca się w ilorazie i dlaczego offset już się nie skraca.',source='ESPA XML; https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products')
slide('Maska jakości',5,f'W granicy: {S["inside_pixels"]:,} pikseli\nWażne: {S["valid_pixels"]:,}\nWoda pozostaje w analizie'.replace(',',' '),image='quality.png',kind='image',notes='Wyjaśnij flagi fill, cień, śnieg, chmury, przesłonięcie terenu i wysoką pewność cirrus. Wskaż osobną kontrolę nasycenia B2–B6. Odrzucono 98 pikseli w granicy, więc obraz jest prawie cały zielony. Białe tło oznacza obszar poza granicą. Poproś o rozkodowanie wartości 4 jako bitu wody.',source='Bity pixel_qa i radsat_qa w dołączonym ESPA XML; outputs/summary.json')
slide('Zero, wartość ujemna i NoData',4,'0 może być poprawną obserwacją\nNaN oznacza brak ważnego wyniku\nMianownik bliski zeru wymaga maski',image='band5_masked.png',kind='image',notes='Porównaj obraz po maskowaniu z poprzednim. Wyjaśnij różnicę między zerową reflektancją a brakiem danych. Znormalizowana różnica równych niezerowych kanałów daje zero. Dwa zera dają wynik nieokreślony. W kodzie granica bezpiecznego mianownika to 1e-6.')
slide('RGB jako odniesienie',4,'Kanały 4 / 3 / 2\nKontrast 2–98 percentyl\nObraz pomaga interpretować wskaźniki',image='rgb.png',kind='image',notes='Wskaż widoczne struktury pól, lasów i zabudowy. Rozciągnięcie kontrastu dotyczy tylko wyświetlania, osobno dla każdego kanału. Nie używamy tak zmodyfikowanych wartości do obliczeń wskaźników. Podkład internetowy może pokazywać nowszy stan terenu niż scena.')
slide('Znormalizowana różnica',4,'I = (A − B) / (A + B)\nA = 0.6, B = 0.2: I = 0.5\nA = B ≠ 0: I = 0',notes='Przykłady są dydaktyczne, nie są zmierzonymi pikselami mapy. Poproś studentów o obliczenie wyniku dla odwróconej pary 0.2 i 0.6. Wynik -0.5 pozostaje poprawny. Przy ujemnych wejściach iloraz może wyjść poza [-1,1]. Kod nie obcina wyników analitycznych.')
slide('NDVI: roślinność',4,'NDVI = (B5 − B4) / (B5 + B4)\nŚrednia w obszarze: 0.618\nInterpretacja zależy od daty i pokrycia',image='ndvi.png',kind='image',notes='Pokaż przestrzenny rozkład wysokich wartości. Zapytaj, czy każdy zielony piksel jest lasem. Wysoki NDVI nie identyfikuje gatunku ani nie jest samodzielną diagnozą zdrowia. Wskaż trzy piksele spoza [-1,1] w raporcie; na mapie kolor ograniczono, ale wartości GeoTIFF zachowano.',source='outputs/summary.json; https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index')
slide('NDBI: zabudowa i gleba',4,'NDBI = (B6 − B5) / (B6 + B5)\nDodatni wynik wymaga sprawdzenia RGB\nPróg nie jest gotową klasyfikacją',image='ndbi.png',kind='image',notes='Omów możliwość pomylenia odsłoniętej gleby z zabudową. Średnia wynosi -0.1905 i nie opisuje sama w sobie urbanizacji regionu. Przykład na tablicy: 0.35 i 0.20 daje około 0.273. Nie zakładaj, że każdy dodatni piksel jest budynkiem.',source='Zha, Gao, Ni (2003), DOI 10.1080/01431160210144570; outputs/summary.json')
slide('MNDWI: wody powierzchniowe',4,'MNDWI = (B3 − B6) / (B3 + B6)\nKanał zielony i SWIR1\nNDWI McFeetersa używa zielonego i NIR',image='mndwi.png',kind='image',notes='Wyjaśnij korektę nazewnictwa starego kodu: B3/B6 odpowiada MNDWI. Zaproponuj odszukanie rzeki i porównanie z RGB. Wąskie cieki mogą dawać piksele mieszane przy 30 m. Dodatni wynik nie zastępuje weryfikacji terenowej.',source='Xu (2006), DOI 10.1080/01431160600589179; dane projektu')
slide('Statystyki tego samego obszaru',4,'Średnia nie pokazuje rozmieszczenia przestrzennego\nWspólna maska ułatwia porównanie\nHistogram ujawnia rozkład wartości',kind='chart',notes='Pokaż edytowalny wykres średnich z summary.json. Uczestnicy powinni równolegle zajrzeć do histogramów w notatniku/PDF. Zwróć uwagę na różne znaczenia poszczególnych indeksów: porównanie wysokości słupków nie oznacza rankingu jakości. Średnie dotyczą wyłącznie ważnych pikseli.')
slide('Ograniczenia interpretacji',3,'Scena przedstawia 2013 rok\nPiksele 30 m mogą mieszać różne obiekty\nMaska QA nie usuwa każdej niepewności\nWskaźnik nie jest etykietą klasy',notes='Poproś o dwa przykłady błędnych wniosków: aktualna powierzchnia zabudowy z dawnej sceny i utożsamienie NDBI>0 z budynkami. Wskaż znaczenie walidacji niezależnymi danymi. Temat MODIS można zasygnalizować jako dalszą analizę czasową, bez dodawania ćwiczenia do tego laboratorium.')
slide('GeoTIFF do dalszych obliczeń',3,'float32 i NoData = −9999\nCRS i transformacja z wejścia\nOdczyt kontrolny sprawdza wartości',notes='Pokaż pliki NDVI.tif i NDVI_display.tif. Ten drugi zapisuje kolory, nie NDVI. Omów test allclose z equal_nan=True oraz sprawdzenie CRS i transformacji. Student powinien rozumieć, dlaczego screenshot mapy nie zastępuje danych.')
slide('Kolor i przezroczystość',3,'Zakres legendy: −1 do 1\nRGBA: kolor oraz kanał alfa\nBrak danych pozostaje przezroczysty',notes='Wyjaśnij wspólny zakres legendy. Dwie mapy z automatycznym min/max mogą wyglądać podobnie mimo różnych wartości. Przedstaw przykład NDVI 1.0062: numerycznie pozostaje w TIFF, a na mapie dostaje skrajny kolor. Odróżnij alfa od globalnej przezroczystości suwaka.')
slide('Kafelki XYZ',4,'256 × 256 pikseli, EPSG:3857\nz / x / y.png, y rośnie na południe\nZoom 9–12: 512 plików dla czterech warstw',notes='Omów piramidę zoomów i wpływ maksymalnego zoomu na liczbę plików. Pomieszanie XYZ z TMS odwraca indeks y. Reprojekcja odbywa się w Pythonie przez Rasterio. Nie zwiększamy informacyjnej rozdzielczości obrazu, kiedy użytkownik powiększa kafelki do zoomu 17.',source='Kod xyz_tiles; https://rasterio.readthedocs.io/en/stable/topics/reproject.html; https://leafletjs.com/reference.html')
slide('Kompletna mapa WWW',3,'index.html oraz katalogi tiles i vendor\nWybór warstwy, legenda i przezroczystość\nPodkład OpenStreetMap wymaga internetu',notes='Przeprowadź krótką demonstrację strony. Nie trzeba instalować Pythona na serwerze AGH, ponieważ przesyłamy statyczne pliki. Bibliotekę Leaflet dołączono lokalnie. Zachowujemy informacje o autorstwie podkładu. Sama publikacja HTML bez tiles prowadzi do pustej mapy.')
slide('Podgląd lokalny',3,'python -m http.server 8000\n--bind 127.0.0.1 --directory outputs/site\nhttp://127.0.0.1:8000/',notes='Dwie pierwsze linie na slajdzie stanowią jedno polecenie. W Markdown jest gotowy blok do skopiowania. Wyjaśnij, dlaczego nie używać file:// i że serwer pozostaje zajęty do Ctrl+C. Drugie okno terminala służy do SSH/SCP. Przy zajętym porcie wybieramy 8001.',kind='command')
slide('SSH i konta AGH',3,'Student: student.agh.edu.pl\nProwadzący: galaxy.agh.edu.pl\nPołączenie z sieci AGH lub przez VPN',notes='Wyjaśnij rozdział hosta SSH i WWW. Dla galaxy WWW to home.agh.edu.pl/~login. Strony studentów są dostępne w sieci AGH/VPN. Używamy loginu UNIX bez sufiksu @student. Pierwsze połączenie wymaga sprawdzenia klucza serwera. Nie zapisujemy haseł w notatniku.',source='https://cri.agh.edu.pl/uslugi/konta-unix, sprawdzono 30.09.2026')
slide('SCP i sprawdzenie publikacji',3,'Osobny katalog public_html/landsat-DATA\nPrzesyłamy całą zawartość outputs/site\nSprawdzamy URL i wszystkie warstwy',notes='Pokaż polecenie scp -r outputs/site/. i składnię login@host:ścieżka. Nowy katalog chroni istniejącą stronę główną. Uprawnienia katalogów 755, plików 644. HTTP 200 dla index.html nie dowodzi poprawnego przesłania kafelków. Pełne polecenia są w notatniku, PDF i Markdown.')
slide('Laboratorium: 90 minut',3,'0–40 min: dane, CRS i jakość\n40–55 min: wskaźniki\n55–70 min: mapa lokalna\n70–90 min: publikacja i oddanie',notes='Przypomnij konieczność przygotowania środowiska przed zajęciami. Każdy student ma uruchomić notatnik i zrozumieć najważniejszy fragment np.divide. Modyfikacja progu NDVI jest krótkim eksperymentem. Rezultat: URL, notatnik, trzy wnioski. Gdy konto nie działa, zachowujemy paczkę strony, ale nie udajemy publikacji.')
slide('Pytania sprawdzające',2,'Dlaczego 0 nie jest NoData?\nCzy dodatni NDBI oznacza budynek?\nCo trzeba przesłać oprócz index.html?\nCzy zoom 17 dodaje szczegóły?',notes='Odpowiedzi: zero może być ważną wartością; dodatni NDBI może oznaczać glebę; potrzebne są tiles, vendor i pliki danych strony; powiększenie nie zmienia rozdzielczości źródłowej. Zakończ wskazaniem konspektu i notatnika. Źródła naukowe oraz dokumentacja znajdują się w końcowej części PDF i notatnika.')
assert len(slides)==25 and sum(s['minutes'] for s in slides)==90
(ROOT/'tools/wyklad_tresc.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
print('Treść 25 slajdów / 90 minut gotowa')
