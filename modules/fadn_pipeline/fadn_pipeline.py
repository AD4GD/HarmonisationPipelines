from modules.fadn_web_zip import fadn_web_zip
from modules.fadn_csv import fadn_csv
from modules.fadn_mappings import fadn_mappings
from modules.fadn_transform import fadn_transform
from modules.fadn_postprocessing import fadn_postprocessing
from modules.fadn_loader.fadn_loader import FadnLoader


def building_webzip(pipe, url, output_dir):
    """
    Function that builds a part of the Pipeline that is responsible for initial handling
    of a zip file containing data.
    :param pipe: Pipeline Class instance.
    :param url: str -> url to the zip file containing data.
    :param output_dir: str -> name for the output directory.
    """
    webzip = fadn_web_zip.WebZip(url=url, results_dir=output_dir)
    pipe.append_actions(webzip.create_main_dir_for_storing_results)
    pipe.append_actions(webzip.set_folder_name)
    pipe.append_actions(webzip.set_destination_path)
    pipe.append_actions(webzip.fetch_data)
    pipe.append_actions(webzip.unpack_all_packages)


def building_csv(pipe, path, output_dir, url='Unknown'):
    """
    Function that builds a part of the Pipeline that is responsible for transformation
    and creation of pre-processed csv file and auxiliary csv files.
    :param pipe: Pipeline Class instance.
    :param path: str -> folder containing data.
    :param output_dir: str -> name for the output directory.
    :param url: str -> optional, url to the source file.
    """
    fadncsv = fadn_csv.FadnCsv(url=url, results_dir=output_dir)
    fadncsv.folder = path   # setting up path to the directory that contains data.
    pipe.append_actions(fadncsv.create_main_dir_for_storing_results)
    pipe.append_actions(fadncsv.set_destination_path)
    pipe.append_actions(fadncsv.copy_folder_to_destination)
    pipe.append_actions(fadncsv.organize_fadn_folder)
    pipe.append_actions(fadncsv.organize_fadn_directories)
    pipe.append_actions(fadncsv.typos_correction)
    pipe.append_actions(fadncsv.preprocess_all_packages)
    pipe.append_actions(fadncsv.create_auxiliary_csv_files)


def building_mappings(pipe, path, output_dir):
    """
    Function that builds a part of the Pipeline that is responsible for creation of all
    mappings.
    :param pipe: Pipeline Class instance.
    :param path: str -> name of the data directory that contains all necessary csv files.
    :param output_dir: str -> name for the output directory.
    """
    fadnmap = fadn_mappings.FadnMapping(results_dir=output_dir)
    fadnmap.folder = path   # setting up path to the directory that contains data.
    pipe.append_actions(fadnmap.create_main_dir_for_storing_results)
    pipe.append_actions(fadnmap.set_destination_path)
    pipe.append_actions(fadnmap.create_mapping)


def building_transformer(pipe, path, output_dir, duplicates_aid=False):
    """
    Function that builds a part of the Pipeline that is responsible for creating dump files.
    :param pipe: Pipeline Class instance.
    :param path: str -> directory containing mappings.
    :param output_dir: str -> name for the output directory.
    :param duplicates_aid: boolean -> if True duplicates will be handled by the external
    transformer tool, otherwise Python will take care of them using internal methods.
    """
    if duplicates_aid:
        transformer = fadn_transform.FadnTransform(results_dir=output_dir, rml_duplicates=True)
    else:
        transformer = fadn_transform.FadnTransform(results_dir=output_dir, rml_duplicates=False)
    transformer.folder = path   # setting up path to the directory that contains data.
    pipe.append_actions(transformer.create_main_dir_for_storing_results)
    pipe.append_actions(transformer.set_destination_path)
    pipe.append_actions(transformer.move_content)
    pipe.append_actions(transformer.run_transformer)


def building_postprocessor(pipe, output_dir, handling_duplicates=True):
    """
    Function that builds a part of the Pipeline that is responsible for postprocessing
    actions on the dump files.
    :param pipe: Pipeline Class instance.
    :param output_dir: str -> name for the output directory.
    :param handling_duplicates: -> boolean -> if true the duplicates will be removed.
    """
    if handling_duplicates:
        postprocessor = fadn_postprocessing.FadnPostProcessor(handling_duplicates=True, results_dir=output_dir)
    else:
        postprocessor = fadn_postprocessing.FadnPostProcessor(handling_duplicates=False, results_dir=output_dir)
    pipe.append_actions(postprocessor.run_postprocessor)
    pipe.append_actions(postprocessor.clean_directories)


def building_loader(pipe, configfile, uri, output_dir, remove_target_graph, graph_per_dump, path=None):
    """
    Function that builds a part of the Pipeline that is responsible for loading dumps into Virtuoso database.
    :param pipe: Pipeline Class instance.
    :param path: str -> directory that contains dumps.
    :param configfile: str -> name of the configuration file that will be used within this vto_loader.
    :param uri: str -> graph's URI.
    :param output_dir: str -> name for the output directory.
    :param remove_target_graph: boolean -> if True, the vto_loader will clear graph before loading the data.
    :param graph_per_dump: boolean -> if True Graph's URI will be used as a base (prefix)
    to which the dump name is appended.
    """
    loader = FadnLoader(uri=uri, results_dir=output_dir, config=configfile)
    if graph_per_dump:
        loader.graph_per_dump = True
    if remove_target_graph:
        loader.remove_target_graph = True
    if path:
        loader.dumps_dir = path
    pipe.append_actions(loader.run_vto_loader)
