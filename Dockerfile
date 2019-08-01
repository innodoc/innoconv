FROM python:3.7-alpine3.10
LABEL maintainer="Mirko Dietrich <dietrich@math.tu-berlin.de>"

ENV PANDOC_VERSION 2.7.3
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
      wget \
      xz

# install TeX Live with PGF/TikZ
# RUN set -xe && \
#     mkdir /tmp/install-tl-unx && \
#     wget -qO- http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
#       | tar -xzf - --strip-components=1 -C /tmp/install-tl-unx && \
#     cat /tmp/install-tl-unx/release-texlive.txt \
#       | head -n1 \
#       | grep -oE '\d{4}' \
#       > /tmp/tex-version.txt && \
#     echo "export PATH=/usr/local/texlive/$(cat /tmp/tex-version.txt)/bin/x86_64-linuxmusl:${PATH}" \
#       > /etc/profile.d/tex_path.sh && \
#     export PATH=/usr/local/texlive/$(cat /tmp/tex-version.txt)/bin/x86_64-linuxmusl:${PATH} && \
#     printf "%s\n" \
#       "selected_scheme scheme-minimal" \
#       "option_doc 0" \
#       "option_src 0" \
#       > /tmp/install-tl-unx/texlive.profile && \
#     echo $PATH && \
#     /tmp/install-tl-unx/install-tl --profile=/tmp/install-tl-unx/texlive.profile && \
#     tlmgr install \
#       collection-latex \
#       pgf \
#       standalone \
#       xcolor \
#       xkeyval && \
#     rm -rf /usr/local/texlive/$(cat /tmp/tex-version.txt)/tlpkg && \
#     find /usr/local/texlive/$(cat /tmp/tex-version.txt) -name '*.log' -exec rm '{}' \;

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
RUN wget -qO- https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux.tar.gz \
    | tar -xzf - --strip-components 2 -C /usr/local/bin pandoc-${PANDOC_VERSION}/bin/pandoc

# FROM $BASE_IMAGE

# RUN set -xe && \
#     apk update && \
#     apk upgrade && \
#     apk add --no-cache \
#       cairo \
#       poppler-glib \
#       texlive

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

# COPY --from=build /usr/local/bin /usr/local/bin

RUN rm -rf /var/cache/apk

VOLUME /content
WORKDIR /content
USER innoconv
ENTRYPOINT ["innoconv"]
CMD ["--help"]
