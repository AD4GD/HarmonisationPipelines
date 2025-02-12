import os

os.makedirs("logs", exist_ok=True)   # creating dir for logger
os.makedirs("temp", exist_ok=True)   # creating dir for temporary files

import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup, RequiredMutuallyExclusiveOptionGroup

# changing the current working directory to avoid errors when script is invoked
# from a different directory.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from modules.fadn_builder import fadn_builder
from modules.generic_builder import generic_builder
from modules.lpis_builder import lpis_builder
from modules.click_customs import ClickIf
from modules.dictionaries import dictionaries
from modules.utils.utils import generic_pipeline_validator
from modules.settings import YARRML_SUPPORTED_DATA_TYPES
from modules._version import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """
    Linked Data Pipeline CLI
    """
    pass


@cli.command()
@click.option('-s', '--stage', help='Runs the whole fadn_pipeline or a single fadn_pipeline stage.',
              type=click.Choice(['all', 'fetch', 'preprocess', 'mapping', 'transform', 'postprocess'],
                                case_sensitive=False), required=True)
@click.option('-u', '--graph_uri', help="Graph's URI that will be used to load dumps into the database. Required when"
                                        " --stage is set to all",
              type=str, cls=ClickIf.FadnOptionRequiredIf)
@click.option('-gpd', '--graph_per_dump', is_flag=True,
              help="Treats -u/--graph_uri as base that will be extended with the dump name for each load."
                   " Optional when --stage is set to all.")
@click.option('-rg', '--reload_graph', is_flag=True,
              help="Removes target graph before loading dumps into the database. Optional when"
                   " --stage is set to all")
@optgroup.group('Input data sources', cls=MutuallyExclusiveOptionGroup,
                help='The source of the input data. The default, '
                     'if neither option is used, is the fadn folder in the current directory.')
@optgroup.option('-ui', '--url_input',
                 help='URL to the zip file with input file package. '
                      'Required when --stage=fetch. Optional in all other cases.',
                 type=str)
@optgroup.option('-di', '--dir_input', help='Directory containing input files.',
                 type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-o', '--output', help='Output folder name. Optional.',
              type=click.Path(exists=False, file_okay=False, dir_okay=True), default="results",
              show_default=True)
@click.option('-c', '--clean', is_flag=True,
              help="Removes all files generated throughout the run of the full pipeline. Optional"
                   " when --stage is set to all.")
def fadn(**kwargs):
    """
    Function that initializes FADN Pipeline.
    """
    illegal_dir_names = dictionaries.illegal_dir_names
    if kwargs['stage'] != "all" and kwargs['reload_graph']:
        print('Illegal usage! -rg/--reload_graph is available only when'
              ' --stage=all.')
        return
    if kwargs['stage'] == 'fetch' and not kwargs['url_input']:
        print('Data URL is mandatory with the chosen Pipeline stage! Please provide URL'
              ' by setting -ui/--url_input flag to the URL value!')
        return
    if kwargs['stage'] != "all" and kwargs['graph_per_dump']:
        print('Illegal usage! -gpd/--graph_per_dump is available only when'
              ' --stage=all.')
        return
    if kwargs['stage'] != "all" and kwargs['clean']:
        print('Illegal usage! -c/--clean flag is available only when --stage=all.')
        return
    if kwargs['dir_input'] in illegal_dir_names:
        print('Please change your value of dir_input. The one you used is prohibited!')
        return
    fadn_builder.fadn_pipeline_builder(**kwargs)


@cli.command()
@click.option('-p', '--process', help='Runs a single process from the generic Pipeline. Can be used'
                                      ' multiple times to evoke set of tasks.',
              type=click.Choice(['preprocess', 'mapping', 'transform', 'postprocess', 'load', 'link'],
                                case_sensitive=False), required=True, multiple=True)
@click.option('-u', '--graph_uri', help="Graph's URI. Required when using load process.",
              type=str, cls=ClickIf.GenericGraphUriOptionRequiredIf)
@optgroup.group('Input data sources', cls=RequiredMutuallyExclusiveOptionGroup,
                help='The source of the input data.')
@optgroup.option('-ui', '--url_input',
                 help='URL to the input zip file package.',
                 type=str)
