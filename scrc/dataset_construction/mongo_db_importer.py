import json

import pymongo
import subprocess

from scrc.dataset_construction.dataset_constructor_component import DatasetConstructorComponent

import configparser

from root import ROOT_DIR
from scrc.utils.log_utils import get_logger


class MongoDBImporter(DatasetConstructorComponent):
    """
    Imports the csv data to a MongoDB and creates indexes on the fields most used for querying
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.logger = get_logger(__name__)

        self.indexes = json.loads(config['mongodb']['indexes'])

    def import_data(self):
        for lang in self.languages:
            # make sure the aggregator ran through successfully before
            self.import_file(self.clean_subdir / f"_{lang}.csv", lang)
            self.create_indexes(lang)

    def create_indexes(self, collection):
        collection = self.get_db()

        collection.create_index([('text', pymongo.TEXT)])  # always create the index on the text
        for index in self.indexes:
            collection.create_index(index)

    def import_file(self, file_to_import, collection):
        bash_command = f"mongoimport --host {self.ip} --port {self.port} -d {self.database} -c {collection} --type csv --file {file_to_import} --headerline"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.logger.info(output)
        self.logger.error(error)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(ROOT_DIR / 'config.ini')  # this stops working when the script is called from the src directory!

    kaggle_dataset_creator = MongoDBImporter(config)
    kaggle_dataset_creator.import_data()
