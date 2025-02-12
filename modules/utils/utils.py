import base64
import os
import uuid
import datetime
import yaml
import shutil
import csv
import rdflib
import json
import re
import dateutil.parser
import zipfile
from distutils.dir_util import copy_tree
import urllib.request
from urllib.error import URLError
from rdflib.term import _is_valid_uri
import geopandas as gpd
import chardet
import codecs

from modules.dictionaries.dictionaries import XSD_dict
from modules.settings import DEFAULT_CRS


def base64_encoding(text, strip_equal=True):
    """
    Helper function that encodes text into base64 format.
    :param text: str -> text to be encoded.
    :param strip_equal: boolean -> if True the '=' sign in encoded string will be stripped.
    :return: base64 code.
    """
    enc = base64.b64encode(bytes(text, 'utf-8'))
    if strip_equal:
        enc = enc.decode('utf-8').strip('=')
    return enc


def base64_decoding(decoded_b64):
    """
    Helper function that decodes base64 into text format.
    :param decoded_b64: encoded base64 object.
    :return: decoded text
    """
    return base64.b64decode(decoded_b64).decode('utf-8')


def is_path_abs(path):
    """
    Helper function that checks if given path is absolute or relative.
    :param path: str -> path.
    :return: boolean -> True if path is abs, else False.
    """
    return os.path.isabs(path)


def generate_uuid():
    """
    Helper function that generates unique uuid number and converts it into a string.
    :return: str -> unique uuid number converted into string.
    """
    return str(uuid.uuid4())


def convert_into_date(input_string):
    """
    Helper function that generated date from a string in format YYYY-MM-DD.
    :param input_string: str -> input date as a string.
    :return: date object.
    """
    try:
        d = datetime.datetime.strptime(input_string, "%Y-%m-%d")
        return datetime.datetime.date(d)
    except ValueError:
        print('Improper string format in the configfile. YYYY-MM-DD format was expected.')
        return None


def generate_current_date():
    """
    Helper function that generates date for current point in time.
    :return: date object.
    """
    return datetime.datetime.now().date()


def url_extract_filename(url):
    """
    Helper function that extracts full filename from the url path.
    :param url: -> str, url to the file.
    :return: -> str, filename with extension.
    """
    filename = get_paths_normalized_basename(url)
    return filename


def set_folder_name_based_on_url(url):
    """
    Helper function that sets folder name based on URL input.
    :param url: str, url to the file.
    :return: str -> folder name.
    """
    filename = url_extract_filename(url)
    if '.' in filename:
        folder = os.path.splitext(filename)[0]
    else:
        folder = None
    return folder


def print_warning():
    """
    Helper function that prints out warnings to the user.
    """
    print('Folder with data was not found in the current directory.')
    print('Please explicitly provide source of data.')
    print('Use --help flag to get more info.')


def load_config_from_path(path, country):
    """
    Helper function that loads config based on the given country name.
    :param path: str -> path to the general config.
    :param country: str -> name of the country.
    :return: str -> name of a country-specific configfile.
    """
    with open(path) as file:
        country_cfg = yaml.load(file, Loader=yaml.FullLoader)
        country = country.upper()
        configfile = country_cfg['lpis_countries'].get(country)
        print(f'INFO: Loading data from {configfile}...')
        return configfile


def remove_duplicated_lines_from_dump(input_path, output_path, logger):
    """
    Helper function that opens a dump file and remove duplicates to save it in the new form afterwards.
    :param input_path: str -> path to the input dump file.
    :param output_path: str -> path for the new dump file that will be generated.
    :param logger: logger instance -> logger from external module that will be used for
    storing action logs.
    """
    unique_lines = set()
    with open(input_path, 'r') as f:
        with open(output_path, 'w') as o:
            for line in f:
                if line not in unique_lines:
                    o.write(line)
                    unique_lines.add(line)
                else:
                    filename = get_paths_normalized_basename(input_path)
                    warning = f'Duplicated line in file {filename}: {line}'
                    logger.info(warning)


def cleaning_preexisting_dir():
    """
    Helper function that takes care of cleaning data from the previous Pipeline runs.
    """
    if os.path.isdir('results'):
        for entity in os.listdir('results'):
            entity_path = os.path.join('results', entity)
            if os.path.isdir(entity_path):
                shutil.rmtree(entity_path)
            elif os.path.isfile(entity_path):
                os.remove(entity_path)
            else:
                print(f"An error occurred. {entity} can't be recognized as directory or file!")


