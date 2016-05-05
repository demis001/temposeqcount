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
    splitext, basename, dirname, exists
)
helpers.setup_shell_environment()
import tasks
import glob
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
inputFile = options.fastq_file
path, inFile = os.path.split(inputFile)# get fastq.gz file
print inputFile
probe = os.path.abspath(options.probe_file)
probPath, probFile = os.path.split(probe)
print probe

plateWall_bc = os.path.abspath(options.plate_well_bc)
pbpath,plateWallBC = os.path.split(plateWall_bc)
print plateWall_bc

cpuNum = options.cpuNum
print cpuNum
trimleft = options.trimleft
trimright = options.trimright

# Do all initial setup
#config = helpers.parse_config()
#helpers.setup_shell_environment(config)

## Setup initial inputs
inputDir = join(proDir, "input")
logsDir = join(proDir, "logs")
resultsDir = join(proDir, "results")
outputDir = join(proDir, 'output')
qualityAnalysisDir = join(proDir, 'quality_analysis')
genomeDir = join(inputDir, "Genome")
#sample1 = join(results_dir, "sample1")
##sample2 = join(results_dir, "sample2")
#paramFile = join(input_dir, "param.txt")

print inputDir
print logsDir
print resultsDir
print outputDir
print qualityAnalysisDir
#print paramFile


param = [
    [inputFile, join(proDir, "input", inFile)],
    [probe, join(proDir, "input", probFile)],
    [plateWall_bc, join(proDir, "input", plateWallBC)]

]
#def report(result):
    #"""Wrapper around Result.report"""
    #result.report(logger_proxy, logging_mutex)
    #print result
@graphviz(height=1.8, width=2, label="Prepare\nanalysis")
@follows(mkdir(proDir, inputDir, resultsDir, logsDir))
@files(param)
def prepare_analysis(input,output):
    """Copy the inputfiles to analysis dir
        -`input`: input file
        -`outfile`: output file
    """
    print "Copy", input, " to ", output
    result = tasks.copyFileToAnaFolder(input, output)
    return result

@graphviz(height=1.8, width=2, label="Prepare DB\nfiles")
@follows(prepare_analysis)
@transform(prepare_analysis, suffix(".probes"), ".fa")
def prepareDB_file(input_file, output_file):
    """docstring for prepareDB__file"""
    print "Creating DB file from probe file ..."
    print input_file
    result =tasks.db_file(input_file, output_file)
    return result

@graphviz(height=1.8, width=2, label="Format \nbarcodes")
@follows(prepare_analysis)
@transform(prepare_analysis, suffix(".bc"),["_platebc.txt", "_wellbc.txt"])
def prepareBarcode(input, output):
    """prepare plate and well barcodes to the right format"""
    print tasks.comment()
    print "Started processing barcode ...."
    print tasks.comment()

    result = tasks.prepare_barcode_file(input, output)
    return result

def qa_outfile(input):
    ''' Generate quality_analysis output file for input file '''
    if input is not None:
        return join(
            qualityAnalysisDir,
            splitext(basename(input).replace('.gz',''))[0] + '_fastqc.zip'
        )
    else:
        return None

#@files([
    #[join(proDir, "input", inFile), qualityAnalysisDir],
#])
graphviz(height=1.8, width=2, label="Generate\nQC")
@follows(mkdir(qualityAnalysisDir))
@transform(prepare_analysis, suffix(".fastq"), "_fastqc.html")
def fastQC(input, output):
    '''
    Runs fastqc on both input files
    '''
    print input
    print output
    print qualityAnalysisDir
    if input is not None:
        tasks.createQuality(input, qualityAnalysisDir)
    return

@graphviz(height=1.8, width=2, label="Index\nDB")
@follows(prepareDB_file)
@follows(mkdir(genomeDir))
@transform(prepareDB_file, formatter(".+.fa"), "SAindex")
def indexGenomeFile(input, output):
    """Index Star Genome File"""
    outputDir = proDir + "/input/Genome"
    print "Creating genome index file from the probe fasta file ...."
    print input
    #print output
    print cpuNum
    result = tasks.index_db_file(input, outputDir, cpuNum)
    return result


