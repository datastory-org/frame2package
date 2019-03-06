import unittest
from frame2package import Concept


class ConceptTestCase(unittest.TestCase):
    def setUp(self):
        concept = {
            'concept': 'country',
            'concept_type': 'entity_domain',
            'description': 'Name of country'
        }
        self.concept = Concept(concept)

    def test_has_name(self):
        self.assertTrue(hasattr(self.concept, 'name'))

    def test_has_correct_name(self):
        self.assertEqual(self.concept.name, 'country')

    def test_has_type(self):
        self.assertTrue(hasattr(self.concept, 'type'))

    def test_has_correct_type(self):
        self.assertEqual(self.concept.type, 'entity_domain')

    def test_if_entity(self):
        self.assertTrue(self.concept.is_entity)

    def test_equality(self):
        self.assertEqual(self.concept, 'country')

    def test_membership(self):
        self.assertIn('country', [self.concept])
