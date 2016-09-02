#!/usr/bin/env python
import sys
from ruffus import *
import yaml
import time
import os
import helpers
from helpers import runCommand,isGzip
from os.path import (
    join, expanduser, expandvars,
    splitext,split, basename, dirname, exists
)
helpers.setup_shell_environment()
import tasks
import glob
#import pyprind
from  termcolor import colored
import datetime
is_64bits = sys.maxsize > 2**32
#import graphviz
if not is_64bits:
    print "Please upgrade your operating system to 64 bit, application such as diamond don't run on 32 bit"
    sys.exit(0)
options = helpers.get_options()
#logger_proxy, logging_mutex = helpers.make_logger(options, __file__)

basedir = os.path.relpath('./')
projectDir = options.outdir  # set output dir
proDir= os.path.basename(projectDir)
print proDir
inputDir = options.fastq_file
inputDir = os.path.abspath(inputDir)# get fastq.gz file
print inputDir
dir_name = basename(inputDir)
probe = os.path.abspath(options.probe_file)
probPath, probFile = os.path.split(probe)
print probe

#plateWall_bc = os.path.abspath(options.sample_sheet)
#pbpath,plateWallBC = os.path.split(plateWall_bc)
#print plateWall_bc

cpuNum = options.cpuNum
print cpuNum
logsDir = join(proDir, "logs")
resultDir = join(proDir, "result")
tempDir = join(resultDir, "tempFolder")
genomeDir = join(proDir, "result", "Genome")
print logsDir
print resultDir

# setup starting files
param = [
    #[inputFile, join(proDir, "input", inFile)],
    [probe, join(proDir, "result", probFile)]

]

@graphviz(height=1.8, width=2, label="Prepare\nanalysis")
@follows(mkdir(proDir,resultDir, logsDir,tempDir))
@files(param)
def prepare_analysis(input,output):
    """Copy the inputfiles to analysis dir
        -`input`: input file to copy to the outdir
        -`outfile`: output file name
    """
    stage1= "Stage1: Copy", input, " to ", output
    print colored(stage1, "green")
    result = tasks.copyFileToAnaFolder(input, output)
    return result


@graphviz(height=1.8, width=2, label="Prepare DB\nfiles")
@follows(prepare_analysis)
@transform(prepare_analysis, suffix("_manifest.csv"), ".fa")
def prepareDB_file(input_file, output_file):

    """docstring for prepareDB__file
    -`input_file`: A manifest probe csv file that contain probe sequences
    -`output_file`: A fasta output file that contain probe sequences
    """
    print colored("Stage 2: Creating DB file from probe file ...", "green")
    print input_file
    result =tasks.db_file(input_file, output_file)
    return result


@graphviz(height=1.8, width=2, label="Create\ngtf file")
@follows(prepare_analysis)
@transform(prepare_analysis, suffix("_manifest.csv"), ".gtf")
def create_gtf_file(input_file, output_file):
    """Create pseudo gtf file for all probes sequences
    `input_file`: A manifest csv file that contain probe information
    `output_file`: A pseudo gtf file that serve for annotation
    """
    print colored("Stage 3: Creating custom gtf file from manifest file ...", "green")
    print input_file
    result =tasks.create_gtf(input_file, output_file)
    return result

@graphviz(height=1.8, width=2, label="Index\nDB")
@follows(prepareDB_file)
@follows(mkdir(genomeDir))
@transform(prepareDB_file, suffix(".fa"), "SAindex")
def indexGenomeFile(input, output):
    """Index STAR genome index file
    `input`: Input probes fasta file
    `output`: SAindex file to check the completion of STAR genome index
    """
    #print input
    #print output
    base =  splitext(input)[0]
    base = base + ".gtf"
    print base
    gtfFile = base
    outputDir = proDir + "/result/Genome"
    print colored("Stage 4: Creating genome index file from the probe fasta file ....", "green")
    print input
    #print output
    #print cpuNum
    result = tasks.index_db_file(input, outputDir, cpuNum, gtfFile)
    return result

@graphviz(height=1.8, width=2, label="Map to\nprobes")
@follows(indexGenomeFile)
@follows(create_gtf_file)
@transform(join(inputDir, "*.fastq.gz"), suffix(".gz"),  ".bam")
def map_to_probes(fastq, output):
    """Map the fastq file to the indexed probe sequences. The fastq must be in the gzipped with the following extension. (*.fastq.gz)
    `fastq`: a dir that contains all *.fastq.gz file for the experment
    `output`: output .bam files and '*fastqReadPrepGene.out.tab' count files
    """
    outfile = basename(output)
    outfile = join(tempDir, outfile)
    suf = splitext(outfile)[0]
    outPrefix = os.path.abspath(suf)
    import re
    p=re.match(r'(.*)_manifest.csv', probFile, re.M|re.I)
    gtfF = p.group(1) + ".gtf"
    gtfFile = join(resultDir,gtfF)
    print tasks.comment()
    print colored("Stage 5: Map sequence fastq file to the indexed genome file ... ", "green")
    print fastq
    print output
    print genomeDir
    print outPrefix
    print gtfFile
    print tasks.comment()
    result = tasks.map_seq_to_probes(fastq, genomeDir, cpuNum, outPrefix, gtfFile)
    return result

