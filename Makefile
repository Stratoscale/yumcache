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
	sudo python setup.py install
	sudo cp yumcache.service /usr/lib/systemd/system/yumcache.service
	test -e /etc/yumcache.config || sudo cp yumcache.config /etc/yumcache.config
	sudo systemctl enable yumcache
	-sudo systemctl stop yumcache
	sudo systemctl start yumcache

uninstall:
	-sudo systemctl stop yumcache
	-sudo systemctl disable yumcache
	-sudo rm -f /usr/lib/systemd/system/yumcache.service
	-yes | sudo pip uninstall yumcache
	echo "CONSIDER ERASING /var/lib/yumcache, /etc/yumcache.config"
