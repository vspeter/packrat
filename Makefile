VERSION := $(shell head -n 1 debian/changelog | awk '{match( $$0, /\(.+?\)/); print substr( $$0, RSTART+1, RLENGTH-2 ) }' | cut -d- -f1 )

all: build-ui
	./setup.py build

install: install-ui
	mkdir -p $(DESTDIR)/var/www/packrat/api
	mkdir -p $(DESTDIR)/etc/apache2/sites-available
	mkdir -p $(DESTDIR)/etc/packrat
	mkdir -p $(DESTDIR)/usr/lib/packrat/cron
	mkdir -p $(DESTDIR)/usr/lib/packrat/setup
	mkdir -p $(DESTDIR)/usr/lib/packrat/util

	install -m 644 api/packrat.wsgi $(DESTDIR)/var/www/packrat/api
	install -m 644 apache.conf $(DESTDIR)/etc/apache2/sites-available/packrat.conf
	install -m 644 master.conf.sample $(DESTDIR)/etc/packrat
	install -m 755 lib/cron/* $(DESTDIR)/usr/lib/packrat/cron
	install -m 755 lib/util/* $(DESTDIR)/usr/lib/packrat/util
	install -m 755 lib/setup/* $(DESTDIR)/usr/lib/packrat/setup

	./setup.py install --root $(DESTDIR) --install-purelib=/usr/lib/python3/dist-packages/ --prefix=/usr --no-compile -O0

version:
	echo $(VERSION)

clean: clean-ui
	./setup.py clean
	$(RM) -r build
	$(RM) dpkg
	$(RM) -r docs/build
	dh_clean || true

dist-clean: clean

.PHONY:: all install version clean dist-clean

ui_files := $(foreach file,$(wildcard ui/src/www/*),ui/build/$(notdir $(file)))

build-ui: ui/build/bundle.js $(ui_files)

ui/build/bundle.js: $(wildcard ui/src/frontend/component/*) ui/src/frontend/index.js
	# cd ui ; npm install
	cd ui && npm run build

ui/build/%:
	cp ui/src/www/$(notdir $@) $@

install-ui: build-ui
	mkdir -p $(DESTDIR)/var/www/packrat/ui/
	install -m 644 ui/build/* $(DESTDIR)/var/www/packrat/ui/
	echo "window.API_BASE_URI = 'http://' + window.location.hostname;" > $(DESTDIR)/var/www/packrat/ui/env.js

clean-ui:
	$(RM) -fr ui/build

.PHONY::

test-distros:
	echo ubuntu-xenial

test-requires:
	echo python3 python3-django python3-psycopg2 python3-dateutil python3-magic postgresql-client postgresql python3-pip python3-pytest python3-pytest-cov python3-pytest-django python3-pytest-mock python3-cinp

test-setup:
	pip3 install -e .
	cp master.conf.sample packrat/settings.py
	su postgres -c"psql -c \"CREATE ROLE packrat WITH LOGIN PASSWORD 'packrat' CREATEDB\""

test:
	py.test-3 -x --cov=packrat --cov-report html --cov-report term --ds=packrat.settings -vv packrat

.PHONY:: test-distros test-requires test-setup test

dpkg-distros:
	echo ubuntu-xenial

dpkg-requires:
	echo dpkg-dev debhelper cdbs python3-dev python3-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	@echo $(shell ls ../packrat_*.deb):xenial

.PHONY:: dpkg-distroy dpkg-requires dpkg-file

docs-distros:
	echo ubuntu-xenial

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

.PHONY:: docs-distros docs-requires docs docs-file docs-file docs-html docs-pdf
