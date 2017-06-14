import os

from setuptools import setup, find_packages

from etc.get_git_version import get_version


def read(fname):
    readme_file_path = os.path.join(os.path.dirname(__file__), fname)

    if os.path.exists(readme_file_path) and os.path.isfile(readme_file_path):
        readme_file = open(readme_file_path)
        return readme_file.read()
    else:
        return "The SoftFIRE Experimenter Manager"


packages = find_packages()

setup(
    name="experiment-manager",
    version=get_version(),
    author="Lorenzo Tomasini",
    author_email="lorenzo.tomasini@gmail.com",
    description="The SoftFIRE Experimenter Manager",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk experiment manager softfire tosca openstack rest",
    url="http://softfire.eu/",
    packages=packages,
    scripts=["experiment-manager"],
    install_requires=[
        'tosca-parser',
        'bottle',
        'beaker',
        'bottle-cork',
        'sqlalchemy',
        'grpcio',
        'dateparser',
        'pyOpenSSL',
    ],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Bottle",
        "Framework :: AsyncIO",

    ]
)
