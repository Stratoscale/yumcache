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
	-sudo pip uninstall yumcache
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
	sudo python -m yumcache.main setupDaemon