@graphviz(height=1.8, width=2, label="Split Plate\nbarcodes")
@follows(prepareBarcode)
@transform(prepareBarcode,formatter(".+_platebc.txt"), ".fq")
def split_barcodes_plate(input,output):
    """Split the fastq file based on well barcode"""
    prefix= inputDir +"/" + splitext(basename(inputFile))[0] + "__"
    print tasks.comment()
    print input
    print output
    print prefix
    print tasks.comment()
    result = tasks.split_plate_barcode(input, inputFile, inputDir, prefix,output)
    return result

@graphviz(height=1.8, width=2, label="split Well\nbarcodes")
@follows(split_barcodes_plate)
@transform(join(inputDir, "*__PL__*.fq"), suffix(".fq"),  ".fastq" )
def split_barcodes_well(input, output):
    """Split each plate barcode splitted fastq to well barcode """
    prefix = splitext(input)[0] + "__"
    suf = splitext(output)[1]
    barcode = glob.glob(join(inputDir, "*wellbc.txt"))
    wellbarcode = barcode[0]
    print tasks.comment()
    print input
    print output
    print suf
    print prefix
    print wellbarcode
    print tasks.comment()
    result = tasks.split_well_barcode(wellbarcode, input, inputDir, prefix, suf)
    return result

@graphviz(height=1.8, width=2, label="Trim\nadaptors")
@follows(split_barcodes_well)
@transform(join(inputDir,"*__WA__*.fastq"), suffix(".fastq"), "__trim.fastq")
def trim_adaptors(infastq,outfastq):
    """Trim TEMPseq barcodes and Adaptots eg if well barcode is 8 nt and  Ad1 (nt=17), the --trimleft=25
    and plate barcode is 7 nt and Ad2 is 17 nt, then the --trimright=24"""
    print tasks.comment()
    print infastq
    print outfastq
    print tasks.comment()

    result = tasks.trim_Ad1_Ad2(infastq, trimleft, trimright, outfastq)
    return result

@graphviz(height=1.8, width=2, label="Generate\nsummary\nbc split")
@follows(trim_adaptors)
@collate(join(inputDir, "*_wellsplit_barcode.log"), formatter("wellsplit_barcode.log"), inputDir + "/wellbarcodesplit_stat.combined.log")
def combine_well_logfiles(input, output):
    """Combine log files to plot the stat of well barcodes splitting"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.combine_wellsplit_logfiles(input, output)
    return result

#@files([
     #[join(proDir, "input", "split_plate_barcode.log"), join(proDir, "input", "split_well_barcode.log"),
      #inputDir, "plateBarcode", "wellBarcode"],
#])
@graphviz(height=1.8, width=2, label="plot bc split\nSummary")
@follows(split_barcodes_well)
@transform(combine_well_logfiles,  suffix(".log"), ".png")
def plot_barcodeSummary(logFileWell,  wellOut):
    """Plot barplot to summarize plate and well barcodes splitting"""

    print "Plot barcode breadown ...."
    print tasks.comment()
    print logFileWell
    print wellOut
    print inputDir
    print tasks.comment()
    result = tasks.plot_summary(logFileWell, inputDir,wellOut)
    return result

@graphviz(height=1.8, width=2, label="Map to\nprobes")
@follows(indexGenomeFile)
@follows(trim_adaptors)
@transform(join(inputDir,"*__WA__*__trim.fastq" ), formatter('(.*)__trim.fastq'), "\1.sam" )
def map_to_probes(fastq, output):
    """Map sequence with barcode """
    genomeDir = inputDir + "/Genome"
    suf = splitext(fastq)[0]
    outPrefix = suf
    print tasks.comment()
    print fastq
    print output
    print genomeDir
    print outPrefix
    print tasks.comment()
    result = tasks.map_seq_to_probes(fastq, genomeDir, cpuNum, outPrefix)
    return result

@graphviz(height=1.8, width=2, label="convert\nsam2bam")
@follows(map_to_probes)
@transform(join(inputDir, "*trimAligned.out.sam"), suffix(".sam"), ".bam")
def convert_sam_bam(input, output):
    """Convert sam to bam"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.convertSamToBam(input, output)
    return result

@graphviz(height=1.8, width=2, label="Sort\nbam")
@follows(convert_sam_bam)
@transform(join(inputDir, "*trimAligned.out.bam"), suffix(".bam"), "sorted")
def sort_bam_file(input, output):
    """Sort bam files"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.sortBamFile(input,output)
    return result

@graphviz(height=1.8, width=2, label="Index\nbam")
@follows(sort_bam_file)
@transform(join(inputDir, "*outsorted.bam"), suffix(".bam"), ".bai")
def indexBam(input,output):
    """Index bam files"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.index_bam_file(input)
    return result

