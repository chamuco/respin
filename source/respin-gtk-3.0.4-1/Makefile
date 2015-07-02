export SHELL = sh
PACKAGE = respin-gtk
VERSION = 3.0.4-1
COPYRIGHTYEAR = 2012
AUTHOR = Respin Team
EMAIL = aicra@faqlinux.com

all: debian

debian: translations
	[ ! -d ./build/debian/ ] || rm -r ./build/debian/
	sed -i 's/APP_VERSION = ".*"/APP_VERSION = "'$(VERSION)'"/' src/respin-gtk.py
	mkdir -p ./build/debian/usr/bin
	mkdir -p ./build/debian/usr/share/applications/
	mkdir -p ./build/debian/usr/share/respin-gtk/
	mkdir -p ./build/debian/usr/share/doc/respin-gtk/
	mkdir -p ./build/debian/usr/share/man/man1/
	mkdir -p ./dist
	
	cp src/respin-gtk.desktop ./build/debian/usr/share/applications/
	cp src/respin-gtk-kde.desktop ./build/debian/usr/share/applications/
	cp src/respin-gtk.py ./build/debian/usr/share/respin-gtk/
	cp src/respin-gtk.glade ./build/debian/usr/share/respin-gtk/
	cp src/respin-gtk ./build/debian/usr/bin/
	cp src/plymouth-preview ./build/debian/usr/bin/
	cp src/respin-gtk.1 ./build/debian/usr/share/man/man1/
	gzip -9 ./build/debian/usr/share/man/man1/respin-gtk.1
	cp src/README ./build/debian/usr/share/doc/respin-gtk/
	cp src/copyright ./build/debian/usr/share/doc/respin-gtk/
	cp src/changelog.Debian ./build/debian/usr/share/doc/respin-gtk/
	gzip -9 ./build/debian/usr/share/doc/respin-gtk/changelog.Debian

	cp -r locale ./build/debian/usr/share
	
	mkdir -p ./build/debian/usr/share/icons/hicolor/128x128/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/64x64/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/48x48/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/32x32/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/24x24/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/22x22/apps/
	mkdir -p ./build/debian/usr/share/icons/hicolor/16x16/apps/
	mkdir -p ./build/debian/usr/share/pixmaps/

	cp src/respin128.png ./build/debian/usr/share/icons/hicolor/128x128/apps/respin-gtk.png
	cp src/respin64.png ./build/debian/usr/share/icons/hicolor/64x64/apps/respin-gtk.png
	cp src/respin48.png ./build/debian/usr/share/icons/hicolor/48x48/apps/respin-gtk.png
	cp src/respin32.png ./build/debian/usr/share/icons/hicolor/32x32/apps/respin-gtk.png
	cp src/respin24.png ./build/debian/usr/share/icons/hicolor/24x24/apps/respin-gtk.png
	cp src/respin22.png ./build/debian/usr/share/icons/hicolor/22x22/apps/respin-gtk.png
	cp src/respin16.png ./build/debian/usr/share/icons/hicolor/16x16/apps/respin-gtk.png
	cp src/respin-gtk.png ./build/debian/usr/share/pixmaps/respin-gtk.png
	
	./tools/debian-package.sh "$(PACKAGE)" "$(VERSION)" "$(AUTHOR)" "$(EMAIL)" "all"

	
pot:
	[ -d ./po/ ] || mkdir ./po
	xgettext --default-domain="$(PACKAGE)" --output="po/$(PACKAGE).pot" src/*.py src/*.glade
	sed -i 's/SOME DESCRIPTIVE TITLE/Translation template for $(PACKAGE)/' po/$(PACKAGE).pot
	sed -i "s/YEAR THE PACKAGE'S COPYRIGHT HOLDER/$(COPYRIGHTYEAR)/" po/$(PACKAGE).pot
	sed -i 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/$(AUTHOR) <$(EMAIL)>, $(COPYRIGHTYEAR)/' po/$(PACKAGE).pot
	sed -i 's/Report-Msgid-Bugs-To: /Report-Msgid-Bugs-To: $(EMAIL)/' po/$(PACKAGE).pot
	sed -i 's/CHARSET/UTF-8/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE VERSION/$(VERSION)/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE/$(PACKAGE)/' po/$(PACKAGE).pot

update-po: pot
	for i in po/*.po ;\
	do \
	mv $$i $${i}.old ; \
	(msgmerge $${i}.old po/$(PACKAGE).pot | msgattrib --no-obsolete > $$i) ; \
	rm $${i}.old ; \
	done

translations: po/*.po
	mkdir -p locale
	@for po in $^; do \
		language=`basename $$po`; \
		language=$${language%%.po}; \
		target="locale/$$language/LC_MESSAGES"; \
		mkdir -p $$target; \
		msgfmt --output=$$target/$(PACKAGE).mo $$po; \
	done

clean:
	rm -rf dist
	rm -rf build
	rm -rf locale
