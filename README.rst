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

This will be the ``README`` for your project. For now, follow these instructions to get this project template set up correctly. Then, come back and replace the contents of this ``README`` with contents specific to your project.

Instructions
------------

Pip ``requirements[-dev].txt`` files vs. Setuptools ``install_requires`` Keyword
------------------------------------------------------------------

The difference in use case between these two mechanisms can be very confusing. The `pip requirements files`_ is the conventionally-named ``requirements.txt`` that sits in the root directory of many repositories, including this one. The `Setuptools install_requires keyword`_ is the list of dependencies declared in ``setup.py`` that is automatically installed by ``pip`` or ``easy_install`` when a package is installed. They have similar but distinct purposes:

``install_requires`` keyword
    Install runtime dependencies for the package. This list is meant to *exclude* versions of dependent packages that do not work with this Python package. This is intended to be run automatically by ``pip`` or ``easy_install``.

pip requirements file
    Install runtime and/or development dependencies for the package. Replicate an environment by specifying exact versions of packages that are confirmed to work together. The goal is to `ensure repeatability`_ and provide developers with an identical development environment. This is intended to be run manually by the developer using ``pip install -r requirements-dev.txt``.

For more information, see the answer provided by Ian Bicking (author of pip) to `this StackOverflow question`_.

.. _Pip requirements files: http://www.pip-installer.org/en/latest/requirements.html
.. _Setuptools install_requires keyword: http://pythonhosted.org/setuptools/setuptools.html?highlight=install_requires#declaring-dependencies
.. _ensure repeatability: http://www.pip-installer.org/en/latest/cookbook.html#ensuring-repeatability
.. _this StackOverflow question: http://stackoverflow.com/questions/6947988/when-to-use-pip-requirements-file-versus-install-requires-in-setup-py

   
Supported Python Versions
=========================

Python Project Template supports the following versions out of the box:

* CPython 2.6, 2.7, 3.3
* PyPy 1.9

CPython 3.0-3.2 may also work but are at this point unsupported. PyPy 2.0.2 is known to work but is not run on Travis-CI.

Jython_ and IronPython_ may also work, but have not been tested. If there is interest in support for these alternative implementations, please open a feature request!

.. _Jython: http://jython.org/
.. _IronPython: http://ironpython.net/

Licenses
========

The code which makes up this Python project template is licensed under the GPL license. Feel free to use it in your free software/open-source or proprietary projects.

The template also uses a number of other pieces of software, whose licenses are listed here for convenience. It is your responsibility to ensure that these licenses are up-to-date for the version of each tool you are using.

+------------------------+----------------------------------+
|Project                 |License                           |
+========================+==================================+
|Python itself           |Python Software Foundation License|
+------------------------+----------------------------------+
|argparse (now in stdlib)|Python Software Foundation License|
+------------------------+----------------------------------+
|Sphinx                  |Simplified BSD License            |
+------------------------+----------------------------------+
|Paver                   |Modified BSD License              |
+------------------------+----------------------------------+
|colorama                |Modified BSD License              |
+------------------------+----------------------------------+
|flake8                  |MIT/X11 License                   |
+------------------------+----------------------------------+
|mock                    |Modified BSD License              |
+------------------------+----------------------------------+
|pytest                  |MIT/X11 License                   |
+------------------------+----------------------------------+
|tox                     |MIT/X11 License                   |
+------------------------+----------------------------------+

Issues
======

Please report any bugs or requests that you have using the GitHub issue tracker!

Development
===========

This command line would just test Python 2.7.

Authors
=======

* Dereje Jima
