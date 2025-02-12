import subprocess
import pathlib
import os
import logging
import datetime
import time
import signal

import yaml
from dotenv import load_dotenv

from modules.utils.utils import base64_encoding, is_path_abs, generate_uuid, base64_decoding
from modules.tools import basic_tool


class VtoLoader(basic_tool.Tool):
    """
    Class that handles loading data in to the Virtuoso Triple Store.
    """
    def __init__(self, configfile, uri, remove_target_graph=False, graph_per_dump=False):
        """
        :param configfile: str -> name of the configuration file that will be used within this vto_loader.
        :param uri: str -> graph's URI.
        :param remove_target_graph: boolean -> if True, the vto_loader will clear graph before loading the data.
        :param graph_per_dump: boolean -> if True Graph's URI will be used as a base (prefix)
        to which the dump name is appended.
        """
        super().__init__()
        self.configfile = configfile
        self.target_dir = None
        self.server = None
        self.passphrase = None
        self.port = None
        self.user = None
        self.password = None
        self.file_extension = None
        self.data_folder = None
        self.data_prefix = None
        self.container = None   # name of the temporary folder for stroring data on the server side.
        self.uri = uri
        self.remove_target_graph = remove_target_graph
        self.graph_per_dump = graph_per_dump
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)   # making sure directory is being crated
        self.temporary_encoding = None
        self.server_abbreviation = None
        self.fadn_naming_convention = False

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_vto_loader_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def load_config(self):
        """
        Function that loads a config file and populates class instance attributes respectively.
        """
        path = os.path.join('cfg', self.configfile)
        with open(path) as file:
            vto_cfg = yaml.load(file, Loader=yaml.FullLoader)
            self.passphrase = vto_cfg['vto_cfg']['SSH_PASSPHRASE']
            if not self.passphrase:
                msg = "Aborting... SSH_PASSPHRASE is incorrect or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

            self.port = vto_cfg['vto_cfg']['VIRTUOSO_PORT']
            if not self.port:
                msg = "Aborting... VIRTUOSO_PORT is incorrect or it ismissing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)
            else:
                # cast port as int
                self.port = int(self.port)

            self.user = vto_cfg['vto_cfg']['VIRTUOSO_USER']
            if not self.user:
                msg = "Aborting... VIRTUOSO_USER is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

            self.password = vto_cfg['vto_cfg']['VIRTUOSO_PASSWORD']
            if not self.password:
                msg = "Aborting... VIRTUOSO_PASSWORD is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

            self.file_extension = vto_cfg['vto_cfg']['DUMP_EXTENSION']
            if not self.file_extension:
                msg = "Aborting... VIRTUOSO_EXTENSION is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

            self.data_folder = vto_cfg['vto_cfg']['DATA_FOLDER']
            if not self.data_folder:
                msg = "Aborting... DATA_FOLDER is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

            server_user = vto_cfg['vto_cfg']['SERVER_USER']
            if not server_user:
                msg = "Aborting... SERVER_USER is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)
            server_host = vto_cfg['vto_cfg']['SERVER_HOST']
            if not server_host:
                msg = "Aborting... SERVER_HOST is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)
            self.server = f"{server_user}@{server_host}"

            self.data_prefix = vto_cfg['vto_cfg']['DATA_PREFIX']
            if not self.data_prefix:
                msg = "Aborting... DATA_PREFIX is incorrect, or it is missing from the config file!"
                self.logger.info(msg)
                raise SystemExit(msg)

    def _set_target_dir(self):
        """
        Semi private helper function that sets up target_dir attribute.
        """
        self.target_dir = os.path.join('home', 'virtuoso', self.data_folder, self.container)
        self.logger.info(f'On the server side data will be stored in: {self.target_dir}')

    def _set_container_name(self):
        """
        Semi private helper function that sets up unique name of the container folder.
        """
        self.container = self.data_prefix + generate_uuid()
        self.logger.info(f"Temporary folder used as a dump container on the server side has an unique"
                    f"name of {self.container}")

    def _set_server_abbreviation(self):
        """
        Semi private helper function that sets up server name abbreviation in order to run ssh keyscan on it.
        """
        try:
            self.server_abbreviation = self.server.split('@')[-1]
            self.logger.info(f"Server abbreviation that will be used for ssh keyscan is "
                        f"saved as: {self.server_abbreviation}")
        except AttributeError:
            self.logger.info("Invalid value for VIRTUOSO_SERVER in the config file! '@' was not found!")

    def _set_ssh_credentials(self, home_dir):
        """
        Semi private helper function that creates private and public key files for ssh connection based
        on the values stored as environment variables.
        :param home_dir: str -> home directory where all credentials will be stored.
        """
        env_file = os.path.join(os.getcwd(), '.env')
        load_dotenv(env_file)   # loading environment variables from file.
        key = os.getenv("VSO_PRIVATE_KEY")   # ssh private key
        pkey = os.getenv("VSO_PUBLIC_KEY")   # ssh public key
        encoded_key = base64_decoding(key)
        encoded_pkey = base64_decoding(pkey)
        self._subprocess_cmd("mkdir vto", cwd=pathlib.Path.home())   # creating vto directory
        self._subprocess_cmd("mkdir .ssh", cwd=home_dir)   # creating .ssh directory
        cmd1 = f"echo '{encoded_key}' >> id_rsa_pipeline"
        cmd2 = f"echo '{encoded_pkey}' >> id_rsa_pipeline.pub"
        self._subprocess_cmd(f"{cmd1}; {cmd2}", cwd=os.path.join(home_dir, '.ssh'))

    def _process_checker(self, pid):
        """
        Semi private function that is checking if there is a process with a given PID
        determines if there is a computer program running with that assigned PID.
        :param pid: int -> process number.
        :return: int -> 0 if process is done, 1 if it is not.
        """
        try:
            os.kill(pid, 0)
        except OSError:
            self.logger.info("pid is unassigned")
            return 0
        else:
            self.logger.info("pid is in use")
            return 1

    def _read_pid_from_file(self, cwd):
        """
        Semi private helper function that reads PID from the file using temporary object identifier.
        :param cwd: str -> directory.
        :return: int -> PID code.
        """
        f = open(os.path.join(cwd, self.temp_dir, f'save_pid-{self.temporary_encoding}.txt'), "r")
        pid = f.read()
        return int(pid)

    def _validate_logfile(self, log_filename):
        """
        Semi private helper function that reads the logfile and returns the code output as well ass potential
        errors.
        :param log_filename: str -> name of the log file.
        :return: code, err: str, str -> output code and error info.
        """
        with open(log_filename, 'r') as f:
            log_line = f.readlines()[-3]
            try:
                code, err = log_line.split()[0], log_line.split()[1]
                self.logger.info(f'{log_filename}, code: {code}, error:{err}.')
            except ValueError:
                code, err = 0, 0
                self.logger.info(f'There was an error associated with {log_filename}. Script was unable'
                                 f' to find expected values, therefore it can not be confirmed that'
                                 f' the dump associated with log was loaded properly!')
            self.logger.info(f'{log_line}')
            return code, err

    def _subprocess_cmd(self, command, cwd=None, stdout=False):
        """
        Semi private helper function for executing commands via the subprocess module.
        :param command: str -> self-explanatory.
        :param cwd: str -> optional, current working directory.
        :param stdout: boolean -> optional, if true the output will be silenced and captured via Pipe.
        """
        if cwd:
            if stdout:
                process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE)
                                           #preexec_fn=os.setsid)
            else:
                process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=None)
                                           #preexec_fn=os.setsid)
        else:
            if stdout:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                                           #preexec_fn=os.setsid)
            else:
                process = subprocess.Popen(command, shell=True, stdout=None)
                                           #preexec_fn=os.setsid)
        process.communicate()
        # process.terminate()
        # try:
        #     os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        #     print("we do terminate")
        # except ProcessLookupError:
        #     print("We entered exception")
        #     pass
        self.logger.info('Process finished.')

    def _generate_shell_scripts_for_multiple_graphs(self, seq, dump, encoded_dump, uri_suffix):
        """
        Semi private function that generates bash scripts for situations where there are multiple
        target graphs.
        :param seq: int -> sequential number.
        :param dump: str -> the name of the dump.
        :param encoded_dump: str -> base64 encryption for the dump file.
        :param uri_suffix: str -> suffix part of the graph's URI that is appended to the base URI.
        """
        if self.remove_target_graph:
            with open(os.path.join(self.temp_dir, f'vso{seq}.sh'), 'w') as rsh:
                rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="delete from db.dba.load_list where ll_graph='{self.uri}{uri_suffix}#';" > /dev/null 2>&1
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="log_enable(3,1); SPARQL CLEAR GRAPH  <{self.uri}{uri_suffix}#> ;" > /dev/null 2>&1
echo "The graph {self.uri}{uri_suffix}# has been cleared!"
echo "Loading data for {self.uri}{uri_suffix}#..."
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="ld_dir ('/{self.target_dir}', '{dump}', '{self.uri}{uri_suffix}#');" > /dev/null 2>&1
                        ''')
        else:
            with open(os.path.join(self.temp_dir, f'vso{seq}.sh'), 'w') as rsh:
                rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
echo "Loading data for {self.uri}{uri_suffix}#..."
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="ld_dir ('/{self.target_dir}', '{dump}', '{self.uri}{uri_suffix}#');" > /dev/null 2>&1
                                ''')

