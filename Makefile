.PHONY: all clean test codetest

all: chaps

PYTHON ?= /usr/bin/env python
QUIET ?= @
SHELL=/bin/bash

GIT_COMMIT=$(shell git describe --always --dirty)
$(info $(GIT_COMMIT))

codetest:
	$(QUIET)flake8 . && echo OK

test:
	$(QUIET)echo "Runing tests..."
	$(QUIET)nosetests --with-coverage --cover-package=chapter_split --cover-html \
--cover-erase --cover-branches --cover-min-percentage=95 --verbose test
	$(QUIET)echo "Checking code formating..."
	$(QUIET)$(MAKE) --no-print-directory codetest

chaps: chapter_split/*.py # youtube_dl/*/*.py
	mkdir -p zip
	for d in chapter_split ; do \
	  mkdir -p zip/$$d ;\
	  cp -pPR $$d/*.py zip/$$d/ ;\
	done
	touch -t 200001010101 zip/chapter_split/*.py # zip/chapter_split/*/*.py
	find zip -type f -name "*.py" -exec sed "s/%(VERSION)s/$(GIT_COMMIT)/g" -i {} \;
	mv zip/chapter_split/__main__.py zip/
	cd zip ; zip -q ../chaps chapter_split/*.py chapter_split/*/*.py __main__.py
	rm -rf zip
	echo '#!$(PYTHON)' > chaps
	cat chaps.zip >> chaps
	rm chaps.zip
	chmod a+x chaps
