all: ui

install:

clean:
	$(RM) -r build
	$(RM) dpkg
	$(RM) -r docs/build
	$(RM) -r ui/build

full-clean: clean
	dh_clean

ui_files := $(foreach file,$(wildcard ui/src/www/*),ui/build/$(notdir $(file)))

ui: ui/build/bundle.js $(ui_files)

ui/build/bundle.js: $(wildcard ui/src/frontend/component/*) ui/src/frontend/index.js
	cd ui && npm run build

ui/build/%:
	cp ui/src/www/$(notdir $@) $@

install:
	mkdir -p $(DESTDIR)var/www/packrat/api
	mkdir -p $(DESTDIR)var/www/packrat/ui
	mkdir -p $(DESTDIR)etc/apache2/sites-available
	mkdir -p $(DESTDIR)etc/packrat
	mkdir -p $(DESTDIR)usr/local/packrat/cron
	mkdir -p $(DESTDIR)usr/local/packrat/setup
	mkdir -p $(DESTDIR)usr/local/packrat/util

	install -m 644 api/packrat.wsgi $(DESTDIR)var/www/packrat/api
	install -m 644 ui/build/* $(DESTDIR)var/www/packrat/ui
	install -m 644 apache.conf $(DESTDIR)etc/apache2/sites-available/packrat.conf
	install -m 644 master.conf.sample $(DESTDIR)etc/packrat
	install -m 755 local/cron/* $(DESTDIR)usr/local/packrat/cron
	install -m 755 local/setup/* $(DESTDIR)usr/local/packrat/setup
	install -m 755 local/util/* $(DESTDIR)usr/local/packrat/util

	echo "window.API_HOST = 'http://' + window.location.hostname;" > $(DESTDIR)var/www/packrat/ui/env.js


test-distros:
	echo xenial

test-requires:
	echo python3 python3-django python3-psycopg2 python3-dateutil python3-magic postgresql-client postgresql python3-pip python3-pytest python3-pytest-cov python3-pytest-django python3-cinp

test-setup:
	pip3 install -e .
	cp master.conf.sample packrat/settings.py
	su postgres -c"psql -c \"CREATE ROLE packrat WITH LOGIN PASSWORD 'packrat' CREATEDB\""

test:
	py.test-3 -x --cov=packrat --cov-report html --cov-report term --ds=packrat.settings -vv packrat


dpkg-distros:
	echo xenial

dpkg-requires:
	echo dpkg-dev debhelper cdbs python3-dev python3-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	@echo $(shell ls ../packrat_*.deb):xenial


docs-distros:
	echo xenial

docs-requires:
	echo python3-sphinx texlive-latex-base texlive-latex-extra python3-django python3-magic python3-psycopg2

docs: docs-pdf

docs-file:
	echo Packrat.pdf:Packrat.pdf

docs-html:
	cd docs ; sphinx-build -b html -d build/doctree . build/html

docs-pdf:
	cd docs ; sphinx-build -b latex -d build/doctree . build/latex
	cd docs/build/latex ; pdflatex CInP.tex
	mv docs/build/latex/CInP.pdf .


.PHONY: all ui install clean dpkg-distros dpkg-requires dpkg-file
