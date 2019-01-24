.. frame2package documentation master file, created by
   sphinx-quickstart on Wed Jan 23 22:40:22 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Frame2Package
=============

Frame2Package is a helper library for converting Pandas dataframes to `DDF packages <https://open-numbers.github.io/ddf.html>`_. 

.. code-block:: python

	f2p = Frame2Package(data=df, concepts=concepts)
	f2p.to_package('my-ddf-folder')


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   usage
   api

