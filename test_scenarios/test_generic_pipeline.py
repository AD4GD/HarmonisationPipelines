import os
import subprocess
import shutil
import pytest
import pandas as pd
import yaml
import csv
import json
import geopandas as gpd

from test_scenarios.base_testing_class import TestBase
from modules.settings import GENERATED_MAPPING_FILENAME

# needed only for testing purposes locally via IDE
#os.chdir(os.path.join(os.path.dirname(__file__), os.pardir))s


class TestGeneric(TestBase):
    PIPELINE = "generic"
    GRAPH_URI = "http://autotest.pipelines/"

###############################################################################
#                               SINGLE STAGES.                                #
###############################################################################


class TestGenericPreprocess(TestGeneric):
    PROCESS = "preprocess"


class TestGenericPreprocessToCrs(TestGenericPreprocess):
    ACTIVITY = "to_crs"
    INPUT_TYPE = "Shapefile"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_shp_data, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_shp_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.shp"])
    def test_expected_json_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.shp"])
    def test_preprocess_to_crs(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df1 = gpd.read_file(target_path)
        df2 = gpd.read_file(target_path2)
        assert df1.crs == "EPSG:4326"
        assert df2.crs == "EPSG:4326"


class TestGenericPreprocessAddEnum(TestGenericPreprocess):
    ACTIVITY = "add_enum"
    INPUT_TYPE = "JSON"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_json_data_enum, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_json_data_enum}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_json_data_enum):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_json_data_enum}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["dane.json"])
    def test_expected_json_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["dane.json"])
    def test_preprocess_enum(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        with open(target_path, 'r') as output:
            data = json.load(output)
        with open(target_path2, 'r') as output2:
            data2 = json.load(output2)
        assert 'id' in data[1].keys()
        assert 'id' in data[2].keys()
        assert data[1].get("id") == 1
        assert data[2].get("id") == 2
        assert 'id' in data2[1].keys()
        assert 'id' in data2[2].keys()
        assert data2[1].get("id") == 1
        assert data2[2].get("id") == 2


class TestGenericPreprocessAddSeqCol(TestGenericPreprocess):
    ACTIVITY = "add_seq_col"
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_csv_data, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_csv_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data}", f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_expected_csv_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_preprocess_seq_col(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1


class TestGenericPreprocessNormalizeDelimiter(TestGenericPreprocess):
    ACTIVITY = "normalize_delimiter"
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_csv_different_delimiter, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_different_delimiter}",
                              f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_csv_different_delimiter):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_different_delimiter}",
                              f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["mock_diff_delimiter.csv"])
    def test_expected_csv_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["mock_diff_delimiter.csv"])
    def test_preprocess_normalize_delimiter(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir,
                                            expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        with open(target_path2, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","
        with open(target_path, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","


class TestGenericPreprocessUnzipMultipleArchives(TestGenericPreprocess):
    ACTIVITY = "unzip_multiple_archives"
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_multiple_archives, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_multiple_archives}",
                              f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_multiple_archives):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_multiple_archives}",
                              f"--preprocess_activity={self.ACTIVITY}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_expected_csv_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)


class TestGenericPreprocessUnzipAndSeqCol(TestGenericPreprocess):
    ACTIVITY_1 = "unzip_multiple_archives"
    ACTIVITY_2 = "add_seq_col"
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_multiple_archives, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_multiple_archives}",
                              f"--preprocess_activity={self.ACTIVITY_1}",
                              f"--preprocess_activity={self.ACTIVITY_2}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_multiple_archives):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_multiple_archives}",
                              f"--preprocess_activity={self.ACTIVITY_1}",
                              f"--preprocess_activity={self.ACTIVITY_2}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_expected_csv_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_preprocess_seq_col(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1