@graphviz(height=1.8, width=2, label="Format\ncount data")
@follows(map_to_probes)
@transform(join(tempDir, "*fastqReadsPerGene.out.tab"), formatter(".tab"), ".txt")
def format_count(input,output):
    """Prepare the count file to merge to  a single file
    `input`: Count file from previous stage (*fastqReadsPerGene.out.tab)
    `output`: Formatted *.txt file with the same file name
    """
    outfile = basename(input)
    out_suffix = splitext(outfile)[0]
    out_file_name = out_suffix + output
    out_file_name = join(tempDir, out_file_name)
    print tasks.comment()
    print colored("Stage 6: Formatting count file ... ", "green")
    print input
    print out_file_name
    print tasks.comment()
    result = tasks.formatCount(input,out_file_name)
    return result

@graphviz(height=1.8, width=2, label="Combine\ncount data")
@follows(format_count)
@collate(join(tempDir, "*fastqReadsPerGene.out.txt"), formatter(".txt"), resultDir + "DATA_COUNT_countcombined.csv")
def combine_count_data(input, output):
    """Combine count files
    `input`: Formatted *.out.txt count files
    `output`: A single summary count csv file nammed 'DATA_COUNT_countcombined.csv' under project dir
    """
    print tasks.comment()
    #print input
    #print output
    print colored("Stage 7: Combining count data ...", "green")
    print tasks.comment()
    result = tasks.combineCount(input, output)
    return result

@graphviz(height=1.8, width=2, label="Alignment\nSummary")
@follows(map_to_probes)
@transform(join(tempDir, "*fastqLog.final.out"), formatter(".out"), ".txt")
def alignment_summary(input, output):
    """Generate Alignment summary
    `input`: *fastqLog.final.out files
    `output`: Extracted necessary data and create *.txt file for each count log file
    """
    outfile = basename(input)
    out_suffix = splitext(outfile)[0]
    out_file_name = out_suffix + output
    out_file_name = join(tempDir, out_file_name)
    print tasks.comment()
    print colored("Stage 8: Generate Alingmnet summary ....", "green")
    #print input
    #print output
    print tasks.comment()
    result = tasks.alignmentSummary(input, out_file_name)
    return result

@graphviz(height=1.8, width=2, label="Combine Alignment\nSummary")
@follows(alignment_summary)
@collate(join(tempDir, "*fastqLog.final.txt"), formatter(".txt"), resultDir + "DATA_alignment_summary.csv")
def combine_alignment_summary(input, output):
    """Combine formatted alignment log files
    `input`: Formatted alignment stat log files (*fastqLog.final.txt)
    `output`: Combined alignment stat csv file named (DATA_alignment_summary.csv)
    """
    print tasks.comment()
    #print input
    #print output
    print colored("Stage 9: Aggrigate alignment summary ....", "green")
    print tasks.comment()
    result = tasks.combineAlignmentSummary(input, output)
    return result

@graphviz(height=1.8, width=2, label="plot\nalignment stat")
@follows(combine_alignment_summary)
@transform(combine_alignment_summary, formatter(".csv"), resultDir + "DATA_alignment_summary.png")
def plot_alignment_summary(input, output):
    """Plot alignment summary
    `input`: Alignment summary csv file
    `output`: output png file bar plot
    """
    print tasks.comment()
    print colored("Stage 10: Plot alignment summary ...", "green")
    print input
    print output
    print tasks.comment()
    result = tasks.plotAlignmentStat(input, output)
    return result

def convertPs(psfile):
    """Utility function to convert ps file to pdf
    during test
    """
    if os.path.isfile(psfile):
        cmd = "ps2pdf %s" % (psfile)
        runCommand(cmd, "T")
    else:
        pass
    return

def commands(commandlist, index):
    '''
    Just return the correct commands from commandlist based on index given

    :param list commandlist: [(commandpath, commandfunc), ...]
    :param int index: Index of item in each tuple to extract
    '''
    return map(lambda x: x[index], commandlist)

def main():
    t0 = time.time()
    print (" Starting time ..... :") + str(t0)
    tasks_torun = [prepare_analysis, prepareDB_file, create_gtf_file, indexGenomeFile,
                   map_to_probes, format_count, combine_count_data, alignment_summary,
                   combine_alignment_summary,plot_alignment_summary]

    pipeline_printout_graph('summary_pipeline_stages_to_run.ps', 'ps', tasks_torun, user_colour_scheme={"colour_scheme_index": 6},
                            no_key_legend=False, pipeline_name="TempO-seq Analysis", size=(11, 8), dpi = 30,
                            forcedtorun_tasks = [indexGenomeFile, combine_count_data],draw_vertically=True, ignore_upstream_of_target=False)
    pipeline_run(["prepare_analysis", "prepareDB_file",'create_gtf_file', 'indexGenomeFile', 'map_to_probes', 'format_count',
                  'combine_count_data', 'alignment_summary', 'combine_alignment_summary','plot_alignment_summary'],
                 verbose = 1, multiprocess = cpuNum)
    print "....................." + resultDir
    tasks.comment()
    psfile = options.flowchart

    #psfile = "./summary_pipeline_stages_to_run.ps"
    convertPs(psfile)
    tasks.comment()

    elapsedTime = int((time.time()) - t0)
    elapsedTime = str(datetime.timedelta(seconds=elapsedTime))
    print("Time to complete the task ....." ) + colored (elapsedTime, "red")
