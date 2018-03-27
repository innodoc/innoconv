# Converting legacy mintmod content

Steps needed to adjust content sources to be used with innoConv.

All content needs to be UTF-8 encoded.

## Remove `\ifttm…\else…\fi` commands

`mintmod_ifttm` gets rid of all `\ifttm` commands.

Usage:

```shell
$ mintmod_ifttm < file_in.tex > file_out.tex
```

Automate on many files:

```
$ find . -name '*.tex' | xargs -I % sh -c 'mintmod_ifttm < % > %_changed && mv %_changed %'
```

The script will only cares about `\ifttm…\else…\fi` with an `\else` command.
There may be occurences of `\ifttm…\fi` (without `\else`!). Remove them
manually.

## Replace strings

### Special characters

- `\"a` → `ä`
- `\"o` → `ö`
- `\"u` → `ü`
- `\"A` → `Ä`
- `\"O` → `Ö`
- `\"U` → `Ü`
- `\"s` → `ß`

<!-- -->

- `"a` → `ä`
- `"o` → `ö`
- `"u` → `ü`
- `"A` → `Ä`
- `"O` → `Ö`
- `"U` → `Ü`

Automate:

```
find . -type f -name '*.tex' | xargs sed -i 's/\\"a/ä/g'
```

### `\IncludeModule`

`\IncludeModule{VBKM01}{vbkm01.tex}` becomes `\input{VBKM01/vbkm01.tex}`.

### Clean up code

Remove unused files.