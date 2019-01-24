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

    def __init__(self, data, concepts, totals={}):
        if type(data) is not pd.DataFrame:
            msg = (f'Expected data to be of type pandas.DataFrame'
                   f', not {type(data)}')
            raise TypeError(msg)

        if type(concepts) is not list:
            msg = (f'Expected concepts to be of type list'
                   f', not {type(concepts)}')
            raise TypeError(msg)

        data.columns = [x.lower() for x in data.columns]
        for concept in concepts:
            concept['concept'] = concept['concept'].lower()

        self.data = data
        self.concepts = concepts
        self.totals = totals
        self.entities = self._build_entities()

    def _get_indicators(self):
        filt = lambda x: x['concept_type'] == 'measure'
        return filter(filt, self.concepts)
    
    def _get_dimensions(self, excludes=[]):
        filt = lambda x: x['concept_type'] != 'measure' and \
                         x['concept'] not in excludes
        return filter(filt, self.concepts)
    
    def _get_entities(self):
        filt = lambda x: x['concept_type'] == 'entity_domain'
        return filter(filt, self.concepts)
    
    def _build_dimensions_string(self, excludes=[]):
        s = [x['concept'] for x in self._get_dimensions(excludes)]
        return '--'.join(s)
    
    def _build_datasets(self):
        """For each indicator, build a dataset."""
        datasets = []
        indicators = list(self._get_indicators())
        dimensions = list(self._get_dimensions())
        dimensions_string = self._build_dimensions_string()
        for i in indicators:
            fname = f'ddf--datapoints--{i["concept"]}--by--{dimensions_string}.csv'
            cols = [x['concept'] for x in dimensions] + [i['concept']]
            dataset = self.data[cols]
            datasets.append({'data': dataset, 'fname': fname})

        # Append datasets without totals
        # TODO: Explain this better...
        for k, v in self.totals.items():
            dimensions = list(self._get_dimensions(excludes=[k]))
            dimensions_string = self._build_dimensions_string(excludes=[k])
            for i in indicators:
                fname = f'ddf--datapoints--{i["concept"]}--by--{dimensions_string}.csv'
                cols = [x['concept'] for x in dimensions] + [i['concept']]
                dataset = self.data[cols]
                datasets.append({'data': dataset, 'fname': fname})
        
        return datasets
    
    def _build_entities(self):
        entities_dict = {}
        entities = self._get_entities()
        for ent in entities:
            data = self.data[[ent['concept']]].drop_duplicates()
            entities_dict[ent['concept']] = data
        
        return entities_dict

    def update_entity(self, name, data):
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
        concepts = pd.DataFrame(self.concepts)
        add_concepts = []
        for c in concepts.columns:
            if c not in ['concept', 'concept_type']:
                add_concepts.append({
                    'concept': c,
                    'concept_type': 'string'
                })
        concepts = concepts.append(pd.DataFrame(add_concepts))
        concepts.to_csv(path, index=False)

        # Create datapackage.json
        meta = datapackage.create_datapackage(dirpath)
        datapackage.dump_json(os.path.join(dirpath, 'datapackage.json'), meta)

    def __repr__(self):
        return (f'<Frame2Package: {self.data.shape[0]} rows, '
                f'{len(self.concepts)} concepts>')
