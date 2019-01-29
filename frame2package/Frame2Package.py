import os
import shutil
import pandas as pd
from ddf_utils import datapackage


class Frame2Package():
    """ Base class of frame2package.

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

    def __init__(self):
        self.data = []
        self.entities = {}

    def add_data(self, data, concepts, totals={}):
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

    def _get_indicators(self, concepts):
        filt = lambda x: x['concept_type'] == 'measure'
        return filter(filt, concepts)
    
    def _get_dimensions(self, concepts, excludes=[]):
        filt = lambda x: x['concept_type'] not in ['measure', 'string'] \
                         and x['concept'] not in excludes
        return filter(filt, concepts)
    
    def _get_entities(self, concepts):
        filt = lambda x: x['concept_type'] == 'entity_domain'
        return filter(filt, concepts)
    
    def _build_dimensions_string(self, excludes=[]):
        s = [x['concept'] for x in self._get_dimensions(excludes)]
        return '--'.join(s)
    
    def _build_datasets(self):
        """For each indicator, build a dataset."""
        files = []

        for dataset in self.data:
            concepts = dataset['concepts']
            indicators = list(self._get_indicators(concepts))
            dimensions = list(self._get_dimensions(concepts))
            dimensions_string = self._build_dimensions_string(concepts)

            for i in indicators:
                fname = f'ddf--datapoints--{i["concept"]}--by--{dimensions_string}.csv'
                cols = [x['concept'] for x in dimensions] + [i['concept']]
                file = dataset['data'][cols]
                files.append({'data': file, 'fname': fname})

            if not 'totals' in dataset:
                continue
            for k, v in dataset['totals'].items():
                dimensions = list(self._get_dimensions(concepts, excludes=[k]))
                dimensions_string = self._build_dimensions_string(concepts, excludes=[k])
                for i in indicators:
                    fname = f'ddf--datapoints--{i["concept"]}--by--{dimensions_string}.csv'
                    cols = [x['concept'] for x in dimensions] + [i['concept']]
                    file = dataset['data'][cols]
                    files.append({'data': file, 'fname': fname})
        
        return files
    
    def _build_entities(self):
        entities_dict = {}
        for dataset in self.data:
            entities = self._get_entities(dataset['concepts'])
            for ent in entities:
                data = dataset['data'][[ent['concept']]].drop_duplicates()
                if ent['concept'] in self.entities:
                    entities_dict[ent['concept']] = \
                        self.entities[ent['concept']].append(data).drop_duplicates()
                else:
                    entities_dict[ent['concept']] = data

        return entities_dict

    def update_entity(self, name, data):
        """ Add extra information about an entity.

        Parameters
        ----------
        name : string
            The name of the entity.
        data : pandas.DataFrame
            All data about the given entity.
        """
        self.entities[name] = data
        for col in data.columns:
            if col != name:
                self.concepts.append({
                    'concept': col,
                    'concept_type': 'string'
                })
    
    def to_package(self, dirname):
        """Save data to a DDF package.

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
        add_concepts = []
        for c in concepts.columns:
            if c not in ['concept', 'concept_type']:
                add_concepts.append({
                    'concept': c,
                    'concept_type': 'string'
                })
        concepts = concepts.append(pd.DataFrame(add_concepts))
        concepts = concepts.drop_duplicates(subset=['concept'])
        concepts.to_csv(path, index=False)

        # Create datapackage.json
        meta = datapackage.create_datapackage(dirpath)
        datapackage.dump_json(os.path.join(dirpath, 'datapackage.json'), meta)

    # def __repr__(self):
    #     return (f'<Frame2Package: {self.data.shape[0]} rows, '
    #             f'{len(self.concepts)} concepts>')
