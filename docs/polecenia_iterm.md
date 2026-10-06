# Polecenia iTerm: obliczenia i publikacja

Polecenia wykonuj kolejno. Bloki `bash` wklejaj do iTerm (macOS, zsh/bash), nie do komórek Pythona. Nie wklejaj znaków zachęty `$`. Instalację i sprawdzenie konta wykonaj **przed laboratorium**. Wymagany Python 3.12 i aktywne konto UNIX AGH. Hasło konta UNIX może różnić się od hasła poczty.

## 1. Katalog i środowisko lokalne

Poniżej rzeczywista ścieżka tego projektu. Na komputerze studenta zastąp ją położeniem otrzymanej paczki `LABOLATORIUM`.

```bash
cd "/Users/owerko/PycharmProjects/NASA/LABOLATORIUM"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import rasterio, numpy; print(rasterio.__version__, numpy.__version__)"
python -m ipykernel install --sys-prefix --name landsat-lab --display-name "Python (Landsat LAB)"
python -m jupyterlab notebooks/landsat_od_danych_do_www.ipynb
```

W Jupyter wybierz kernel **Python (Landsat LAB)**. Jeżeli lokalny `python3` ma wersję 3.12, możesz użyć go zamiast `python3.12`. Środowisko `.venv` odtwarzaj z pliku requirements, nie kopiuj go między komputerami. W nowym oknie terminala ponownie przejdź do `LABOLATORIUM` i wykonaj `source .venv/bin/activate`.

## 2. Całość obliczeń jednym poleceniem

Alternatywa dla uruchamiania notatnika krok po kroku:

```bash
python src/landsat_lab.py
python -m unittest discover -s tests
```

Powstaną `outputs/rasters`, `outputs/figures`, `outputs/site` oraz `outputs/summary.json`. Uruchomienie ponownie odtwarza te same wyniki. Zmiana zakresu zoomów może pozostawić na dysku stare, nieużywane kafelki; do osobnego eksperymentu użyj osobnego katalogu:

```bash
python src/landsat_lab.py --output outputs/eksperyment --minzoom 9 --maxzoom 11
```

## 3. Podgląd strony lokalnie

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory outputs/site
```

Otwórz `http://127.0.0.1:8000/`. Pozostaw ten terminal uruchomiony. Zatrzymanie: **Ctrl+C**. Gdy port 8000 jest zajęty, wybierz 8001 i zmień adres w przeglądarce. Nie uruchamiaj podglądu przez `file://`.

Sprawdź NDVI, NDBI, MNDWI i RGB, legendę, przezroczystość i powiększenie. Podkład OpenStreetMap wymaga internetu. Kafelki wynikowe i biblioteka Leaflet są dołączone do strony.

## 4. Wybór konta i sprawdzenie SSH

