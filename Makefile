all:

clean:
	$(RM) -fr build
	$(RM) -f dpkg

full-clean: clean
	dh_clean

dpkg-distros:
	echo trusty

dpkg-requires:
	echo dpkg-dev debhelper cdbs

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	@echo $(shell ls ../packrat*.deb)

.PHONY: all install clean dpkg-distros dpkg-requires dpkg-file
