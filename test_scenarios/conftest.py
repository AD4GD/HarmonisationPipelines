import os

import pytest


@pytest.fixture(scope="module")
def provide_fadn_data():
    return "https://box.psnc.pl/f/27e3fee316/?raw=1"


@pytest.fixture(scope="module")
def provide_lpis_data():
    return "https://box.psnc.pl/f/5b80101bc9/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csv_data():
    return "https://box.psnc.pl/f/3b1aabed37/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csv_data_rmlmapper():
    return "https://box.psnc.pl/f/d27e4deaa3/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_netcdf_data():
    return "https://box.psnc.pl/f/e251aeb90a/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_mixed_data():
    return "https://box.psnc.pl/f/e64946d6dd/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_shp_data():
    return "https://box.psnc.pl/f/0e891f34ab/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_json_data():
    return "https://box.psnc.pl/f/8fe56107d3/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_json_data_enum():
    return "https://box.psnc.pl/f/3f2df85dc8/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csv_mapping():
    return "https://box.psnc.pl/f/634cb2c8b4/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csv_mapping_rmlmapper():
    return "https://box.psnc.pl/f/2ba8c77919/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_shp_mapping():
    return "https://box.psnc.pl/f/480c361d8e/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_json_mapping():
    return "https://box.psnc.pl/f/54ff8991c0/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_dump():
    return "https://box.psnc.pl/f/29938077f7/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_postprocessed_dump():
    return "https://box.psnc.pl/f/feb21b2022/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_db_mapping():
    return "https://box.psnc.pl/f/6cd6869ba5/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_tarql_query():
    return "https://box.psnc.pl/f/de34dda373/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_tarql_data():
    return "https://box.psnc.pl/f/ba0cf6a8a6/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csvw_data():
    return "https://box.psnc.pl/f/6a0660d188/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csvw_mapping():
    return "https://box.psnc.pl/f/1bccd130df/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_csv_different_delimiter():
    return "https://box.psnc.pl/f/3c997906ca/?raw=1"


@pytest.fixture(scope="module")
def provide_generic_multiple_archives():
    return "https://box.psnc.pl/f/4c1b08e5b9/?raw=1"


@pytest.fixture(scope="module")
def provide_linking_data():
    return "https://box.psnc.pl/f/7d856fd71a/?raw=1"


@pytest.fixture(scope="module")
def provide_shp_data_for_general_mapping_generation():
    return "https://box.psnc.pl/f/2479bde978/?raw=1"


@pytest.fixture(scope="module")
def provide_csv_data_for_general_mapping_generation():
    return "https://box.psnc.pl/f/c82e270a32/?raw=1"


@pytest.fixture(scope="module")
def provide_dump_for_expression_replacement():
    return "https://box.psnc.pl/f/b7ef7f6862/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_csv_data():
    return "https://box.psnc.pl/f/576ec8317e/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_csv_rules():
    return "https://box.psnc.pl/f/b91a2be793/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_csv_rules_complex():
    return "https://box.psnc.pl/f/1b609bf9d9/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_json_data():
    return "https://box.psnc.pl/f/fde2659758/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_json_rules():
    return "https://box.psnc.pl/f/bdb76add5c/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_xml_data():
    return "https://box.psnc.pl/f/26702201b8/?raw=1"


@pytest.fixture(scope="module")
def provide_yarrrml_xml_rules():
    return "https://box.psnc.pl/f/6b22472828/?raw=1"


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(os.path.join(request.fspath.dirname, os.pardir))
