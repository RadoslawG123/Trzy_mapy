import datetime
import json
import os
import subprocess
import numpy as np
import gdal


def get_filelist(folder, infile='', file_ending=''):
    output_filelist = []

    filelist = os.listdir(folder)
    check_infile = (len(infile) > 0)
    check_file_suffix = (len(file_ending) > 0)

    if check_infile or check_file_suffix:
        for filename in filelist:
            if check_infile and check_file_suffix:
                if (infile in filename) and filename.endswith(file_ending):
                    output_filelist.append(filename)
            elif check_infile:
                if infile in filename:
                    output_filelist.append(filename)
            else:
                if filename.endswith(file_ending):
                    output_filelist.append(filename)
    else:
        output_filelist = filelist
    return output_filelist


def get_modis_subdataset(filename, subdataset_number):
    dataset = gdal.Open(filename)
    subdatasets = dataset.GetSubDatasets()
    subdataset = subdatasets[subdataset_number][0]
    del dataset
    return subdataset


def get_date_from_filename(fname: str):

    fname_parts = fname.split('.')
    for idx, part in enumerate(fname_parts):
        if 'MOD' in part:
            next_part = fname_parts[idx + 1]
            next_pt_len = len(next_part)
            if next_pt_len == 8 and next_part.startswith('A'):
                julian_date = next_part[1:]
                return julian_date
    return 0


def convert_date(julian_date: str):

    string_len = len(julian_date)

    # Test if string has a proper number of chars
    assert string_len == 7, 'Passed string must have 7 characters in the form of YYYYDDD'

    standard_date = datetime.datetime.strptime(julian_date, '%Y%j').date()
    standard_date_tuple = (standard_date.year, standard_date.month, standard_date.day)
    return standard_date_tuple


# Data clipping

def clip_dataset(input_raster, input_mask, output_filename):

    subprocess.call(['gdalwarp',
                     '-cutline',
                     input_mask,
                     '-crop_to_cutline',
                     '-dstalpha',
                     input_raster,
                     output_filename])


# LST calculation

def calculate_mean_lst(input_raster):
    scaling_factor = 0.02
    lst_day = gdal.Open(input_raster)
    array_lst_day = (lst_day.ReadAsArray().astype(np.float32))[0] * scaling_factor
    del lst_day
    mean_value = np.mean(array_lst_day[array_lst_day > 0])
    return float(mean_value)


# Save dictionary into a csv file

def dict_to_json(temperature_dict, json_path):

    with open(json_path, 'w') as json_file:
        json.dump(temperature_dict, json_file)
    print('File {} saved successfully'.format(
        json_path))



# Base variables
# Raw data
data_folder = 'data/'
infile = 'h19v03'
hdf_file_end = '.hdf'
tiff_file_end = '.tiff'

# TIFF
subdatasets = {'lst_day': 0,
              'lst_night': 4}
vector = 'vector/czernichow.shp'
tiff_folder = 'tiffs/'

# JSON
output_filename = 'temperature_modis.json'
json_folder = 'json/'


# Get filelist
filelist = get_filelist(data_folder, infile, hdf_file_end)



# First loop of the function - raw hdf images to tiffs
for key in subdatasets:
    for file in filelist:
        tiff_filename = key + '_' + file[:-4] + tiff_file_end
        tiff_path = os.path.join(tiff_folder, tiff_filename)
        raw_file_path = os.path.join(data_folder, file)
        mod_subdataset = get_modis_subdataset(raw_file_path, subdatasets[key])
        clip_dataset(mod_subdataset, vector, tiff_path)

# Get new filelist with processed tiffs

tiffs = get_filelist(tiff_folder, infile, tiff_file_end)

# Build dictionary which simulates a JSON file

data_dicts = {}

for subdataset in subdatasets:
    if subdataset not in data_dicts:
        data_dicts[subdataset] = {}
    for tiff in tiffs:
        if subdataset in tiff:
            # Get date
            file_date = get_date_from_filename(tiff)
            converted_date = convert_date(file_date)
            date_key = str(converted_date[0]) + '-' + str(converted_date[1])

            # Get LST value
            mean_value = calculate_mean_lst(tiff_folder + tiff)

            # Update dictionary
            data_dicts[subdataset][date_key] = mean_value


# Save a new JSON file

dict_to_json(data_dicts, json_folder + output_filename)