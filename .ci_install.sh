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
echo Installing Necessary LaTeX Packages
if ! [ -e .local/tex_packages ]; then
  echo packages not present yet, downloading them
  mkdir .local/tex_packages
  mkdir standalone
  cd standalone
  wget -q http://mirrors.ctan.org/install/macros/latex/contrib/standalone.tds.zip
  unzip standalone.tds.zip
  cd ..
  cp -rv standalone/* .local/tex_packages/
  rm -rf standalone
  rm -f standalone.tds.zip
fi

ln -s .local/tex_packages `kpsewhich -var-value TEXMFHOME`
texhash `kpsewhich -var-value TEXMFHOME`

# Install pdf2svg
if [ -e .local/bin/pdf2svg ]; then
  echo pdf2svg already installed, found in `which pdf2svg`
else
  echo Installing pdf2svg
  wget -q https://github.com/dawbarton/pdf2svg/archive/v0.2.3.tar.gz
  tar -zxf v0.2.3.tar.gz
  mv pdf2svg-0.2.3 pdf2svg
  rm -f v0.2.3.tar.gz
  cd pdf2svg
  ./configure --quiet --enable-silent-rules --prefix=`pwd`/../.local
  make
  make install
  cd ..
  rm -rf pdf2svg
  echo Installed pdf2svg to `which pdf2svg`
fi
