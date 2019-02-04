#!/bin/sh

# Stop on first error
set -e

apk add build-base

# setup cache, include setuptools as that means we have to setup everything
if ! [ -e .local ]; then
  echo "Setting up cache"
  mkdir -p .local
fi

if ! [ -e venv ]; then
  echo "Setting up pip"
  python -m venv venv
  source venv/bin/activate
  pip install --upgrade pip setuptools
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

# Install pdflatex
apk add texlive

# Install necessary latex packages
echo Installing necessary LaTeX packages
if ! [ -e .local/tex_packages ]; then
  echo Packages not present yet, downloading them
  mkdir .local/tex_packages
  mkdir standalone
  cd standalone
  wget -q http://mirrors.ctan.org/install/macros/latex/contrib/standalone.tds.zip
  unzip -qq standalone.tds.zip
  cd ..
  cp -r standalone/* .local/tex_packages/
  rm -rf standalone
  rm -f standalone.tds.zip
fi

mkdir `kpsewhich -var-value TEXMFHOME`
cp -r .local/tex_packages/* `kpsewhich -var-value TEXMFHOME`/
texhash `kpsewhich -var-value TEXMFHOME`
echo Installed packages, using `kpsewhich standalone`

# Install pdf2svg
if ! [ -e .local/bin/pdf2svg ]; then
  echo Installing pdf2svg
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
else
  echo Using pdf2svg in `which pdf2svg`
fi

if ! [ -e .local/bin/pandoc ]; then
  echo Installing pandoc
  wget -qO- https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux.tar.gz | tar -xvzf - --strip-components 1 -C .local
  echo Installed pandoc to `which pandoc`
else
  echo Using pandoc in `which pandoc`
fi
