===============
map_to_probes
===============

Align all `*.fastq.gz` to the indexed probe sequences using `STAR` aligner.  It accept the directory  that contains `*.fastq.gz`, created `.gtf` files and the number of CPU to use (default =4). This steps run the alignment in parallel. For example if you run a 384 well plate, you will get 384 `fastq.gz` after demultiplexing. Depending on the CPU resource you passed these files aligned to the idexed probe sequences.   

#. It accept a directory that contain  `*.fastq.gz` files and generate `.bam` file for each sample under `tempFolder`
#. The result is found under `results/tempFolder`

Output
======

*  `.bam` file and the count files 
