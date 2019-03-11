import numpy as np
import pandas as pd
from .Concept import Concept


class Dataset():
    """Wrapper for input datasets, resulting in one or more DDF tables.

    Parameters
    ----------
    data : pandas.DataFrame
        The data to packaged.
    concepts : list
        List of dictionaries each with keys concept and
        concept_type for every concept in the dataset.
    """
    entities_metadata = {}

    def __init__(self, data, concepts):
        if type(data) is not pd.DataFrame:
            msg = (f'Expected data to be of type pandas.DataFrame'
                   f', not {type(data)}')
            raise TypeError(msg)

        if type(concepts) is not list:
            msg = (f'Expected concepts to be of type list'
                   f', not {type(concepts)}')
            raise TypeError(msg)

        if not all([x in [y['concept'] for y in concepts]
                    for x in data.columns]):
            raise ValueError('Missing concepts.')
        self.data = data
        self.concepts = [Concept(x) for x in concepts]

    @property
    def entities(self):
        ent_map = {}
        entities = filter(lambda x: x.is_entity, self.concepts)

        for ent in entities:
            name = ent.name
            values = self.data[[name]]
            values = values.drop_duplicates()
            values = values.dropna(subset=[name])
            values = values.applymap(str.lower)

            if name in self.entities_metadata:
                metadata = self.entities_metadata[name]
                values = values.merge(metadata, on=name)

            ent_map[name] = values

        return ent_map

    def update_entity(self, name, data):
        if name not in self.entities:
            raise ValueError(f'Entity {name} does not exist')

        self.entities_metadata[name] = data
        for col in data.columns:
            if col in self.concepts:
                continue
            concept = {'concept': col, 'concept_type': 'string'}
            self.concepts.append(Concept(concept))

    def _filter_concepts(self, types):
        filt_func = lambda x: x.type in types
        return filter(filt_func, self.concepts)

    @property
    def tables(self):
        tables = []
        measures = self._filter_concepts(['measure'])
        pks = self._filter_concepts(['time', 'entity_domain'])

        for m in measures:
            fname = f'ddf--datapoints--{m.name}'
            cols = [x.name for x in pks] + [m.name]
            table = self.data[cols]
            table = table.replace('', np.nan)
            table = table.dropna(subset=[m.name])
            table = table.dropna(how='all', axis=1)
            table = table.applymap(lambda x: x.lower() if type(x) is str else x)

            # Missing primary keys interpreted as summaries
            # so we add extra tables
            if table.isnull().any().any():
                null_cols = list(table.columns[table.isnull().any()])
                for nc in null_cols:
                    nct = table[table[nc].isnull()]
                    nct = nct.drop(nc, axis=1)
                    pk = "--".join(sorted(nct.columns.drop(m.name)))
                    fnamenc = f'{fname}--by--{pk}.csv'
                    tables.append((fnamenc, nct))

                table = table.dropna(subset=null_cols)

            pk = "--".join(sorted(table.columns.drop(m.name)))
            fname = f'{fname}--by--{pk}.csv'

            if len(table) > 0:
                tables.append((fname, table))

        return tables

    def __repr__(self):
        return f'<Dataset: {list(self.data.columns)}>'
