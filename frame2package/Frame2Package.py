import os
import pandas as pd
from ddf_utils import datapackage


class Frame2Package():
    def __init__(self, data, concepts):
        data.columns = [x.lower() for x in data.columns]
        for concept in concepts:
            concept['concept'] = concept['concept'].lower()

        self.data = data
        self.concepts = concepts

    def _get_indicators(self):
        filt = lambda x: x['concept_type'] == 'measure'
        return filter(filt, self.concepts)
    
    def _get_dimensions(self):
        filt = lambda x: x['concept_type'] != 'measure'
        return filter(filt, self.concepts)
    
    def _get_entities(self):
        filt = lambda x: x['concept_type'] == 'entity_domain'
        return filter(filt, self.concepts)
    
    def _build_dimensions_string(self):
        s = [x['concept'] for x in self._get_dimensions()]
        return '--'.join(s)
    
    def _build_datasets(self):
        """For each indicator, build a dataset."""
        datasets = []
        indicators = self._get_indicators()
        dimensions = self._get_dimensions()
        dimensions_string = self._build_dimensions_string()
        for i in indicators:
            fname = f'ddf--datapoints--{i["concept"]}--by--{dimensions_string}.csv'
            cols = [x['concept'] for x in dimensions] + [i['concept']]
            dataset = self.data[cols]
            datasets.append({'data': dataset, 'fname': fname})
        
        return datasets
    
    def _build_entities(self):
        entities_lists = []
        entities = self._get_entities()
        for ent in entities:
            data = self.data[[ent['concept']]].drop_duplicates()
            entities_lists.append(data)
        
        return entities_lists
    
    def to_package(self, dirname):
        cwd = os.getcwd()
        dirpath = os.path.join(cwd, dirname)
        
        if os.path.exists(dirpath):
            os.rmdir(dirpath)
        
        os.mkdir(dirpath)
        
        # Create data files
        datasets = self._build_datasets()
        for dataset in datasets:
            path = os.path.join(dirpath, dataset['fname'])
            dataset['data'].to_csv(path, index=False)
            
        # Create entity files
        entities = self._build_entities()
        for ent in entities:
            path = f'ddf--entities--{ent.columns[0]}.csv'
            path = os.path.join(dirpath, path)
            ent.to_csv(path, index=False)
            
        # Create concepts file
        path = os.path.join(dirpath, 'ddf--concepts.csv')
        pd.DataFrame(self.concepts).to_csv(path, index=False)

        # Create datapackage.json
        meta = datapackage.create_datapackage(dirpath)
        datapackage.dump_json(os.path.join(dirpath, 'datapackage.json'), meta)
