=================
alignment_summary
=================

Takes `*fastqLog.final.out` under the alignment output `tempFolder` and extract the necessary alignment
stat information and write to `*fastqLog.final.txt` for all sample

#. Generate `*fastqLog.final.txt` alignment stats  for each `*fastqLog.final.out` generated using `STAR` aligner duing alignment. 

Input
=====

#. Alignment output tempFolder that contains `*fastqLog.final.out` files
#. Generated `*fastqLog.final.txt` alignment stat for each sample


Output
======

#. `*fastqLog.final.txt` files for all `*fastqLog.final.out` files
#. All ouput are under `result/tempFolder`

