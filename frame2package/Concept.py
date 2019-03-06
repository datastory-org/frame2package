class Concept():
    """Simple wrapper around concept dicts.

    Parameters
    ----------
    data : dict
        Dictionary with mandatory keys `concept` and `concept_type`.
    """

    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data['concept']

    @property
    def type(self):
        return self.data['concept_type']

    @property
    def is_entity(self):
        return self.data['concept_type'] == 'entity_domain'

    def __eq__(self, value):
        return self.name == value

    def __repr__(self):
        name = self.data['concept']
        kind = self.data['concept_type']
        return f'<Concept: {name} ({kind})>'
