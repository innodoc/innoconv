#!/bin/sh

# Stop on first error
set -e

# Install necessary build tools
apk add build-base
apk add --no-cache\
  cairo-dev\
  cairo\
  cairo-tools\
  jpeg-dev\
  zlib-dev\
  freetype-dev\
  lcms2-dev openjpeg-dev\
  tiff-dev\
  tk-dev\
  tcl-dev\
  poppler-dev
pip install "flask==1.0.1" "CairoSVG==2.1.3"

# Install pdflatex
apk add texlive

# Install necessary latex packages
mkdir `kpsewhich -var-value TEXMFHOME`
mkdir standalone
cd standalone
wget http://mirrors.ctan.org/install/macros/latex/contrib/standalone.tds.zip
unzip standalone.tds.zip
cd ..
cp -rv standalone/* `kpsewhich -var-value TEXMFHOME`/
rm -rf standalone
rm -rf standalone.tds.zip
texhash `kpsewhich -var-value TEXMFHOME` --verbose

# Install pdf2svg
if [ -e .local/bin/pdf2svg ]; then
  echo Installing pdf2svg
  wget https://github.com/dawbarton/pdf2svg/archive/v0.2.3.tar.gz
  tar -zxf v0.2.3.tar.gz
  mv pdf2svg-0.2.3 pdf2svg
  rm -f v0.2.3.tar.gz
  cd pdf2svg
  ./configure --quiet --enable-silent-rules --prefix=`pwd`/../.local
  make
  make install
  cd ..
  rm -rf pdf2svg
else
  echo pdf2svg already installed, found in `which pdf2svg`
fi
