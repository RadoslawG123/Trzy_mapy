from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'notebooks/landsat_od_danych_do_www.ipynb'
nb=nbformat.read(p,as_version=4)
NotebookClient(nb,timeout=300,kernel_name='landsat-lab',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,p)
print('Notatnik wykonany od czystego kernela:',len(nb.cells),'komórek')
