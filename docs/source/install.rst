============
Installation
============

.. _install-system-packages:


System Packages
===============

In order to installed developer tools you will need root privileges; that is, somebody who can use
su or sudo. The package may be already installed on your system

CentOS
------

.. code-block:: bash

    #> yum install openmpi openmpi-devel git  ghostscript python-devel zlib-devel ncurses-devel freetype-devel libpng-devel wget java-1.6.0 dejavu*
    #> yum groupinstall Development Tools
    
Ubuntu

------

.. code-block:: bash

    #> apt-get install openmpi-bin libopenmpi-dev python-dev  ghostscript git zlib1g-dev build-essential libncurses5	libncurses5-dev libpng12-dev libfreetype6-dev



Installation
============

#. Clone the repository

    .. code-block:: bash

        git clone $(eval echo https://$(read -p "Gitub username: " gu; echo $gu)@github.com/demis001/raslpipe.git)
        
    .. code-block:: bash
    
        cd raslpipe

#. Setup a `virtualenv <activate>` to install into and build documentation

    #. Install virtualenv python environment

        .. code-block:: bash

            wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.6.tar.gz -O- | tar xzf -
            python virtualenv-1.11.6/virtualenv.py raslpipe

    #. Activate the virtualenv to install everything into

        .. code-block:: bash

            source raslpipe/bin/activate
            pip install paver

    #. If you want to view/install the built html documentation

        .. code-block:: bash

            paver doc_html
            firefox docs/build/html/install.html#id1

    #. If you want to view/install the man page documentation

        .. code-block:: bash

            paver doc_man
            mkdir -p raslpipe/man/man1
            cp docs/build/man/* raslpipe/man/man1
            man raslpipe

#. Install the pipeline into the virtualenv

    .. code-block:: bash

        python setup.py install

#. Quick verify of a few thi
   ngs

    * See if required executables are available

        .. code-block:: bash

            # These should now all be in your path so should work
            apps=( STAR samtools fastqc R seqtk f2py raslpipe_cli)
            for p in ${apps[@]}; do $p --help 2>&1 | grep -qiE '\[main\]|usage|useage|qualifiers|DESCRIPTION|Syntax' && echo "$p ok" || echo "$p broken?"; done


#. Optional: Run a test dataset

    Anytime you run the pipeline you need to activate the pipeline first. If the pipeline is activated you will see 
    ```(raslpipe)``` in front of your prompt.
    
    If it is not activated:
    
    .. code-block:: bash
    
        source ~/raslpipe/raslpipe/bin/activate

    .. code-block:: bash

        raslpipe_cli --flowchart outdir_pipeline_stages_to_run.ps -o outdir -f ./testData -p ./testData/160219_tox_3d_manifest.csv
        

#. The END