def clean_scripts_directory(results_dir):
    """
    :param results_dir: str -> name of the directory containing results.
    Function that is taking care of clearing all the files created throughout the pipeline run.
    """
    print('INFO: Running the cleaning script. All files generated by the Pipeline will be removed'
          ' from the current directory.')
    shutil.rmtree(os.path.join(results_dir))
    for file in os.listdir('temp'):
        if file.endswith('.sh'):
            os.remove(os.path.join('temp', file))
    print('*************************************************************')
    print('Finished!')


def generic_pipeline_validator(stages):
    """
    Function that is validating if processes passed by the user are valid or not.
    :param stages: tuple -> process or processes chosen by the user in the CLI.
    :return: list -> list of processes that should be executed.
    """
    stages_in_sequence = ['link', 'load', 'postprocess', 'transform', 'mapping', 'preprocess', 'fetch']
    optional_stages = ['postprocess', 'preprocess', 'mapping']
    stages_no_duplicates = set(stages)
    new_stages = []
    if len(stages_no_duplicates) == 1:
        return list(stages_no_duplicates)
    else:
        for stage in stages_in_sequence:
            if len(new_stages) == len(stages_no_duplicates):
                return new_stages
            if stage in stages_no_duplicates:
                new_stages.append(stage)
            else:
                if not len(new_stages) == 0:
                    if stage not in optional_stages:
                        print(f"Illegal usage! With a set of processes that were chosen the {stage} process"
                              f" can not be omitted.")
                        return None
        return new_stages


def identify_delimiter(csv_file):
    """
    Function that uses CSV sniffer to detect delimiter in CSV file.
    :param csv_file: str -> path to the CSV file.
    :return: str -> delimiter.
    """
    with open(csv_file, 'r') as f:
        dialect = csv.Sniffer().sniff(f.readline())
        return dialect.delimiter


def parse_config_value(value):
    """
    Function that uses regex to parse value from a config entry.
    :param value: str -> config entry.
    :return: str -> parsed value.
    """
    return re.split("[|]", value)[0]


def match_datatype(val):
    """
    Function that matches appropriate XSD datatype to a given string.
    :param val: str -> value based on datatype will be derived.
    :return: XSD datatype object.
    """
    val = val.strip("<>")
    val = val.split(":")[-1]
    datatype = XSD_dict.get(val, None)
    return datatype


def match_predicate_with_datatype(value):
    """
    Function that matches appropriate datatype with a predicate based on given value.
    :param value: str -> input value from which datatype and predicate are derived.
    :return: tuple -> URIRef with a predicate, datatype.
    """
    if value.startswith("http"):
        return tuple((rdflib.term.URIRef('http://www.w3.org/ns/r2rml#termType'),
                      rdflib.term.URIRef('http://www.w3.org/ns/r2rml#IRI')))
    else:
        val = re.split("[|]", value)
        if len(val) > 1:
            string = val[-1]
            datatype = match_datatype(val=string)
            return tuple((rdflib.term.URIRef('http://www.w3.org/ns/r2rml#datatype'), datatype))
        else:
            # we are changing the default behaviour, it will be treated as IRI if no datatype provided
            return tuple((rdflib.term.URIRef('http://www.w3.org/ns/r2rml#termType'),
                          rdflib.term.URIRef('http://www.w3.org/ns/r2rml#IRI')))


def parse_complex_name_from_template(template_uri, template_id):
    """
    Function that parses template name from a secondary type.
    :param template_uri: str -> template uri.
    :param template_id: str -> template value.
    :return: str -> template name.
    """
    try:
        return template_uri.split(template_id)[1].split("/")[-1]
    except IndexError:
        return template_uri.split("/")[-1]


def generate_missing_uri(base_uri, template_id, key):
    """
    Function that generates URI based on the config file in case it was not explicitly provided.
    :param base_uri: str -> base uri from config.
    :param template_id: str -> template id from config.
    :param key: str -> respective key in the yaml config.
    :return: str -> URI value.
    """
    generated_uri = base_uri + "/" + template_id + "/" + key
    return generated_uri


