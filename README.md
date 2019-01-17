Frame2Package
=============

A helper library for converting Pandas dataframes to DDF packages.

## Usage

```python
import pandas as pd
import io
from frame2package import Frame2Package

# Load some sample data

data = """area	year	age	education	distribution
Bahamas	2000	15+	Total	1.0
Fiji	1970	80+	Total	1.0
Gabon	2025	20--64	Under 15	0.0
Brunei Darussalam	2045	All	Total	1.0
Thailand	1985	15+	Upper Secondary	0.07
"""

df = pd.read_csv(io.StringIO(data), sep='\t')

# Specify all the concepts in the dataset
# as per the DDF data format specification.

concepts = [
    {
        'concept': 'area',
        'concept_type': 'entity_domain'
    },
    {
        'concept': 'year',
        'concept_type': 'time'
    },
    {
        'concept': 'age',
        'concept_type': 'string'
    },
    {
        'concept': 'education',
        'concept_type': 'entity_domain'
    },
    {
        'concept': 'distribution',
        'concept_type': 'measure'
    },
]

# Initialize a Frame2Package object
f2p = Frame2Package(data=df, concepts=concepts)

# Save the package
f2p.to_package('sample-dataset')
```