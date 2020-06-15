.PHONY: all clean test codetest install uninstall

all: chaps

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python
QUIET ?= @
SHELL=/bin/bash

GIT_COMMIT=$(shell git describe --always)
GIT_TAG=$(shell git describe --tags 2>/dev/null)

codetest:
	$(QUIET)flake8 . && echo OK

test:
	$(QUIET)echo "Runing tests..."
	$(QUIET)nosetests --with-coverage --cover-package=chapter_split --cover-html \
--cover-erase --cover-branches --verbose test # --cover-min-percentage=95
	$(QUIET)echo "Checking code formating..."
	$(QUIET)$(MAKE) --no-print-directory codetest

chaps: chapter_split/*.py # youtube_dl/*/*.py
	mkdir -p zip
	for d in chapter_split ; do \
	  mkdir -p zip/$$d ;\
	  cp -pPR $$d/*.py zip/$$d/ ;\
	done
	touch -t 200001010101 zip/chapter_split/*.py # zip/chapter_split/*/*.py
	find zip -type f -name "version.py" -exec sed -e "s/%%TAG%%/$(GIT_TAG)/g" -e "s/%%COMMIT%%/$(GIT_COMMIT)/g" -i {} \;
	mv zip/chapter_split/__main__.py zip/
	cd zip ; zip -q ../chaps chapter_split/*.py chapter_split/*/*.py __main__.py
	rm -rf zip
	echo '#!$(PYTHON)' > chaps
	cat chaps.zip >> chaps
	rm chaps.zip
	chmod a+x chaps

install: chaps
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 chaps $(DESTDIR)$(BINDIR)
	install -d $(DESTDIR)$(MANDIR)/man1
	install -m 644 doc/chaps.1 $(DESTDIR)$(MANDIR)/man1
	# install -d $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	# install -m 644 chaps.bash-completion $(DESTDIR)$(SYSCONFDIR)/bash_completion.d/chapsb

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/chaps
	if test -z "$(ls -A $(DESTDIR)$(BINDIR))" -a -d $(DESTDIR)$(BINDIR); then rmdir $(DESTDIR)$(BINDIR); fi
	rm -f $(DESTDIR)$(MANDIR)/man1/chaps.1
	if test -z "$(ls -A $(DESTDIR)$(MANDIR)/man1)" -a -d $(DESTDIR)$(MANDIR)/man1; then rmdir $(DESTDIR)$(MANDIR)/man1; fi
	if test -z "$(ls -A $(DESTDIR)$(MANDIR))" -a -d $(DESTDIR)$(MANDIR); then rmdir $(DESTDIR)$(MANDIR); fi