def perform_standard_postprocessing(input_path, output_path, logger):
    """
    Helper function for post-processing dumps.
    :param input_path: str -> full path to the input_file.
    :param output_path: str -> full path to the output_file.
    :param logger: logger instance -> logger from external module that will be used for
    storing action logs.
    """
    regex_pattern = re.compile(r"\w{3}\s\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}\s\w+\s+\d{4}")
    with open(input_path, 'r') as f:
        with open(output_path, 'w') as o:
            for line in f:
                potential_datetime = regex_pattern.findall(line)
                if "<http://www.opengis.net/def/crs/EPSG/0/4258>" in line:
                    new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4258> ", "")
                    o.write(new_line)
                    logger.info(f"{line} was changed in the post-processing stage!")
                elif "<http://www.opengis.net/def/crs/EPSG/0/4326>" in line:
                    new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4326> ", "")
                    o.write(new_line)
                    logger.info(f"{line} was changed in the post-processing stage!")
                elif potential_datetime:
                    if len(potential_datetime) == 1:
                        datetime_match = potential_datetime[0]
                        parsed_datetime = dateutil.parser.parse(datetime_match)
                        converted_datetime = parsed_datetime.strftime("%Y-%m-%d")
                        new_line = line.replace(datetime_match, converted_datetime)
                        o.write(new_line)
                        logger.info(f"{line} was changed in the post-processing stage!")
                    else:
                        logger.info(f"WARNING: The following line consists potentially of more than one"
                                    f" match for the datetime object!         {line}")
                        o.write(line)
                else:
                    o.write(line)


def is_valid_zip(path_to_file):
    """
    Helper function for checking if file is a legit zip archive.
    :param path_to_file: str -> path to the file.
    :return: boolean -> True if file is a zip archive, False otherwise.
    """
    return zipfile.is_zipfile(path_to_file)


def extract_zip_with_delete(path_to_zip, extract_to):
    """
    Helper function for extracting a zip file into directory and removing the archive afterwards.
    :param path_to_zip: str -> path to the zip archive.
    :param extract_to: str -> directory where files should be extracted to.
    """
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(path_to_zip)


def copy_dir(from_dir, to_dir):
    """
    Helper function for copying the whole folder into another one.
    :param from_dir: str -> directory that will be copied.
    :param to_dir: str -> target directory.
    """
    copy_tree(from_dir, to_dir)


def get_paths_normalized_basename(path):
    """
    Function that extracts basename from a path using normalized path to avoid differences between cause by trailing
    slash at the end.
    """
    return os.path.basename(os.path.normpath(path))


def open_context_url(link):
    """
    Function that loads data from jsonld url into python object
    """
    try:
        with urllib.request.urlopen(link) as url:
            data = json.load(url)
            return data
    except URLError:
        print("Opening context file failed! URL for jsonld is incorrect or missing!")
        return None


class InvalidURIRef(Exception):
    """Raise when URIs are invalid."""
    pass


def validate_uriref(uri_candid):
    """
    Helper function for validating uriref value candidate.
    """
    if _is_valid_uri(uri_candid):
        return True
    raise InvalidURIRef(f"Aborting... Config value for {uri_candid} does not look like legit value that can be "
                        f"properly serialized as URIRef! Please remove illegal characters and run the process again!")


def change_field_value_in_json_and_save_file(path_to_input_json, field_name, field_value):
    """
    Helper function for adjusting value related to specific field and saving file afterwards.
    :param path_to_input_json -> str
    :param field_name -> str
    :param field_value -> str
    """
    temp_file = "temp.json"
    with open(path_to_input_json, 'r') as f:
        with open(temp_file, 'w') as f2:
            data = json.load(f)
            data[field_name] = field_value
            f2.write(json.dumps(data))
    os.remove(path_to_input_json)
    os.rename(temp_file, path_to_input_json)


def is_key_enum_entry(key):
    """
    Function that checks if key in the dictionary was created as a product of adjusting enumerator from user's input.
    """
    v = key.split("_")
    try:
        v2 = int(v[-1])
        if v2:
            return True
    except ValueError:
        return False


def is_it_enum(key):
    """
    Function that checks if specific key is in fact an enumerator.
    """
    if key.startswith('@'):
        # grab value following special character and evaluate if it can be converted to int
        to_eval = key.split("@")[-1]
        try:
            int(to_eval)
            return True
        except ValueError as e:
            return False
    else:
        return False


