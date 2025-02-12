import os
import logging
import datetime
import shutil

from modules.generic import generic
from modules.tools.rdfconvert import rdfconvert
from modules.utils.utils import remove_duplicated_lines_from_dump, perform_standard_postprocessing, \
    replace_expression, convert_encoding, remove_line_based_on_string


class GenericPostprocess(generic.Generic):
    """
    Subclass of Generic that deals with post-processing tasks.
    """
    def __init__(self):
        super().__init__()

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_generic_postprocess'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.propagate = False

    def run_postprocessor(self):
        """
        Function that executes all the post-processing actions for the Generic Pipeline.
        """
        print('########## Post-processing dumps...')
        dumps_dir = os.path.join(self.results_dir, self.dumps_dir)
        for dump in os.listdir(dumps_dir):
            print(f'Currently post-processing {dump}...')
            location = os.path.join(dumps_dir, dump)
            target_dir = os.path.join(self.results_dir, self.postprocess_dir)
            os.makedirs(target_dir, exist_ok=True)
            destination = os.path.join(target_dir, dump)
            remove_duplicated_lines_from_dump(input_path=location, output_path=destination,
                                              logger=self.logger)
            os.makedirs(os.path.join(self.results_dir, 'pp_specific'), exist_ok=True)
            input_path = os.path.join(self.results_dir, self.postprocess_dir, dump)
            output_path = os.path.join(self.results_dir, 'pp_specific', dump)
            perform_standard_postprocessing(input_path=input_path, output_path=output_path,
                                            logger=self.logger)
        self.clean_directories()

    def clean_directories(self):
        """
        Function that manages redundant files and directories after the post-processing actions.
        """
        # Cleaning all the initial dumps
        pp_folder = os.path.join(self.results_dir, self.postprocess_dir)
        pp_specific_folder = os.path.join(self.results_dir, 'pp_specific')
        if os.path.isdir(pp_specific_folder):
            shutil.rmtree(pp_folder)
            os.makedirs(pp_folder, exist_ok=True)
            for file in os.listdir(pp_specific_folder):
                shutil.move(os.path.join(pp_specific_folder, file), pp_folder)
            os.rmdir(pp_specific_folder)   # deleting an empty folder all files were moved.
        else:
            self.logger.info(f"The following folder was not found but was expected: {pp_specific_folder}.")

    def convert_to_turtle(self):
        """
        Function that converts a dump as n-triple into turtle.
        """
        pp_dir = os.path.join(self.results_dir, self.postprocess_dir)
        for file in os.listdir(pp_dir):
            if file.endswith(".nt"):
                print(f"Currently converting a {file} into turtle...")
                dump_path = os.path.join(pp_dir, file)
                turtle_path = os.path.join(pp_dir, f"{os.path.splitext(file)[0]}.ttl")
                converter = rdfconvert.RdfConvert()
                converter.serialize_to_ttl(input_path=dump_path, output_path=turtle_path)
                # remove redundant n-triples file
                print("Converting complete. Removing redundant n-triples file...")
                os.remove(dump_path)

    def replace_expression_postprocessing(self, to_be_replaced, replacement):
        """
        Function that replaces specific expression with a different one as a post-processing task.
        :param: to_be_replaced -> str
        :param: replacement -> str
        """
        print('########## Post-processing dumps - expression replacement ...')
        dumps_dir = os.path.join(self.results_dir, self.postprocess_dir)
        for dump in os.listdir(dumps_dir):
            os.makedirs(os.path.join(self.results_dir, 'pp_specific'), exist_ok=True)
            input_path = os.path.join(self.results_dir, self.postprocess_dir, dump)
            output_path = os.path.join(self.results_dir, 'pp_specific', dump)
            replace_expression(input_path=input_path, output_path=output_path, to_be_replaced=to_be_replaced,
                               replacement=replacement, logger=self.logger)
        self.clean_directories()

    def remove_line_containing_specific_string(self, target_string):
        """
        Function that removes specific line (triple) from dump file based on target string.
        :param: target_string -> str
        """
        print('########## Post-processing dumps - line removal based on provided string ...')
        dumps_dir = os.path.join(self.results_dir, self.postprocess_dir)
        for dump in os.listdir(dumps_dir):
            os.makedirs(os.path.join(self.results_dir, 'pp_specific'), exist_ok=True)
            input_path = os.path.join(self.results_dir, self.postprocess_dir, dump)
            output_path = os.path.join(self.results_dir, 'pp_specific', dump)
            remove_line_based_on_string(input_path, output_path, target_string=target_string, logger=self.logger)
        self.clean_directories()

    def adjust_encoding(self, target_encoding, source_encoding):
        """
        Function that changes file encoding to desired one.
        :param: target_encoding -> str
        :param: source_encoding -> str
        """
        print('########## Post-processing dumps - changing encoding ...')
        dumps_dir = os.path.join(self.results_dir, self.postprocess_dir)
        for dump in os.listdir(dumps_dir):
            os.makedirs(os.path.join(self.results_dir, 'pp_specific'), exist_ok=True)
            input_path = os.path.join(self.results_dir, self.postprocess_dir, dump)
            output_path = os.path.join(self.results_dir, 'pp_specific', dump)
            convert_encoding(input_path=input_path, output_path=output_path, target_encoding=target_encoding,
                             source_encoding=source_encoding,
                             logger=self.logger)
        self.clean_directories()
