from setuptools import setup, Extension
from bear import version

entries = {'console_scripts': ['bear = bear.runtime:main']}

setup(
    name='bear',
    version=version.V,
    packages=['bear', 'bear.core'],
    entry_points=entries,
)
