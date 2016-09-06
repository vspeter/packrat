=============================
Packrat
=============================

A single interface for managing package lifecycle into apt, yum, and JSON repos.

see the documentation in the docs folder.  The docs can be compiled 
with sphinx to a local html directory or a pdf.

To build the docs::

  sudo apt install python3-sphinx texlive-latex-base texlive-latex-extra

the for local html::

  make docs-html

point your browser to the docs/build/index.html file

for pdf::

  make docs-pdf

This will build packrat.pdf

Enjoy

