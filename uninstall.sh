#!/usr/bin/env bash

# Should perform all necessary steps to uninstall the pipeline

# Clean out compiled binaries so they are recopied
function clean_bin() {
    for f in parallel* compare_* STAR fastqc fastx_* filter_* make_* sum* bam* bed* biom* blast* merg* 
    do
        rm -f temposeqcount/bin/${f}
    done
}

# Full clean build and egg
rm -rf build
rm -rf temposeqcount.egg-info

# Should we uninstall everything or just the pathdiscov package
# Takes a long time to reinstall numpy/matplotlib
if [ "$1" == "-full" ]
then
    # Remove all things that installer touches
    rm -rf temposeqcount/{lib,lib64,include,bin}
	rm -rf temposeqcount/{download}/*
    # Replace download from git
    #git checkout temposeqcount/download
else
    # Use pip to uninstall(If multiple version, may need to call more than once)
    # Ensure activated
    . temposeqcount/bin/activate
    while pip uninstall -y temposeqcount; do sleep 1; done;
    clean_bin
fi

echo "The pipeline should be uninstalled"
