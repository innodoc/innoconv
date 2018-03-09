# innoConv

Converter for interactive educational content.

## Development

### Setup environment

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Commands

#### Build tub_base

```
$ ./setup.py build_tub_base
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
