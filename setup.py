#!/usr/bin/env python


from setuptools import setup, find_packages


readme = open('README.md').read()
# history = open('HISTORY.rm').read()

setup(
    name='Marmitek-Gw',
    version='0.1',
    description=('A gateway to use the marmitek sensors'),
    long_description=readme,
    author='Clément Pallière',
    author_email='clement.palliere@hotmail.fr',
    url='https://github.com/pawmint/marmitek-gw',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ubigate>=0.0.2'
    ],
    license='Copyright',
    zip_safe=True,  # To be verified
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Environment :: Console',
        'License :: Other/Proprietary License',
        'Topic :: Scientific/Engineering',
    ],
)
