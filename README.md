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

### tox

Development for innoConv relies on [tox](https://tox.readthedocs.io/). It
handles virtualenv creation, running linters and test suites across different
Python versions and is also used in the CI pipeline.

Make sure to have it installed.

### Commands

For a exhaustive list of commands please have a look at `tox.ini`.

#### Using the innoconv command

Use the following to convert the base course.

```sh
$ git clone https://gitlab.tubit.tu-berlin.de/innodoc/tub_base.git
$ tox -e venv -- innoconv tub_base
```

#### Linting

Adhere to [code style black](https://github.com/ambv/black) and
[PEP8](https://www.python.org/dev/peps/pep-0008/).

```sh
$ tox -e linters
```

#### Tests

Run unit and integration tests.

```sh
$ tox -e py37-unit,py37-integration
```

#### HTML coverage report

A coverage report will be created in `./htmlcov`. Look at it using a browser.

```sh
$ tox -e py37-unit,cov-html,serve-cov
```

#### Documentation

After building you can find the documentation in `docs/build/html`.

```sh
$ tox -e docs
```

Serve the documentation to the browser for convenience.

```sh
$ tox -e serve-docs
```
