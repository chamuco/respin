export SHELL = sh
PACKAGE = respin-deb
VERSION = 1.0.0-1
COPYRIGHTYEAR = 2015
AUTHOR = Respin Team
EMAIL = aicra@linuxrespin.org

all: debian

debian: 
	[ ! -d ./build/debian/ ] || rm -r ./build/debian/
	mkdir -p ./build/debian/
	mkdir -p ./dist
	
	cp -r src/* ./build/debian/
	
	./tools/debian-package.sh "$(PACKAGE)" "$(VERSION)" "$(AUTHOR)" "$(EMAIL)" "all"


clean:
	rm -rf dist
	rm -rf build

