import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="frame2package",
    version="0.0.4",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    description="Pandas dataframes to DDF packages.",
    download_url="https://github.com/datastory-org/frame2package/archive/0.0.4.tar.gz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas>=0.23',
        'ddf_utils==0.6.4'
     ],
)