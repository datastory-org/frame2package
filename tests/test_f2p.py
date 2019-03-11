import unittest
import time
import os
import shutil
import pandas as pd
from frame2package import Frame2Package


class Frame2PackageIoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
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

        f2p = Frame2Package()
        f2p.add_data(pd.DataFrame(data), concepts)
        path = f'ddf-package-test-{str(int(time.time()))}'
        f2p.to_package(path)

        self.f2p = f2p
        self.path = path

    def test_package_was_created(self):
        self.assertTrue(os.path.exists(self.path))

    def test_concepts_csv_was_created(self):
        concepts_path = os.path.join(self.path, 'ddf--concepts.csv')
        self.assertTrue(os.path.exists(concepts_path))

    def test_datapackage_json_was_created(self):
        datapackage_path = os.path.join(self.path, 'datapackage.json')
        self.assertTrue(os.path.exists(datapackage_path))

    def test_entities_csv_was_created(self):
        country_path = os.path.join(self.path, 'ddf--entities--country.csv')
        self.assertTrue(os.path.exists(country_path))

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.path)


class Frame2PackageDataTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        data = [
            {
                'country': 'Sweden',
                'region': 'Nordic',
                'population': 9_000_000
            },
            {
                'country': 'Sweden',
                'region': 'Nordic',
                'population': 10_000_000
            },
            {
                'country': 'Denmark',
                'region': 'Nordic',
                'population': 5_000_000
            },
            {
                'country': None,
                'region': 'Nordic',
                'population': 50_000_000
            },
        ]

        concepts = [
            {
                'concept': 'country',
                'concept_type': 'entity_domain'
            },
            {
                'concept': 'region',
                'concept_type': 'entity_domain'
            },
            {
                'concept': 'population',
                'concept_type': 'measure'
            }
        ]

        f2p = Frame2Package()
        f2p.add_data(pd.DataFrame(data), concepts)
        self.f2p = f2p

    def test_disaggregation_levels(self):
        fnames = [x[0] for x in self.f2p.data[0].tables]

        country_region = 'ddf--datapoints--population--by--country--region.csv'
        self.assertIn(country_region, fnames)

        region = 'ddf--datapoints--population--by--region.csv'
        self.assertIn(region, fnames)
