=========================
temposeqcount
=========================


.. image:: https://travis-ci.org/demis001/temposeqcount.png
   :target: https://travis-ci.org/demis001/temposeqcount

`temposeqcount` is analysis pipeline for TempO-Seq/RASL-Seq project that utilizes all next-generation  sequencing platforms such as RADSeq. TempO-Seq allow targeted sequencing to high-throughput sample  processing with the use of templates-dependent oligo ligation on 384 well plate. Knowing the number of reads mapped to the probes per well is the first step in the analysis. The application accept demultiplexed fastq folder and the manifest csv file that has probes and sample information to quantify the reads mapped to the probe per well in parallel.

The project attempt to streamline the analysis with all its dependencies handled.

It is an all-in-one solution, the tools uses many python packages and other dependencies. But,the application install the dependancies during installation.  It include:

* Setuptools_ for distribution (Setuptools and Distribute_ have merged_)
* Sphinx_ for documentation
* flake8_ for source code checking
* pytest_ for unit testing
* mock_ for mocking (not required by the template, but included anyway)
* tox_ for testing on multiple Python versions


Follow the insturciton under the install link.

Installation
------------

See `Installation <docs/source/install.rst>`_

Changelog
---------

See `Changelog <CHANGELOG.rst>`_
   
Supported Python Versions
-------------------------

The Project  supports the following versions out of the box:

* Python 2.6, 2.7
* Tested on Ubuntu 14.04, 15, 16.04 and CentOS-7

Application routine template
----------------------------

.. image:: raslpip_stages_to_run.png


Licenses
========

The code that makes temposeqcount is licensed under the GPL license. Feel free to use it in your free software/open-source.


Issues
======

Please report any bugs or requests that you have using the GitHub issue tracker!

Development
===========

I have tested on  Python 2.7.

Authors
=======

* Dereje Jima