@optgroup.option('-di', '--dir_input', help='Directory containing input files.',
                 type=click.Path(exists=True, file_okay=False, dir_okay=True))
@optgroup.option('-db', '--db_input', help='Flag indicating database input. Details are provided through'
                                           ' cfg/config.yaml by updating sql_cfg section.', is_flag=True)
@click.option('-o', '--output', help='Output folder name. Optional. !!!WARNING!!! if directory already exist the '
                                     'content of it will be erased before pipeline execution. Select your output path '
                                     'with caution! ',
              type=click.Path(exists=False, file_okay=False, dir_okay=True), default="results",
              show_default=True)
@click.option('-it', '--input_type', help='Type of input data that has to be transformed. Required if'
                                          ' process is transform, mapping or preprocess. '
                                          'WARNING: this option is case sensitive!',
              type=click.Choice(['Shapefile', 'GML', 'KML', 'GeoJson', 'CSV', 'JSON', 'XML', 'DB', 'netCDF', 'CSVW'],
                                case_sensitive=True), cls=ClickIf.GenericInputTypeOptionRequiredIf)
@click.option('-mi', '--mapping_input', help='Input path to the mapping directory. Required when '
                                             'process is transform and there is no preceding mapping process.',
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              cls=ClickIf.GenericMappingInputDirOptionRequiredIf)
@click.option('-mu', '--mapping_url', help='Input mapping as URL to a zip package '
                                           '(works only with data provided as url_input).'
                                           ' Required when '
                                           'process is transform and there is no preceding mapping process.',
              type=str,
              cls=ClickIf.GenericMappingInputUrlOptionRequiredIf)
@click.option('-bu', '--base_uri', help='Base URI. Required with mapping process and transform '
                                        'when processing shapefiles.', type=str,
              cls=ClickIf.GenericBaseUriOptionRequiredIf)
@click.option('-gpd', '--graph_per_dump', is_flag=True,
              help="Treats -u/--graph_uri as base that will be extended with the dump name for each load."
                   " Optional when --process is set to load.")
@click.option('-rg', '--reload_graph', is_flag=True,
              help="Removes target graph before loading dumps into the database. Optional when"
                   " --process is set to load.")
@click.option('-ppa', '--preprocess_activity', help='List of available methods to choose from for the '
                                                    'preprocessing part of the Pipeline. Required with --'
                                                    'process=preprocess. unzip_multiple_archives works '
                                                    'for every input type. add_seq_col and normalize_delimiter are'
                                                    'consequential only for CSV input type, to_crs works '
                                                    'only with Shapefiles and add_enum is somewhat equivalent to '
                                                    'add_seq_col but works for json files.',
              type=click.Choice(['add_seq_col', 'unzip_multiple_archives', 'normalize_delimiter', 'to_crs', 'add_enum'],
                                case_sensitive=False), multiple=True)
@click.option('-ttl', '--to_ttl', is_flag=True,
              help="Converts output from n-triples to turtle as a part of post-processing. Available only"
                   " with post-processing.",
              default=False)
@click.option('-re', '--replace_expression', nargs=2, type=str, help="Replaces all occurrences of X with Y as a "
                                                                     "part of additional dump postprocessing. Optional "
                                                                     "when process is set to postprocess. Regular "
                                                                     "expression patterns are accepted but they need"
                                                                     "to be properly escaped!")
@click.option('-rl', '--remove_line', type=str, help="Removes every line containing provided string in the "
                                                     "of dump file. Optional when process=postprocess")
@click.option('-te', '--target_encoding', help='Desired encoding for output dump. '
                                               'Optional when process is set to postprocess.', type=str)
@click.option('-se', '--source_encoding', help='Encoding of a source file. Optional when --target_encoding is provided.'
                                               ' if source encoding was not provided program will try to make an '
                                               'educated guess on the source encoding.', type=str,
              required=False)
@click.option('-fc', '--from_config', default=False, is_flag=True,
              help="Flag indicating that the mapping should be generated based on the config"
                   "file (Supports Shapefiles and CSV). Optional when"
                   " --process is set to mapping.")
