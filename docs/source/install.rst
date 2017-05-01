============
Installation
============

.. _install-system-packages:


System Packages
===============

In order to install developer tools you will need  a root privileges; that is, somebody who can use
su or sudo. The package may be already installed on your system

CentOS
------

.. code-block:: bash

    #> yum install git python-sphinx.noarch g++ ghostscript python-devel zlib-devel ncurses-devel freetype-devel libjpeg-turbo-utils.x86_64 libjpeg-turbo-devel.x86_64  libjpeg-turbo-static.x86_64 libpng-devel wget java-1.6.0 dejavu*
    #> yum groupinstall Development Tools
    #> yum install blas-devel.x86_64 blas-static.x86_64  blas.x86_64   blas64.x86_64 lapack-devel.x86_64 lapack-static.x86_64  lapack.x86_64 lapack64.x86_64
    #> yum bzip2.x86_64 bzip2-libs.x86_64  bzip2-devel.x86_64 perl-ExtUtils-Embed
Ubuntu 14.04
------------

I have tested on Ubuntu 14.04. STAR aligner require GLIBCXX_3.4.20, if your gcc version is less than 4.9. STAR will not properly install. Make sure your gcc version using "gcc -v", if it is upgrade it. The code shown below.

.. code-block:: bash
    
    #> sudo apt-get update
    #> sudo apt-get install python-dev g++ libjpeg-dev pkg-config ghostscript git gfortran zlib1g-dev build-essential libopenblas-base libopenblas-dev liblapack-dev python-sphinx libncurses5	libncurses5-dev libpng12-dev libfreetype6-dev
    #> sudo add-apt-repository ppa:ubuntu-toolchain-r/testsudo && sudo apt-get update && sudo apt-get install gcc-5

Check the version:

.. code-block:: bash

    #> strings /usr/lib/x86_64-linux-gnu/libstdc++.so.6 | grep GLIBCXX
   
Ubuntu 16.04 LTS (Xenial Xerus) 
-------------------------------

.. code-block:: bash
   #> sudo apt-get update
   #> sudo apt-get install python-dev g++ libjpeg-dev pkg-config ghostscript git gfortran zlib1g-dev build-essential libopenblas-base libopenblas-dev liblapack-dev python-sphinx libncurses5  libncurses5-dev libpng12-dev libfreetype6-dev


Installation
============

#. Clone the repository

    .. code-block:: bash

        git clone https://github.com/demis001/temposeqcount.git
        
    .. code-block:: bash
    
        cd temposeqcount


#. Setup a `virtualenv <activate>` to install into and build documentation

    #. Install temposeqcount in a virtualenv python environment

        .. code-block:: bash

            make install 


    #. Activate the virtualenv whenever you went to run temposeqcount_cli

        .. code-block:: bash

            source temposeqcount/bin/activate

     #. To install docs (optional)
        
        .. code-block:: bash
           
            paver doc_html && paver doc_man &&  mkdir -p temposeqcount/man/man1
            cp docs/build/man/* temposeqcount/man/man1

    #. If you want to view  the built html documentation (Optional)

        .. code-block:: bash

            firefox docs/build/html/install.html#id1 &

    #. If you want to view/install the man page documentation (Optional)

        .. code-block:: bash

            man temposeqcount


#. Quick verify of a few things

    * See if required executables are available

        .. code-block:: bash

            # These should now all be in your path so should work
            apps=( STAR samtools fastqc seqtk dot temposeqcount_cli)
            for p in ${apps[@]}; do $p --help 2>&1 | grep -qiE '\[main\]|usage|useage|qualifiers|DESCRIPTION|Syntax' && echo "$p ok" || echo "$p broken?"; done


            
#. Optional: Run a test dataset (make sure the virtualenv is active, else activate it as follows)

    Anytime you run the pipeline you need to activate the pipeline first. If the pipeline is activated you will see 
    ```(temposeqcount)``` in front of your prompt.
    
    If it is not activated:

    .. code-block:: bash
 
         source ~/temposeqcount/temposeqcount/bin/activate 

    Inputs:

         * `--flowchart` [file name to print the ps figure showing the workflow chart]
         * `-o`   [ Output directory name ]
         * `-f`  [Directory that contain `*.fastq.gz files`, rename your fastq files to `*_fastq.gz` for the script to work ]
         * `-p` [`*_manifest.csv` file that contains the probe information, see the format from test data]

    .. code-block:: bash

        # get detail help using 
        temposeqcount_cli -h

    Run test data and inspect the result folder:

    .. code-block:: bash

        temposeqcount_cli --flowchart outdir_pipeline_stages_to_run.ps -o outdir -f ./testData -p ./testData/160219_tox_3d_manifest.csv
        

#. The END