class TestGenericPreprocessSeqColAndDelimiterNorm(TestGenericPreprocess):
    ACTIVITY_1 = "normalize_delimiter"
    ACTIVITY_2 = "add_seq_col"
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_generic_csv_different_delimiter, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_different_delimiter}",
                              f"--preprocess_activity={self.ACTIVITY_1}",
                              f"--preprocess_activity={self.ACTIVITY_2}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_generic_csv_different_delimiter):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_different_delimiter}",
                              f"--preprocess_activity={self.ACTIVITY_1}",
                              f"--preprocess_activity={self.ACTIVITY_2}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_output(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        out, err, _ = preprocess_pipeline_default_dir
        out2, err2, _ = preprocess_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()

    def test_preprocess_dir_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["mock_diff_delimiter.csv"])
    def test_expected_csv_exist(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["mock_diff_delimiter.csv"])
    def test_preprocess_seq_col(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1

    @pytest.mark.parametrize("expected_file", ["mock_diff_delimiter.csv"])
    def test_preprocess_normalize_delimiter(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir,
                                            expected_file):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        with open(target_path2, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","
        with open(target_path, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","


class TestGenericMapping(TestGeneric):
    PROCESS = "mapping"


class TestGenericCsvMapping(TestGenericMapping):
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def mapping_pipeline_csv_default_dir(self, provide_generic_csv_data, mapping_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data}", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_csv_custom_dir(self, provide_generic_csv_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data}", f"--base_uri={self.GRAPH_URI}",
                              "--output", custom_dir, f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_csv_mapping_output(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir):
        out, err, _ = mapping_pipeline_csv_default_dir
        out2, err2, _ = mapping_pipeline_csv_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_csv_mapping_dir_exist(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.ttl"])
    def test_csv_expected_mapping_exist(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir,
                                        expected_file):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["gaigroup.ttl"])
    def test_csv_mapping_files_size(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir,
                                    mapping):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericNetCdfMapping(TestGenericMapping):
    INPUT_TYPE = "netCDF"

    @pytest.fixture(scope="class")
    def mapping_pipeline_netcdf_default_dir(self, provide_generic_netcdf_data, mapping_pipeline_netcdf_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_netcdf_data}", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_netcdf_custom_dir(self, provide_generic_netcdf_data):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_netcdf_data}", f"--base_uri={self.GRAPH_URI}",
                              "--output", custom_dir, f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_netcdf_mapping_output(self, mapping_pipeline_netcdf_default_dir, mapping_pipeline_netcdf_custom_dir):
        out, err, _ = mapping_pipeline_netcdf_default_dir
        out2, err2, _ = mapping_pipeline_netcdf_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_netcdf_mapping_dir_exist(self, mapping_pipeline_netcdf_default_dir, mapping_pipeline_netcdf_custom_dir):
        _, _, folder2 = mapping_pipeline_netcdf_custom_dir
        _, _, folder = mapping_pipeline_netcdf_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["simulation.ttl"])
    def test_netcdf_expected_mapping_exist(self, mapping_pipeline_netcdf_default_dir, mapping_pipeline_netcdf_custom_dir,
                                           expected_file):
        _, _, folder2 = mapping_pipeline_netcdf_custom_dir
        _, _, folder = mapping_pipeline_netcdf_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["simulation.ttl"])
    def test_netcdf_mapping_files_size(self, mapping_pipeline_netcdf_default_dir, mapping_pipeline_netcdf_custom_dir,
                                       mapping):
        _, _, folder2 = mapping_pipeline_netcdf_custom_dir
        _, _, folder = mapping_pipeline_netcdf_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericShpMapping(TestGenericMapping):
    INPUT_TYPE = "Shapefile"

    @pytest.fixture(scope="class")
    def mapping_pipeline_shp_default_dir(self, provide_generic_shp_data, mapping_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_shp_custom_dir(self, provide_generic_shp_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--base_uri={self.GRAPH_URI}",
                              "--output", custom_dir, f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_shp_mapping_output(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir):
        out, err, _ = mapping_pipeline_shp_default_dir
        out2, err2, _ = mapping_pipeline_shp_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_shp_mapping_dir_exist(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.ttl"])
    def test_shp_expected_mapping_exist(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir,
                                        expected_file):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["eppol_45047_20200923.ttl"])
    def test_shp_mapping_files_size(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir,
                                    mapping):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


def _check_db_credentials():
    with open(os.path.join("cfg", "config.yaml")) as file:
        cfg = yaml.load(file, Loader=yaml.FullLoader)
        db_cfg = cfg.get("sql_cfg")
        if not db_cfg:
            msg = "Missing sql_cfg section in the config.yaml file. Tests using db connection will be skipped!"
            print(msg)
            return False
        db_type = db_cfg.get("DB_TYPE")
        db_username = db_cfg.get("DB_USERNAME")
        db_host = db_cfg.get("DB_HOST")
        db_name = db_cfg.get("DB_NAME")
        required_fields = (db_type, db_username, db_host, db_name)
        if any(field is None for field in required_fields):
            msg = "Incomplete config file for db support. Tests using db connection will be skipped!"
            print(msg)
            return False
        return True


@pytest.mark.skipif(not _check_db_credentials(), reason="Missing or incomplete config file for db support.")
class TestGenericDbMapping(TestGenericMapping):
    INPUT_TYPE = "DB"

    @pytest.fixture(scope="class")
    def mapping_pipeline_db_default_dir(self, mapping_pipeline_db_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              "--db_input", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_db_custom_dir(self):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              "--db_input", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_db_mapping_output(self, mapping_pipeline_db_default_dir, mapping_pipeline_db_custom_dir):
        out, err, _ = mapping_pipeline_db_default_dir
        out2, err2, _ = mapping_pipeline_db_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_db_mapping_dir_exist(self, mapping_pipeline_db_default_dir, mapping_pipeline_db_custom_dir):
        _, _, folder2 = mapping_pipeline_db_custom_dir
        _, _, folder = mapping_pipeline_db_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["mapping_from_db.ttl"])
    def test_db_expected_mapping_exist(self, mapping_pipeline_db_default_dir, mapping_pipeline_db_custom_dir,
                                        expected_file):
        _, _, folder2 = mapping_pipeline_db_custom_dir
        _, _, folder = mapping_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["mapping_from_db.ttl"])
    def test_db_mapping_files_size(self, mapping_pipeline_db_default_dir, mapping_pipeline_db_custom_dir,
                                    mapping):
        _, _, folder2 = mapping_pipeline_db_custom_dir
        _, _, folder = mapping_pipeline_db_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericTransform(TestGeneric):
    PROCESS = "transform"


class TestGenericCsvTransform(TestGenericTransform):
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def transform_pipeline_csv_default_dir(self, provide_generic_csv_data_rmlmapper,
                                           provide_generic_csv_mapping_rmlmapper,
                                           transform_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--mapping_url={provide_generic_csv_mapping_rmlmapper}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_csv_custom_dir(self, provide_generic_csv_data_rmlmapper,
                                          provide_generic_csv_mapping_rmlmapper):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--mapping_url={provide_generic_csv_mapping_rmlmapper}",
                              "--output", custom_dir, f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_csv_transform_output(self, transform_pipeline_csv_default_dir, transform_pipeline_csv_custom_dir):
        out, err, _ = transform_pipeline_csv_default_dir
        out2, err2, _ = transform_pipeline_csv_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()

    def test_csv_transform_dir_exist(self, transform_pipeline_csv_default_dir, transform_pipeline_csv_custom_dir):
        _, _, folder2 = transform_pipeline_csv_custom_dir
        _, _, folder = transform_pipeline_csv_default_dir
        assert "dumps" in os.listdir(folder2)
        assert "dumps" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_expected_transform_exist(self, transform_pipeline_csv_default_dir, transform_pipeline_csv_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_csv_custom_dir
        _, _, folder = transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_csv_transform_files_size(self, transform_pipeline_csv_default_dir, transform_pipeline_csv_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_csv_custom_dir
        _, _, folder = transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericShpTransform(TestGenericTransform):
    INPUT_TYPE = "Shapefile"

    @pytest.fixture(scope="class")
    def transform_pipeline_shp_default_dir(self, provide_generic_shp_data, provide_generic_shp_mapping,
                                           transform_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--mapping_url={provide_generic_shp_mapping}",
                              f"--input_type={self.INPUT_TYPE}", f"--base_uri={self.GRAPH_URI}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_shp_custom_dir(self, provide_generic_shp_data, provide_generic_shp_mapping):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_shp_data}", f"--mapping_url={provide_generic_shp_mapping}",
                              "--output", custom_dir, f"--input_type={self.INPUT_TYPE}",
                              f"--base_uri={self.GRAPH_URI}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_shp_transform_output(self, transform_pipeline_shp_default_dir, transform_pipeline_shp_custom_dir):
        out, err, _ = transform_pipeline_shp_default_dir
        out2, err2, _ = transform_pipeline_shp_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()

    def test_shp_transform_dir_exist(self, transform_pipeline_shp_default_dir, transform_pipeline_shp_custom_dir):
        _, _, folder2 = transform_pipeline_shp_custom_dir
        _, _, folder = transform_pipeline_shp_default_dir
        assert "dumps" in os.listdir(folder2)
        assert "dumps" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_expected_transform_exist(self, transform_pipeline_shp_default_dir, transform_pipeline_shp_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_shp_custom_dir
        _, _, folder = transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_shp_transform_files_size(self, transform_pipeline_shp_default_dir, transform_pipeline_shp_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_shp_custom_dir
        _, _, folder = transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericJsonTransform(TestGenericTransform):
    INPUT_TYPE = "JSON"

    @pytest.fixture(scope="class")
    def transform_pipeline_json_default_dir(self, provide_generic_json_data, provide_generic_json_mapping,
                                            transform_pipeline_json_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_json_data}",
                              f"--mapping_url={provide_generic_json_mapping}", f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_json_custom_dir(self, provide_generic_json_data, provide_generic_json_mapping):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_json_data}",
                              f"--mapping_url={provide_generic_json_mapping}", "--output", custom_dir,
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_json_transform_output(self, transform_pipeline_json_default_dir, transform_pipeline_json_custom_dir):
        out, err, _ = transform_pipeline_json_default_dir
        out2, err2, _ = transform_pipeline_json_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()

    def test_json_transform_dir_exist(self, transform_pipeline_json_default_dir, transform_pipeline_json_custom_dir):
        _, _, folder2 = transform_pipeline_json_custom_dir
        _, _, folder = transform_pipeline_json_default_dir
        assert "dumps" in os.listdir(folder2)
        assert "dumps" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["business-sample.nt"])
    def test_expected_transform_exist(self, transform_pipeline_json_default_dir, transform_pipeline_json_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_json_custom_dir
        _, _, folder = transform_pipeline_json_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["business-sample.nt"])
    def test_json_transform_files_size(self, transform_pipeline_json_default_dir, transform_pipeline_json_custom_dir,
                                       expected_file):
        _, _, folder2 = transform_pipeline_json_custom_dir
        _, _, folder = transform_pipeline_json_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


@pytest.mark.skipif(not _check_db_credentials(), reason="Missing or incomplete config file for db support.")
class TestGenericDbTransform(TestGenericTransform):
    INPUT_TYPE = "DB"

    @pytest.fixture(scope="class")
    def transform_pipeline_db_default_dir(self, provide_generic_db_mapping, transform_pipeline_db_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              "--db_input", f"--mapping_url={provide_generic_db_mapping}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_db_custom_dir(self, provide_generic_db_mapping):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              "--db_input", f"--mapping_url={provide_generic_db_mapping}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_db_transform_output(self, transform_pipeline_db_default_dir, transform_pipeline_db_custom_dir):
        out, err, _ = transform_pipeline_db_default_dir
        out2, err2, _ = transform_pipeline_db_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()

    def test_db_transform_dir_exist(self, transform_pipeline_db_default_dir, transform_pipeline_db_custom_dir):
        _, _, folder2 = transform_pipeline_db_custom_dir
        _, _, folder = transform_pipeline_db_default_dir
        assert "dumps" in os.listdir(folder2)
        assert "dumps" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["dump_from_db.nt"])
    def test_expected_transform_exist(self, transform_pipeline_db_default_dir, transform_pipeline_db_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_db_custom_dir
        _, _, folder = transform_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["dump_from_db.nt"])
    def test_db_transform_files_size(self, transform_pipeline_db_default_dir, transform_pipeline_db_custom_dir,
                                       expected_file):
        _, _, folder2 = transform_pipeline_db_custom_dir
        _, _, folder = transform_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericTarqlTransform(TestGenericTransform):
    INPUT_TYPE = "CSV"

    @pytest.fixture(scope="class")
    def transform_pipeline_tarql_default_dir(self, provide_generic_tarql_data, provide_generic_tarql_query,
                                           transform_pipeline_tarql_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_tarql_data}",
                              f"--mapping_url={provide_generic_tarql_query}",
                              f"--input_type={self.INPUT_TYPE}", "--sparql_query"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_tarql_custom_dir(self, provide_generic_tarql_data, provide_generic_tarql_query):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_tarql_data}",
                              f"--mapping_url={provide_generic_tarql_query}",
                              f"--input_type={self.INPUT_TYPE}", "--sparql_query", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_csv_transform_output(self, transform_pipeline_tarql_default_dir, transform_pipeline_tarql_custom_dir):
        out, err, _ = transform_pipeline_tarql_default_dir
        out2, err2, _ = transform_pipeline_tarql_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()

    def test_csv_transform_dir_exist(self, transform_pipeline_tarql_default_dir, transform_pipeline_tarql_custom_dir):
        _, _, folder2 = transform_pipeline_tarql_custom_dir
        _, _, folder = transform_pipeline_tarql_default_dir
        assert "dumps" in os.listdir(folder2)
        assert "dumps" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["tarql_mock.nt"])
    def test_expected_transform_exist(self, transform_pipeline_tarql_default_dir, transform_pipeline_tarql_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_tarql_custom_dir
        _, _, folder = transform_pipeline_tarql_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["tarql_mock.nt"])
    def test_csv_transform_files_size(self, transform_pipeline_tarql_default_dir, transform_pipeline_tarql_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_tarql_custom_dir
        _, _, folder = transform_pipeline_tarql_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericPostprocess(TestGeneric):
    PROCESS = "postprocess"


class TestGenericStandardPostprocessing(TestGenericPostprocess):

    @pytest.fixture(scope="class")
    def postprocess_pipeline_default_dir(self, provide_generic_dump, postprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_dump}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def postprocess_pipeline_custom_dir(self, provide_generic_dump):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_dump}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_postprocess_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        out, err, _ = postprocess_pipeline_default_dir
        out2, err2, _ = postprocess_pipeline_custom_dir
        assert err is None
        assert "Postprocessing is done!" in out.decode()
        assert err2 is None
        assert "Postprocessing is done!" in out2.decode()

    def test_postprocess_dir_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert "postprocessed_data" in os.listdir(folder2)
        assert "postprocessed_data" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_expected_postprocess_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                        expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_postprocess_files_size(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_postprocess_tasks_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                      expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)

        def _check_target(target_path):
            with open(target_path, 'r') as target:
                for line in target:
                    if "<http://bogusz.test/eppol_45047_20200923/Geometry/9>" in line:
                        if "<http://www.opengis.net/ont/geosparql#asWKT>" in line:
                            return "<http://www.opengis.net/def/crs/EPSG/0/4258>" not in line

        assert _check_target(target_path2) is True
        assert _check_target(target_path) is True


class TestGenericTtlConversionPostprocessing(TestGenericPostprocess):

    @pytest.fixture(scope="class")
    def postprocess_pipeline_default_dir(self, provide_generic_dump, postprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_dump}", "--to_ttl"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def postprocess_pipeline_custom_dir(self, provide_generic_dump):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_dump}", "--output", custom_dir, "--to_ttl"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_postprocess_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        out, err, _ = postprocess_pipeline_default_dir
        out2, err2, _ = postprocess_pipeline_custom_dir
        assert err is None
        assert "Postprocessing is done!" in out.decode()
        assert err2 is None
        assert "Postprocessing is done!" in out2.decode()

    def test_postprocess_dir_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert "postprocessed_data" in os.listdir(folder2)
        assert "postprocessed_data" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.ttl"])
    def test_expected_postprocess_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                        expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.ttl"])
    def test_postprocess_files_size(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericExpressionReplacementPostprocessing(TestGenericPostprocess):
    EXP_TO_BE_REPLACED = "%C2%"
    EXP_REPLACEMENT = "\\\\u00"

    @pytest.fixture(scope="class")
    def postprocess_pipeline_default_dir(self, provide_dump_for_expression_replacement, postprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_dump_for_expression_replacement}", "--replace_expression",
                              self.EXP_TO_BE_REPLACED, self.EXP_REPLACEMENT],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def postprocess_pipeline_custom_dir(self, provide_dump_for_expression_replacement):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_dump_for_expression_replacement}", "--output", custom_dir,
                              "--replace_expression", self.EXP_TO_BE_REPLACED, self.EXP_REPLACEMENT],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_postprocess_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        out, err, _ = postprocess_pipeline_default_dir
        out2, err2, _ = postprocess_pipeline_custom_dir
        assert err is None
        assert "Postprocessing is done!" in out.decode()
        assert err2 is None
        assert "Postprocessing is done!" in out2.decode()

    def test_postprocess_dir_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert "postprocessed_data" in os.listdir(folder2)
        assert "postprocessed_data" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["test_replace_exp.nt"])
    def test_expected_postprocess_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                        expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["test_replace_exp.nt"])
    def test_postprocess_files_size(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

    @pytest.mark.parametrize("expected_file", ["test_replace_exp.nt"])
    def test_postprocess_task_result(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)

        def _check_target(path):
            with open(path, 'r') as target:
                file_content = target.read()
                escaped_replacement = self.EXP_REPLACEMENT.encode().decode('unicode-escape')
                escaped_to_be_replaced = self.EXP_TO_BE_REPLACED.encode().decode('unicode-escape')
                if escaped_replacement in file_content and escaped_to_be_replaced not in file_content:
                    return True

        assert _check_target(target_path2) is True
        assert _check_target(target_path) is True


class TestGenericLoad(TestGeneric):
    PROCESS = "load"

    @pytest.fixture(scope="class")
    def load_pipeline(self, provide_generic_postprocessed_dump):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_generic_postprocessed_dump}", f"--graph_uri={self.GRAPH_URI}",
                              "-rg"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.mark.parametrize("output_msg", ["Loading data to the triplestore...",
                                            "Uploading files to the server",
                                            "has been cleared!",
                                            "Data have been loaded",
                                            "eppol_45047_20200923.nt loaded successfully!",
                                            "Loading data into triplestore is done!"])
    def test_load_output(self, load_pipeline, output_msg):
        out, err, _ = load_pipeline
        assert err is None
        assert output_msg in out.decode()


