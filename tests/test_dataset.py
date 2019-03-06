import unittest
import pandas as pd
from frame2package import Dataset, Concept


class DatasetTestCase(unittest.TestCase):
    def setUp(self):
        data = [
            {
                'country': 'Sweden',
                'capital': 'Stockholm',
                'year': 2000,
                'population': 9_000_000
            },
            {
                'country': 'Sweden',
                'capital': 'Stockholm',
                'year': 2019,
                'population': 10_000_000
            },
            {
                'country': 'Norway',
                'capital': 'Oslo',
                'year': 2000,
                'population': 5_000_000
            },
            {
                'country': 'Norway',
                'capital': 'Oslo',
                'year': 2019,
                'population': 6_000_000
            },
        ]

        concepts = [
            {
                'concept': 'country',
                'concept_type': 'entity_domain'
            },
            {
                'concept': 'capital',
                'concept_type': 'string'
            },
            {
                'concept': 'population',
                'concept_type': 'measure'
            },
            {
                'concept': 'year',
                'concept_type': 'time'
            }
        ]

        self.data = data
        self.concepts = concepts
        self.dataset = Dataset(pd.DataFrame(data), concepts)

    def test_has_concepts(self):
        self.assertTrue(hasattr(self.dataset, 'concepts'))

    def test_has_entities(self):
        self.assertTrue(hasattr(self.dataset, 'entities'))

    def test_has_tables(self):
        self.assertTrue(hasattr(self.dataset, 'tables'))

    def test_has_data(self):
        self.assertTrue(hasattr(self.dataset, 'data'))

    def test_data_is_frame(self):
        self.assertTrue(type(self.dataset.data) is pd.DataFrame)

    def test_concept_type(self):
        self.assertTrue(all([type(x) is Concept
                        for x in self.dataset.concepts]))

    def test_has_correct_number_of_entities(self):
        self.assertEqual(len(self.dataset.entities), 1)

    def test_fails_if_missing_concepts(self):
        data = pd.DataFrame(self.data)

        def create_dataset_with_missing_concepts():
            return Dataset(data, self.concepts[:-1])

        self.assertRaises(ValueError, create_dataset_with_missing_concepts)

    def test_creates_correct_table_name(self):
        table_name = self.dataset.tables[0][0]
        expected = 'ddf--datapoints--population--by--country--year.csv'
        self.assertEqual(table_name, expected)

    def test_creates_correct_table_size(self):
        self.assertEqual(self.dataset.tables[0][1].shape, (4, 3))

    def test_records_extra_string_concepts(self):
        self.assertIn('capital', self.dataset.concepts)
