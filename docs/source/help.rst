====
Help
====

Eventually you will run across some errors. No application/software is without bugs. Here we will compile all of the most common errors and what to look for to find out what is going on

.. _faq:

Frequently Asked Questions
==========================

#. How many CPU's does my computer have?

    This will print how many CPU Cores your computer has

    .. code-block:: bash

        lscpu | awk -F':' 'BEGIN {cpu=1} /(Core|Socket)/ {gsub(/ /,"",$0); cpu *= $2;} END {print cpu}'

#. I'm not sure if the pipeline completed sucessfully. How do I check the log files?

    The analysis folder has three two folders: logs and results. The result dir has the alignment tempFolder, Indexed probes Genome dir and  the the input files. An easy way to just look this three files:
    
    .. code-block:: bash

        ls outdir
              #resultDATA_alignment_summary.csv
              #resultDATA_alignment_summary.png
              #resultDATA_COUNT_countcombined.csv   - count file

    If you are looking for something specific, such as bam files. You can find hunder result/tempFolder

