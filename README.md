[![build status](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/badges/master/build.svg)](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/commits/master) [![coverage report](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/badges/master/coverage.svg)](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/commits/master) [![Documentation Status](https://readthedocs.org/projects/innoconv/badge/?version=latest)](https://innoconv.readthedocs.io/en/latest/?badge=latest)

# innoConv

Converter for interactive educational content.

Please refer to the [documentation](https://innoconv.readthedocs.io/) for installation and usage.

## Quickstart

```sh
# Install innoconv locally using pip
$ pip install --user innoconv
# Convert some content
$ innoconv .
```

## Development

### Setup environment

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -e .[doc,lint,test]
```

### Commands

#### Build example content

Get the content source code and convert it to JSON.

```sh
$ git clone -b innoconv git@gitlab.tubit.tu-berlin.de:innodoc/tub_base
$ innoconv tub_base
```

#### Linting

Adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/).

```sh
$ tox -e lint
```

#### Tests

```sh
$ tox -e py37-unit
$ tox -e py37-integration
```

#### Build HTML coverage report

A coverage report will be created in `./htmlcov`.

```sh
$ tox -e py37-unit,cov-html
```

#### Documentation

You can find the documentation in `.tox/doc/tmp/html`.

```sh
$ tox -e doc
```
