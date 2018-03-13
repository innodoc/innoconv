# innoConv

Converter for interactive educational content.

## Development

### Setup environment

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ ./setup.py develop
```

### Commands

#### Build tub_base

##### JSON

Get the content source code and convert it to JSON.

```
$ git clone -b pandoc git@gitlab.tubit.tu-berlin.de:innodoc/tub_base
$ innoconv tub_base
```

##### HTML (for debugging/development)

```
$ innoconv -d tub_base
```

#### Linting

Adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/). Before pushing
code please run lint and fix **all** problems.

```
$ ./setup.py lint
```

#### Tests

```
$ ./setup.py test
```

#### Build HTML coverage report

Do this after calling `./setup.py test`.

```
$ ./setup.py coverage
```

#### Documentation

```
$ ./setup.py build_doc
```

You can find the documentation in `build/sphinx`.
