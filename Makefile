all:

clean:
	$(RM) -r build
	$(RM) dpkg
	$(RM) -r docs/build

full-clean: clean
	dh_clean

dpkg-distros:
	echo trusty

dpkg-requires:
	echo dpkg-dev debhelper cdbs python-dev python-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	@echo $(shell ls ../packrat_*.deb):trusty


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


.PHONY: all install clean dpkg-distros dpkg-requires dpkg-file
