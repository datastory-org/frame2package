Usage
=====

Data format
-----------

In order for `frame2package` to create a datapackage, your data needs to adhere to the `tidy format <http://vita.had.co.nz/papers/tidy-data.pdf>`_:

1. Each variable forms a column.
2. Each observation forms a row.
3. Each type of observational unit forms a table.

Concepts
--------

In addition to the data itself, you also need to specify what types of variables the dataset consists of. The variables are referred to as `concepts`. Each concept has a name and a type.

.. code-block:: python

	concepts = [
		{
			'concept': 'country',
			'concept_type': 'entity_domain'
		},
		{
			'concept': 'gdp',
			'concept_type': 'measure'
		}
	]

Feel free to add additional information about your concepts:

.. code-block:: python

		{
			'concept': 'country',
			'concept_type': 'entity_domain',
			'description': 'ISO 3 code of countries'
		}

Disaggregation levels
---------------------

Some of your variables may have "total" entries. For instance, a `sex` column may have the unique values `male`, `female`, and `both`. In such cases, the DDF package will create separate datasets with and without the sex dimension. To enable this feature, specify what variables have "total" entries and what they are called in the data.

.. code-block:: python

	f2p = Frame2Package(df, concepts, totals={'sex': 'both'})

Entities
--------

For each concept of type `entity_domain`, frame2package will generate an entity file `ddf--entities--<entity-name>.csv` listing all the unique values for that entity.

If you want to add additional information about the values, such as a description column, create a dataframe with all the unique values for that entity and any additional columns and use `.update_entity` to add the information to the package.


.. code-block:: python

	# Assuming entity with name "sex" and values "M", "F", "B"
	
	# First copy the entity data
	sex = f2p.entities['sex'].copy()

	# Add a description column
	sex['description'] = ['Male', 'Female', 'Both']

	# Update the entity in the package
	f2p.update_entity(name='sex', data=sex)