from operator import itemgetter

import pymodis
import seaborn
import statsmodels


# Credit: S.Moliński

class ModisRequest:

    def __init__(self, interactive=False, output_folder=''):
        self.interactive = interactive
        self.modis_request = None
        available_datasets = self._initialize_datasets()
        self.data_dict = available_datasets[0]
        self.datasets_description = available_datasets[1]
        self.output = output_folder

    @staticmethod
    def _initialize_datasets():

        # VARIABLES
        # Create variables based on this example below
        lst_annual = ['MOD11B3.006',
                      'MODIS/Terra Land Surface Temperature and Emissivity Monthly L3 Global 6 km Grid SIN V006']
        vi_annual = ['MOD13C2.006',
                     'MODIS/Terra Vegetation Indices Monthly L3 Global 0.05 Deg CMG V006']

        # VARIABLES GROUP
        variables = [lst_annual, vi_annual]  # Add here new variables
        sorted_variables = sorted(variables, key=itemgetter(0))

        # DATA TYPE DICTIONARY and DESCRIPTION TEXT
        data_type_dict = {}
        description_text = 'Select number to get a modis set:\n'
        i = 0
        for variable in sorted_variables:
            i = i + 1
            data_type_dict[i] = variable[0]
            description_text = description_text + (str(i) + ': ' + variable[1] + '\n')

        return data_type_dict, description_text

    def prepare_requests(self, username=None, password=None, input_information=None):

        if self.interactive:
            input_information = self._get_input_data()

        variable = self.data_dict[input_information[0]]

        if username is None:
            username = input('Please, provide your username and press RETURN:\n')

        if password is None:
            password = input('Please, provide your password and press RETURN:\n')

        downloading_object = pymodis.downmodis.downModis(destinationFolder=input_information[4],
                                                         password='uNVGP_i3paYC3L4RcNMc',
                                                         user='owerko',
                                                         tiles=input_information[1],
                                                         path='MOLT',
                                                         product=variable,
                                                         today=input_information[2],
                                                         enddate=input_information[3])
        self.modis_request = downloading_object
        return downloading_object

    def _get_input_data(self):

        input_info = []

        # Select variable
        selected_variable = int(input(self.datasets_description + 'After selection press RETURN\n'))
        input_info.append(selected_variable)

        # Select tiles
        tiles_text = 'Please, choose tiles for download. Default are h18v03, h18v04, h19v03, h19v04\n' \
                     'If default type d and press RETURN else type tilenames separated by comma and press RETURN\n'

        tiles_text = input(tiles_text)

        if tiles_text == 'd':
            tiles = 'h18v03,h18v04,h19v03,h19v04'
        else:
            tiles = tiles_text

        input_info.append(tiles)

        # Select years
        year_selection_start = 'Please provide start year-month-day of analysis in the form:\n' \
                               'YYYY-MM-DD and press RETURN):\n'
        year_selection_end = 'Please provide end year-month-day of analysis in the form:\n' \
                             'YYYY-MM-DD and press RETURN):\n'
        input_info.append(input(year_selection_start))
        input_info.append(input(year_selection_end))

        # Output file
        output_filename = self.output
        name = input('Please, provide output filename and press RETURN:\n')
        input_info.append(output_filename + name)
        return input_info

    def get_modis_data(self):
        self.modis_request.connect()
        self.modis_request.downloadsAllDay()
        return True

    def __str__(self):
        output = ''
        for key in self.data_dict:
            output = 'Select key {} to get the {}'.format(key, self.data_dict[key])
        return output


if __name__ == '__main__':
    mr = ModisRequest(True)
    mr.prepare_requests()
    mr.get_modis_data()