#         with open(os.path.join('temp', f'pid{seq}.sh'), 'w') as rsh:
#             rsh.write(f'''\
# #!/bin/bash
# mkdir -p temp
# scp {self.server}:~/save_pid-{encoded_dump}.txt ~/vto/temp/save_pid-{encoded_dump}.txt
#                              ''')

    def _generate_shell_scripts_for_single_graph(self, encoded_target):
        """
        Semi private function that generates bash scripts for situations where there is a single
        target graph.
        :param encoded_target: str -> base64 encryption for the dump file.
        """
        if self.remove_target_graph:
            with open(os.path.join(self.temp_dir, 'vso.sh'), 'w') as rsh:
                rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="delete from db.dba.load_list where ll_graph='{self.uri}';" > /dev/null 2>&1
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="log_enable(3,1); SPARQL CLEAR GRAPH  <{self.uri}> ;" > /dev/null 2>&1
echo "The graph has been cleared!"
echo "Loading data..."
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="ld_dir ('/{self.target_dir}', '%{self.file_extension}', '{self.uri}');" > /dev/null 2>&1
                          ''')
        else:
            with open(os.path.join(self.temp_dir, 'vso.sh'), 'w') as rsh:
                rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
echo "Loading data..."
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="ld_dir ('/{self.target_dir}', '%{self.file_extension}', '{self.uri}');" > /dev/null 2>&1
                           ''')
