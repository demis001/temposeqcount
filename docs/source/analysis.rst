====================
Running the temposeqcount
====================

.. _activate:

Activating the temposeqcount
=======================

You must always ensure that the virtualenv that you installed into during the
:doc:`install` is activated prior to running any portion of the pipeline.

You only have to do this if you have closed your terminal since the last time your
activated.

You need to specify the full path to the activate script such as

.. code-block:: bash

    $> . /path/to/temposeqcount/temposeqcount/bin/activate

When you ran the :doc:`install` the full path to activate should have been printed
during step #2

You can read more about what virtualenv is `here <https://virtualenv.pypa.io/en/latest/>`_

To get help
===========

.. code-block:: bash

    temposeqcount_cli -h 

If your fastq file has a `.fq` extension, make sure to rename to `.fastq` extension.
The name of the fastq file require the following nameing `SampleName_WellNumber_*.fastq.gz`.
Example: `A02B_S27_All_R1_001.fastq.gz`. The application uses `A02B_S27` as sample name while running

The manifest csv file that contain the probe information must have named `[ANYTHING]_manifest.csv`. Example: `160219_tox_3d_manifest.csv` 

Usage Examples
==============

You may use ``.fastq.gz``

Typical Usage
-------------


.. code-block:: bash

    temposeqcount_cli --flowchart outdir_pipeline_stages_to_run.ps -o outdir -f ./testData -p ./testData/160219_tox_3d_manifest.csv 

Manifest csv file (Probe information format)
-----------------------------------------------

The application uses this file to create indexed genome from the probe sequence 
and create suedo gtf file for annotation for the each probe. The format must be 
looks like this:

.. code-block:: bash

   Probe_ID,Attenuation_Correction_Factor,Gene_Symbol,Probe_Sequence,Main_RefSeq,RefSeqs_Targeted,Distance_from_5_Prime_End_of_mRNA
   A2M_12371,1,A2M,CTTCAGGTTCAACCAACAGAGGCTTGATGACTGTGTCTTTCCTTCCGTGT,NM_000014,NM_000014,2838

The required are `Probe_ID, Gene_Symbol and the Probe_Sequence`. Fill anything for the remaining column and it will not affect the analysis. But the csv file has to have  7 columns in a specified order. `Probe_ID` must be column 1, `Gene_Symbol` in column 3 and `Probe_Sequence` in column 4. The header must be named the same way. 

