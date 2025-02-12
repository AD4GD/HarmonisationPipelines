from modules.lpis_web_zip import lpis_web_zip
from modules.lpis_mappings import lpis_mappings
from modules.lpis_transform import lpis_transform
from modules.lpis_postprocessing import lpis_postprocessing
from modules.lpis_loader import lpis_loader


def building_lpis_fetch(pipe, url, output_dir):
    """
    Function that builds LPIS Pipeline for the fetching data stage.
    :param pipe: Pipeline instace.
    :param url: str -> data url.
    :param output_dir: str -> name for the output directory.
    """
    webzip = lpis_web_zip.LpisWebZip(url=url, result_dir=output_dir)
    pipe.append_actions(webzip.create_main_dir_for_storing_results)
    pipe.append_actions(webzip.set_destination_path)
    pipe.append_actions(webzip.fetch_data)
    pipe.append_actions(webzip.remove_zip)


def building_lpis_mappings(pipe, output_dir, configfile, data_dir=None):
    """
    Function that builds LPIS Pipeline for the generation of mappings stage.
    :param pipe: Pipeline instance.
    :param output_dir: str -> name for the output directory.
    :param configfile: str -> name of the config file.
    :param data_dir: str -> data directory.
    """
    mapper = lpis_mappings.LpisMappings(configfile=configfile, results_dir=output_dir)
    if data_dir:
        mapper.folder = data_dir
    pipe.append_actions(mapper.create_main_dir_for_storing_results)
    pipe.append_actions(mapper.set_destination_path)
    pipe.append_actions(mapper.copy_folder_to_destination)
    pipe.append_actions(mapper.create_list_of_input_files)
    pipe.append_actions(mapper.load_from_config)
    pipe.append_actions(mapper.create_mapping)


def building_lpis_transform(pipe, output_dir, data_dir=None):
    """
    Function that builds LPIS Pipeline for the transformation stage.
    :param pipe: Pipeline instance.
    :param output_dir: str -> name for the output directory.
    :param data_dir: str -> data directory.
    """
    transformer = lpis_transform.LpisTransform(results_dir=output_dir)
    if data_dir:
        transformer.folder = data_dir
    pipe.append_actions(transformer.create_main_dir_for_storing_results)
    pipe.append_actions(transformer.set_destination_path)
    pipe.append_actions(transformer.run_transformer)


def building_lpis_postprocess(pipe, output_dir, configfile):
    """
    Function that builds LPIS Pipeline for the post-processing stage.
    :param pipe: Pipeline instance.
    :param output_dir: str -> name for the output directory.
    :param configfile: str -> name of the config file.
    """
    postprocessor = lpis_postprocessing.LpisPostProcessor(configfile=configfile, results_dir=output_dir)
    pipe.append_actions(postprocessor.run_postprocessor)
    pipe.append_actions(postprocessor.clean_directories)


def building_lpis_loader(pipe, configfile, uri, output_dir, remove_target_graph, graph_per_dump, path=None):
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
    loader = lpis_loader.LpisLoader(uri=uri, config=configfile, results_dir=output_dir)
    if graph_per_dump:
        loader.graph_per_dump = True
    if remove_target_graph:
        loader.remove_target_graph = True
    if path:
        loader.dumps_dir = path
    pipe.append_actions(loader.run_vto_loader)
