# VE&MINT

## Development

### Setup environment

```
$ virtualenv --no-site-packages venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Linting

Adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/). Before pushing
code please run `make lint` and fix **all** linter and docstring problems.

### Documentation

```
$ make doc
```

You can find the documentation in `doc/_build/html`.