@pytest.mark.skipif(not os.path.exists("utils/silk"), reason="Silk not installed.")
class TestGenericLinking(TestGeneric):
    PROCESS = "link"

    @pytest.fixture(scope="class")
    def link_pipeline_default_dir(self, provide_linking_data, link_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_linking_data}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def link_pipeline_custom_dir(self, provide_linking_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_linking_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_link_output(self, link_pipeline_default_dir, link_pipeline_custom_dir):
        out, err, _ = link_pipeline_default_dir
        out2, err2, _ = link_pipeline_custom_dir
        assert err is None
        assert "Linking is done!" in out.decode()
        assert err2 is None
        assert "Linking is done!" in out2.decode()

    @pytest.mark.parametrize("expected_file", ["links.nt"])
    def test_expected_link_exist(self, link_pipeline_default_dir, link_pipeline_custom_dir,
                                 expected_file):
        _, _, folder2 = link_pipeline_custom_dir
        _, _, folder = link_pipeline_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

###############################################################################
#                               MULTIPLE STAGES.                              #
###############################################################################


class TestGenericPreprocessAndMapping(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "preprocess"
    PROCESS_2 = "mapping"

    @pytest.fixture(scope="class")
    def preprocess_and_mapping_pipeline_default_dir(self, provide_generic_csv_data,
                                                    preprocess_and_mapping_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--preprocess_activity=add_seq_col",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_csv_data}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_and_mapping_pipeline_custom_dir(self, provide_generic_csv_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--preprocess_activity=add_seq_col",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_csv_data}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_and_mapping_pipeline_output(self, preprocess_and_mapping_pipeline_default_dir,
                                                    preprocess_and_mapping_pipeline_custom_dir):
        out, err, _ = preprocess_and_mapping_pipeline_default_dir
        out2, err2, _ = preprocess_and_mapping_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_preprocess_and_mapping_pipeline_dir_exist(self, preprocess_and_mapping_pipeline_default_dir,
                                              preprocess_and_mapping_pipeline_custom_dir):
        _, _, folder2 = preprocess_and_mapping_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_expected_csv_exist(self, preprocess_and_mapping_pipeline_default_dir,
                                preprocess_and_mapping_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.ttl"])
    def test_csv_expected_mapping_exist(self, preprocess_and_mapping_pipeline_default_dir,
                                        preprocess_and_mapping_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_pipeline_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_preprocess_seq_col(self, preprocess_and_mapping_pipeline_default_dir,
                                preprocess_and_mapping_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1

    @pytest.mark.parametrize("mapping", ["gaigroup.ttl"])
    def test_csv_mapping_files_size(self, preprocess_and_mapping_pipeline_default_dir,
                                    preprocess_and_mapping_pipeline_custom_dir, mapping):
        _, _, folder2 = preprocess_and_mapping_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericMappingAndTransform(TestGeneric):
    INPUT_TYPE = "Shapefile"
    PROCESS_1 = "transform"
    PROCESS_2 = "mapping"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_shp_default_dir(self, provide_generic_shp_data,
                                                   mapping_and_transform_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--base_uri={self.GRAPH_URI}",
                              f"--url_input={provide_generic_shp_data}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_shp_custom_dir(self, provide_generic_shp_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--base_uri={self.GRAPH_URI}",
                              f"--url_input={provide_generic_shp_data}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_shp_output(self, mapping_and_transform_pipeline_shp_default_dir,
                                                   mapping_and_transform_pipeline_shp_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_shp_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_shp_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_shp_dir_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                                      mapping_and_transform_pipeline_shp_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.ttl"])
    def test_shp_expected_mapping_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                        mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_expected_transform_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                      mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["eppol_45047_20200923.ttl"])
    def test_shp_mapping_files_size(self, mapping_and_transform_pipeline_shp_default_dir,
                                    mapping_and_transform_pipeline_shp_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_shp_transform_files_size(self, mapping_and_transform_pipeline_shp_default_dir,
                                      mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericPreprocessAndMappingAndTransform(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "preprocess"
    PROCESS_2 = "mapping"
    PROCESS_3 = "transform"

    @pytest.fixture(scope="class")
    def preprocess_and_mapping_and_transform_pipeline_default_dir(self, provide_generic_csv_data_rmlmapper,
                                                    preprocess_and_mapping_and_transform_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              "--preprocess_activity=add_seq_col",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_and_mapping_and_transform_pipeline_custom_dir(self, provide_generic_csv_data_rmlmapper):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              "--preprocess_activity=add_seq_col",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_and_mapping_and_transform_pipeline_output(self,
                                                                  preprocess_and_mapping_and_transform_pipeline_default_dir,
                                                                  preprocess_and_mapping_and_transform_pipeline_custom_dir):
        out, err, _ = preprocess_and_mapping_and_transform_pipeline_default_dir
        out2, err2, _ = preprocess_and_mapping_and_transform_pipeline_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()
        assert "Transformation is done!" in out2.decode()

    def test_preprocess_and_mapping_and_transform_pipeline_dir_exist(self,
                                                                     preprocess_and_mapping_and_transform_pipeline_default_dir,
                                                                     preprocess_and_mapping_and_transform_pipeline_custom_dir):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_expected_csv_exist(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                preprocess_and_mapping_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.ttl"])
    def test_csv_expected_mapping_exist(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                        preprocess_and_mapping_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_expected_transform_exist(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                      preprocess_and_mapping_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.csv"])
    def test_preprocess_seq_col(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                preprocess_and_mapping_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1

    @pytest.mark.parametrize("mapping", ["gaigroup.ttl"])
    def test_csv_mapping_files_size(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                    preprocess_and_mapping_and_transform_pipeline_custom_dir, mapping):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_csv_transform_files_size(self, preprocess_and_mapping_and_transform_pipeline_default_dir,
                                      preprocess_and_mapping_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = preprocess_and_mapping_and_transform_pipeline_custom_dir
        _, _, folder = preprocess_and_mapping_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericTransformPostprocessLoad(TestGeneric):
    INPUT_TYPE = "Shapefile"
    PROCESS_1 = "transform"
    PROCESS_2 = "postprocess"
    PROCESS_3 = "load"

    @pytest.fixture(scope="class")
    def transform_postprocess_and_load_pipeline_shp_default_dir(self, provide_generic_shp_data,
                                                                provide_generic_shp_mapping,
                                                                transform_postprocess_and_load_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_shp_data}",
                              f"--input_type={self.INPUT_TYPE}", f"--mapping_url={provide_generic_shp_mapping}",
                              "-rg", f"--graph_uri={self.GRAPH_URI}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_postprocess_and_load_pipeline_shp_custom_dir(self, provide_generic_shp_data,
                                                               provide_generic_shp_mapping):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              f"--base_uri={self.GRAPH_URI}", f"--url_input={provide_generic_shp_data}",
                              f"--input_type={self.INPUT_TYPE}", f"--mapping_url={provide_generic_shp_mapping}",
                              "-rg", "--output", custom_dir, f"--graph_uri={self.GRAPH_URI}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_transform_postprocess_and_load_pipeline_shp_output(self,
                                                                transform_postprocess_and_load_pipeline_shp_default_dir,
                                                                transform_postprocess_and_load_pipeline_shp_custom_dir):
        out, err, _ = transform_postprocess_and_load_pipeline_shp_default_dir
        out2, err2, _ = transform_postprocess_and_load_pipeline_shp_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Postprocessing is done!" in out.decode()
        assert "Loading data into triplestore is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Postprocessing is done!" in out2.decode()
        assert "Loading data into triplestore is done!" in out2.decode()

    def test_transform_postprocess_and_load_pipeline_shp_dir_exist(self,
                                                                   transform_postprocess_and_load_pipeline_shp_default_dir,
                                                                   transform_postprocess_and_load_pipeline_shp_custom_dir):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.ttl"])
    def test_shp_expected_mapping_exist(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                        transform_postprocess_and_load_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_expected_transform_exist(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                      transform_postprocess_and_load_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_expected_postprocess_exist(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                        transform_postprocess_and_load_pipeline_shp_custom_dir, expected_file):
            _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
            _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
            target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
            target_path = os.path.join(folder, "postprocessed_data", expected_file)
            assert os.path.isfile(target_path2)
            assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["eppol_45047_20200923.ttl"])
    def test_shp_mapping_files_size(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                    transform_postprocess_and_load_pipeline_shp_custom_dir, mapping):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_shp_transform_files_size(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                      transform_postprocess_and_load_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_postprocess_files_size(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                    transform_postprocess_and_load_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

    @pytest.mark.parametrize("expected_file", ["eppol_45047_20200923.nt"])
    def test_postprocess_tasks_output(self, transform_postprocess_and_load_pipeline_shp_default_dir,
                                      transform_postprocess_and_load_pipeline_shp_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_postprocess_and_load_pipeline_shp_custom_dir
        _, _, folder = transform_postprocess_and_load_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "postprocessed_data", expected_file)
        target_path = os.path.join(folder, "postprocessed_data", expected_file)

        def _check_target(target_path):
            with open(target_path, 'r') as target:
                for line in target:
                    if "<http://bogusz.test/eppol_45047_20200923/Geometry/9>" in line:
                        if "<http://www.opengis.net/ont/geosparql#asWKT>" in line:
                            return "<http://www.opengis.net/def/crs/EPSG/0/4258>" not in line

        assert _check_target(target_path2) is True
        assert _check_target(target_path) is True


class TestGenericTransformLoad(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "transform"
    PROCESS_2 = "load"

    @pytest.fixture(scope="class")
    def transform_and_load_and_transform_pipeline_default_dir(self, provide_generic_csv_data_rmlmapper,
                                                              provide_generic_csv_mapping_rmlmapper,
                                                              transform_and_load_and_transform_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--graph_uri={self.GRAPH_URI}",
                              f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--mapping_url={provide_generic_csv_mapping_rmlmapper}",
                              f"--input_type={self.INPUT_TYPE}", "-rg"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_and_load_and_transform_pipeline_custom_dir(self, provide_generic_csv_data_rmlmapper,
                                                             provide_generic_csv_mapping_rmlmapper):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--graph_uri={self.GRAPH_URI}",
                              f"--url_input={provide_generic_csv_data_rmlmapper}",
                              f"--mapping_url={provide_generic_csv_mapping_rmlmapper}",
                              f"--input_type={self.INPUT_TYPE}", "-rg", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_transform_and_load_and_transform_pipeline_output(self,
                                                              transform_and_load_and_transform_pipeline_default_dir,
                                                              transform_and_load_and_transform_pipeline_custom_dir):
        out, err, _ = transform_and_load_and_transform_pipeline_default_dir
        out2, err2, _ = transform_and_load_and_transform_pipeline_custom_dir
        assert err is None
        assert "Loading data into triplestore is done!" in out.decode()
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Loading data into triplestore is done!" in out2.decode()
        assert "Transformation is done!" in out2.decode()

    def test_transform_and_load_and_transform_pipeline_dir_exist(self,
                                                                 transform_and_load_and_transform_pipeline_default_dir,
                                                                 transform_and_load_and_transform_pipeline_custom_dir):
        _, _, folder2 = transform_and_load_and_transform_pipeline_custom_dir
        _, _, folder = transform_and_load_and_transform_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["test-generic-csv.ttl"])
    def test_csv_expected_mapping_exist(self, transform_and_load_and_transform_pipeline_default_dir,
                                        transform_and_load_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = transform_and_load_and_transform_pipeline_custom_dir
        _, _, folder = transform_and_load_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_expected_transform_exist(self, transform_and_load_and_transform_pipeline_default_dir,
                                      transform_and_load_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = transform_and_load_and_transform_pipeline_custom_dir
        _, _, folder = transform_and_load_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["gaigroup.nt"])
    def test_csv_transform_files_size(self, transform_and_load_and_transform_pipeline_default_dir,
                                      transform_and_load_and_transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = transform_and_load_and_transform_pipeline_custom_dir
        _, _, folder = transform_and_load_and_transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


@pytest.mark.skipif(not _check_db_credentials(), reason="Missing or incomplete config file for db support.")
class TestGenericDbMappingTransform(TestGeneric):
    INPUT_TYPE = "DB"
    PROCESS_1 = "transform"
    PROCESS_2 = "mapping"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_db_default_dir(self, mapping_and_transform_pipeline_db_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--db_input", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_db_custom_dir(self):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--db_input", f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_db_output(self, mapping_and_transform_pipeline_db_default_dir,
                                                      mapping_and_transform_pipeline_db_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_db_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_db_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_db_dir_exist(self, mapping_and_transform_pipeline_db_default_dir,
                                                         mapping_and_transform_pipeline_db_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_db_custom_dir
        _, _, folder = mapping_and_transform_pipeline_db_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["mapping_from_db.ttl"])
    def test_shp_expected_mapping_exist(self, mapping_and_transform_pipeline_db_default_dir,
                                        mapping_and_transform_pipeline_db_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_db_custom_dir
        _, _, folder = mapping_and_transform_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["dump_from_db.nt"])
    def test_expected_transform_exist(self, mapping_and_transform_pipeline_db_default_dir,
                                      mapping_and_transform_pipeline_db_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_db_custom_dir
        _, _, folder = mapping_and_transform_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["mapping_from_db.ttl"])
    def test_shp_mapping_files_size(self, mapping_and_transform_pipeline_db_default_dir,
                                    mapping_and_transform_pipeline_db_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_db_custom_dir
        _, _, folder = mapping_and_transform_pipeline_db_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["dump_from_db.nt"])
    def test_shp_transform_files_size(self, mapping_and_transform_pipeline_db_default_dir,
                                      mapping_and_transform_pipeline_db_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_db_custom_dir
        _, _, folder = mapping_and_transform_pipeline_db_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericPreprocessAndTransformTarql(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "preprocess"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def preprocess_and_transform_tarql_default_dir(self, provide_generic_tarql_data, provide_generic_tarql_query,
                                                    preprocess_and_transform_tarql_custom_dir,
                                                   preprocess_and_transform_tarql_custom2_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--preprocess_activity=add_seq_col",
                              f"--url_input={provide_generic_tarql_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_tarql_query}", "--sparql_query"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_and_transform_tarql_custom_dir(self, provide_generic_tarql_data, provide_generic_tarql_query,
                                                  preprocess_and_transform_tarql_custom2_dir):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--preprocess_activity=add_seq_col",
                              f"--url_input={provide_generic_tarql_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_tarql_query}", "--sparql_query", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    @pytest.fixture(scope="class")
    def preprocess_and_transform_tarql_custom2_dir(self, provide_generic_tarql_data, provide_generic_tarql_query):
        custom_dir = "custom_opt/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", "--preprocess_activity=add_seq_col",
                              f"--url_input={provide_generic_tarql_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_tarql_query}", "--sparql_query", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_and_transform_tarql_output(self, preprocess_and_transform_tarql_default_dir,
                                                   preprocess_and_transform_tarql_custom_dir,
                                                   preprocess_and_transform_tarql_custom2_dir):
        out, err, _ = preprocess_and_transform_tarql_default_dir
        out2, err2, _ = preprocess_and_transform_tarql_custom_dir
        out3, err3, _ = preprocess_and_transform_tarql_custom2_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()
        assert "Transformation is done!" in out2.decode()
        assert err3 is None
        assert "Preprocessing is done!" in out3.decode()
        assert "Transformation is done!" in out3.decode()

    def test_preprocess_and_transform_tarql_dir_exist(self, preprocess_and_transform_tarql_default_dir,
                                                      preprocess_and_transform_tarql_custom_dir,
                                                      preprocess_and_transform_tarql_custom2_dir):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        assert os.path.exists(folder3)
        assert os.path.isdir(folder3)
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["tarql_mock.csv"])
    def test_expected_csv_exist(self, preprocess_and_transform_tarql_default_dir,
                                preprocess_and_transform_tarql_custom_dir,
                                preprocess_and_transform_tarql_custom2_dir, expected_file):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        target_path3 = os.path.join(folder3, "preprocessed_data", expected_file)
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path3)
        assert os.path.isfile(target_path3)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["mock_tarql.rq"])
    def test_csv_expected_mapping_exist(self, preprocess_and_transform_tarql_default_dir,
                                        preprocess_and_transform_tarql_custom_dir,
                                        preprocess_and_transform_tarql_custom2_dir, expected_file):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        target_path3 = os.path.join(folder3, "mappings", expected_file)
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path3)
        assert os.path.isfile(target_path3)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["tarql_mock.nt"])
    def test_expected_transform_exist(self, preprocess_and_transform_tarql_default_dir,
                                      preprocess_and_transform_tarql_custom_dir,
                                      preprocess_and_transform_tarql_custom2_dir, expected_file):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        target_path3 = os.path.join(folder3, "dumps", expected_file)
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path3)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["tarql_mock.csv"])
    def test_preprocess_seq_col(self, preprocess_and_transform_tarql_default_dir,
                                preprocess_and_transform_tarql_custom_dir,
                                preprocess_and_transform_tarql_custom2_dir, expected_file):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        target_path3 = os.path.join(folder3, "preprocessed_data", expected_file)
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        df3 = pd.read_csv(target_path3)
        df2 = pd.read_csv(target_path2)
        df = pd.read_csv(target_path)
        assert df3.columns[0] == "seq"
        assert df2.columns[0] == "seq"
        assert df.columns[0] == "seq"
        assert df3.iloc[0, 0] == 1
        assert df2.iloc[0, 0] == 1
        assert df.iloc[0, 0] == 1

    @pytest.mark.parametrize("mapping", ["mock_tarql.rq"])
    def test_csv_mapping_files_size(self, preprocess_and_transform_tarql_default_dir,
                                    preprocess_and_transform_tarql_custom_dir,
                                    preprocess_and_transform_tarql_custom2_dir, mapping):
        _, _, folder3 = preprocess_and_transform_tarql_custom2_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        assert os.path.getsize(os.path.join(folder3, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["tarql_mock.nt"])
    def test_csv_transform_files_size(self, preprocess_and_transform_tarql_default_dir,
                                      preprocess_and_transform_tarql_custom_dir,
                                      preprocess_and_transform_tarql_custom2_dir, expected_file):
        _, _, folder3 = preprocess_and_transform_tarql_custom_dir
        _, _, folder2 = preprocess_and_transform_tarql_custom_dir
        _, _, folder = preprocess_and_transform_tarql_default_dir
        target_path3 = os.path.join(folder2, "dumps", expected_file)
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path3) > 1000
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericTransformCsvw(TestGeneric):
    INPUT_TYPE = "CSVW"
    PROCESS_1 = "transform"

    @pytest.fixture(scope="class")
    def transform_csvw_default_dir(self, provide_generic_csvw_data, provide_generic_csvw_mapping,
                                   transform_csvw_custom_dir, transform_csvw_custom2_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--url_input={provide_generic_csvw_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_csvw_mapping}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_csvw_custom_dir(self, provide_generic_csvw_data, provide_generic_csvw_mapping,
                                  transform_csvw_custom2_dir):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--url_input={provide_generic_csvw_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_csvw_mapping}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    @pytest.fixture(scope="class")
    def transform_csvw_custom2_dir(self, provide_generic_csvw_data, provide_generic_csvw_mapping):
        custom_dir = "custom_opt/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--url_input={provide_generic_csvw_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--mapping_url={provide_generic_csvw_mapping}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_transform_csvw_output(self, transform_csvw_default_dir, transform_csvw_custom_dir,
                                   transform_csvw_custom2_dir):
        out, err, _ = transform_csvw_default_dir
        out2, err2, _ = transform_csvw_custom_dir
        out3, err3, _ = transform_csvw_custom2_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert err3 is None
        assert "Transformation is done!" in out3.decode()

    def transform_csvw_dir_exist(self, transform_csvw_default_dir, transform_csvw_custom_dir,
                                 transform_csvw_custom2_dir):
        _, _, folder3 = transform_csvw_custom2_dir
        _, _, folder2 = transform_csvw_custom_dir
        _, _, folder = transform_csvw_default_dir
        assert os.path.exists(folder3)
        assert os.path.isdir(folder3)
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["csvw_mapping.nt"])
    def test_expected_transform_exist(self, transform_csvw_default_dir,
                                      transform_csvw_custom_dir, transform_csvw_custom2_dir, expected_file):
        _, _, folder3 = transform_csvw_custom2_dir
        _, _, folder2 = transform_csvw_custom_dir
        _, _, folder = transform_csvw_default_dir
        target_path3 = os.path.join(folder3, "dumps", expected_file)
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path3)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["csvw_mapping.nt"])
    def test_csv_transform_files_size(self, transform_csvw_default_dir,
                                      transform_csvw_custom_dir, transform_csvw_custom2_dir, expected_file):
        _, _, folder3 = transform_csvw_custom2_dir
        _, _, folder2 = transform_csvw_custom_dir
        _, _, folder = transform_csvw_default_dir
        target_path3 = os.path.join(folder3, "dumps", expected_file)
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path3) > 1
        assert os.path.getsize(target_path2) > 1
        assert os.path.getsize(target_path) > 1

###############################################################################
#                               GENERAL MAPPING SOLUTION.                     #
###############################################################################


class TestGenericMappingSolutionShp(TestGenericShpMapping):
    CONFIG_PATH = "cfg/GENERIC/TEST_CASES/SHP/shp.yaml"

    @pytest.fixture(scope="class")
    def mapping_pipeline_shp_default_dir(self, provide_shp_data_for_general_mapping_generation,
                                         mapping_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_shp_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_shp_custom_dir(self, provide_shp_data_for_general_mapping_generation):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_shp_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_shp_mapping_output(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir):
        out, err, _ = mapping_pipeline_shp_default_dir
        out2, err2, _ = mapping_pipeline_shp_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_shp_mapping_dir_exist(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", [GENERATED_MAPPING_FILENAME])
    def test_shp_expected_mapping_exist(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir,
                                        expected_file):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", [GENERATED_MAPPING_FILENAME])
    def test_shp_mapping_files_size(self, mapping_pipeline_shp_default_dir, mapping_pipeline_shp_custom_dir,
                                    mapping):
        _, _, folder2 = mapping_pipeline_shp_custom_dir
        _, _, folder = mapping_pipeline_shp_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericMappingSolutionCsv(TestGenericCsvMapping):
    CONFIG_PATH = "cfg/GENERIC/TEST_CASES/CSV/csv.yaml"

    @pytest.fixture(scope="class")
    def mapping_pipeline_csv_default_dir(self, provide_csv_data_for_general_mapping_generation,
                                         mapping_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_csv_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", "--preprocess_activity=add_seq_col",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_csv_custom_dir(self, provide_csv_data_for_general_mapping_generation):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS}",
                              f"--url_input={provide_csv_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", "--preprocess_activity=add_seq_col",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_csv_mapping_output(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir):
        out, err, _ = mapping_pipeline_csv_default_dir
        out2, err2, _ = mapping_pipeline_csv_custom_dir
        assert err is None
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Mappings generation is done!" in out2.decode()

    def test_csv_mapping_dir_exist(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", [GENERATED_MAPPING_FILENAME])
    def test_csv_expected_mapping_exist(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir,
                                        expected_file):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", [GENERATED_MAPPING_FILENAME])
    def test_csv_mapping_files_size(self, mapping_pipeline_csv_default_dir, mapping_pipeline_csv_custom_dir,
                                    mapping):
        _, _, folder2 = mapping_pipeline_csv_custom_dir
        _, _, folder = mapping_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestGenericMappingSolutionAndTransformShp(TestGeneric):
    CONFIG_PATH = "cfg/GENERIC/TEST_CASES/SHP/shp.yaml"
    INPUT_TYPE = "Shapefile"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_shp_default_dir(self, provide_shp_data_for_general_mapping_generation,
                                                       mapping_and_transform_pipeline_shp_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_shp_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_shp_custom_dir(self, provide_shp_data_for_general_mapping_generation):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_shp_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_shp_output(self, mapping_and_transform_pipeline_shp_default_dir,
                                                       mapping_and_transform_pipeline_shp_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_shp_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_shp_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_shp_dir_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                                          mapping_and_transform_pipeline_shp_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", [GENERATED_MAPPING_FILENAME])
    def test_shp_expected_mapping_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                        mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["VALIDATED_GSAA_DATA_2022_wgs84-sample.nt"])
    def test_shp_expected_transform_exist(self, mapping_and_transform_pipeline_shp_default_dir,
                                          mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", [GENERATED_MAPPING_FILENAME])
    def test_shp_mapping_files_size(self, mapping_and_transform_pipeline_shp_default_dir,
                                    mapping_and_transform_pipeline_shp_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["VALIDATED_GSAA_DATA_2022_wgs84-sample.nt"])
    def test_shp_transform_files_size(self, mapping_and_transform_pipeline_shp_default_dir,
                                      mapping_and_transform_pipeline_shp_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_shp_custom_dir
        _, _, folder = mapping_and_transform_pipeline_shp_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericMappingSolutionAndTransformCsv(TestGeneric):
    CONFIG_PATH = "cfg/GENERIC/TEST_CASES/CSV/csv.yaml"
    INPUT_TYPE = "CSV"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_default_dir(self, provide_csv_data_for_general_mapping_generation,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_csv_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", "--preprocess_activity=add_seq_col",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_custom_dir(self, provide_csv_data_for_general_mapping_generation):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_csv_data_for_general_mapping_generation}",
                              f"--base_uri={self.GRAPH_URI}", "--preprocess_activity=add_seq_col",
                              f"--input_type={self.INPUT_TYPE}", "--from_config",
                              f"--from_config_value={self.CONFIG_PATH}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_csv_output(self, mapping_and_transform_pipeline_csv_default_dir,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_csv_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_csv_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_csv_dir_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                                          mapping_and_transform_pipeline_csv_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", [GENERATED_MAPPING_FILENAME])
    def test_csv_expected_mapping_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                        mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["Oilspill_simulation_ILIAD_07.08.2023_preprocesed-sample.nt"])
    def test_csv_expected_transform_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                          mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", [GENERATED_MAPPING_FILENAME])
    def test_csv_mapping_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                    mapping_and_transform_pipeline_csv_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["Oilspill_simulation_ILIAD_07.08.2023_preprocesed-sample.nt"])
    def test_csv_transform_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                      mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

###############################################################################
#                               YARRRML.                                      #
###############################################################################


class TestGenericYarrrmlMappingTransformCsv(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_default_dir(self, provide_yarrrml_csv_data, provide_yarrrml_csv_rules,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_custom_dir(self, provide_yarrrml_csv_data, provide_yarrrml_csv_rules):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_csv_output(self, mapping_and_transform_pipeline_csv_default_dir,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_csv_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_csv_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_shp_dir_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                                          mapping_and_transform_pipeline_csv_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["rules.ttl"])
    def test_csv_expected_mapping_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                        mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_csv_expected_transform_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                          mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["rules.ttl"])
    def test_csv_mapping_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                    mapping_and_transform_pipeline_csv_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_csv_transform_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                      mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericYarrrmlMappingTransformCsvComplex(TestGeneric):
    INPUT_TYPE = "CSV"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_default_dir(self, provide_yarrrml_csv_data, provide_yarrrml_csv_rules_complex,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules_complex}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_csv_custom_dir(self, provide_yarrrml_csv_data, provide_yarrrml_csv_rules_complex):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules_complex}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_csv_output(self, mapping_and_transform_pipeline_csv_default_dir,
                                                       mapping_and_transform_pipeline_csv_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_csv_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_csv_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_shp_dir_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                                          mapping_and_transform_pipeline_csv_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["rules-complex.ttl"])
    def test_csv_expected_mapping_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                        mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_csv_expected_transform_exist(self, mapping_and_transform_pipeline_csv_default_dir,
                                          mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["rules-complex.ttl"])
    def test_csv_mapping_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                    mapping_and_transform_pipeline_csv_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_csv_transform_files_size(self, mapping_and_transform_pipeline_csv_default_dir,
                                      mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestGenericYarrrmlMappingTransformJson(TestGeneric):
    INPUT_TYPE = "JSON"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_json_default_dir(self, provide_yarrrml_json_data, provide_yarrrml_json_rules,
                                                        mapping_and_transform_pipeline_json_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_json_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_json_rules}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_json_custom_dir(self, provide_yarrrml_json_data, provide_yarrrml_json_rules):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_json_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_json_rules}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_json_output(self, mapping_and_transform_pipeline_json_default_dir,
                                                       mapping_and_transform_pipeline_json_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_json_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_json_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_shp_dir_exist(self, mapping_and_transform_pipeline_json_default_dir,
                                                          mapping_and_transform_pipeline_json_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_json_custom_dir
        _, _, folder = mapping_and_transform_pipeline_json_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["rules-json.ttl"])
    def test_json_expected_mapping_exist(self, mapping_and_transform_pipeline_json_default_dir,
                                        mapping_and_transform_pipeline_json_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_json_custom_dir
        _, _, folder = mapping_and_transform_pipeline_json_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["episodes.nt"])
    def test_json_expected_transform_exist(self, mapping_and_transform_pipeline_json_default_dir,
                                          mapping_and_transform_pipeline_json_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_json_custom_dir
        _, _, folder = mapping_and_transform_pipeline_json_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["rules-json.ttl"])
    def test_json_mapping_files_size(self, mapping_and_transform_pipeline_json_default_dir,
                                    mapping_and_transform_pipeline_json_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_json_custom_dir
        _, _, folder = mapping_and_transform_pipeline_json_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["episodes.nt"])
    def test_json_transform_files_size(self, mapping_and_transform_pipeline_json_default_dir,
                                      mapping_and_transform_pipeline_json_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_json_custom_dir
        _, _, folder = mapping_and_transform_pipeline_json_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 500
        assert os.path.getsize(target_path) > 500


class TestGenericYarrrmlMappingTransformXml(TestGeneric):
    INPUT_TYPE = "XML"
    PROCESS_1 = "mapping"
    PROCESS_2 = "transform"

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_xml_default_dir(self, provide_yarrrml_xml_data, provide_yarrrml_xml_rules,
                                                       mapping_and_transform_pipeline_xml_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_xml_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_xml_rules}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_and_transform_pipeline_xml_custom_dir(self, provide_yarrrml_xml_data, provide_yarrrml_xml_rules):
        custom_dir = "custom_output/subdir"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}",
                              f"--url_input={provide_yarrrml_xml_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_xml_rules}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_and_transform_pipeline_xml_output(self, mapping_and_transform_pipeline_xml_default_dir,
                                                       mapping_and_transform_pipeline_xml_custom_dir):
        out, err, _ = mapping_and_transform_pipeline_xml_default_dir
        out2, err2, _ = mapping_and_transform_pipeline_xml_custom_dir
        assert err is None
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_mapping_and_transform_pipeline_xml_dir_exist(self, mapping_and_transform_pipeline_xml_default_dir,
                                                          mapping_and_transform_pipeline_xml_custom_dir):
        _, _, folder2 = mapping_and_transform_pipeline_xml_custom_dir
        _, _, folder = mapping_and_transform_pipeline_xml_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["rules-xml.ttl"])
    def test_xml_expected_mapping_exist(self, mapping_and_transform_pipeline_xml_default_dir,
                                        mapping_and_transform_pipeline_xml_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_xml_custom_dir
        _, _, folder = mapping_and_transform_pipeline_xml_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["episodes.nt"])
    def test_xml_expected_transform_exist(self, mapping_and_transform_pipeline_xml_default_dir,
                                          mapping_and_transform_pipeline_xml_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_xml_custom_dir
        _, _, folder = mapping_and_transform_pipeline_xml_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["rules-xml.ttl"])
    def test_xml_mapping_files_size(self, mapping_and_transform_pipeline_xml_default_dir,
                                    mapping_and_transform_pipeline_xml_custom_dir, mapping):
        _, _, folder2 = mapping_and_transform_pipeline_xml_custom_dir
        _, _, folder = mapping_and_transform_pipeline_xml_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["episodes.nt"])
    def test_xml_transform_files_size(self, mapping_and_transform_pipeline_xml_default_dir,
                                      mapping_and_transform_pipeline_xml_custom_dir, expected_file):
        _, _, folder2 = mapping_and_transform_pipeline_xml_custom_dir
        _, _, folder = mapping_and_transform_pipeline_xml_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 500
        assert os.path.getsize(target_path) > 500


class TestGenericYarrrmlPreprocessMappingTransformCsv(TestGeneric):
    INPUT_TYPE = "CSV"
    ACTIVITY = "normalize_delimiter"
    PROCESS_1 = "preprocess"
    PROCESS_2 = "mapping"
    PROCESS_3 = "transform"

    @pytest.fixture(scope="class")
    def preprocess_mapping_and_transform_pipeline_csv_default_dir(self, provide_yarrrml_csv_data, provide_yarrrml_csv_rules,
                                                       preprocess_mapping_and_transform_pipeline_csv_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules}",
                              f"--preprocess_activity={self.ACTIVITY}"],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_mapping_and_transform_pipeline_csv_custom_dir(self, provide_yarrrml_csv_data,
                                                                 provide_yarrrml_csv_rules):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--process={self.PROCESS_1}",
                              f"--process={self.PROCESS_2}", f"--process={self.PROCESS_3}",
                              f"--url_input={provide_yarrrml_csv_data}", f"--input_type={self.INPUT_TYPE}",
                              f"--yarrrml_rules_url={provide_yarrrml_csv_rules}",
                              f"--preprocess_activity={self.ACTIVITY}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_preprocess_mapping_and_transform_pipeline_csv_output(self,
                                                                  preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                                       preprocess_mapping_and_transform_pipeline_csv_custom_dir):
        out, err, _ = preprocess_mapping_and_transform_pipeline_csv_default_dir
        out2, err2, _ = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        assert err is None
        assert "Preprocessing is done!" in out.decode()
        assert "Transformation is done!" in out.decode()
        assert "Mappings generation is done!" in out.decode()
        assert err2 is None
        assert "Preprocessing is done!" in out2.decode()
        assert "Transformation is done!" in out2.decode()
        assert "Mappings generation is done!" in out2.decode()

    def test_preprocess_mapping_and_transform_pipeline_dir_exist(self,
                                                          preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                                          preprocess_mapping_and_transform_pipeline_csv_custom_dir):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["episodes.csv", "people.csv"])
    def test_expected_csv_exist(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                preprocess_mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["rules.ttl"])
    def test_expected_mapping_exist(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                        preprocess_mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_expected_transform_exist(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                          preprocess_mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["people.csv", "episodes.csv"])
    def test_preprocess_normalize_delimiter(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                            preprocess_mapping_and_transform_pipeline_csv_custom_dir,
                                            expected_file):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "preprocessed_data", expected_file)
        target_path = os.path.join(folder, "preprocessed_data", expected_file)
        with open(target_path2, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","
        with open(target_path, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            assert dialect.delimiter == ","

    @pytest.mark.parametrize("mapping", ["rules.ttl"])
    def test_mapping_files_size(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                    preprocess_mapping_and_transform_pipeline_csv_custom_dir, mapping):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100

    @pytest.mark.parametrize("expected_file", ["episodes.nt", "people.nt"])
    def test_transform_files_size(self, preprocess_mapping_and_transform_pipeline_csv_default_dir,
                                      preprocess_mapping_and_transform_pipeline_csv_custom_dir, expected_file):
        _, _, folder2 = preprocess_mapping_and_transform_pipeline_csv_custom_dir
        _, _, folder = preprocess_mapping_and_transform_pipeline_csv_default_dir
        target_path2 = os.path.join(folder2, "dumps", expected_file)
        target_path = os.path.join(folder, "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

