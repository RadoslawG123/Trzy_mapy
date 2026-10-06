import subprocess
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

test_image = 'data/MOD11B3.A2016214.h19v03.006.2016286174218.hdf'

vector = 'vector/czernichow.shp'
lst_output = 'test2_lst.tiff'

# Read image and process it

dataset = gdal.Open(test_image)
subdatasets = dataset.GetSubDatasets()
del dataset

lst_day = subdatasets[0][0]
subprocess.call(['gdalwarp',
                 '-cutline',
                 vector,
                 '-crop_to_cutline',
                 '-dstalpha',
                 lst_day,
                 lst_output])
del lst_day

# Check output
scaling_factor = 0.02
lst_day = gdal.Open(lst_output)
array_lst_day = (lst_day.ReadAsArray().astype(np.float32))[0] * scaling_factor
del lst_day

celsius_lst_day = array_lst_day - 273.15
celsius_lst_day[celsius_lst_day < 0] = np.nan

plt.figure(figsize=(10,10))
imgplot = plt.imshow(celsius_lst_day)
imgplot.set_cmap('plasma')
plt.colorbar()
plt.title('LST daytime selected Area')
plt.show()
