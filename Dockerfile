FROM python:3.7-alpine
LABEL maintainer="Mirko Dietrich <dietrich@math.tu-berlin.de>"

ENV PANDOC_VERSION 2.7
ENV PDF2SVG_VERSION 0.2.3
ENV PATH "/usr/local/texlive/2018/bin/x86_64-linuxmusl:${PATH}"

RUN set -xe && \
    apk update && \
    apk upgrade && \
    apk add --no-cache \
      build-base \
      cairo \
      poppler-glib

# add user/group to run as
RUN set -xe && \
    addgroup -S innoconv && \
    adduser -S -g innoconv innoconv

# install TeX Live with PGF/TikZ
RUN set -xe && \
    mkdir /tmp/install-tl-unx && \
    apk add --no-cache \
      perl \
      xz \
      wget && \
    wget -qO- http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
      | tar -xvzf - --strip-components=1 -C /tmp/install-tl-unx && \
    printf "%s\n" \
      "selected_scheme scheme-minimal" \
      "option_doc 0" \
      "option_src 0" \
      > /tmp/install-tl-unx/texlive.profile && \
    /tmp/install-tl-unx/install-tl --profile=/tmp/install-tl-unx/texlive.profile && \
    tlmgr install \
      collection-latex \
      pgf \
      standalone \
      xcolor \
      xkeyval && \
    rm -rf \
      /tmp/install-tl-unx \
      /usr/local/texlive/2018/tlpkg && \
    find /usr/local/texlive/2018 -name '*.log' -exec rm '{}' \; && \
    apk del \
      perl \
      xz \
      wget

# install pdf2svg
RUN set -xe && \
    apk add --no-cache \
      cairo-dev \
      poppler-dev && \
    wget -qO- https://github.com/dawbarton/pdf2svg/archive/v${PDF2SVG_VERSION}.tar.gz \
      | tar -xzf - -C /tmp && \
    cd /tmp/pdf2svg-${PDF2SVG_VERSION} && \
    ./configure --prefix=/usr/local && \
    make && \
    strip pdf2svg && \
    make install && \
    rm -rf /tmp/pdf2svg-${PDF2SVG_VERSION} && \
    apk del \
      cairo-dev \
      poppler-dev

# install pandoc
RUN wget -qO- https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux.tar.gz \
    | tar -xzf - --strip-components 2 -C /usr/local/bin pandoc-${PANDOC_VERSION}/bin/pandoc

# install innoconv
WORKDIR /tmp/innodoc-webapp
COPY --chown=innoconv:innoconv . ./
RUN set -xe && \
    ./setup.py install && \
    rm -rf /tmp/innodoc-webapp

# clean up
RUN set -xe && \
    apk del \
      build-base && \
    rm -rf \
      /var/cache/apk/* \
      /usr/share/man \
      /home/innoconv/.cache \
      /tmp/*

VOLUME /content /output

WORKDIR /content
USER innoconv
ENTRYPOINT ["innoconv"]
CMD ["--help"]
