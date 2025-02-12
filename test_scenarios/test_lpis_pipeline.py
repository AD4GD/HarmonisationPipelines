import os
import subprocess
import shutil
import pytest

from test_scenarios.base_testing_class import TestBase


class TestLpis(TestBase):
    PIPELINE = "lpis"
    GRAPH_URI = "http://autotest.pipelines/"


class TestLpisFetch(TestLpis):
    STAGE = "fetch"

    @pytest.fixture(scope="class")
    def fetch_pipeline_default_dir(self, provide_lpis_data, fetch_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def fetch_pipeline_custom_dir(self, provide_lpis_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_fetch_output(self, fetch_pipeline_default_dir, fetch_pipeline_custom_dir):
        out, err, _ = fetch_pipeline_default_dir
        out2, err2, _ = fetch_pipeline_custom_dir
        assert err is None
        assert "Done!" in out.decode()
        assert err2 is None
        assert "Done!" in out2.decode()

    def test_fetch_dir_exist(self, fetch_pipeline_default_dir, fetch_pipeline_custom_dir):
        _, _, folder2 = fetch_pipeline_custom_dir
        _, _, folder = fetch_pipeline_default_dir
        assert os.path.exists(folder2)
        assert os.path.isdir(folder2)
        assert os.path.exists(folder)
        assert os.path.isdir(folder)

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407.dbf", "rec_13057_20200407.prj",
                                               "rec_13057_20200407.shp", "rec_13057_20200407.shx"])
    def test_expected_shapefile_exist(self, fetch_pipeline_default_dir, fetch_pipeline_custom_dir, expected_file):
        _, _, folder2 = fetch_pipeline_custom_dir
        _, _, folder = fetch_pipeline_default_dir
        target_path2 = os.path.join(folder2, "lpis_data", expected_file)
        target_path = os.path.join(folder, "lpis_data", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)


class TestLpisMapping(TestLpis):
    STAGE = "mapping"

    @pytest.fixture(scope="class")
    def mapping_pipeline_default_dir(self, provide_lpis_data, mapping_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_custom_dir(self, provide_lpis_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", "--output", custom_dir, '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_output(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir):
        out, err, _ = mapping_pipeline_default_dir
        out2, err2, _ = mapping_pipeline_custom_dir
        assert err is None
        assert "Done!" in out.decode()
        assert err2 is None
        assert "Done!" in out2.decode()

    def test_mapping_dir_exist(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("expected_file", ["LPIS_mapping_rec_13057_20200407.ttl"])
    def test_expected_mapping_exist(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        target_path2 = os.path.join(folder2, "mappings", expected_file)
        target_path = os.path.join(folder, "mappings", expected_file)
        assert os.path.exists(target_path2)
        assert os.path.isfile(target_path2)
        assert os.path.exists(target_path)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("mapping", ["LPIS_mapping_rec_13057_20200407.ttl"])
    def test_mapping_files_size(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir, mapping):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


class TestLpisTransform(TestLpis):
    STAGE = "transform"

    @pytest.fixture(scope="class")
    def transform_pipeline_default_dir(self, provide_lpis_data, transform_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_custom_dir(self, provide_lpis_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", "--output", custom_dir, '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_transform_output(self, transform_pipeline_default_dir, transform_pipeline_custom_dir):
        out, err, _ = transform_pipeline_default_dir
        out2, err2, _ = transform_pipeline_custom_dir
        assert err is None
        assert "Done!" in out.decode()
        assert err2 is None
        assert "Done!" in out2.decode()

    def test_transform_dir_exist(self, transform_pipeline_default_dir, transform_pipeline_custom_dir):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        assert "output" in os.listdir(folder2)
        assert "output" in os.listdir(folder)
        assert "dumps" in os.listdir(os.path.join(folder2, "output"))
        assert "dumps" in os.listdir(os.path.join(folder, "output"))

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407_dump.nt"])
    def test_expected_transform_exist(self, transform_pipeline_default_dir, transform_pipeline_custom_dir,
                                      expected_file):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407_dump.nt"])
    def test_transform_files_size(self, transform_pipeline_default_dir, transform_pipeline_custom_dir, expected_file):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000


class TestLpisPostprocess(TestLpis):
    STAGE = "postprocess"

    @pytest.fixture(scope="class")
    def postprocess_pipeline_default_dir(self, provide_lpis_data, postprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def postprocess_pipeline_custom_dir(self, provide_lpis_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", "--output", custom_dir, '--country', 'spain'],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_postprocess_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        out, err, _ = postprocess_pipeline_default_dir
        out2, err2, _ = postprocess_pipeline_custom_dir
        assert err is None
        assert "Done!" in out.decode()
        assert err2 is None
        assert "Done!" in out2.decode()

    def test_postprocess_dir_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert "output" in os.listdir(folder2)
        assert "output" in os.listdir(folder)
        assert "dumps" in os.listdir(os.path.join(folder2, "output"))
        assert "dumps" in os.listdir(os.path.join(folder, "output"))

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407_dump.nt"])
    def test_expected_postprocess_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                        expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)
        assert os.path.isfile(target_path2)
        assert os.path.isfile(target_path)

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407_dump.nt"])
    def test_postprocess_files_size(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                    expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)
        assert os.path.getsize(target_path2) > 1000
        assert os.path.getsize(target_path) > 1000

    @pytest.mark.parametrize("expected_file", ["rec_13057_20200407_dump.nt"])
    def test_postprocess_tasks_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                      expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)

        def _check_target(target_path):
            with open(target_path, 'r') as target:
                for line in target:
                    if "<http://w3id.org/iacs/open/es/LPIS/Parcel/Geometry/1416507980>" in line:
                        if "<http://www.opengis.net/ont/geosparql#asWKT>" in line:
                            return "<http://www.opengis.net/def/crs/EPSG/0/4258>" not in line

        assert _check_target(target_path2) is True
        assert _check_target(target_path) is True


class TestLpisAll(TestLpis):
    STAGE = "all"

    @pytest.fixture(scope="class")
    def all_pipeline_default_dir(self, provide_lpis_data, all_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", '--country', 'spain',
                              "-rg", "-gpd", "--graph_uri", self.GRAPH_URI],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def all_pipeline_custom_dir(self, provide_lpis_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_lpis_data}", "--output", custom_dir, '--country', 'spain',
                              "-rg", "-gpd", "--graph_uri", self.GRAPH_URI
                              ],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    @pytest.mark.parametrize("output_msg", ["Loading dumps into triplestore",
                                            "Uploading files to the server",
                                            "has been cleared!",
                                            "Data have been loaded",
                                            "rec_13057_20200407_dump.nt loaded successfully!",
                                            "Done!"])
    def test_all_output(self, all_pipeline_default_dir, all_pipeline_custom_dir, output_msg):
        out, err, _ = all_pipeline_default_dir
        out2, err2, _ = all_pipeline_custom_dir
        assert err is None
        assert output_msg in out.decode()
        assert err2 is None
        assert output_msg in out2.decode()
