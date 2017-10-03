#
# Makefile
# ddjima, 2016-12-01 10:09
#
INSTALL_PATH=.
help:
	@echo "		install"
	@echo "		Install python package"

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force {} +
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	unlink temposeqcount/lib64
	rm --force --recursive temposeqcount/bin
	rm --force --recursive temposeqcount/lib
	rm --force --recursive temposeqcount/include

lint:
	flake8 --exclude=.tox

install:
	pip install virtualenv --user && \
	python ./virtualenv-15.1.0/virtualenv.py temposeqcount && \
	. temposeqcount/bin/activate && \
	pip install -U  Paver sphinx_rtd_theme && \
	python setup.py install
docs:
	paver doc_html && \
	paver doc_man && \
	mkdir -p temposeqcount/man/man1 && \
	cp docs/build/man/* temposeqcount/man/man1

	




# vim:ft=make
#
