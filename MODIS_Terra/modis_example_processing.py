import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt

example_file = 'data/MOD11B3.A2016214.h19v03.006.2016286174218.hdf'

dataset = gdal.Open(example_file)
subdatasets = dataset.GetSubDatasets()
for subdataset in subdatasets:
    print(subdataset[1])

scale = 0.02
lst_day = gdal.Open(subdatasets[0][0])
lst_night = gdal.Open(subdatasets[4][0])

array_lst_day = lst_day.ReadAsArray().astype(np.float32) * scale
array_lst_night = lst_night.ReadAsArray().astype(np.float32) * scale

print('Max LST during the day:', np.max(array_lst_day))
print('Max LST during the night:',  np.max(array_lst_night))
celsius_lst_day = array_lst_day - 273.15
celsius_lst_day[celsius_lst_day < 0] = np.nan
celsius_lst_night = array_lst_night - 273.15
celsius_lst_night[celsius_lst_night < 0] = np.nan

plt.figure(figsize=(10,10))
imgplot = plt.imshow(celsius_lst_day)
imgplot.set_cmap('plasma')
plt.colorbar()
plt.title('LST daytime')
plt.show()

plt.figure(figsize=(10,10))
imgplot = plt.imshow(celsius_lst_night)
imgplot.set_cmap('plasma')
plt.colorbar()
plt.title('LST nighttime')
plt.show()

del lst_day
del lst_night
del dataset
