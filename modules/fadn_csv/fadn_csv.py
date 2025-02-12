import shutil
import os
import logging
import datetime
import sys

import pandas as pd

from modules.fadn import fadn
from modules.dictionaries import dictionaries


class FadnCsv(fadn.Fadn):
    """
    Subclass of Fadn that deals with pre-processing tasks performed on csv files provided in Fadn package.
    """
    def __init__(self, url, results_dir):
        """
        :param url: str -> url to the zip file.
        """
        super().__init__(results_dir=results_dir)
        self.directory = os.path.join('statics', 'templates', 'csv')
        self.main_dictionary = dictionaries.fadn_dictionary
        self.range = None
        self.url = url

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_fadn_csv_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def set_range(self, file_path):
        """
        Function that sets up range of dates based on the content of main CSV file.
        The range is used in further processing.
        file_path -> str, path to the CSV file that range should be derived from.
        """
        df = pd.read_csv(file_path, delimiter=';')
        mn = df['YEAR'].min()   # grabbing the lowest YEAR value in the data set.
        mx = df['YEAR'].max()   # grabbing the highest YEAR value in the data set.
        r = range(mn, mx + 1)
        self.range = r

    # PIPELINE OPERATIONS

    def organize_fadn_folder(self, delete_folder='SGM', folder='SO'):
        """
        Function that deletes redundant files in FADN data.
        delete_folder-> str, folder that has to be deleted including all the contents.
        folder-> str, folder for which the content has to be moved to the main directory.
        """
        print('########## Organizing folders...')
        del_folder_path = os.path.join(self.destination_path, delete_folder)
        if os.path.isdir(del_folder_path):
            shutil.rmtree(del_folder_path)
        else:
            print("The data folder does not contain files that were expected... Shutting down the Pipeline. "
                  "Inspect log files to get more info!")
            self.logger.info("The SGM folder was not found in the data directory. Script can not recognize this structure"
                        " of data properly!")
            sys.exit()
        folder_path = os.path.join(self.destination_path, folder)
        if os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            for file in files:
                file_path = os.path.join(folder_path, file)
                shutil.move(file_path, self.destination_path)
            os.rmdir(folder_path)
        else:
            print("The data folder does not contain files that were expected... Shutting down the Pipeline. "
                  "Inspect log files to get more info!")
            self.logger.info("The SO folder was not found in the data directory. Script can not recognize this structure"
                        " of data properly!")
            sys.exit()

    def organize_fadn_directories(self):
        """
        Function that creates a set of directories for each csv file.
        """
        self.set_date()   # setting proper data based on the filename.
        files = os.listdir(self.destination_path)
        for file in files:
            if file.endswith(".csv"):
                filename = file[:-4]
                if 'REGION' in filename:
                    filename = filename.replace('.COUNTRY', '')   # removing COUNTRY from the directory name.
                folder_path = os.path.join(self.destination_path, filename)
                os.mkdir(folder_path)
                file_path = os.path.join(self.destination_path, file)   # path to existing csv file.
                file_new_path = os.path.join(folder_path, file)   # new path where csv file should be moved.
                shutil.move(file_path, file_new_path)

    def typos_correction(self, package_name='YEAR.COUNTRY.TF_GEN1.TF_PRIN2.TF_SUBP4'):
        """
        Function that makes correction to few typing errors provided with the original csv files.
        package_name -> str, name of the package that should be amended.
        """
        print('########## Typos correction to the vanilla CSV...')
        file = package_name + '.csv'
        file_path = os.path.join(self.destination_path, package_name, file)
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path, delimiter=';')
            # 1st fix
            df['TF_GEN1'] = df['TF_GEN1'].str.replace('Specialist  granivore', 'Specialist granivore')
            # 2nd fix
            df['TF_SUBP4'] = df['TF_SUBP4'].str.replace('Specialist fruit, citrus, subtropical fruits and nuts: '
                                                        'mixed productio',
                                                        'Specialist fruit citrus subtropical fruits and nuts: '
                                                        'mixed production')
            df.to_csv(file_path, sep=';', index=False)

    def preprocess_all_packages(self, auxiliary_directory=True):
        """
        Function that executes all the preprocessing transformations for each package
        present in the data location.
        """
        print('########## Pre-processing all packages...')
        for subdir, dirs, files in os.walk(self.destination_path):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(subdir, file)
                    filename = file[:-4]
                    if 'REGION' in filename:
                        filename = filename.replace('.COUNTRY', '')  # removing COUNTRY from the CSV filename.
                    if auxiliary_directory:
                        folder_path = os.path.join(subdir, 'auxiliary_csv')
                        os.mkdir(folder_path)
                        print(f'Currently processing {file}...')
                        self.logger.info(f'{file}:')
                        self._process_csv_content(file_path, filename, folder_path, auxiliary_directory=True)
                    else:
                        print(f'Currently processing {file}...')
                        self.logger.info(f'{file}:')
                        self._process_csv_content(file_path, filename, folder_path=None, auxiliary_directory=False)

    def create_auxiliary_csv_files(self):
        """
        Function that creates auxiliary csv files for each of the package present in the data location.
        """
        print('########## Creating auxiliary CSV files for all packages...')
        folders = os.listdir(self.destination_path)
        r_path = os.path.join(self.destination_path, 'YEAR.COUNTRY', 'YEAR.COUNTRY.csv')   # path to the main CSV.
        if not os.path.isfile(r_path):
            print("The expected file was not found. Shutting down the Pipeline, please check log files for more info.")
            self.logger.info(f"Script was expecting to find a file using following path: {r_path}. Please revise your"
                        f" input data.")
            sys.exit()
        self.set_range(r_path)
        for folder in folders:
            print(f'Creating auxiliary csv files for {folder}')
            save_to_path = os.path.join(self.destination_path, folder, 'auxiliary_csv', folder.lower())
            # 1 file: Measures
            self._create_measures(save_to_path)
            # 2 file: Organisation
            self._create_org(save_to_path)
            # 3 file: Dataset
            self._create_dataset(save_to_path, folder)
            # 4 file: Dimensions
            self._create_dimensions(save_to_path, folder)
            # 5 file: Datastructure
            self._create_datastructure(save_to_path, folder)
            # 6 file: SliceKey
            self._create_slicekey(save_to_path, folder)
            # checking if csv should be created for a particular package.
            # 7 file: ANC3
            if 'anc3' in folder.lower():
                self._create_anc3(save_to_path)
            # 8 file: SIZC
            if 'sizc' in folder.lower():
                self._create_sizc(save_to_path)
            # 9 file: TF8
            if 'tf8' in folder.lower():
                self._create_tf8(save_to_path)
            # 10 file: TF14
            if 'tf14' in folder.lower():
                self._create_tf14(save_to_path)
            # 11 file: SIZ6
            if 'siz6' in folder.lower():
                self._create_siz6(save_to_path)
            # 12 file: PRIN2
            if 'prin2' in folder.lower():
                self._create_prin2(save_to_path)
            # 13 file: SUBP4
            if 'subp4' in folder.lower():
                self._create_subp4(save_to_path)
            # 14 file: GEN1
            if 'gen1' in folder.lower():
                self._create_gen1(save_to_path)
            self._create_slices(save_to_path, folder)

    # PRE-PROCESSING PART

    def _process_csv_content(self, file_path, filename, folder_path, auxiliary_directory):
        """
        Semi-private function that pre-process single inputted csv file into desired csv
        by set of actions performed by Pandas library.
        :param file_path: str -> path to the file.
        :param filename: str -> name of the file.
        :param folder_path: -> path to the folder.
        :param auxiliary_directory: boolean -> if true there will be auxiliary directory created, else
        it will be omitted.
        """
        df = pd.read_csv(file_path, delimiter=';')
        if 'REGION' in df:
            df.drop('COUNTRY', axis=1, inplace=True)
            self._merge_region(df)
            self._adjust_sizc_code(df)
            self._adjust_siz6_code(df)
            self._adjust_tf8_code(df)
            self._adjust_tf14_code(df)
            self._set_index_column(df)
        else:
            self._adjust_country_code(df)
            self._adjust_anc3_code(df)
            self._adjust_siz6_code(df)
            self._adjust_sizc_code(df)
            self._adjust_tf8_code(df)
            self._adjust_tf14_code(df)
            self._adjust_typology(df)
            self._merge_prin2(df)
            self._merge_subp4(df)
            self._set_index_column(df)

        if auxiliary_directory:
            new_file_path = os.path.join(folder_path, filename + f'_preprocessed_{self.year}.csv')
            df.to_csv(new_file_path, index=False)
        else:
            new_file_path = filename + f'_preprocessed_{self.year}.csv'
            df.to_csv(new_file_path, index=False)

    def _adjust_country_code(self, df):
        """
        Semi-private function that maps each country to the respective country code.
        :param df: Pandas DataFrame object.
        """
        # Getting rid of white spaces due to the way dictionary was created.
        try:
            country_code = df['COUNTRY'].str.replace(' ', '').map(self.main_dictionary['country_dictionary'])
            country_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('COUNTRY')
            df.insert(idx + 1, 'COUNTRYCODE', country_code)
        except KeyError:
            self.logger.info('The document does not contain COUNTRY column. Skipping...')

    def _adjust_anc3_code(self, df):
        """
        Semi-private function that maps each anc3 value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            anc3_code = df['ANC3'].map(self.main_dictionary['anc3_dictionary'])
            anc3_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('ANC3')
            df.insert(idx + 1, 'ANC3CODE', anc3_code)
        except KeyError:
            self.logger.info('The document does not contain ANC3 column. Skipping...')

    def _adjust_lfa_code(self, df):
        """
        Semi-private function that maps each lfa value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            lfa_code = df['LFA'].map(self.main_dictionary['lfa_dictionary'])
            lfa_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('LFA')
            df.insert(idx + 1, 'LFACODE', lfa_code)
        except KeyError:
            self.logger.info('The document does not contain LFA column. Skipping...')

    def _adjust_organic_code(self, df):
        """
        Semi-private function that maps each organic value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            organic_code = df['ORGANIC'].map(self.main_dictionary['organic_dictionary'])
            organic_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('ORGANIC')
            df.insert(idx + 1, 'ORGANICCODE', organic_code)
        except KeyError:
            self.logger.info('The document does not contain ORGANIC column. Skipping...')

    def _adjust_siz6_code(self, df):
        """
        Semi-private function that maps each siz6 value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            siz6_code = df['SIZ6'].map(self.main_dictionary['siz6_dictionary'])
            siz6_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('SIZ6')
            df.insert(idx + 1, 'SIZ6CODE', siz6_code)
        except KeyError:
            self.logger.info('The document does not contain SIZ6 column. Skipping...')

    def _adjust_tf8_code(self, df):
        """
        Semi-private function that maps each tf8 value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            tf8_code = df['TF8'].map(self.main_dictionary['tf8_dictionary'])
            tf8_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('TF8')
            df.insert(idx + 1, 'TF8CODE', tf8_code)
        except KeyError:
            self.logger.info('The document does not contain TF8 column. Skipping...')

    def _adjust_tf14_code(self, df):
        """
        Semi-private function that maps each tf14 value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            tf14_code = df['TF14'].map(self.main_dictionary['tf14_dictionary'])
            tf14_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('TF14')
            df.insert(idx + 1, 'TF14CODE', tf14_code)
        except KeyError:
            self.logger.info('The document does not contain TF14 column. Skipping...')

    def _adjust_sizc_code(self, df):
        """
        Semi-private function that maps each sizc value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            sizc_code = df['SIZC'].map(self.main_dictionary['sizc_dictionary'])
            sizc_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('SIZC')
            df.insert(idx + 1, 'SIZCCODE', sizc_code)
        except KeyError:
            self.logger.info('The document does not contain SIZC column. Skipping...')

    def _merge_region(self, df):
        """
        Semi-private function that merges regioncode column from external csv file into the main DataFrame.
        :param df: Pandas DataFrame object.
        """
        csv_path = os.path.join(self.directory, 'REGION.csv')
        try:
            df_region = pd.read_csv(f'{csv_path}')
            df_merged = df.merge(df_region, on='REGION', how='left')
            idx = df.columns.get_loc('REGION')
            df.insert(idx + 1, 'REGIONCODE', df_merged['REGIONCODE'])
        except KeyError:
            self.logger.info('The document does not contain REGIONCODE column. Skipping...')

    def _adjust_typology(self, df):
        """
        Semi-private function that maps each typology value to the respective code.
        :param df: Pandas DataFrame object.
        """
        try:
            tf_gen1_code = df['TF_GEN1'].map(self.main_dictionary['typology_dictionary'])
            tf_gen1_code.fillna('x', inplace=True)
            idx = df.columns.get_loc('TF_GEN1')
            df.insert(idx + 1, 'TF_GEN1CODE', tf_gen1_code)
        except KeyError:
            self.logger.info('The document does not contain TF_GEN1 column. Skipping...')

    def _merge_prin2(self, df):
        """
        Semi-private function that merges prin2 column from external csv file into the main DataFrame.
        :param df: Pandas DataFrame object.
        """
        csv_path = os.path.join(self.directory, 'TF_PRIN2.csv')
        try:
            df_prin2 = pd.read_csv(f'{csv_path}')
            df_merged = df.merge(df_prin2, on='TF_PRIN2', how='left')
            idx = df.columns.get_loc('TF_PRIN2')
            df.insert(idx + 1, 'TF_PRIN2CODE', df_merged['TF_PRIN2CODE'])
        except KeyError:
            self.logger.info('The document does not contain TF_PRIN2CODE column. Skipping...')

    def _merge_subp4(self, df):
        """
        Semi-private function that merges subp4 column from external csv file into the main DataFrame.
        :param df: Pandas DataFrame object.
        """
        csv_path = os.path.join(self.directory, 'TF_SUBP4.csv')
        try:
            df_subp4 = pd.read_csv(f'{csv_path}')
            df_merged = df.merge(df_subp4, on='TF_SUBP4', how='left')
            idx = df.columns.get_loc('TF_SUBP4')
            df.insert(idx + 1, 'TF_SUBP4CODE', df_merged['TF_SUBP4CODE'])
        except KeyError:
            self.logger.info('The document does not contain TF_SUBP4CODE column. Skipping...')

    @staticmethod
    def _set_index_column(df):
        """
        Semi-private function that adds a column called seq which will be treated as an index
        in the csv output. By design the Pandas indexing starts from 0 and, the desired output is
        starting from 1 though.
        :param df: Pandas DataFrame object.
        """
        df.insert(0, 'seq', range(1, 1 + len(df)))

    # AUXILIARY CSV CREATION

    def _create_measures(self, file_path):
        """
        Semi-private function that creates auxiliary measures csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        csv_path = os.path.join(self.directory, 'year.country.measures_temp.csv')
        df_measures = pd.read_csv(f'{csv_path}')
        df_measures.to_csv(file_path + f'.measures_{self.year}.csv', index=False)

    def _create_org(self, file_path):
        """
        Semi-private function that creates auxiliary organisation csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        csv_path = os.path.join(self.directory, 'year.country.organisation_temp.csv')
        df_org = pd.read_csv(f'{csv_path}')
        df_org.to_csv(file_path + f'.organisation_{self.year}.csv', index=False)

    def _create_dataset(self, file_path, folder):
        """
        Semi-private function that creates auxiliary dataset csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        :param folder: str -> name of the package's folder.
        """
        # specifics of a what the package contains.
        specifics = folder.lower().split('.')
        specifics_up = folder.split('.')
        # initialize new DataFrame object.
        df_dataset = pd.DataFrame()

        # filling seq column.
        df_dataset['seq'] = [1]

        # filling uri, label and structure columns.
        base = 'http://w3id.org/foodie/fadn#dataset_'
        base2 = None
        base3 = 'http://w3id.org/foodie/fadn#dataStructureDef_'

        if 'country' in specifics[1]:
            base2 = f'Dataset of Countries by Year'
        elif 'region' in specifics[1]:
            base2 = f'Dataset of Regions by Year'
        else:
            self.logger.info(f'Dataset csv issue: {folder} does not specify neither country nor region!')

        if len(specifics) == 2:
            df_dataset['uri'] = [base + f'{specifics[0]}_{specifics[1]}']
            df_dataset['label'] = [base2]
            df_dataset['structure'] = [base3 + specifics[1]]
        elif len(specifics) == 3:
            df_dataset['uri'] = [base + f'{specifics[0]}_{specifics[1]}_{specifics[2]}']
            df_dataset['label'] = [base2 + f' and by {specifics_up[2]} value']
            df_dataset['structure'] = [base3 + specifics[1] + f'_{specifics[2]}']
        elif len(specifics) == 4:
            df_dataset['uri'] = [base + f'{specifics[0]}_{specifics[1]}_{specifics[2]}_{specifics[3]}']
            df_dataset['label'] = [base2 + f' {specifics_up[2]} and {specifics_up[3]} values']
            df_dataset['structure'] = [base3 + specifics[1] + f'_{specifics[2]}_{specifics[3]}']
        elif len(specifics) == 5:
            df_dataset['uri'] = [base + f'{specifics[0]}_{specifics[1]}_{specifics[2]}_{specifics[3]}_{specifics[4]}']
            df_dataset['label'] = [base2 + f' {specifics_up[2]} {specifics_up[3]} and {specifics_up[4]} values']
            df_dataset['structure'] = [base3 + specifics[1] + f'_{specifics[2]}_{specifics[3]}_{specifics[4]}']
        else:
            self.logger.info(f'Dataset csv issue: There is a problem with extracting specifics from {folder} file.')

        # filling publisher column.
        df_dataset['publisher'] = ['http://w3id.org/foodie/fadn#psnc']

        # filling source column.
        df_dataset['source'] = [self.url]

        # filling versionInfo column.
        df_dataset['versionInfo'] = [f'fadn {self.year}/{self.month}/{self.day}']

        # saving results to csv.
        df_dataset.to_csv(file_path + f'.dataset_{self.year}.csv', index=False)

    def _create_dimensions(self, file_path, folder):
        """
        Semi-private function that creates auxiliary dimensions csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        :param folder: str -> name of the package's folder.
        """
        # specifics of a what the package contains.
        specifics = folder.lower().split('.')
        specifics_up = folder.split('.')
        # initialize new DataFrame object.
        df_dimensions = pd.DataFrame()

        # filling seq column.
        seq = []   # empty column where the seq values will be appended based on the name of the file.
        for i in range(len(specifics)):
            seq.append(i + 1)
        df_dimensions['seq'] = seq

        # filling uri, label, subPropertyOf, concept and range columns.
        base = 'http://w3id.org/foodie/fadn#ref'
        base2 = 'reference '
        base3 = 'http://purl.org/linked-data/sdmx/2009/dimension#ref'
        base4 = 'http://purl.org/linked-data/sdmx/2009/concept#refPeriod'
        base5 = 'http://purl.org/linked-data/sdmx/2009/concept#refArea'
        base6 = None
        base7 = 'http://reference.data.gov.uk/def/intervals/CalenderYear'

        if 'country' in specifics[1]:
            base6 = 'http://www.w3.org/ns/locn#adminUnitL1'
        elif 'region' in specifics[1]:
            base6 = 'http://www.w3.org/ns/locn#adminUnitL2'
        else:
            self.logger.info(f'Dataset csv issue: {folder} does not specify neither country nor region!')

        if len(specifics) == 2:
            df_dimensions['uri'] = [base + specifics[1].capitalize(), base + specifics[0].capitalize()]
            df_dimensions['label'] = [base2 + specifics_up[1], base2 + specifics_up[0]]
            df_dimensions['subPropertyOf'] = [base3 + 'Area', base3 + 'Period']
            df_dimensions['range'] = [base6, base7]
            df_dimensions['concept'] = [base5, base4]
        elif len(specifics) == 3:
            df_dimensions['uri'] = [base + specifics[1].capitalize(), base + specifics[0].capitalize(),
                                    base + specifics[2].capitalize()]
            df_dimensions['label'] = [base2 + specifics_up[1], base2 + specifics_up[0],
                                      base2 + specifics_up[2]]
            df_dimensions['subPropertyOf'] = [base3 + 'Area', base3 + 'Period', None]
            df_dimensions['range'] = [base6, base7, None]
            df_dimensions['concept'] = [base5, base4, None]
        elif len(specifics) == 4:
            df_dimensions['uri'] = [base + specifics[1].capitalize(), base + specifics[0].capitalize(),
                                    base + specifics[2].capitalize(), base + specifics[3].capitalize()]
            df_dimensions['label'] = [base2 + specifics_up[1], base2 + specifics_up[0],
                                      base2 + specifics_up[2], base2 + specifics_up[3]]
            df_dimensions['subPropertyOf'] = [base3 + 'Area', base3 + 'Period', None, None]
            df_dimensions['range'] = [base6, base7, None, None]
            df_dimensions['concept'] = [base5, base4, None, None]
        elif len(specifics) == 5:
            df_dimensions['uri'] = [base + specifics[1].capitalize(), base + specifics[0].capitalize(),
                                    base + specifics[2].capitalize(), base + specifics[3].capitalize(),
                                    base + specifics[4].capitalize()]
            df_dimensions['label'] = [base2 + specifics_up[1], base2 + specifics_up[0],
                                      base2 + specifics_up[2], base2 + specifics_up[3], base2 + specifics_up[4]]
            df_dimensions['subPropertyOf'] = [base3 + 'Area', base3 + 'Period', None, None, None]
            df_dimensions['range'] = [base6, base7, None, None, None]
            df_dimensions['concept'] = [base5, base4, None, None, None]
        else:
            self.logger.info(f'Dimensions csv issue: There is a problem with extracting specifics from {folder} file.')

        # saving results to csv.
        df_dimensions.to_csv(file_path + f'.dimensions_{self.year}.csv', index=False)

    def _create_datastructure(self, file_path, folder):
        """
        Semi-private function that creates auxiliary datastructure csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        :param folder: str -> name of the package's folder.
        """
        # specifics of a what the package contains.
        specifics = folder.lower().split('.')
        # initialize new DataFrame object.
        df_datastructure = pd.DataFrame()

        # filling seq column.
        df_datastructure['seq'] = [1]

        # filling uri and sliceKey, columns.
        base = 'http://w3id.org/foodie/fadn#dataStructureDef_'
        base2 = 'http://w3id.org/foodie/fadn#ref'
        base3 = 'http://w3id.org/foodie/fadn#sliceBy'

        if len(specifics) == 2:
            df_datastructure['uri'] = [base + specifics[1]]
            df_datastructure['sliceKey'] = [base3 + specifics[1].capitalize()]
        elif len(specifics) == 3:
            df_datastructure['uri'] = [base + specifics[1] + f'_{specifics[2]}']
            df_datastructure['sliceKey'] = [base3 + specifics[1].capitalize() + f'_{specifics[2]}']
        elif len(specifics) == 4:
            df_datastructure['uri'] = [base + specifics[1] + f'_{specifics[2]}_{specifics[3]}']
            df_datastructure['sliceKey'] = [base3 + specifics[1].capitalize() + f'_{specifics[2]}' + f'_{specifics[3]}']
        elif len(specifics) == 5:
            df_datastructure['uri'] = [base + specifics[1] + f'_{specifics[2]}_{specifics[3]}_{specifics[4]}']
            df_datastructure['sliceKey'] = [base3 + specifics[1].capitalize() + f'_{specifics[2]}' + f'_{specifics[3]}'
                                            + f'_{specifics[4]}']
        else:
            self.logger.info(f'Datastructure csv issue: There is a problem with extracting specifics from {folder} file.')

        # filling dimension1, dimension1Order, dimension2, dimension2Order, dimension3, dimension3Order,
        # dimension4, dimension4Order, dimension5 and dimension5Order columns.

        df_datastructure['dimension1'] = [base2 + specifics[1].capitalize()]
        df_datastructure['dimension1Order'] = [1]
        df_datastructure['dimension2'] = [base2 + specifics[0].capitalize()]
        df_datastructure['dimension2Order'] = [2]
        try:
            df_datastructure['dimension3'] = [base2 + specifics[2].capitalize()]
            df_datastructure['dimension3Order'] = [3]
        except IndexError:
            df_datastructure['dimension3'] = None
            df_datastructure['dimension3Order'] = None
        try:
            df_datastructure['dimension4'] = [base2 + specifics[3].capitalize()]
            df_datastructure['dimension4Order'] = [4]
        except IndexError:
            df_datastructure['dimension4'] = None
            df_datastructure['dimension4Order'] = None
        try:
            df_datastructure['dimension5'] = [base2 + specifics[4].capitalize()]
            df_datastructure['dimension5Order'] = [5]
        except IndexError:
            df_datastructure['dimension5'] = None
            df_datastructure['dimension5Order'] = None

        # saving results to csv.
        df_datastructure.to_csv(file_path + f'.datastructure_{self.year}.csv', index=False)

    def _create_slicekey(self, file_path, folder):
        """
        Semi-private function that creates auxiliary slicekey csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        :param folder: str -> name of the package's folder.
        """
        # specifics of a what the package contains.
        specifics = folder.lower().split('.')
        specifics_up = folder.split('.')
        # initialize new DataFrame object.
        df_slicekey = pd.DataFrame()

        # filling seq column.
        df_slicekey['seq'] = [1]

        # filling uri, comment, columns.
        base = 'http://w3id.org/foodie/fadn#sliceBy'
        base3 = None

        if 'country' in specifics[1]:
            base3 = 'Slice by grouping countries together fixing time values'
        elif 'region' in specifics[1]:
            base3 = 'Slice by grouping regions together fixing time values'
        else:
            self.logger.info(f'Dataset csv issue: {folder} does not specify neither country nor region!')

        if len(specifics) == 2:
            df_slicekey['uri'] = [base + specifics[1].capitalize()]
            df_slicekey['comment'] = [base3]
        elif len(specifics) == 3:
            df_slicekey['uri'] = [base + specifics[1].capitalize() + f'_{specifics[2]}']
            df_slicekey['comment'] = [base3 + f' and {specifics_up[2]} values']
        elif len(specifics) == 4:
            df_slicekey['uri'] = [base + specifics[1].capitalize() + f'_{specifics[2]}' + f'_{specifics[3]}']
            df_slicekey['comment'] = [base3 + f' and {specifics_up[2]} values' + f' and {specifics_up[3]} values']
        elif len(specifics) == 5:
            df_slicekey['uri'] = [base + specifics[1].capitalize() + f'_{specifics[2]}' + f'_{specifics[3]}'
                                  + f'_{specifics[4]}']
            df_slicekey['comment'] = [base3 + f' and {specifics_up[2]} values' + f' and {specifics_up[3]} values'
                                      + f' and {specifics_up[4]} values']
        else:
            self.logger.info(f'Dataset csv issue: There is a problem with extracting specifics from {folder} file.')

        # filling label, componentProperty1, componentProperty2, componentProperty3 and componentProperty4 columns.
        base2 = 'slice by '
        base4 = 'http://w3id.org/foodie/fadn#ref'
        df_slicekey.insert(2, 'label', [base2 + specifics[1].capitalize()])
        df_slicekey['componentProperty1'] = [base4 + specifics[0].capitalize()]
        try:
            df_slicekey['componentProperty2'] = [base4 + specifics[2].capitalize()]
        except IndexError:
            df_slicekey['componentProperty2'] = None
        try:
            df_slicekey['componentProperty3'] = [base4 + specifics[3].capitalize()]
        except IndexError:
            df_slicekey['componentProperty3'] = None
        try:
            df_slicekey['componentProperty4'] = [base4 + specifics[4].capitalize()]
        except IndexError:
            df_slicekey['componentProperty4'] = None

        # saving results to csv.
        df_slicekey.to_csv(file_path + f'.slicekey_{self.year}.csv', index=False)

    def _create_anc3(self, file_path):
        """
        Semi-private function that creates auxiliary ANC3 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_anc3 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['anc3_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())
        # reversing both lists to match the output provided in transformation example.
        code.reverse()
        label.reverse()

        # filling seq column based on the amount of keys in dictionary.
        df_anc3['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_anc3['uri'] = uri
        df_anc3['label'] = label

        # saving results to csv.
        df_anc3.to_csv(file_path + f'.anc3Values_{self.year}.csv', index=False)

    def _create_sizc(self, file_path):
        """
        Semi-private function that creates auxiliary SIZC csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_sizc = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['sizc_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())

        # filling seq column based on the amount of keys in dictionary.
        df_sizc['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_sizc['uri'] = uri
        df_sizc['label'] = label

        # saving results to csv.
        df_sizc.to_csv(file_path + f'.sizcValues_{self.year}.csv', index=False)

    def _create_tf8(self, file_path):
        """
        Semi-private function that creates auxiliary TF8 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_tf8 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['tf8_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())

        # filling seq column based on the amount of keys in dictionary.
        df_tf8['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_tf8['uri'] = uri
        df_tf8['label'] = label

        # saving results to csv.
        df_tf8.to_csv(file_path + f'.tf8Values_{self.year}.csv', index=False)

    def _create_tf14(self, file_path):
        """
        Semi-private function that creates auxiliary TF14 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_tf14 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['tf14_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())

        # filling seq column based on the amount of keys in dictionary.
        df_tf14['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_tf14['uri'] = uri
        df_tf14['label'] = label

        # saving results to csv.
        df_tf14.to_csv(file_path + f'.tf14Values_{self.year}.csv', index=False)

    def _create_siz6(self, file_path):
        """
        Semi-private function that creates auxiliary SIZ6 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_siz6 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['siz6_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())

        # filling seq column based on the amount of keys in dictionary.
        df_siz6['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_siz6['uri'] = uri
        df_siz6['label'] = label

        # saving results to csv.
        df_siz6.to_csv(file_path + f'.siz6Values_{self.year}.csv', index=False)

    def _create_prin2(self, file_path):
        """
        Semi-private function that creates auxiliary PRIN2 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_prin2 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['prin2_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.keys()), list(dictionary.values())

        # filling seq column based on the amount of keys in dictionary.
        df_prin2['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_prin2['uri'] = uri
        df_prin2['label'] = label

        # saving results to csv.
        df_prin2.to_csv(file_path + f'.prin2Values_{self.year}.csv', index=False)

    def _create_subp4(self, file_path):
        """
        Semi-private function that creates auxiliary PRIN2 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_subp4 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['subp4_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.keys()), list(dictionary.values())

        # filling seq column based on the amount of keys in dictionary.
        df_subp4['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_subp4['uri'] = uri
        df_subp4['label'] = label

        # saving results to csv.
        df_subp4.to_csv(file_path + f'.subp4Values_{self.year}.csv', index=False)

    def _create_gen1(self, file_path):
        """
        Semi-private function that creates auxiliary GEN1 csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        """
        # initialize new DataFrame object.
        df_gen1 = pd.DataFrame()

        dictionary = dictionaries.fadn_dictionary['typology_dictionary']
        # unpacking dictionary values and keys into two separated lists.
        code, label = list(dictionary.values()), list(dictionary.keys())

        # filling seq column based on the amount of keys in dictionary.
        df_gen1['seq'] = [x for x in range(1, len(label) + 1)]

        # filling uri, label columns.
        base = 'http://w3id.org/foodie/fadn#'
        uri = [base + x for x in code]   # adding prefix (base) to the list of codes.
        df_gen1['uri'] = uri
        df_gen1['label'] = label

        # saving results to csv.
        df_gen1.to_csv(file_path + f'.gen1Values_{self.year}.csv', index=False)

    def _create_slices(self, file_path, folder):
        """
        Semi-private function that creates auxiliary SLICES csv file.
        :param file_path: str -> directory where the auxiliary csv should be saved.
        :param folder: str -> name of the package's folder.
        """
        # creating a mapping between component names and dictionaries
        component_mapping = {
            'anc3': 'anc3_dictionary',
            'siz6': 'siz6_dictionary',
            'tf8': 'tf8_dictionary',
            'sizc': 'sizc_dictionary',
            'tf14': 'tf14_dictionary',
            'tf_gen1': 'typology_dictionary',
            'tf_prin2': 'prin2_dictionary',
            'tf_subp4': 'subp4_dictionary',
        }

        # specifics of a what the package contains.
        specifics = folder.lower().split('.')
        specifics_up = folder.split('.')

        # initialize new DataFrame object.
        df_slices = pd.DataFrame()
        year_list = [x for x in self.range]   # basic list of years created for 0 additional components.

        if len(specifics) == 2:
            df_slices['YEAR'] = year_list   # no additional components, hence no changes required to the stock list.
        elif len(specifics) == 3:
            mapping = component_mapping[specifics[2]]
            column_name = specifics_up[2]
            dictionary = dictionaries.fadn_dictionary[mapping]   # accessing congruent dictionary.
            # unpacking dictionary values and keys into two separated lists.
            code, label = list(dictionary.values()), list(dictionary.keys())
            n_year_list = []
            for year in year_list:
                n_year_list += [year] * len(code)
            df_slices['YEAR'] = n_year_list   # list getting tuned with component's size.
            df_slices[column_name] = label * len(year_list)
            df_slices[column_name + 'CODE'] = code * len(year_list)
        elif len(specifics) == 4:
            mapping = component_mapping[specifics[2]]
            mapping_2 = component_mapping[specifics[3]]
            column_name = specifics_up[2]
            column_name_2 = specifics_up[3]
            dictionary = dictionaries.fadn_dictionary[mapping]
            dictionary_2 = dictionaries.fadn_dictionary[mapping_2]
            code, label = list(dictionary.values()), list(dictionary.keys())
            code_2, label_2 = list(dictionary_2.values()), list(dictionary_2.keys())
            n_year_list = []
            for year in year_list:
                n_year_list += [year] * (len(code) * len(code_2))
            df_slices['YEAR'] = n_year_list
            df_slices[column_name] = label * (len(year_list) * len(code_2))
            df_slices[column_name + 'CODE'] = code * (len(year_list) * len(code_2))
            n_code_2_list = []
            n_label_2_list = []
            for _ in year_list:
                for lab in label_2:
                    n_label_2_list += [lab] * len(code)
                for c in code_2:
                    n_code_2_list += [c] * len(code)
            df_slices[column_name_2] = n_label_2_list
            df_slices[column_name_2 + 'CODE'] = n_code_2_list
        elif len(specifics) == 5 and all(s in specifics for s in ['tf_prin2', 'tf_gen1', 'tf_subp4']):
            mapping = component_mapping[specifics[2]]
            mapping_2 = component_mapping[specifics[3]]
            mapping_3 = component_mapping[specifics[4]]
            column_name = specifics_up[2]
            column_name_2 = specifics_up[3]
            column_name_3 = specifics_up[4]
            dictionary = dictionaries.fadn_dictionary[mapping]
            dictionary_2 = dictionaries.fadn_dictionary[mapping_2]
            dictionary_3 = dictionaries.fadn_dictionary[mapping_3]
            code, label = list(dictionary.values()), list(dictionary.keys())
            label_2, code_2 = list(dictionary_2.values()), list(dictionary_2.keys())
            label_3, code_3 = list(dictionary_3.values()), list(dictionary_3.keys())
            n_year_list = []
            for year in year_list:
                n_year_list += [year] * len(code_3)
            df_slices['YEAR'] = n_year_list
            # slices that have to be hard-coded in a nasty way, due to nature of the data set.
            occurrence = [9, 9, 11, 7, 7, 6, 4, 8]
            if len(code) != len(occurrence):
                self.logger.debug(f'The length of occurrence list({len(occurrence)}) is different '
                             f'than the number of items in the dictionary ({len(code)})')
            if pd.Series(occurrence).sum() != len(code_3):
                self.logger.debug(f'The number of occurrences specified in the list is not valid '
                             f'({pd.Series(occurrence).sum()}). It has to match with number of {column_name_3} items.')
            first_slice = []
            first_slice_code = []
            for i in range(len(code)):
                first_slice += [label[i]] * occurrence[i]
                first_slice_code += [code[i]] * occurrence[i]

            occurrence_2 = [4, 5, 3, 3, 3, 5, 4, 1, 1, 1, 4, 1, 1, 3, 3, 1, 6, 2, 2, 4, 4]
            if len(code_2) != len(occurrence_2):
                self.logger.warning(f'The length of occurrence_2 list({len(occurrence_2)}) is different '
                               f'than the number of items in the dictionary ({len(code_2)})')
            if pd.Series(occurrence_2).sum() != len(code_3):
                self.logger.warning(f'The number of occurrences_2 specified in the list is not valid '
                               f'({pd.Series(occurrence_2).sum()}). It has to match with number of '
                               f'{column_name_3} items.')
            second_slice = []
            second_slice_code = []
            for i in range(len(code_2)):
                second_slice += [label_2[i]] * occurrence_2[i]
                second_slice_code += [code_2[i]] * occurrence_2[i]

            df_slices[column_name] = first_slice * len(year_list)
            df_slices[column_name + 'CODE'] = first_slice_code * len(year_list)
            df_slices[column_name_2] = second_slice * len(year_list)
            df_slices[column_name_2 + 'CODE'] = second_slice_code * len(year_list)
            df_slices[column_name_3] = label_3 * len(year_list)
            df_slices[column_name_3 + 'CODE'] = code_3 * len(year_list)
        else:
            self.logger.info(f'Dataset csv issue: There is a problem with extracting specifics from {folder} file.')

        seq = [x for x in range(1, len(df_slices['YEAR']) + 1)]
        df_slices.insert(0, 'seq', seq)

        # saving results to csv.
        df_slices.to_csv(file_path + f'.slices_{self.year}.csv', index=False)
