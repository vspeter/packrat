Packrat
=============================

Packrat is a REST Like HTTP/JSON service the manages the life cycle of packages.
A package file (package file is a Packrat term for an individual package ie a
.deb, .rpm, .img, container file, binary blob, etc) may follow a track through
customizable stages, for exmaple, new, ci, dev, stage, prod.  Promotion from
one stage to the next can require a Cange Control.  When Change Control is
required, Packrat checks with the Change Control software to verify the package
is allowed to be promoted.  Thus building a package and promoting it to (in our
example list) stage can be fully automated, and then require specific Change
Controll processes to be followed to promote to prod.  All stages of promotion
and when an external Change Control controller is required is fully customizable.

Pacrat it's self is simply a Django website that stores the PackageFiles and
tracks their status and what mirror/repo they belong to.  An agent is required
to poll Packrat and build on disk repos such as a apt or YUM repo.  A sister
project packrat-agent is aviable to perform this task if desired, otherwise you
can comsume the web api and put it to disk as if fits your needs.



To build the docs::

  sudo apt install python3-sphinx texlive-latex-base texlive-latex-extra

the for local html::

  make docs-html

point your browser to the docs/build/index.html file

for pdf::

  make docs-pdf

This will build packrat.pdf

Enjoy
