import os
import shutil
import pandas as pd
import numpy as np
from ddf_utils import package
from ddf_utils.io import dump_json
from .Dataset import Dataset
from .Concept import Concept


class Frame2Package():
    """ Main class of frame2package."""

    def __init__(self):
        self.data = []

    def add_data(self, data, concepts):
        dataset = Dataset(data, concepts)
        self.data.append(dataset)

    def update_entity(self, name, data):
        for dataset in self.data:
            if name in dataset.entities:
                dataset.update_entity(name, data)

    def from_package(self, path):
        raise NotImplementedError

    @property
    def concepts(self):
        return [y for x in self.data for y in x.concepts]

    @property
    def entities(self):
        entities = {}
        for dataset in self.data:
            entities.update(dataset.entities)
        return entities

    def to_package(self, dirname, attrs={}):
        """ Save data to a DDF package.

        Parameters
        ----------
        dirname : str
            Name of the DDF directory to be created.
        attrs : dict
            Attributes to add/update in datapackage.json.
        """

        cwd = os.getcwd()
        dirpath = os.path.join(cwd, dirname)

        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)

        os.mkdir(dirpath)

        # Create data files
        for dataset in self.data:
            for table in dataset.tables:
                path = os.path.join(dirpath, table[0])
                table[1].to_csv(path, index=False)

        # Create entity files
        for entity_name, entity_items in self.entities.items():
            path = os.path.join(dirpath, f'ddf--entities--{entity_name}.csv')
            entity_items.to_csv(path, index=False)

        # Create concepts file
        path = os.path.join(dirpath, 'ddf--concepts.csv')
        concepts = pd.DataFrame([x.data for x in self.concepts])
        concepts = concepts.drop_duplicates(subset=['concept'])
        concepts.to_csv(path, index=False)

        # Create datapackage.json
        meta = package.create_datapackage(dirpath, **attrs)
        dump_json(os.path.join(dirpath, 'datapackage.json'), meta)

    def __repr__(self):
        return (f'<Frame2Package: {len(self.data)} datasets, '
                f'{len(self.concepts)} concepts, '
                f'{len(self.entities)} entities>')
