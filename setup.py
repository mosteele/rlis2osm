from setuptools import find_packages, setup

setup(
    name='rlis2osm',
    version='0.2.0',
    author='Grant Humphries',
    dependency_links=[
        'git+https://github.com/grant-humphries/ogr2osm.git#egg=ogr2osm-0.1.0'
    ],
    description='',
    entry_points={
        'console_scripts': [
            'ogr2osm = ogr2osm.ogr2osm:main',
            'rlis2osm = rlis2osm.main:main'
        ]
    },
    extras_require=dict(
        test=['pprofile>=1.9.2']
    ),
    install_requires=[
        'fiona>=1.6.1',
        'gdal>=1.11.3',
        'ogr2osm>=0.1.0',
        'shapely>=1.5.16',
        'titlecase>=0.8.1'
    ],
    license='GPL',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['rlis2osm.tests*']),
    url='https://github.com/grant-humphries/rlis2osm'
)
