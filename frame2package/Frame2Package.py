import os
import shutil
import pandas as pd
import numpy as np
from ddf_utils import package
from ddf_utils.io import dump_json


class Frame2Package():
    """ Base class of frame2package."""

    def __init__(self):
        self.data = []
        self.entities = {}

    def add_data(self, data, concepts, totals={}):
        """
        Parameters
        ----------
        data : pandas.DataFrame
            The data to packaged.
        concepts : list
            List of dictionaries each with keys concept and
            concept_type for every concept in the dataset.
        totals : dict
            Mapping from variable name to name of value that
            refers to a total, e.g. "all genders" in a gender
            column.
        """
        if type(data) is not pd.DataFrame:
            msg = (f'Expected data to be of type pandas.DataFrame'
                   f', not {type(data)}')
            raise TypeError(msg)

        if type(concepts) is not list:
            msg = (f'Expected concepts to be of type list'
                   f', not {type(concepts)}')
            raise TypeError(msg)

        for concept in concepts:
            concept['concept'] = concept['concept'].lower()

        data.columns = [x.lower() for x in data.columns]

        self.data.append({
            'data': data,
            'concepts': concepts,
            'totals': totals
        })

        self.entities = self._build_entities()

    def _get_measures(self, concepts):
        def filt(x): return x['concept_type'] == 'measure'
        return filter(filt, concepts)

    def _get_dimensions(self, concepts, excludes=[]):
        def filt(x): return x['concept_type'] not in ['measure', 'string'] \
                     and x['concept'] not in excludes
        return filter(filt, concepts)

    def _get_entities(self, concepts):
        return filter(lambda x: x['concept_type'] == 'entity_domain',
                      concepts)

    def _build_dimensions_string(self, concepts, excludes=[]):
        s = [x['concept'] for x in self._get_dimensions(concepts, excludes)]
        return '--'.join(s)

    def _lowercase(self, df):
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.lower()
        return df

    def _build_datasets(self):
        """For each measure, build a dataset."""
        files = []

        for dataset in self.data:
            if len(dataset['data']) == 0:
                continue

            concepts = dataset['concepts']
            measures = list(self._get_measures(concepts))
            dimensions = list(self._get_dimensions(concepts))
            for m in measures:
                fname = f'ddf--datapoints--{m["concept"]}'
                cols = [x['concept'] for x in dimensions] + [m['concept']]
                file = dataset['data'][cols]
                file = file.replace('', np.nan)
                file = file.dropna(subset=[m['concept']])
                file = file.dropna(how='all', axis=1)
                file = self._lowercase(file)
                try:
                    pk = "--".join(file.columns.drop(m["concept"]))
                    fname = f'{fname}--by--{pk}.csv'
                except KeyError:
                    print('Empty data', m['concept'])
                    continue
                if len(file) > 0:
                    files.append({'data': file, 'fname': fname})

        return files

    def _build_entities(self):
        entities_dict = {}
        for dataset in self.data:
            if len(dataset['data']) == 0:
                continue
            entities = self._get_entities(dataset['concepts'])
            for ent in entities:
                data = dataset['data'][[ent['concept']]]
                data = data.drop_duplicates().dropna()
                data = self._lowercase(data)
                if ent['concept'] in self.entities:
                    entities_dict[ent['concept']] = \
                        (self.entities[ent['concept']]
                            .append(data, sort=True)
                            .drop_duplicates())
                else:
                    entities_dict[ent['concept']] = data

        return entities_dict

    def update_entity(self, name, data, id=None):
        """ Add extra information about an entity.

        Parameters
        ----------
        name : string
            The name of the entity.
        data : pandas.DataFrame
            All data about the given entity.
        """
        data[id] = data[id].str.lower()
        if name in self.entities and id is not None:
            self.entities[name] = self.entities[name].merge(data,
                                                            on=id,
                                                            how='outer')
        else:
            self.entities[name] = data

    def add_concepts(self, concepts):
        self.data.append({'data': [], 'concepts': concepts})

    def to_package(self, dirname):
        """ Save data to a DDF package.

        Parameters
        ----------
        dirname : str
            Name of the DDF directory to be created.
        """

        cwd = os.getcwd()
        dirpath = os.path.join(cwd, dirname)

        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)

        os.mkdir(dirpath)

        # Create data files
        datasets = self._build_datasets()
        for dataset in datasets:
            path = os.path.join(dirpath, dataset['fname'])
            dataset['data'].to_csv(path, index=False)

        # Create entity files
        for name, data in self.entities.items():
            path = f'ddf--entities--{name}.csv'
            path = os.path.join(dirpath, path)
            data.to_csv(path, index=False)

        # Create concepts file
        path = os.path.join(dirpath, 'ddf--concepts.csv')
        concepts = []
        for data in self.data:
            concepts = concepts + data['concepts']
        concepts = pd.DataFrame(concepts)

        # Add updated entity information
        add_concepts = []
        for k, v in self.entities.items():
            for c in v.columns:
                if c != k:
                    add_concepts.append({
                        'concept': c,
                        'concept_type': 'string'
                    })

        # Add extra data on concepts
        for c in concepts.columns:
            if c not in ['concept', 'concept_type']:
                add_concepts.append({
                    'concept': c,
                    'concept_type': 'string'
                })
        concepts = concepts.append(pd.DataFrame(add_concepts), sort=True)
        concepts = concepts.drop_duplicates(subset=['concept'])
        concepts.to_csv(path, index=False)

        # Create datapackage.json
        meta = package.create_datapackage(dirpath)
        dump_json(os.path.join(dirpath, 'datapackage.json'), meta)
