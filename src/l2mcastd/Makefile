.DEFAULT_GOAL := $(DEST)/l2mcastd.deb

$(DEST)/l2mcastd.deb:
	mkdir -p build/usr/bin build/DEBIAN
	install -m 0755 l2mcastd.sh build/usr/bin/l2mcastd
	dpkg-deb --build --root-owner-group build l2mcastd.deb
	mkdir -p $(DEST)
	mv l2mcastd.deb $(DEST)/

clean:
	rm -rf build l2mcastd.deb