@click.option('-fcv', '--from_config_value', required=False,
              help="Alternative path to the config file for generating a custom mapping.",
              default=os.path.join("cfg", "GENERIC", "generic_cfg.yaml"),
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              show_default=True)
@click.option('-sq', '--sparql_query', required=False,
              help="Uses a SPARQL query as a mapping to produce dumps. Query file should be provided "
                   "like the regular mapping either through --mapping_input or --mapping_url. Can be used only"
                   " with a transform process.",
              is_flag=True)
@click.option('-yrv', '--yarrrml_rules_value', required=False,
              help="Path to YAML containing all the rules for mapping generation using YARRRML tool.",
              type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-yru', '--yarrrml_rules_url', required=False,
              help="URL to zip package containing YAML file with rules for mapping generation using YARRRML tool.",
              type=str)
@click.option('-c', '--clean', is_flag=True,
              help="Removes all files generated throughout the run of the full pipeline. Optional"
                   " when --process=load.")
def generic(**kwargs):
    """
    Function that initializes Generic Pipeline.
    """
    if kwargs['dir_input'] == kwargs['output']:
        print('Illegal usage! dir_input value has to be different than output!')
        return
    if "mapping" not in kwargs['process'] and (kwargs['yarrrml_rules_value'] or kwargs['yarrrml_rules_url']):
        print('Illegal usage! -yrv/--yarrrml_rules_value is available only when --process=mapping .')
        return
    if (kwargs['yarrrml_rules_value'] or kwargs['yarrrml_rules_url']) and kwargs['input_type'] not in \
            YARRML_SUPPORTED_DATA_TYPES:
        print(f'Sorry, Yarrml mapping generation supports only following types od data: {YARRML_SUPPORTED_DATA_TYPES}!')
        return
    if "mapping" not in kwargs['process'] and kwargs['from_config']:
        print('Illegal usage! -fc/--from_config is available only when --process=mapping .')
        return
    if "load" not in kwargs['process'] and kwargs['clean']:
        print('Illegal usage! -c/--clean flag is available only when --process=load.')
        return
    if kwargs['from_config'] and kwargs['input_type'] not in ["Shapefile", "CSV", "netCDF"]:
        print('Sorry, from_config option is currently supporting only Shapefile, CSV and netCDF input type!')
        return
    if "load" not in kwargs['process'] and kwargs['reload_graph']:
        print('Illegal usage! -rg/--reload_graph is available only when'
              ' --process=load .')
        return
    if "load" not in kwargs['process'] and kwargs['graph_per_dump']:
        print('Illegal usage! -gpd/--graph_per_dump is available only when'
              ' --process=load .')
        return
    if "mapping" not in kwargs['process'] and "transform" not in kwargs['process'] and kwargs['base_uri']:
        print('Illegal usage! -bu/--base_uri is available only when'
              ' --process=mapping or --process=transform.')
        return
    if "preprocess" in kwargs['process'] and not kwargs['preprocess_activity']:
        print('Illegal usage! Preprocess_activity has to be chosen when --process=preprocess!')
        return
    if "preprocess" in kwargs['process'] and kwargs['db_input']:
        print("Illegal usage! Preprocessing is not supported when input data comes from the relational database.")
        return
    if kwargs['db_input'] and 'mapping' not in kwargs['process'] \
            and not any([kwargs['mapping_url'], kwargs['mapping_input']]):
        print("Either url or directory with existing mapping is required to make a transformation from the database!")
        return
    if kwargs['sparql_query'] and 'transform' not in kwargs['process']:
        print("Illegal usage! Transform has to be a process in order to use sparql_query flag!")
        return
    if kwargs['sparql_query'] and 'mapping' in kwargs['process']:
        print("Illegal usage! Mapping can not be used with sparql_query flag. One either wants to generate a "
              "regular mapping or create it from a sparql query!")
        return
    if kwargs['sparql_query'] and kwargs['input_type'] not in ["CSV", "netCDF"]:
        print("Illegal usage! Sparql_query flag supports only CSV and netCDF input type!")
        return
    if kwargs['to_ttl'] and 'postprocess' not in kwargs['process']:
        print("Illegal usage! to_ttl flag can be used only whe post-processing was chosen!")
        return
    if kwargs['replace_expression'] and 'postprocess' not in kwargs['process']:
        print("Illegal usage! replace_expression option can be used only whe post-processing was chosen!")
        return
    if kwargs['remove_line'] and 'postprocess' not in kwargs['process']:
        print("Illegal usage! remove_line option can be used only whe post-processing was chosen!")
        return
    if kwargs['target_encoding'] and 'postprocess' not in kwargs['process']:
        print("Illegal usage! target_encoding option can be used only whe post-processing was chosen!")
        return
    if 'link' in kwargs['process'] and len(kwargs['process']) > 1:
        print("Illegal usage! link can't be chained with other processes, please proceed with separated job.")
        return
    if kwargs['source_encoding'] and not kwargs['target_encoding']:
        print("Illegal usage! source_encoding is available only in combination with target_encoding!")
        return
    stages = generic_pipeline_validator(kwargs['process'])
    # this part allows treating netcdf conversion as a pre-processing step that is completely hidden from the user
    if kwargs["input_type"] == "netCDF":
        stages.append("preprocess")
        kwargs["preprocess_activity"] = (*kwargs["preprocess_activity"], "convert_netcdf_to_csv")
        kwargs["input_type"] = "CSV"
    if not stages:
        return
    generic_builder.generic_pipeline_builder(stages=stages, **kwargs)


