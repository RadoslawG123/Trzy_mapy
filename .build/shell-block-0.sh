cd "/Users/owerko/PycharmProjects/NASA/LABOLATORIUM"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import rasterio, numpy; print(rasterio.__version__, numpy.__version__)"
python -m ipykernel install --sys-prefix --name landsat-lab --display-name "Python (Landsat LAB)"
python -m jupyterlab notebooks/landsat_od_danych_do_www.ipynb
