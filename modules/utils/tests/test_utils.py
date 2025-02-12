import os
from uuid import UUID
import pytest
import datetime

from modules.utils import utils


def test_base64_encoding():
    text = "this_is_a_test_string"
    text2 = "testing_numbers_12345"
    assert utils.base64_encoding(text) == str("dGhpc19pc19hX3Rlc3Rfc3RyaW5n")
    assert utils.base64_encoding(text2) == str("dGVzdGluZ19udW1iZXJzXzEyMzQ1")


def test_base64_decoding():
    encoded_b64 = utils.base64_encoding('this_is_a_test_string', strip_equal=False)
    encoded2_b64 = utils.base64_encoding('testing_numbers_12345', strip_equal=False)
    decoded = utils.base64_decoding(encoded_b64)
    decoded2 = utils.base64_decoding(encoded2_b64)
    assert decoded == str("this_is_a_test_string")
    assert decoded2 == str("testing_numbers_12345")


def test_is_path_abs():
    path1 = os.path.join('test', 'folder', 'relative_path')
    cwd = os.getcwd()
    path2 = os.path.join(cwd, 'this', 'should_be', 'abspath')
    assert utils.is_path_abs(path1) == False
    assert utils.is_path_abs(path2) == True


def test_generate_uuid():
    proper_code = utils.generate_uuid()
    not_a_proper_code = 'f95da011-e3f9-405f-851a-5a5f5612'
    UUID(proper_code, version=4)
    with pytest.raises(ValueError):
        UUID(not_a_proper_code, version=4)


def test_url_extract_filename():
    assert utils.url_extract_filename('http://testsite.com/module/1/name.gz') == 'name.gz'
    assert utils.url_extract_filename('http://testsite.com/module/1/name.zip') == 'name.zip'
    assert utils.url_extract_filename('http://testsite.com/module/1/name.tar.gz') == 'name.tar.gz'


def test_convert_into_date():
    correct_string = '2021-01-01'
    incorrect_string = '01.01.2021'
    assert isinstance(utils.convert_into_date(correct_string), datetime.date) is True
    assert utils.convert_into_date(correct_string) == datetime.date(2021, 1, 1)
    assert isinstance(utils.convert_into_date(incorrect_string), datetime.date) is False
    assert utils.convert_into_date(incorrect_string) is None


def test_set_folder_name_based_on_url():
    url1 = "http://test.com/file.zip"
    url2 = "http://test.com/myfile.7z"
    assert utils.set_folder_name_based_on_url(url1) == "file"
    assert utils.set_folder_name_based_on_url(url2) == "myfile"