#         with open(os.path.join('temp', f'pid.sh'), 'w') as rsh:
#             rsh.write(f'''\
# #!/bin/bash
# mkdir -p temp
# scp {self.server}:~/save_pid-{encoded_target}.txt ~/vto/temp/save_pid-{encoded_target}.txt
#                             ''')

    def _generate_loading_script(self):
        """
        Semi private function that generates bash script for loading files into graph.
        :return:
        """
        with open(os.path.join(self.temp_dir, 'loader.sh'), 'w') as rsh:
            rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
nohup ./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="rdf_loader_run();" > my.log 2>&1           
            ''')

    def _generate_validation_scripts(self, seq, dump):
        """
        Semi private function that generates bash scripts for validation of each file that was loaded.
        :param seq: int -> sequential number.
        :param dump: str -> dump file name.
        """
        with open(os.path.join(self.temp_dir, f'val{seq}.sh'), 'w') as rsh:
            rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso
./virtuoso-opensource/bin/isql {self.port} {self.user} {self.password} exec="select ll_state, ll_error from DB.DBA.load_list where ll_file='/{self.target_dir}/{dump}';" > val{seq}.log 2>&1
                                        ''')
        with open(os.path.join('temp', f'val_ex{seq}.sh'), 'w') as rsh:
            rsh.write(f'''\
#!/bin/bash
scp {self.server}:~/val{seq}.log ~/vto/temp/val{seq}.log
                                        ''')

    def _generate_cleaner_script(self):
        """
        Semi private helper function that creates a shell script that will remove redundant files from the
        server after the loading was performed.
        """
        with open(os.path.join(self.temp_dir, 'cleaner.sh'), 'w') as rsh:
            rsh.write(f'''\
#!/bin/bash
cd /home/virtuoso/{self.data_folder}
rm -r {self.container}
echo "Temporary data was removed from the server!"
                        ''')

    def _execute_set_of_shell_scripts(self, data_directory, cwd, eval_cmd):
        """
        Semi private function that executes a set of shell scripts based on the loading parameters.
        :param data_directory str -> path to the folder that contains data.
        :param cwd: str -> current working directory.
        :param eval_cmd str -> command for ssh validation.
        """
        if self.graph_per_dump:
            seq = 0
            for dump in os.listdir(data_directory):
                if dump.endswith(self.file_extension):
                    filename = os.path.splitext(dump)[0]
                    if self.fadn_naming_convention:
                        parts = filename.split('-')
                        uri_suffix = '-'.join(parts[1:-2])   # creating URI suffix from the filename (specific to FADN).
                    else:
                        uri_suffix = filename   # for other Pipeline uri_suffix is just a filename.
                    encoded_dump = base64_encoding(dump)
                    self.temporary_encoding = encoded_dump
                    seq += 1
                    self._generate_shell_scripts_for_multiple_graphs(seq=seq, dump=dump,
                                                                     encoded_dump=encoded_dump,
                                                                     uri_suffix=uri_suffix)
                    self._subprocess_cmd(f"cp {self.temp_dir}/vso{seq}.sh ~/vto/")
                    vso_cmd = f"ssh {self.server} 'bash -s' < vso{seq}.sh"
                    self._subprocess_cmd(f"{eval_cmd}; {vso_cmd}", cwd=cwd, stdout=False)
                    # self._subprocess_cmd(f"cp temp/pid{seq}.sh ~/vto/")
                    # pid_cmd = f"bash -s < pid{seq}.sh"
                    # self._subprocess_cmd(f"{eval_cmd}; {pid_cmd}", cwd=cwd, stdout=False)
                    # print('Confirming the status of a process...')
                    # pid = self._read_pid_from_file(cwd=cwd)
                    # while True:
                    #     if self._process_checker(pid) == 0:
                    #         print('Process is free now. Moving on.')
                    #         break
                    #     else:
                    #         print('Process is currently busy...')
                    #         time.sleep(5)
                    # rm_cmd = f"ssh {self.server} 'rm save_pid-{encoded_dump}.txt'"
                    # self._subprocess_cmd(f"{eval_cmd}; {rm_cmd}", cwd=cwd, stdout=False)

        else:
            encoded_target = base64_encoding(self.target_dir)
            self.temporary_encoding = encoded_target
            self._generate_shell_scripts_for_single_graph(encoded_target=encoded_target)
            self._subprocess_cmd(f"cp {self.temp_dir}/vso.sh ~/vto/")
            self._subprocess_cmd("chmod +x vso.sh", cwd=cwd)
            vso_cmd = f"ssh {self.server} 'bash -s' < vso.sh"
            self._subprocess_cmd(f"{eval_cmd}; {vso_cmd}", cwd=cwd, stdout=False)
            # self._subprocess_cmd(f"cp temp/pid.sh ~/vto/")
            # pid_cmd = "bash -s < pid.sh"
            # self._subprocess_cmd(f"{eval_cmd}; {pid_cmd}", cwd=cwd, stdout=False)
            # print('Confirming the status of a process...')
            # pid = self._read_pid_from_file(cwd=cwd)
            # while True:
            #     if self._process_checker(pid) == 0:
            #         print('Process is free now. Moving on.')
            #         break
            #     else:
            #         print('Process is currently busy...')
            #         time.sleep(5)
            # rm_cmd = f"ssh {self.server} 'rm save_pid-{encoded_target}.txt'"
            # self._subprocess_cmd(f"{eval_cmd}; {rm_cmd}", cwd=cwd, stdout=False)

    def _execute_loading_script(self, cwd, eval_cmd):
        """
        Semi private function that executes shell script for loading data into graph.
        :param cwd: str -> current working directory.
        :param eval_cmd: str -> command for ssh validation.
        """
        self._generate_loading_script()
        self._subprocess_cmd(f"cp {self.temp_dir}/loader.sh ~/vto/")
        loading_cmd = f"ssh {self.server} 'bash -s' < loader.sh"
        self._subprocess_cmd(f"{eval_cmd}; {loading_cmd}", cwd=cwd, stdout=False)

    def _execute_set_of_validation_scripts(self, data_directory, cwd, eval_cmd):
        """
        Semi private function that executes a set of shell scripts used for validation of all files
        that have been loaded.
        :param data_directory str -> path to the folder that contains data.
        :param cwd: str -> current working directory.
        :param eval_cmd: str -> command for ssh validation.
        """
        seq = 0
        for dump in os.listdir(data_directory):
            if dump.endswith(self.file_extension):
                seq += 1
                self._generate_validation_scripts(seq=seq, dump=dump)
                self._subprocess_cmd(f"cp {self.temp_dir}/val{seq}.sh ~/vto/")
                self._subprocess_cmd(f"cp {self.temp_dir}/val_ex{seq}.sh ~/vto/")
                val_cmd = f"ssh {self.server} 'bash -s' < val{seq}.sh"
                self._subprocess_cmd(f"{eval_cmd}; {val_cmd}", cwd=cwd, stdout=False)
                val_ex_cmd = f"bash -s < val_ex{seq}.sh"
                self._subprocess_cmd(f"{eval_cmd}; {val_ex_cmd}", cwd=cwd, stdout=False)
                code, err = self._validate_logfile(os.path.join(cwd, self.temp_dir, f'val{seq}.log'))
                if int(code) == 2:
                    if err == 'NULL':
                        msg = f'{dump} loaded successfully!'
                        print(msg)
                        self.logger.info(msg)
                    else:
                        msg = f'The {dump} was loaded but there was an error associated with it. ' \
                              f'Please check log file for more details!'
                        print(msg)
                        self.logger.info(msg)
                elif int(code) == 1:
                    print(f'Loading of {dump} is still in progress...')
                    counter = 0   # counter for number of times validation was repeated.
                    validated = False
                    while counter < 5:
                        time.sleep(5)
                        counter += 1
                        msg = f'Checking validation status of {dump} again...'
                        print(msg)
                        self.logger.info(msg)
                        self._generate_validation_scripts(seq=seq, dump=dump)
                        self._subprocess_cmd(f"cp {self.temp_dir}/val{seq}.sh ~/vto/")
                        self._subprocess_cmd(f"cp {self.temp_dir}/val_ex{seq}.sh ~/vto/")
                        val_cmd = f"ssh {self.server} 'bash -s' < val{seq}.sh"
                        self._subprocess_cmd(f"{eval_cmd}; {val_cmd}", cwd=cwd, stdout=False)
                        val_ex_cmd = f"bash -s < val_ex{seq}.sh"
                        self._subprocess_cmd(f"{eval_cmd}; {val_ex_cmd}", cwd=cwd, stdout=False)
                        code, err = self._validate_logfile(os.path.join(cwd, self.temp_dir, f'val{seq}.log'))
                        if int(code) == 2:
                            validated = True
                            if err == 'NULL':
                                msg = f'{dump} loaded successfully!'
                                print(msg)
                                self.logger.info(msg)
                                break
                            else:
                                msg = f'The {dump} was loaded but there was an error associated with it. ' \
                                      f'Please check log file for more details!'
                                print(msg)
                                self.logger.info(msg)
                                break
                    if not validated:
                        msg = f'It was not possible to verify if the loading of {dump} finished correctly.'
                        print(msg)
                        self.logger.info(msg)
                else:
                    msg = f'Loading of {dump} failed!'
                    print(msg)
                    self.logger.info(msg)
                rm_cmd = f"ssh {self.server} 'rm val{seq}.log'"
                self._subprocess_cmd(f"{eval_cmd}; {rm_cmd}", cwd=cwd, stdout=False)

    def _execute_cleaner_script(self, cwd, eval_cmd):
        """
        Semi private function that executes a set of shell scripts used for cleaning all files
        from the server.
        :param cwd: str -> current working directory.
        :param eval_cmd str -> command for ssh validation.
        """

        self._generate_cleaner_script()
        self._subprocess_cmd(f"cp {self.temp_dir}/cleaner.sh ~/vto/")
        self._subprocess_cmd("chmod +x cleaner.sh", cwd=cwd)
        cleaner_cmd = f"ssh {self.server} 'bash -s' < cleaner.sh"
        self._subprocess_cmd(f"{eval_cmd}; {cleaner_cmd}", cwd=cwd, stdout=False)

    def vto_loader(self, data_directory):
        """
        The main function responsible for executing all steps required for the loading operation.
        :param data_directory str -> path to the folder that contains data.
        """
        self._set_container_name()   # setting temporary data container on the server side.
        self._set_target_dir()   # setting full path of data directory on the server side.
        self._set_server_abbreviation()   # setting a variable that will be used later to perform ssh-keyscan.
        cwd = os.getcwd()   # capturing current directory
        # checking if this is unix based system.
        if self.unix:
            home_dir = os.path.join(pathlib.Path.home(), 'vto')   # setting the working directory for further actions.
            self._set_ssh_credentials(home_dir=home_dir)   # creating files containing ssh credentials.
            self._subprocess_cmd(f'cp -r {self.temp_dir} ~/vto/')  # copying necessary files to the working directory.
            # creating file that will contain passphrase.
            self._subprocess_cmd(f"echo 'echo {self.passphrase}' > x", cwd=home_dir)
            # setting up suitable file permissions.
            self._subprocess_cmd("chmod 600 .ssh/id_rsa_pipeline", cwd=home_dir)
            self._subprocess_cmd("chmod 711 x", cwd=home_dir)
            # performing all the required steps for ssh connection.
            if is_path_abs(data_directory):
                dumps_directory = data_directory
            else:
                dumps_directory = os.path.join(cwd, data_directory)
            cmd1 = "eval $(ssh-agent) > /dev/null && DISPLAY=1 SSH_ASKPASS='./x' ssh-add -k >/dev/null 2>&1" \
                   " .ssh/id_rsa_pipeline < /dev/null"
            cmd2 = f"ssh-keyscan -H {self.server_abbreviation} >> ~/.ssh/known_hosts"
            cmd3 = "echo Uploading files to the server..."
            cmd4 = f"scp -r {dumps_directory} {self.server}:~/{self.data_folder}/{self.container}"
            self._subprocess_cmd(f"{cmd1}; {cmd2}; {cmd3}; {cmd4}", cwd=home_dir)
            print('Loading files into the database...')
            # executing shell scripts.
            self._execute_set_of_shell_scripts(cwd=home_dir, eval_cmd=cmd1, data_directory=data_directory)
            # loading graphs
            self._execute_loading_script(cwd=home_dir, eval_cmd=cmd1)
            print('Data have been loaded. Running validation now...')
            self._execute_set_of_validation_scripts(cwd=home_dir, eval_cmd=cmd1, data_directory=data_directory)
            # executing cleaner script.
            print('Validation has ended. Cleaning directories...')
            self._execute_cleaner_script(cwd=home_dir, eval_cmd=cmd1)
            # killing processes associated with ssh-agent
            self._subprocess_cmd(command="kill -15 $(ps aux | grep 'ssh-agent' | awk '{print $2}')",
                                 cwd=home_dir, stdout=True)
            # removing redundant files.
            self._subprocess_cmd("rm -r vto", cwd=pathlib.Path.home())
        else:
            print('Functionality is currently not implemented for non-Unix bases systems!')
