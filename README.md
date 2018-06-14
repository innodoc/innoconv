# innoConv

Converter for interactive educational content.

## Installation

It is recommended to install innoConv in a [virtual environment](https://docs.python.org/3/library/venv.html).

```sh
# Create a virtual environment in a place of your choice
$ python3 -m venv /path/to/virtual/environment
# Activate venv
$ source /path/to/virtual/environment/bin/activate
# Install into venv using pip
$ pip install --process-dependency-links -e git+https://gitlab.tubit.tu-berlin.de/innodoc/innoconv.git#egg=innoconv
```

The ``innoconv`` command is now available.

You can add ``source /path/to/virtual/environment/bin/activate`` to your
``.bashrc`` (or similar file) to make ``innoconv`` available automatically.

## Usage

*TODO: update later*

Please [build the documentation](#documentation) and read the section *Usage*.

## Development

### Setup environment

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ ./setup.py develop
```

### Commands

#### Build tub_base

##### JSON

Get the content source code and convert it to JSON.

```sh
$ git clone -b innoconv git@gitlab.tubit.tu-berlin.de:innodoc/tub_base
$ innoconv tub_base
```

##### HTML (for debugging/development)

```
$ innoconv -d tub_base
```

#### Linting

Adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/). Before pushing
code please run lint and fix **all** problems.

```sh
$ ./setup.py lint
```

#### Tests

```sh
$ ./setup.py test
```

#### Build HTML coverage report

Do this after calling `./setup.py test`.

```sh
$ ./setup.py coverage
```

#### Documentation

```sh
$ ./setup.py build_doc
```

You can find the documentation in `build/sphinx`.
