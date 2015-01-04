all: unittest whiteboxtest check_convention

clean:
	rm -fr build dist yumcache.egg-info

check_convention:
	pep8 . --max-line-length=109

unittest:
	PYTHONPATH=. python -m unittest yumcache.tests.test_growingblob
	
whiteboxtest:
	PYTHONPATH=. python -m unittest yumcache.tests.test_whitebox

install:
	-yes | sudo pip uninstall yumcache
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo python setup.py install
	test -e /etc/yumcache.config || sudo cp yumcache.config /etc/yumcache.config
	if grep -i ubuntu /etc/os-release >/dev/null 2>/dev/null; then make install_service_upstart; else make install_service_systemd; fi

install_service_systemd:
	sudo cp yumcache.service /usr/lib/systemd/system/yumcache.service
	sudo systemctl enable yumcache.service
	-sudo systemctl stop yumcache
	if ["$(DONT_START_SERVICE)" == ""]; then sudo systemctl start yumcache; fi

install_service_upstart:
	sudo cp upstart_yumcache.conf /etc/init/yumcache.conf
	if ["$(DONT_START_SERVICE)" == ""]; then sudo service yumcache start; fi

uninstall:
	-sudo systemctl stop yumcache
	-sudo systemctl disable yumcache.service
	-sudo rm -f /usr/lib/systemd/system/yumcache.service /etc/init/yumcache.conf
	-yes | sudo pip uninstall yumcache
	echo "CONSIDER ERASING /var/lib/yumcache, /etc/yumcache.config"
