all:

clean:
	$(RM) -fr build
	$(RM) -f dpkg

full-clean: clean
	dh_clean

dpkg-distros:
	echo trusty

dpkg-requires:
	echo dpkg-dev debhelper cdbs python-dev python-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc > /tmp/dpkg-build.log 2>&1
	touch dpkg

dpkg-file:
	@echo $(shell ls ../packrat*.deb)

.PHONY: all install clean dpkg-distros dpkg-requires dpkg-file