FROM python:3.10-alpine3.16
LABEL maintainer="Mirko Dietrich <dietrich@math.tu-berlin.de>"

ENV PANDOC_VERSION 2.19.2
ENV PDF2SVG_VERSION 0.2.3

RUN set -xe && \
    apk update && \
    apk upgrade && \
    apk add --no-cache \
      build-base \
      cairo \
      cairo-dev \
      perl \
      poppler-dev \
      poppler-glib \
      texlive \
      texmf-dist \
      texmf-dist-latexextra \
      texmf-dist-pictures \
      wget \
      xz

# install pdf2svg
RUN set -xe && \
    wget -qO- https://github.com/dawbarton/pdf2svg/archive/v${PDF2SVG_VERSION}.tar.gz \
      | tar -xzf - -C /tmp && \
    cd /tmp/pdf2svg-${PDF2SVG_VERSION} && \
    ./configure --prefix=/usr/local && \
    make && \
    strip pdf2svg && \
    make install && \
    rm -r /tmp/pdf2svg-${PDF2SVG_VERSION}

# install pandoc
RUN wget -qO- https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz \
    | tar -xzf - --strip-components 2 -C /usr/local/bin pandoc-${PANDOC_VERSION}/bin/pandoc

# install innoconv
COPY . /tmp/innoconv
RUN set -xe && \
    cd /tmp/innoconv && \
    ./setup.py install && \
    rm -rf /tmp/innoconv

# add user/group to run as
RUN set -xe && \
    addgroup -S innoconv && \
    adduser -S -g innoconv innoconv

RUN set -xe && \
    rm -rf /var/cache/apk && \
    apk del \
      build-base \
      cairo-dev \
      poppler-dev \
      wget \
      xz

VOLUME /content
WORKDIR /content
USER innoconv
ENTRYPOINT ["innoconv"]
CMD ["--help"]
