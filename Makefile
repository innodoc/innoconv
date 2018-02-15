REPOBASE = https://gitlab.tu-berlin.de/stefan.born/VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/
WGET = wget --quiet

all: content/tub_base/de/tree_pandoc.html

content/tub_base/de/de.tex:
	echo $(WGET) $(REPOBASE)$(basename $@) -O $@
	$(WGET) $(REPOBASE)$(basename $@) -O $@

content/tub_base/de/tree_pandoc.tex:
	mkdir -p content && cd content && git clone -b pandoc git@gitlab.tubit.tu-berlin.de:nplessing/tub_base.git

content/tub_base/de/tree_pandoc.html: content/tub_base/de/tree_pandoc.tex content/tub_base/de/module.tex mintmod_filter/*.py mintmod_pandoc.tex content/tub_base/de/de.tex
	cd content/tub_base/de && pandoc -f latex+raw_tex -t html5+empty_paragraphs -s --mathjax --filter=../../../mintmod_filter/__main__.py -o $(basename $@) tree_pandoc.tex

clean:
	rm -rf content

.PHONY: all clean
