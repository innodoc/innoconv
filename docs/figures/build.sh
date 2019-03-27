#!/usr/bin/env bash

set -xe

for figure in *.tex; do
  pdflatex -halt-on-error -interaction=nonstopmode -file-line-error "${figure}"
  pdf2svg "${figure%.tex}.pdf" "${figure%.tex}.svg"
done
