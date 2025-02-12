import os
import subprocess
import shutil
import glob
import pytest

from test_scenarios.base_testing_class import TestBase


class TestFadn(TestBase):
    PIPELINE = "fadn"
    GRAPH_URI = "http://autotest.pipelines/"

class TestFadnFetch(TestFadn):
    STAGE = "fetch"

    @pytest.fixture(scope="class")
    def fetch_pipeline_default_dir(self, provide_fadn_data, fetch_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def fetch_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir],
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

    @pytest.mark.parametrize("expected_dir", ["YEAR.COUNTRY", "YEAR.COUNTRY.ANC3", "SGM", "SO"])
    def test_fetch_dir_structure(self, fetch_pipeline_default_dir, fetch_pipeline_custom_dir, expected_dir):
        _, _, folder2 = fetch_pipeline_custom_dir
        _, _, folder = fetch_pipeline_default_dir
        target_search2 = glob.glob(f"{folder2}/**/YEAR.*", recursive=True)
        target_search = glob.glob(f"{folder}/**/YEAR.*", recursive=True)
        assert any(expected_dir in path for path in target_search2)
        assert any(expected_dir in path for path in target_search)


class TestFadnPreprocess(TestFadn):
    STAGE = "preprocess"

    @pytest.fixture(scope="class")
    def preprocess_pipeline_default_dir(self, provide_fadn_data, preprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def preprocess_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    @pytest.mark.parametrize("expected_dir", ["YEAR.COUNTRY_preprocessed", "YEAR.COUNTRY.ANC3_preprocessed"])
    def test_preprocess_dir_structure(self, preprocess_pipeline_default_dir, preprocess_pipeline_custom_dir,
                                      expected_dir):
        _, _, folder2 = preprocess_pipeline_custom_dir
        _, _, folder = preprocess_pipeline_default_dir
        target_search2 = glob.glob(f"{folder2}/**/YEAR.*", recursive=True)
        target_search = glob.glob(f"{folder}/**/YEAR.*", recursive=True)
        assert any(expected_dir in path for path in target_search2)
        assert any(expected_dir in path for path in target_search)


class TestFadnMapping(TestFadn):
    STAGE = "mapping"

    @pytest.fixture(scope="class")
    def mapping_pipeline_default_dir(self, provide_fadn_data, mapping_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def mapping_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_mapping_dir_exist(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        assert "mappings" in os.listdir(folder2)
        assert "mappings" in os.listdir(folder)

    @pytest.mark.parametrize("mapping", ["mapping-year-country-2022.ttl", "mapping-year-country-2022.ttl"])
    def test_mapping_files_exist(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir, mapping):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        assert os.path.isfile(os.path.join(folder2, "mappings", mapping))
        assert os.path.isfile(os.path.join(folder, "mappings", mapping))

    @pytest.mark.parametrize("mapping", ["mapping-year-country-2022.ttl", "mapping-year-country-2022.ttl"])
    def test_mapping_files_size(self, mapping_pipeline_default_dir, mapping_pipeline_custom_dir, mapping):
        _, _, folder2 = mapping_pipeline_custom_dir
        _, _, folder = mapping_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "mappings", mapping)) > 100
        assert os.path.getsize(os.path.join(folder, "mappings", mapping)) > 100


@pytest.mark.skipif(not os.path.exists("utils/rmlmapper"), reason="RMLmapper not installed.")
class TestFadnTransform(TestFadn):
    STAGE = "transform"

    @pytest.fixture(scope="class")
    def transform_pipeline_default_dir(self, provide_fadn_data, transform_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def transform_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_transform_dir_exist(self, transform_pipeline_default_dir, transform_pipeline_custom_dir):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        assert "output" in os.listdir(folder2)
        assert "output" in os.listdir(folder)
        assert "dumps" in os.listdir(os.path.join(folder2, "output"))
        assert "dumps" in os.listdir(os.path.join(folder, "output"))

    @pytest.mark.parametrize("dump", ["fadn-year-country-2022-fadn_data.nt", "fadn-year-country-anc3-2022-fadn_data.nt"])
    def test_transform_files_exist(self, transform_pipeline_default_dir, transform_pipeline_custom_dir, dump):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        assert os.path.isfile(os.path.join(folder2, "output", "dumps", dump))
        assert os.path.isfile(os.path.join(folder, "output", "dumps", dump))

    @pytest.mark.parametrize("dump", ["fadn-year-country-2022-fadn_data.nt", "fadn-year-country-anc3-2022-fadn_data.nt"])
    def test_transform_files_size(self, transform_pipeline_default_dir, transform_pipeline_custom_dir, dump):
        _, _, folder2 = transform_pipeline_custom_dir
        _, _, folder = transform_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "output", "dumps", dump)) > 1000
        assert os.path.getsize(os.path.join(folder, "output", "dumps", dump)) > 1000


