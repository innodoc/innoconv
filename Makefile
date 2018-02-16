REPOBASE = https://gitlab.tu-berlin.de/stefan.born/VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/
WGET = wget --quiet

all: tub_base

tub_base: content/tub_base/de/tree_pandoc.html

content/tub_base/de/tree_pandoc.html: export PYTHONPATH=../../..
content/tub_base/de/tree_pandoc.html: content/tub_base/de/tree_pandoc.tex content/tub_base/de/module.tex mintmod_filter/*.py content/tub_base/de/de.tex
	cd content/tub_base/de && \
	pandoc -f latex+raw_tex \
		-t html5+empty_paragraphs \
		-s --mathjax \
		--filter=../../../mintmod_filter/__main__.py \
		-o $(notdir $@) \
		tree_pandoc.tex

content/tub_base/de/de.tex:
	$(WGET) $(REPOBASE)$(notdir $@) -O $@

content/tub_base/de/tree_pandoc.tex:
	mkdir -p content && \
	cd content && \
	git clone -b pandoc git@gitlab.tubit.tu-berlin.de:nplessing/tub_base.git

clean:
	rm -rf content doc/_build/html

lint:
	flake8 mintmod_filter

doc:
	$(MAKE) -C $@ html

.PHONY: all tub_base clean lint doc
