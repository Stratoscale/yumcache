all: unittest whiteboxtest_nonstandard check_convention

clean:
	rm -fr build dist yumcache.egg-info

check_convention:
	pep8 . --max-line-length=109

unittest:
	PYTHONPATH=. python -m unittest yumcache.tests.test_growingblob
	
whiteboxtest_nonstandard:
	PYTHONPATH=. python -m unittest yumcache.tests.test_whitebox

install:
	-yes | sudo pip uninstall yumcache
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
	sudo cp yumcache.service /usr/lib/systemd/system/yumcache.service
	test -e /etc/yumcache.config || sudo cp yumcache.config /etc/yumcache.config
	sudo systemctl enable yumcache.service
	-sudo systemctl stop yumcache
	if ["$(DONT_START_SERVICE)" == ""]; then sudo systemctl start yumcache; fi

uninstall:
	-sudo systemctl stop yumcache
	-sudo systemctl disable yumcache.service
	-sudo rm -f /usr/lib/systemd/system/yumcache.service
	-yes | sudo pip uninstall yumcache
	echo "CONSIDER ERASING /var/lib/yumcache, /etc/yumcache.config"