@pytest.mark.skipif(not os.path.exists("utils/rmlmapper"), reason="RMLmapper not installed.")
class TestFadnPostprocess(TestFadn):
    STAGE = "postprocess"

    @pytest.fixture(scope="class")
    def postprocess_pipeline_default_dir(self, provide_fadn_data, postprocess_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}"], shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def postprocess_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    def test_postprocess_dir_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert "output" in os.listdir(folder2)
        assert "output" in os.listdir(folder)
        assert "dumps" in os.listdir(os.path.join(folder2, "output"))
        assert "dumps" in os.listdir(os.path.join(folder, "output"))

    @pytest.mark.parametrize("dump", ["fadn-year-country-2022-fadn_data.nt", "fadn-year-country-anc3-2022-fadn_data.nt"])
    def test_postprocess_files_exist(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir, dump):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert os.path.isfile(os.path.join(folder2, "output", "dumps", dump))
        assert os.path.isfile(os.path.join(folder, "output", "dumps", dump))

    @pytest.mark.parametrize("dump", ["fadn-year-country-2022-fadn_data.nt", "fadn-year-country-anc3-2022-fadn_data.nt"])
    def test_postprocess_files_size(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir, dump):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        assert os.path.getsize(os.path.join(folder2, "output", "dumps", dump)) > 1000
        assert os.path.getsize(os.path.join(folder, "output", "dumps", dump)) > 1000

    @pytest.mark.parametrize("expected_file",
                             ["fadn-year-country-2022-fadn_data.nt", "fadn-year-country-anc3-2022-fadn_data.nt"])
    def test_postprocess_tasks_output(self, postprocess_pipeline_default_dir, postprocess_pipeline_custom_dir,
                                      expected_file):
        _, _, folder2 = postprocess_pipeline_custom_dir
        _, _, folder = postprocess_pipeline_default_dir
        target_path2 = os.path.join(folder2, "output", "dumps", expected_file)
        target_path = os.path.join(folder, "output", "dumps", expected_file)

        def _check_target(target_path):
            with open(target_path, 'r') as target:
                for line in target:
                    if '""^^' in line:
                        return False
                return True

        assert _check_target(target_path2) is True
        assert _check_target(target_path) is True


@pytest.mark.skipif(not os.path.exists("utils/rmlmapper"), reason="RMLmapper not installed.")
class TestFadnAll(TestFadn):
    STAGE = "all"

    @pytest.fixture(scope="class")
    def all_pipeline_default_dir(self, provide_fadn_data, all_pipeline_custom_dir):
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "-rg", "-gpd", "--graph_uri", self.GRAPH_URI],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, self.DEFAULT_DIR
        shutil.rmtree(self.DEFAULT_DIR)

    @pytest.fixture(scope="class")
    def all_pipeline_custom_dir(self, provide_fadn_data):
        custom_dir = "custom_output"
        p = subprocess.Popen([self.EXECUTABLE, self.MODULE, self.PIPELINE, f"--stage={self.STAGE}",
                              f"--url_input={provide_fadn_data}", "--output", custom_dir, "-rg", "-gpd",
                              "--graph_uri", self.GRAPH_URI],
                             shell=False, stdout=subprocess.PIPE)
        out, err = p.communicate()
        yield out, err, custom_dir
        shutil.rmtree(custom_dir)

    @pytest.mark.parametrize("output_msg", ["Loading dumps into triplestore",
                                            "Uploading files to the server",
                                            "has been cleared!",
                                            "Data have been loaded",
                                            "fadn-year-country-2022-fadn_data.nt loaded successfully!",
                                            "fadn-year-country-anc3-2022-fadn_data.nt loaded successfully!",
                                            "Done!"])
    def test_all_output(self, all_pipeline_default_dir, all_pipeline_custom_dir, output_msg):
        out, err, _ = all_pipeline_default_dir
        out2, err2, _ = all_pipeline_custom_dir
        assert err is None
        assert output_msg in out.decode()
        assert err2 is None
        assert output_msg in out2.decode()