Według [CRI AGH](https://cri.agh.edu.pl/uslugi/konta-unix) SSH/SCP wymaga sieci AGH lub VPN. Serwer studentów to `student.agh.edu.pl`, a pracowników i doktorantów `galaxy.agh.edu.pl`. Strony na serwerze student są dostępne w sieci uczelni/VPN, nie w całym internecie.

W **nowym lokalnym terminalu**, w katalogu LABOLATORIUM, wybierz JEDEN wariant. Używaj loginu UNIX, bez części `@...`.

**Student:**

```bash
read "AGH_LOGIN?Podaj login UNIX AGH: "
AGH_HOST="student.agh.edu.pl"
AGH_WEB="https://student.agh.edu.pl"
```

`read "zmienna?tekst"` jest składnią zsh w iTerm/macOS. W bash zamiast pierwszej linii użyj `read -r -p "Podaj login UNIX AGH: " AGH_LOGIN`.

**Prowadzący, konto odpowiadające stronie home.agh.edu.pl/~owerko:**

```bash
AGH_LOGIN="owerko"
AGH_HOST="galaxy.agh.edu.pl"
AGH_WEB="https://home.agh.edu.pl"
```

Następnie w obu wariantach:

```bash
ssh "${AGH_LOGIN}@${AGH_HOST}"
```

Przy pierwszym połączeniu zweryfikuj odcisk klucza hosta według informacji administratora. Nie wyłączaj sprawdzania kluczy SSH. Terminal nie pokazuje wpisywanych znaków hasła.

Poniższe trzy polecenia wykonujesz już **na serwerze**:

```bash
pwd
ls -ld "$HOME" public_html
exit
```

Brak `public_html` przy pierwszym logowaniu jest normalny. `exit` kończy sesję zdalną. Kolejne polecenia wykonujesz ponownie lokalnie. Zmienne AGH ustawione lokalnie pozostają dostępne.

## 5. Przygotowanie osobnego katalogu publikacji

Publikujemy w nowym podkatalogu z datą i godziną. Główna strona `~/public_html/index.html` pozostaje nietknięta. Nazwa powstaje automatycznie i zawiera wyłącznie bezpieczne znaki.

```bash
AGH_FOLDER="landsat-$(date +%Y%m%d-%H%M%S)"
ssh "${AGH_LOGIN}@${AGH_HOST}" "mkdir -p public_html/${AGH_FOLDER} && chmod 755 public_html public_html/${AGH_FOLDER}"
```

## 6. Przesłanie CAŁEJ strony przez SCP

Polecenie wykonaj lokalnie z katalogu `LABOLATORIUM`. Końcówka `/.` oznacza zawartość katalogu strony.

```bash
scp -r outputs/site/. "${AGH_LOGIN}@${AGH_HOST}:public_html/${AGH_FOLDER}/"
ssh "${AGH_LOGIN}@${AGH_HOST}" "find public_html/${AGH_FOLDER} -type d -exec chmod 755 {} + && find public_html/${AGH_FOLDER} -type f -exec chmod 644 {} +"
```

Na serwer trafiają `index.html`, `vendor`, `tiles`, `aoi.geojson` i `summary.json`. Nie przesyłaj `.venv`, surowych danych ani całego projektu. Ponowne SCP do tego samego katalogu aktualizuje znajdujące się tam pliki.

## 7. Weryfikacja publikacji

```bash
ssh "${AGH_LOGIN}@${AGH_HOST}" "test -f public_html/${AGH_FOLDER}/index.html && test -f public_html/${AGH_FOLDER}/vendor/leaflet.js && find public_html/${AGH_FOLDER}/tiles -name '*.png' | wc -l"
AGH_URL="${AGH_WEB}/~${AGH_LOGIN}/${AGH_FOLDER}/"
printf '%s\n' "$AGH_URL"
curl -I "$AGH_URL"
open "$AGH_URL"
```

`open` jest poleceniem macOS. Na innym systemie skopiuj wypisany adres do przeglądarki. Oczekuj odpowiedzi HTTP 200 (lub przekierowania prowadzącego do 200), działających warstw i kompletnej legendy. Sama odpowiedź 200 dla HTML nie potwierdza obecności kafelków.

Gdy pojawi się 403, sprawdź prawa katalogów i plików. Jeśli serwer wymaga prawa przejścia przez katalog domowy, po sprawdzeniu ustawień konta możesz nadać wyłącznie to prawo: `ssh "${AGH_LOGIN}@${AGH_HOST}" 'chmod o+x "$HOME"'`. Nie stosuj `chmod -R 777`.

## 8. Oddanie zadania

Zapisz notatnik z wynikami. W jego ostatniej komórce Markdown wpisz rzeczywisty adres mapy i trzy wnioski, po jednym dla każdego wskaźnika. Nie zapisuj haseł ani prywatnych kluczy w notatniku.

## Typowe problemy

| Objaw | Działanie |
|---|---|
| `python3.12: command not found` | Zainstaluj Python 3.12 przed zajęciami lub użyj środowiska prowadzącego. |
| `ModuleNotFoundError` | Aktywuj .venv i wybierz poprawny kernel. |
| `Address already in use` | Użyj wolnego portu, np. 8001. |
| SSH timeout | Połącz VPN AGH, sprawdź host. |
| `Permission denied` | Sprawdź login UNIX, hasło konta i aktywację konta. |
| HTTP 404 | Sprawdź nazwę katalogu, wielkość liter i index.html. |
| HTTP 403 | Sprawdź 755 dla katalogów, 644 dla plików oraz prawo przejścia katalogu domowego. |
| Mapa bez danych | Prześlij również tiles i vendor; sprawdź błędy żądań w przeglądarce. |
| Brak podkładu | Sprawdź internet; warstwy lokalne powinny działać niezależnie. |

Parametry infrastruktury zweryfikowano w dokumentacji CRI AGH 30.09.2026. Połączenie z indywidualnym kontem i faktyczna publikacja wymagają uwierzytelnienia właściciela konta; nie są wykonywane automatycznie przez notatnik.
