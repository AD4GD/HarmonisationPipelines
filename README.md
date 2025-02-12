# Table of contents

- [1. Introduction ](#1-introduction-)
- [2. Installation ](#2-installation-)
  - [2.1 Automatically, from the DockerHub Image (recommended) ](#21-automatically-from-the-dockerhub-image-recommended-)
  - [2.2 Manually, by building a container ](#22-manually-by-building-a-container-)
- [3. Configuration ](#3-configuration-)
  - [3.1 Virtuoso instance ](#31-virtuoso-instance-)
  - [3.2 LPIS country configuration files ](#32-lpis-country-configuration-files-)
  - [3.3 General mapping generator ](#33-general-mapping-generator-)
  - [3.4 SPARQL mapping ](#34-sparql-mapping-)
  - [3.5 Relational Database as input source ](#35-relational-database-as-input-source-)
  - [3.6 Link discovery process ](#36-link-discovery-process-)
- [4. Usage ](#4-usage-)
  - [4.1 FADN Pipeline ](#41-fadn-pipeline-)
  - [4.2 LPIS Pipeline ](#42-lpis-pipeline-)
  - [4.3 GENERIC Pipeline ](#43-generic-pipeline-)
- [5. Version ](#5-version-)
- [6. Team ](#6-team-)
- [7. License ](#7-license-)


# 1. Introduction <a name="introduction"></a>

The Linked Data Pipelines is an ETL tool written in Python. It takes care of fetching, extracting, preprocessing, transforming, post-processing, and loading linked data into the triplestore. The interaction with the user is performed through CLI (Command Line Interface) and configuration files. Users can choose from a set of specific pipelines, as well as the generic pipeline. Generic pipeline enables single and flexible operations on a different type of data. 
The tool re-uses other existing tools, such as [Geotriples](https://github.com/LinkedEOData/GeoTriples), [RMLmapper](https://github.com/RMLio/rmlmapper-java), and others, for particular tasks,  providing a unified interface over them and connecting them transparently in sequences to implement full pipelines.


# 2. Installation <a name="installation"></a>

The project is distributed with a Dockerfile which helps immensely with setting up the whole environment in a stable and reproducible way. It is recommended to use this tool inside the docker container, although if one takes care of all dependencies it is also possible to set it up locally.

## 2.1 Automatically, from the DockerHub Image (recommended) <a name="installation-auto"></a>

1. Make sure Docker is installed on your machine.
2. Pull the image from the docker repository by typing: ```docker pull montanaz0r/demeter-pipelines:latest```
3. Next, in console/terminal run the container type ```docker run -ti montanaz0r/demeter-pipelines:latest```
4. Inside the container type ```source pipelines/bin/activate``` to activate the virtual environment created for the python dependencies.
5. Move to the src directory by typing ```cd src```.
6. You are now ready to use the tool.
7. (Optional) In step 3 you can optionally use docker run with the bind-mounting command to forward the output directly into a local directory. 
  e.g. ```docker run -v {local host directory}:{container output directory} -ti montanaz0r/demeter-pipelines:latest```

## 2.2 Manually, by building a container <a name="installation-manual"></a>

1. Download project's Dockerfile.
2. Make sure Docker is installed on your machine.
3. Go to the directory where Dockerfile is stored.
4. In console/terminal type ```docker build -f Dockerfile -t {image name} . ```
    e.g. ```docker build -f Dockerfile -t pipelines .```.
5. Next, in console/terminal run the container type ```docker run -ti {image name}```
   e.g. ```docker run -ti pipelines```
6. Inside the container type ```source pipelines/bin/activate``` to activate the virtual environment created for the python dependencies.
7. Move to the src directory by typing ```cd src```.
8. You are now ready to use the tool.
9. (Optional) In step 5 you can optionally use docker run with the bind-mounting command to forward the output directly into a local directory. 
  e.g. ```docker run -v {local host directory}:{container output directory} -ti {image name}```

# 3. Configuration <a name="configuration"></a>

## 3.1 Virtuoso instance <a name="virtuoso-instance"></a>

The tools allow users to load RDF dumps into a preconfigured Virtuoso triple store.
The tool assumes that connection to the virtuoso server can be done via ssh from the machine where it is running (i.e., port 22 is open in the virtuoso server to CLI machine). Additionally, the tool assumes access to the virtuoso server is via ssh keys. Therefore, the virtuoso server should have the public key (in its authorized keys) of an account that will be used by the CLI tool. 

Accordingly, to use this functionality, users need to configure the following two files:
* ./.env
* ./cfg/config.yaml

**.env configuration file**

In this file, the user should provide both the private and public ssh keys used to log in to the virtuoso server. SSH credentials should be provided decoded as base64, and the values will be automatically encoded in the tool. The key values should be provided as follows:  
``export VSO_PRIVATE_KEY = “<virtuoso_server_account_private_key>”  ``
``export VSO_PUBLIC_KEY = “<virtuoso_server_account_public_key>”  ``

**./cfg/config.yaml configuration file**

This is the master config file which should be populated. The template can be found under ./cfg/config_template.yaml. It includes a section, called  vto_cfg, with the virtuoso server settings, which include:

  •   SSH_PASSPHRASE  
  •   VIRTUOSO_PORT (*Virtuoso DB port, by default 1111*)  
  •   VIRTUOSO_USER (*Virtuoso DB user account with write access permissions*)  
  •   VIRTUOSO_PASSWORD (*Virtuoso DB user's account password*)  
  •   DUMP_EXTENSION (*Extension of dump files to be loaded in virtuoso, i.e. .nt*)  
  •   DATA_FOLDER (*The main directory in the Virtuoso server where all data is stored*)  
  •   DATA_PREFIX (*A prefix that will be temporarily added to the data in the DATA_FOLDER. This is inconsequential if data was properly loaded since the original data is removed from the server after it was loaded into a graph. However, it might be useful to always have some kind of tag to your data in case something goes wrong and manual intervention is needed.*)  
  •   SERVER_USER (*Username that connects to the machine where Virtuoso DB is located.*)  
  •   SERVER_HOST (*Hostname for the machine where Viurtoso DB is located.*)  

## 3.2 LPIS country configuration files <a name="lpis-country-configuration-files"></a>

For the LPIS Pipelines, the mappings are generated based on the configuration files that can differ between countries. 
The list of supported countries can be found in ./cfg/config.yaml in the "lpis_countries" section. 
The section specifies the link between country name and the specific configuration file that will be used in the mapping generation.

Country-specific pre-defined mapping coniguration files are stored under **./cfg/LPIS/**. Currently there are pre-defined mappings for **Spain**, **Poland** and **Lithuania**. Additionally, there the folder includes the **other** configuration file, which can be used to configure mapping for any other country. Users can change the content of the respective configuration file, including the **other** configuration file, by changing the values in key-value pairs or removing/adding items.

**Note: There are keys that are required to generate the mapping and those should always be present in the configuration file with a respective value! Below is the list of supported keys that can be included in the country-specific LPIS configuration file:**

**Required:**
  - BASE_URI
  - LABEL
  - IACS_ID
  - TEMPLATE_ID

**Optional:**
  - VALID_FROM
  - SHORT_ID
  - SPECIFIC_LAND_USE
  - PARENT_ADM2
  - PARENT_ADM3
  - MUNICIPALITY_ID
  - AREA
  - PERIMETER
  - LAYER_ABBREVIATION

## 3.3 General mapping generator <a name="general-mapping-generator"></a>

A general mapping generator can be used as a part of the **GENERIC Pipeline** (*--from_config flag*) to create mappings from scratch based on a simple YAML configuration file provided by the user. 

Users can use this feature by modifying **[this config file](cfg/GENERIC/generic_cfg.yaml)**. There are examples provided [here](cfg/GENERIC/) to allow users to get a grasp of how this YAML should be specified. With that being said, there are a couple of general rules for constructing the YAML configuration file:

1. The specification should be placed under the cfg section key
2. The TEMPLATE_ID is the URL path that is added to the base URL provided via the *base_uri* parameter. The automatically generated URL will be created by concatenating base_uri, TEMPLATE_ID, and entity_name. This path can include multiple / characters and can reference fields in the data source by enclosing them in single quotes. e.g., ```"RPL/2022/Parcel/{`BLOKAS_ID`}"```
3. The CONTEXT key is required. CONTEXT provides a list of terms that can be used for defining entities in the config. CONTEXT can be a single reference to the context file (JSONLD), or a list with multiple context files,
4. CONTEXT value can also consist of dictionary like key/value pairs for additional references that are not included in context file/files
5. The MAIN_TYPE key type is required and provides information about entities that are related to the core section of the mapping.
6. Each property consist of predicate (key) and object (value),
7. For complex types additional information are nested under the predicate (key),
8. @type is a special keyword that is referencing type that can contain multiple types in a list-like object
9. the value of predicate can be i) column/variable from datasource, ii) fixed value (of particular datatype), iii) string with reference to columns/variables, iv) URL with reference to columns/variables. 
10. column/variable should be surrounded by curly brackets abd single quotes in the config i.e. {\`variable_value\`}
11. fixed values (of any datatype) are specified using angle brackets i.e. <fixed_value>.
12. The data type can be specified by adding a vertical bar after the value with a specific datatype. i.e.
     ```
    `some_value`|<integer>
    ```
13. If datatype is not explicitly provided the value will be resolved as IRI by default.
14. Enumerated values can be provided using special keywords that consist of an "@" symbol followed by integer. For example, @1.
15. The Enumerator should be placed under the property that is to be enumerated; for example, 
    ``` 
    propertyName:
       @1:
         ...
       @2
         ...
    ```
16. If the uri value for a complex type is left empty (by YAML convention this should be either null or ~) the program will generate uri for this type automatically using base_uri and template_id. However, the key is mandatory, so even though it can be left empty, do not delete the key!

17. Be careful of illegal characters in cases where datatype is not specified. Proper URI might not be generated in some cases, and program will throw an error.

## 3.4 SPARQL mapping <a name="sparql-mapping"></a>

The **GENERIC Pipeline** supports mappings specified as SPARQL queries (in a .sparql file) since version 0.2.1. This option is reserved for cases where the input data is provided in the form of a CSV file!


## 3.5 Relational Database as input source <a name="relational-database-as-input-source"></a>

The **GENERIC pipeline** supports relational databases as a source of input data. Such source be used to generate mappings, transform the data (using an existing mapping), or both.

The user has to provide a set of details in order to successfully establish database connection. This information is provided in the main configuration file, i.e., **/cfg/config.yaml**, under the sql_cfg section. The tool is expecting and accepting the following details:

  •   DB_TYPE (*REQUIRED Type of the database i.e. postgresql, mysql*)  
  •   DB_USERNAME (*REQUIRED Username that can access the database*)  
  •   DB_PASSWORD (*OPTIONAL If db uses password, then this should be filled in*)  
  •   DB_HOST (*REQUIRED*)  
  •   DB_PORT (*OPTIONAL*)  
  •   DB_NAME (*REQUIRED*)  


## 3.6 Link discovery process <a name="linking-process"></a>

The **GENERIC pipeline** supports link discovery from version 1.0.0, which relies on the [Silk tool](https://github.com/silk-framework/silk) tool. To carry out this process, the user needs to provide a linking configuration file, as specified by the [Link Specification Language](https://app.assembla.com/wiki/show/silk/Link_Specification_Language), as input - either in the local directory or through a URL.

Note that the linking configuration file specifies can specify different types of inputs, e.g., RDF dump files or SPARQL endpoints. If the user links physical files and not SPARQL endpoints, those files should be provided together with a linking config file (either through dir_input or url_input). This is because the input files (e.g., n-triple files) are provided with simple filenames instead of complete paths, so the tool assumes that the input files are on the same level as the provided configuration file. 

In the following example, the input zip file consists of a config file (XML) and the two input files (as specified in the config file).

```python main.py generic --process=link --url_input="https://box.psnc.pl/f/7d856fd71a/?raw=1"```


# 4. Usage <a name="usage"></a>

There are currently three different pipeline types supported by the tool: FADN, LPIS, and Generic. Each of them has a specific set of parameters, options, and rules, which will be briefly described underneath. 

To list the supported pipelines the following command can should be used:
```python main.py -h```

To get details for specific pipeline the following command should be used:
```python main.py <pipeline_name> -h```

## 4.1 FADN Pipeline <a name="fadn-pipeline"></a>

The FADN Pipeline is used to handle FADN data that is provided through the https://ec.europa.eu site. Data comes in packages, and each package contains a specific structure of the CSV file. The full pipeline can be evoked by running the following command:

```python main.py fadn --stage=all --url_input=<url_to_the_zip_file_containing_data> --graph_uri=<graph_uri_value>```

Stage parameter is required, and instead of running the whole pipeline, one may choose to run it up until a particular stage. The chosen stage is **inclusive** so far instance running --stage=transform will perform all the tasks that are preceding transformation and the transformation itself as a final step. In that way, the output will consist of a set of dumps. Other stages are incorporating similar logic, and they all are inclusive. Here is the list of all available stages for the FADN Pipeline with corresponding output in the brackets:

- **all** (set of dumps loaded into a triplestore),
- **postprocess** (a set of post-processed dumps),
- **transform** (a set of dumps),
- **mapping** (a set of mapping files),
- **preprocess** (a set of auxiliary CSV files),
- **fetch** (raw data acquired and unzipped from the source).

Here is the list of all parameters and options for FADN Pipeline with a corresponding description:

```
Usage: main.py fadn [OPTIONS]

  Function that initializes FADN Pipeline.

Options:
  Input data sources: [mutually_exclusive]
                                  The source of the input data. The default,
                                  if neither option is used, is the fadn
                                  folder in the current directory.

    -ui, --url_input TEXT         URL to the zip file with input file package.
                                  Required when --stage=fetch. Optional in all
                                  other cases.

    -di, --dir_input DIRECTORY    Directory containing input files.

  -s, --stage [all|fetch|preprocess|mapping|transform|postprocess]
                                  Runs the whole fadn_pipeline or a single
                                  fadn_pipeline stage.  [required]

  -u, --graph_uri TEXT            Graph's URI that will be used to load dumps
                                  into the database. Required when --stage is
                                  set to all

  -gpd, --graph_per_dump          Treats -u/--graph_uri as base that will be
                                  extended with the dump name for each load.
                                  Optional when --stage is set to all.

  -rg, --reload_graph             Removes target graph before loading dumps
                                  into the database. Optional when --stage is
                                  set to all

  -o, --output DIRECTORY          Output folder name. Optional.  [default:
                                  results]

  -c, --clean                     Removes all files generated throughout the
                                  run of the full pipeline. Optional when
                                  --stage is set to all.

  -h, --help                      Show this message and exit.
  ```

   **Example**:
    Running the whole FADN Pipeline using url_input and graph_per_dump flag:

    python main.py fadn --stage=all --graph_uri=http://testing/FADN/ --url_input=https://ec.europa.eu/agriculture/rica/database/reports/archives/fadn20200621.zip -gpd

## 4.2 LPIS Pipeline <a name="lpis-pipeline"></a>

The LPIS Pipeline handles datasets provided in the form of shapefiles. The pipeline will process each shapefile that is present in the provided input. Similar to the FADN pipeline, the input can be either in the form of an URL or a directory.
Just as with the FADN pipeline, a user can choose to run a different stage by picking a value for the --stage parameter. The full pipeline can be ran using the following command:

```python main.py lpis--stage=all --url_input=<url_to_the_zip_file_containing_data> --graph_uri=<graph_uri_value> --country=<name_of_the_country_selected_from_a_list>```

LPIS pipeline currently handles transformation for three specific countries: Lithuania, Poland, and Spain. The details regarding the mapping are be provided through configuration files as explained in [LPIS country configuration files](#lpis-country-configuration-files) section. The pre-configured files for those countries can be found under the **./cfg/LPIS/** directory along with the other.yaml, which can be used for processing any other country. For such case, the country parameter should be "other" and the user should fill the correspondig YAML file (other.yaml).

The following stages with their respective output are available for the LPIS type of pipeline:

  - **all** (set of dumps loaded into a triplestore),
  - **postprocess** (a set of post-processed dumps),
  - **transform** (a set of dumps),
  - **mapping** (a set of mapping files),
  - **fetch** (raw data acquired and unzipped from the source).

Here is the list of all parameters and options for LPIS Pipeline with a corresponding description:

```
Usage: main.py lpis [OPTIONS]

  Function that initializes LPIS Pipeline.

Options:
  Input data sources: [mutually_exclusive]
                                  The source of the input data. The default,
                                  if neither option is used, is the current
                                  directory.

    -ui, --url_input TEXT         URL to the zip file with input file package.
                                  The file is unpacked and the directory
                                  traversed to find all existing shapefiles.
                                  Required when --stage=fetch.

    -di, --dir_input DIRECTORY    Directory containing input data. The the
                                  directory is traversed to find all existing
                                  shapefiles.
  
  -s, --stage [all|fetch|mapping|transform|postprocess]
                                  Runs the whole LPIS Pipeline or a single
                                  LPIS Pipeline stage.  [required]

  -cn, --country [other|spain|poland|lithuania]
                                  Mappings will be generated for a specific
                                  country that was chosen from the list.
                                  Required when --stage=all, mapping,
                                  transformor postprocess.

  -u, --graph_uri TEXT            Graph's URI that will be used to load dumps
                                  into the database. Required when --stage is
                                  set to all.

  -gpd, --graph_per_dump          Treats -u/--graph_uri as base that will be
                                  extended with the dump name for each load.
                                  Optional when --stage is set to all.

  -rg, --reload_graph             Removes target graph before loading dumps
                                  into the database. Optional when --stage is
                                  set to all

  -o, --output DIRECTORY          Output folder name. Optional.  [default:
                                  results]


  -c, --clean                     Removes all files generated throughout the
                                  run of the full pipeline. Optional when
                                  --stage is set to all.

  -h, --help                      Show this message and exit.
  ```
     
   **Example**:
    Running the postp-processing LPIS Pipeline for Spain using url_input:

    python main.py lpis --stage=postprocess --country=SPAIN --url_input=<url>

## 4.3 GENERIC Pipeline <a name="generic-pipeline"></a>

The Generic Pipeline aims at providing as much flexibility to the user as possible. The tool can work with multiple data types, including:

- **Shapefiles**
- **JSON files**
- **CSV files**
- **Databases**

Similar to FADN and LPIS Pipeline, though, users can choose to provide data through a URL (url_input) or just point to the directory (dir_input). But unlike other pipelines, there is no full pipeline method, as every process can be treated as an autonomous step. With that being said, the Generic Pipeline supports to stack multiple processes. 

For the transformation process, this pipeline can handle different situations:
* when the number of mapping files is equal to the number of input files (in this scenario, mapping files should have the same base name as data files)
* when a single mapping files is used with multiple input files
* when a single mapping file is used with a single input file
For the last two scenarios, the tool will adjust the mapping appropriately to align it with input file/files.


The following processes are currently available for the Generic pipeline. 

- **preprocess** Currently supporting only CSV files (output: preprocessed file),
- **mapping generation** Currently supporting only CSV and Shapefiles (output: mapping file),
- **transform**. Supporting all available data types (output: dump file),
- **postprocess** (output: post-processed dump file),
- **load** (output: dump loaded into a triplestore),
- **link** (output: dump file with discovered links). See details in section [Link discovery process](#linking-process)


It is useful to know that processes do not need to be stacked in any particular order, as the tool handles the sequence of actions by itself. Therefore the two examples below, are treated equally:

```--process=transform --process=mapping --process=preprocess```

```--process=mapping --process=preprocess --process=transform```


Below is the list of all parameters and options for Generic Pipeline with a short description:

```
Usage: main.py generic [OPTIONS]

  Function that initializes Generic Pipeline.

Options:
  -p, --process [preprocess|mapping|transform|postprocess|load|link]
                                  Runs a single process from the generic
                                  Pipeline. Can be used multiple times to
                                  evoke set of tasks.  [required]

  -u, --graph_uri TEXT            Graph's URI. Required when using load
                                  process.

  Input data sources: [mutually_exclusive, required]
                                  The source of the input data.
    -ui, --url_input TEXT         URL to the input zip file package.
    -di, --dir_input DIRECTORY    Directory containing input files.
    -db, --db_input               Flag indicating database input. Details are
                                  provided through cfg/config.yaml by updating
                                  sql_cfg section.

  -o, --output DIRECTORY          Output folder name. Optional. !!!WARNING!!!
                                  if directory already exist the content of it
                                  will be erased before pipeline execution.
                                  Select your output path with caution!
                                  [default: results]

  -it, --input_type [Shapefile|GML|KML|GeoJson|CSV|JSON|XML|DB|netCDF|CSVW]
                                  Type of input data that has to be
                                  transformed. Required if process is
                                  transform, mapping or preprocess. WARNING:
                                  this option is case sensitive!

  -mi, --mapping_input DIRECTORY  Input path to the mapping directory.
                                  Required when process is transform and there
                                  is no preceding mapping process.

  -mu, --mapping_url TEXT         Input mapping as URL to a zip package (works
                                  only with data provided as url_input).
                                  Required when process is transform and there
                                  is no preceding mapping process.

  -bu, --base_uri TEXT            Base URI. Required with mapping process and
                                  transform when processing shapefiles.

  -gpd, --graph_per_dump          Treats -u/--graph_uri as base that will be
                                  extended with the dump name for each load.
                                  Optional when --process is set to load.

  -rg, --reload_graph             Removes target graph before loading dumps
                                  into the database. Optional when --process
                                  is set to load.

  -ppa, --preprocess_activity [add_seq_col|unzip_multiple_archives|normalize_delimiter|to_crs|add_enum]
                                  List of available methods to choose from for
                                  the preprocessing part of the Pipeline.
                                  Required with --process=preprocess.
                                  unzip_multiple_archives works for every
                                  input type. add_seq_col and
                                  normalize_delimiter areconsequential only
                                  for CSV input type, to_crs works only with
                                  Shapefiles and add_enum is somewhat
                                  equivalent to add_seq_col but works for json
                                  files.

  -ttl, --to_ttl                  Converts output from n-triples to turtle as
                                  a part of post-processing. Available only
                                  with post-processing.

  -re, --replace_expression TEXT...
                                  Replaces all occurrences of X with Y as a
                                  part of additional dump postprocessing.
                                  Optional when process is set to postprocess.
                                  Regular expression patterns are accepted but
                                  they needto be properly escaped!

  -rl, --remove_line TEXT         Removes every line containing provided
                                  string in the of dump file. Optional when
                                  process=postprocess

  -te, --target_encoding TEXT     Desired encoding for output dump. Optional
                                  when process is set to postprocess.

  -se, --source_encoding TEXT     Encoding of a source file. Optional when
                                  --target_encoding is provided. if source
                                  encoding was not provided program will try
                                  to make an educated guess on the source
                                  encoding.

  -fc, --from_config              Flag indicating that the mapping should be
                                  generated based on the configfile (Supports
                                  Shapefiles and CSV). Optional when --process
                                  is set to mapping.

  -fcv, --from_config_value FILE  Alternative path to the config file for
                                  generating a custom mapping.  [default:
                                  cfg/GENERIC/generic_cfg.yaml]

  -sq, --sparql_query             Uses a SPARQL query as a mapping to produce
                                  dumps. Query file should be provided like
                                  the regular mapping either through
                                  --mapping_input or --mapping_url. Can be
                                  used only with a transform process.

  -yrv, --yarrrml_rules_value FILE
                                  Path to YAML containing all the rules for
                                  mapping generation using YARRRML tool.

  -yru, --yarrrml_rules_url TEXT  URL to zip package containing YAML file with
                                  rules for mapping generation using YARRRML
                                  tool.

  -c, --clean                     Removes all files generated throughout the
                                  run of the full pipeline. Optional when
                                  --process=load.

  -h, --help                      Show this message and exit.
```

# 5. Version <a name="version"></a>

Latest version:
**version v1.1.2**

To check the version of the tool you are currently using, you can pass
 ```python main.py --version``` into the terminal.

# 6. Team <a name="team"></a>

The Linked Data Pipelines was built with an effort of the Data Analytics and Semantics Department in Poznan Supercomputing and Networking Center. [Bogusz Janiak](http://boguszjaniak.xyz/) is the main creator and maintainer. People who contributed to the project: [Raul Palma](http://orcid.org/0000-0003-4289-4922>), [Soumya Brahma](https://github.com/sbrahma), [Andrzej Mazurek](andrzej.a.mazurek@gmail.com).

# 7. License <a name="license"></a>

The Linked Data Pipelines has an MIT License, as found in the [LICENSE](LICENSE) file.

![alt text](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/License_icon-mit.svg/384px-License_icon-mit.svg.png)