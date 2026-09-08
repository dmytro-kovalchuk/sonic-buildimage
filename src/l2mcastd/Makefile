.DEFAULT_GOAL := $(DEST)/l2mcastd.deb

$(DEST)/l2mcastd.deb:
	rm -rf build
	mkdir -p build/usr/bin build/DEBIAN
	install -m 0755 l2mcastd.py build/usr/bin/l2mcastd
	echo "Package: l2mcastd" > build/DEBIAN/control
	echo "Version: 1.0.0" >> build/DEBIAN/control
	echo "Section: net" >> build/DEBIAN/control
	echo "Priority: optional" >> build/DEBIAN/control
	echo "Architecture: amd64" >> build/DEBIAN/control
	echo "Maintainer: SONiC" >> build/DEBIAN/control
	echo "Description: L2MC Python Daemon" >> build/DEBIAN/control
	dpkg-deb --build --root-owner-group build l2mcastd.deb
	mkdir -p $(DEST)
	mv l2mcastd.deb $(DEST)/

clean:
	rm -rf build l2mcastd.deb