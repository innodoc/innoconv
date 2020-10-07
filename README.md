[![build status](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/badges/master/build.svg)](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/commits/master) [![coverage report](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/badges/master/coverage.svg)](https://gitlab.tubit.tu-berlin.de/innodoc/innoconv/commits/master) [![Documentation Status](https://readthedocs.org/projects/innoconv/badge/?version=latest)](https://innoconv.readthedocs.io/en/latest/?badge=latest)

# innoConv

Converter for interactive educational content.

Please refer to the [documentation](https://innoconv.readthedocs.io/) for installation and usage.

## Requirements

- [Python >=3.6](https://www.python.org/)
- [Pandoc](https://pandoc.org/)

For Ti<i>k</i>z support:

- [LaTeX](https://www.latex-project.org/)
- [pdf2svg](https://github.com/dawbarton/pdf2svg)

## Quickstart

```sh
# Install innoconv locally using pip
$ pip install --user innoconv
# Convert some content
$ innoconv /path/to/content
```

## Docker

The [Docker image](https://hub.docker.com/r/innodoc/innoconv) has all
dependencies bundled and works out-of-the-box. It allows you to call the
`innoconv` command inside a container.

```sh
$ docker run innodoc/innoconv --help
```

For passing content into and receiving the result from the container, you can
use a volume.

```sh
$ cd /path/to/content
$ docker run \
  -v $(pwd):/content \
  -u $(id -u $USER) \
  innodoc/innoconv .
```

## Development

### tox

Development for innoConv relies on [tox](https://tox.readthedocs.io/). It
handles virtualenv creation, running linters and test suites across different
Python versions and is also used in the CI pipeline.

Make sure to have it installed.

### Commands

For an exhaustive list of commands please have a look at `tox.ini`.

#### Using the innoconv command (dev version)

Spawn a shell in a development environment.

```sh
$ tox -e shell
```

Or directly start your current development version.

```sh
$ tox -e shell -- innoconv /path/to/content
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
$ tox -e py38-unit,py38-integration
```

#### HTML coverage report

A coverage report will be created in `./htmlcov` and served via HTTP.

```sh
$ tox -e py38-unit,cov-html,serve-cov
```

#### Documentation

After building you can find the documentation in `docs/build/html` and look at
it using a browser.

```sh
$ tox -e docs,serve-docs
```