@cli.command()
@click.option('-s', '--stage', help='Runs the whole LPIS Pipeline or a single LPIS Pipeline stage.',
              type=click.Choice(['all', 'fetch', 'mapping', 'transform', 'postprocess'],
                                case_sensitive=False), required=True)
@click.option('-u', '--graph_uri', help="Graph's URI that will be used to load dumps into the database. "
                                        "Required when --stage is set to all.",
              type=str, cls=ClickIf.LpisOptionRequiredIf)
@click.option('-gpd', '--graph_per_dump', is_flag=True,
              help="Treats -u/--graph_uri as base that will be extended with the dump name for each load."
                   " Optional when --stage is set to all.")
@click.option('-rg', '--reload_graph', is_flag=True,
              help="Removes target graph before loading dumps into the database. Optional when"
                   " --stage is set to all")
@optgroup.group('Input data sources', cls=MutuallyExclusiveOptionGroup,
                help='The source of the input data. The default, '
                     'if neither option is used, is the current directory.')
@optgroup.option('-ui', '--url_input',
                 help='URL to the zip file with input file package. '
                      'The file is unpacked and the directory traversed to find all existing shapefiles. '
                 'Required when --stage=fetch.',
                 type=str)
@optgroup.option('-di', '--dir_input', help='Directory containing input data. '
                                            'The the directory is traversed to find all existing shapefiles.',
                 type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-o', '--output', help='Output folder name. Optional.',
              type=click.Path(exists=False, file_okay=False, dir_okay=True), default="results",
              show_default=True)
@click.option('-cn', '--country', help='Mappings will be generated for a specific country that was'
                                       ' chosen from the list. Required when --stage=all, mapping, transform'
                                       'or postprocess.',
              type=click.Choice(['other', 'spain', 'poland', 'lithuania'], case_sensitive=False),
              cls=ClickIf.LpisCountryOptionRequiredIf)
@click.option('-c', '--clean', is_flag=True,
              help="Removes all files generated throughout the run of the full pipeline. Optional"
                   " when --stage is set to all.")
def lpis(**kwargs):
    """
    Function that initializes LPIS Pipeline.
    """
    illegal_dir_names = dictionaries.illegal_dir_names
    if kwargs['stage'] == 'fetch' and not kwargs['url_input']:
        print('Data URL is mandatory with the chosen Pipeline stage! Please provide URL'
              ' by setting -ui/--url_input flag to the URL value!')
        return
    if kwargs['stage'] != "all" and kwargs['clean']:
        print('Illegal usage! -c/--clean flag is available only when --stage=all.')
        return
    if kwargs['dir_input'] in illegal_dir_names:
        print('Please change your value of dir_input. The one you used is prohibited!')
        return
    if kwargs['stage'] != "all" and kwargs['reload_graph']:
        print('Illegal usage! -rg/--reload_graph is available only when'
              ' --stage=all.')
        return
    if kwargs['stage'] != "all" and kwargs['graph_per_dump']:
        print('Illegal usage! -gpd/--graph_per_dump is available only when'
              ' --stage=all.')
        return
    lpis_builder.lpis_pipeline_builder(**kwargs)


if __name__ == '__main__':
    cli()