def replace_expression(input_path, output_path, to_be_replaced, replacement, logger):
    """
    Function for replacing expressions.
    """
    logger.info(f"{to_be_replaced=}")
    logger.info(f"{replacement=}")
    # raw_tbr = repr(to_be_replaced)[1:-1]
    # raw_rep = repr(replacement)[1:-1]
    # logger.info(f"{raw_tbr=}")
    # logger.info(f"{raw_rep=}")
    with open(input_path, 'r', encoding="utf-8") as f:
        file_content = f.read()
        file_content = re.sub(to_be_replaced, replacement, file_content)
    with open(output_path, 'w', encoding="utf-8") as f2:
        f2.write(file_content)


def remove_line_based_on_string(input_path, output_path, target_string, logger):
    """
    Function for removing line based on string.
    """
    with open(input_path, 'r') as f:
        with open(output_path, 'w') as o:
            for line in f:
                if target_string in line:
                    logger.info(f"{line} was removed in the post-processing stage!")
                else:
                    o.write(line)


# def convert_encoding(input_path, output_path, target_encoding, logger):
#     """
#     Function that changes file encoding.
#     """
#     logger.info(f"{target_encoding=}")
#     with open(input_path, 'rb') as src:
#         binary_data = src.read()
#         decoded_data = binary_data.decode(target_encoding, errors="ignore")
#     with open(output_path, 'w', encoding=target_encoding) as target:
#         target.write(decoded_data)

# def convert_encoding(input_path, output_path, target_encoding, source_encoding, logger):
#     """
#     Function that changes file encoding.
#     """
#     logger.info(f"{target_encoding=}")
#     if not source_encoding:
#         source_encoding = predict_encoding(input_path)
#     logger.info(f"{source_encoding=}")
#     with open(input_path, 'r', encoding=source_encoding) as src:
#         content = src.read()
#     with open(output_path, 'w', encoding=target_encoding) as target:
#         try:
#             target.write(content)
#         except UnicodeEncodeError as e:
#             print(f"Error writing the file with encoding {target_encoding}: {e}")

def convert_encoding(input_path, output_path, target_encoding, source_encoding, logger):
    """
    Function that changes file encoding.
    """
    logger.info(f"{target_encoding=}")
    if not source_encoding:
        source_encoding = predict_encoding(input_path)
    logger.info(f"{source_encoding=}")
    with open(input_path, 'r') as src:
        content = src.read()
        decoded_content = content.encode(source_encoding).decode('unicode_escape')
        try:
            target_content = decoded_content.encode(source_encoding).decode(target_encoding, "strict")
        except UnicodeEncodeError as e:
            print(f"Something went wrong with decoding {input_path} into {target_encoding}:{e}")

    with open(output_path, 'w', encoding=target_encoding) as target:
        try:
            target.write(target_content)
        except UnicodeEncodeError as e:
            print(f"Error writing the file with encoding {target_encoding}: {e}")

# def convert_encoding(input_path, output_path, target_encoding, source_encoding, logger):
#     """
#     Function that changes file encoding.
#     """
#     logger.info(f"{target_encoding=}")
#     if not source_encoding:
#         source_encoding = predict_encoding(input_path)
#     logger.info(f"{source_encoding=}")
#     with codecs.open(input_path, 'r', 'unicode_escape') as src:
#         content = src.read()
#         # decoded_content = content.encode(source_encoding).decode('unicode_escape')
#         # try:
#         #     target_content = decoded_content.encode(source_encoding).decode(target_encoding, "strict")
#         # except UnicodeEncodeError as e:
#         #     print(f"Something went wrong with decoding {input_path} into {target_encoding}:{e}")
#
#     with open(output_path, 'w', encoding=target_encoding) as target:
#         try:
#             target.write(content)
#         except UnicodeEncodeError as e:
#             print(f"Error writing the file with encoding {target_encoding}: {e}")


def predict_encoding(file_path, n_lines=20):
    """
    Predict a file's encoding using chardet
    """
    with open(file_path, 'rb') as f:
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
    return chardet.detect(rawdata)['encoding']


def adjust_crs(input_path, output_path, logger, crs=DEFAULT_CRS):
    """
    Function for adjusting crs in Shapefile.
    """
    logger.info(f"{input_path=}")
    logger.info(f"{output_path=}")
    logger.info(f"{crs=}")
    gdf = gpd.read_file(input_path)
    logger.info(f"{gdf.crs=}")
    gdf2 = gdf.to_crs(crs=crs)
    logger.info(f"{gdf2.crs=}")
    gdf2.to_file(driver="ESRI Shapefile", filename=output_path)
