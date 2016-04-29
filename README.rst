=========================
 Python Project raslpipe
=========================


.. image:: https://travis-ci.org/demis001/raslpipe.png
   :target: https://travis-ci.org/demis001k/raslpipe

raslpipe is analysis pipeline for RASL-Seq project, this is the development stage right now. The project attempt to streamline the analysis with all its dependencies handled.

It is an all-in-one solution, the tools uses many python packages and other dependencies. But, user doesn't need to install the dependancies, the application handled that automatically.  They include:

* Paver_ for running miscellaneous tasks
* Setuptools_ for distribution (Setuptools and Distribute_ have merged_)
* Sphinx_ for documentation
* flake8_ for source code checking
* pytest_ for unit testing
* mock_ for mocking (not required by the template, but included anyway)
* tox_ for testing on multiple Python versions

If you are new to Python or new to creating Python projects, see Kenneth Reitz's `Hitchhiker's Guide to Python`_ for an explanation of some of the tools used here.

.. _Paver: http://paver.github.io/paver/
.. _Setuptools: http://pythonhosted.org/setuptools/merge.html
.. _Distribute: http://pythonhosted.org/distribute/
.. _merged: http://pythonhosted.org/setuptools/merge.html
.. _Sphinx: http://sphinx-doc.org/
.. _flake8: https://pypi.python.org/pypi/flake8
.. _pytest: http://pytest.org/latest/
.. _mock: http://www.voidspace.org.uk/python/mock/
.. _tox: http://testrun.org/tox/latest/
.. _Hitchhiker's Guide to Python: http://docs.python-guide.org/en/latest/


Project Setup
=============

This will be the ``README`` for your project. For now, follow these instructions to get this project template set up correctly. Then, the documentation will be available using Sphinx later on.

Instructions
------------

   
Supported Python Versions

=========================

The Project  supports the following versions out of the box:

* CPython 2.6, 2.7, 3.3
* PyPy 1.9

CPython 3.0-3.2 may also work but are at this point unsupported. PyPy 2.0.2 is known to work but is not run on Travis-CI.

Jython_ and IronPython_ may also work, but have not been tested. If there is interest in support for these alternative implementations, please open a feature request!

.. _Jython: http://jython.org/
.. _IronPython: http://ironpython.net/

Licenses
========

The code which makes up this raslpipe is licensed under the GPL license. Feel free to use it in your free software/open-source or proprietary projects.


Issues
======

Please report any bugs or requests that you have using the GitHub issue tracker!

Development
===========

This command line would just test Python 2.7.

Authors
=======

* Dereje Jima