@graphviz(height=1.8, width=2, label="Count\nreads")
@follows(indexBam)
@transform(join(inputDir, "*outsorted.bam"), suffix(".bam"), ".count.txt")
def count_read_mapped_to_probes(input, output):
    """Map aligned reads that mapped to the probe sequence"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.countReadsMappedToProbes(input, output)
    return result

@graphviz(height=1.8, width=2, label="Combine\ncount data")
@follows(count_read_mapped_to_probes)
@collate(join(inputDir, "*outsorted.count.txt"), formatter(".txt"), inputDir + "/summary_countcombined.csv")
def combine_count_data(input, output):
    """Combine count files and format it"""
    print tasks.comment()
    print input
    print output
    print tasks.comment()
    result = tasks.combineCount(input, output)
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
#def createPram(output_file):
    #'''
    #Create param.txt inside projectdir/input
    #'''
    #config['NODE_NUM'] = str(options.cpuNum)
    #helpers.setup_param(config, output_file)

#def qa_outfile(input):
    #''' Generate quality_analysis output file for input file '''
    #if input is not None:
        #return j_oin(
            #quality_analysis_dir,
            #splitext(basename(input).replace('.gz',''))[0] + '_fastqc.zip'
        #)
    #else:
        #return None

#@follows(createPram)
#@follows(mkdir(quality_analysis_dir))
#@files([
    #[R1, qa_outfile(R1)],
    #[R2, qa_outfile(R2)],
#])
#def fastQC(input, output):
    #'''
    #Runs fastqc on both input files(or only R1 if only -R1)
    #'''
    #if input is not None:
        #tasks.createQuality(input, dirname(output))

#@follows(fastQC)
#@files(
    #[R1, R2],
    #[join(results_dir,'analysis.log')]
#)
#def priStage(input, output):
    #'''
    #Run run_standard.pl with all supplied options
    #'''
    #result = tasks.priStage(
        #input, project_dir, paramFile,
        #blast_unassembled, sge, results_dir
    #)
    #return result

#def verify_standard_stages_files(projectpath):
    #''' Hardcoded verification of standard stages '''
    ##templates.append(resource_filename(__name__, tfile))
    #from verifyproject import STAGES, verify_standard_stages_files
    #projectname = basename(projectpath)
    #import yaml
    #from termcolor import colored
    #templatesdir = resource_filename(__name__, 'output_files_templates')
    #missingfiles = verify_standard_stages_files(projectpath, templatesdir)
    #if missingfiles:
        #for path, reason in missingfiles:
            ## Don't care about 0 sized files
            #if reason == 'Size zero':
                #continue
            #fname = basename(path)
            #if fname == "param.txt":
                #print colored("WARNING! :  Unable to create param.txt under the inpute directory", "red")
                #sys.exit(1)
            #elif  fname == "quality_filter.R1":
                #print colored("WARNING! :  Unable to run quality filter step, please check if prinseq is installed and running or the log file under host_map if bowtie2 succeeded", "red")
                #sys.exit(1)
            #elif fname == "out.bam":
                #print colored("WARNING! :  Unable to map the read to the ref genome, please check if bowtie2 is installed or the ref ~/databases exist", "red")
                #sys.exit(1)
            #elif fname == "out.cap.fa":
                #print colored("WARNING! : Unable find out.cap.fa file, please check if cap3 program is running and  ray2_assembly error log", "red")
                #sys.exit(1)
            #elif fname == "out.ray.fa":
                #print colored("WARNING! : Unable to run Ray assembly, please check if Ray2 program is running and possible error in the log file", "red")
                #sys.exit(1)
            #elif fname == "1.contig.blast":
                #print colored("WARNING! : Unable to run iterative_blast_phylo_1, please check the log file under iterative_blast_phylo_1", "red")
                #sys.exit(1)
            #elif fname == "1.contig.fasta":
                #print colored("WARNING! : Unable to run iterative_blast_phylo_1, please check the log file under iterative_blast_phylo_2", "red")
                #sys.exit(1)
            #elif fname == "contig." + pro_dir + ".top.smallreport.txt":
                #print fname
                #print colored("WARNING! : Unable to run iterative_blast_phylo , please check the log file under iterative_blast_phylo_1 or iterative_blast_phylo_2", "red")
                #sys.exit(1)
    #else:
        #print colored(" SUCCESS! the tasks completed successfully", "green")

#symlink_files = [
    #[join(results_dir,'output'), join(project_dir, 'output')],
    #[join(results_dir,'iterative_blast_phylo_1','reports'), join(project_dir,'contig_reports')],
    #[join(results_dir,'iterative_blast_phylo_2','reports'), join(project_dir,'unassembled_read_reports')],
    #[join(results_dir,'step1','R1.count'), join(project_dir, 'R1.count')],
    #[join(results_dir,'quality_analysis'), join(project_dir, 'quality_analysis')],
    #[join(results_dir,'analysis.log'), join(project_dir, 'analysis.log')]
#]
#if R2:
    #symlink_files += [[join(results_dir,'step1','R2.count'), join(project_dir, 'R2.count')]]

#@follows(priStage)
#@files(symlink_files)
#def symlink(src, dst):
    #'''
    #Create symlink src -> dst
    #Overwrite dst if exists
    #Do not create if src does not exist
    #'''
    #helpers.symlink(src, dst)

#def commands(commandlist, index):
    #'''
    #Just return the correct commands from commandlist based on index given

    #:param list commandlist: [(commandpath, commandfunc), ...]
    #:param int index: Index of item in each tuple to extract
    #'''
    #return map(lambda x: x[index], commandlist)

def main():
    #from helpers import which
    t0 = time.time()
    print (" Starting time ..... :") + str(t0)
    ## Will be all the commands to run
    #pipeline_commands = [
        #(__name__ + '.prepare_analysis', prepare_analysis),
    #]
    tasks_torun = [prepare_analysis, prepareDB_file, prepareBarcode, fastQC, indexGenomeFile, split_barcodes_plate, split_barcodes_well,
                   trim_adaptors, combine_well_logfiles, plot_barcodeSummary, map_to_probes, convert_sam_bam,
                   sort_bam_file, indexBam, count_read_mapped_to_probes, combine_count_data]

    pipeline_printout_graph('summary_pipeline_stages.ps', 'ps', tasks_torun, user_colour_scheme={"colour_scheme_index": 6},
                            no_key_legend=False, pipeline_name="TempO-seq Analysis", size=(11, 8), dpi = 30, forcedtorun_tasks = [indexGenomeFile, combine_count_data],
                            draw_vertically=True, ignore_upstream_of_target=False)
    pipeline_run(["prepare_analysis", "prepareDB_file", "prepareBarcode", "fastQC","indexGenomeFile", "split_barcodes_plate", "split_barcodes_well",
                  "trim_adaptors", "combine_well_logfiles", "plot_barcodeSummary", "map_to_probes", "convert_sam_bam",
                  "sort_bam_file", "indexBam", "count_read_mapped_to_probes", "combine_count_data"], verbose = 1, multiprocess = cpuNum)
    #print "....................." + basedir + "/" + project_dir
    tasks.comment()
    helpers.run(options)
    psfile = "./summary_pipeline_stages.ps"
    convertPs(psfile)
    tasks.comment()

    #if options.param:
        #helpers.create_new_project(project_dir)
    #elif not options.noparam:
        #pipeline_commands = [
            #(__name__ + '.fastQC', fastQC),
            #(__name__ + '.priStage', priStage),
            #(__name__ + '.symlink', symlink)
        #]
    #else:
        #helpers.create_new_project(project_dir)
                #pipeline_commands += [
            #(__name__ + '.fastQC', fastQC),
            #(__name__ + '.priStage', priStage),
            #(__name__ + '.symlink', symlink),
        #]

    #pipeline_printout(sys.stdout, commands(pipeline_commands, 1), verbose=6)
    #pipeline_run(commands(pipeline_commands, 0), multiprocess=6)
    #pipeline_get_task_names()

    #import datetime
    #from termcolor import colored
    ##if not options.param:
        ##verify_standard_stages_files(project_dir)
    ##elapsedTime = int((time.time()) - t0)
    ##elapsedTime = str(datetime.timedelta(seconds=elapsedTime))
    print (" End time ..... :") + str(t0)
    #print("Time to complete the task ....." ) + colored (elapsedTime, "red")
