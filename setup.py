import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="frame2package",
    version="0.0.1",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    description="Pandas dataframes to DDF packages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
		'pandas',
        'ddf_utils'
     ],
)