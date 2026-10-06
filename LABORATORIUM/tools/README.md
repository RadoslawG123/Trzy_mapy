# Odtwarzanie materiałów przez prowadzącego

Student korzysta z gotowego notatnika i `src/landsat_lab.py`. Poniższe skrypty są narzędziami redakcyjnymi.

1. `przygotuj_dane.py` odtwarza `data/` z oryginalnego katalogu `../Landsat8`. Wymaga dodatkowo Fiona. Nie zmienia oryginałów. Założenie CRS granicy jest jawnie zapisane w kodzie i manifeście.
2. `build_notebook.py` odtwarza notatnik źródłowy z instrukcją publikacji pobraną z `docs/polecenia_iterm.md`. **Zastępuje bieżący notatnik i usuwa jego zapisane wyniki**, dlatego najpierw zachowaj kopię pracy studentów.
3. `execute_notebook.py` wykonuje notatnik z czystego kernela `landsat-lab` i zapisuje wyniki. Kernel zarejestruj zgodnie z głównym README.
4. `build_materials.py` buduje konspekt PDF i `wyklad_tresc.json` z `outputs/summary.json` i ilustracji. Potrzebuje ReportLab i Pillow. Pełne środowisko odtwarza `requirements-lock.txt`. Zrzut `outputs/figures/map_web.png` pokazuje działającą mapę w przeglądarce; odśwież go po zmianie wyglądu strony.
5. `build_slides.mjs` tworzy PPTX przez dostarczone środowisko prezentacji Codex (`@oai/artifact-tool`), sprawdza plik i renderuje slajdy. Wymaga `RUNTIME_NODE_MODULES`, `RUNTIME_PYTHON`, `PRESENTATION_SKILL_DIR` i Node dostarczonego przez to środowisko. Podaj ścieżkę do LABOLATORIUM jako pierwszy argument. Import pakietu wymaga `node_modules` wskazującego na pakiety środowiska. Wynik ma nazwę `wyklad_landsat_90min_rebuild.pptx`; przed kolejnym przebudowaniem przenieś poprzedni wynik i raport `.build/presentation-validation-rebuild.json`, ponieważ walidator ich nie nadpisuje.

PPTX zawiera edytowalny tekst i edytowalny wykres z osadzonym arkuszem danych. Mapy rastrowe są ilustracjami. Wersję do rozdania można edytować bez tych narzędzi bezpośrednio w PowerPoint.
