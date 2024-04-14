from setuptools import find_packages, setup

setup(
    name='tl_simplification',
    packages=find_packages(include=['tl_simplification', 'tl_simplification.*']),
    version='0.1.0',
    description='This library offers functionalities for the simplification of LTLf formulas',
    author='Paul Manfred Reisenberg',
    install_requires=[],
    setup_requires=[]
)