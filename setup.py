from setuptools import setup

setup(
    name='innoConv',
    version='0.1',
    author='innoCampus',
    author_email='dietrich@math.tu-berlin.de',
    entry_points={
        'console_scripts': [
            'mintmod_filter = mintmod_filter.__main__:main',
        ],
    },
    packages=[
        'mintmod_filter',
    ],
    license='GPLv3',
    long_description=open('README.md').read(),
    setup_requires=[
        'green',
    ],
)
