import subprocess
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

experimental_file = 'data/MOD11B3.A2016214.h19v03.006.2016286174218.hdf'
dataset = gdal.Open(experimental_file)
subdatasets = dataset.GetSubDatasets()
scaling_factor = 0.02

lst_day = gdal.Open(subdatasets[0][0])
array_lst_day = lst_day.ReadAsArray().astype(np.float32) * scaling_factor

celsius_lst_day = array_lst_day - 273.15
celsius_lst_day[celsius_lst_day < 0] = np.nan

# plt.rcParams.update({'figure.figsize': (20, 20), 'figure.dpi': 300})

plt.figure(figsize=(15, 12), dpi=300)
# plt.figure(figsize=(10, 20), dpi=150)
imgplot = plt.imshow(celsius_lst_day)
imgplot.set_cmap('plasma')
plt.colorbar(label='Temperature in Celsius')
plt.title('Land Surface Temperature Daytime')
plt.ylabel('MODIS Grid Vertical number')
plt.xlabel('MODIS Grid Horizontal number')

plt.show()
