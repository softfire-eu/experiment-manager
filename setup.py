import os

from setuptools import setup, find_packages


def read(fname):
    readme_file_path = os.path.join(os.path.dirname(__file__), fname)

    if os.path.exists(readme_file_path) and os.path.isfile(readme_file_path):
        readme_file = open(readme_file_path)
        return readme_file.read()
    else:
        return "The SoftFIRE Experimenter Manager"


setup(
    name="experiment-manager",
    version="0.0.1",
    author="Lorenzo Tomasini",
    author_email="lorenzo.tomasini@gmail.com",
    description="The SoftFIRE Experimenter Manager",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk experiment manager softfire tosca openstack rest",
    url="http://softfire.eu/",
    packages=find_packages(),
    scripts=["experiment-manager"],
    install_requires=[
        'asyncio',
        'tosca-parser',
        'bottle',
        'beaker',
        'bottle-cork',
        'pyaml',
        'sqlalchemy',
        'grpcio',
    ],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",

    ],
    entry_points={
        'console_scripts': [
            'experiment-manager = eu.softfire.tub.main.ExperimentManager:start',
        ]
    }
)
