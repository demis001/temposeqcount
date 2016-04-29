import time
import datetime
import os
import sys
import subprocess
import yaml
import shutil
from helpers import get_options, make_logger, runCommand,which,run_cmd
import os.path
from pkg_resources import resource_filename, resource_stream
from pandas import DataFrame
from rpy2 import robjects
import rpy2
from rpy2.robjects import pandas2ri
from rpy2.robjects.lib import ggplot2
from rpy2.robjects.packages import importr
from tabulate import tabulate
grdevices = importr('grDevices')
pandas2ri.activate()


def work_dir(dirname):
    """get the current working dir"""
    if not dirname:
        currpath =os.getcwd()
        dir_to_create = currpath + "/" + dirname
        print dir_to_create
        os.mkdir(dir_to_create, 0755)
        return

def rmdir(dirname):
    """remove dir"""
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
        return

def mkdir(dirname):
    """make dir"""
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        return

def copyFileToAnaFolder(file_to_copy, file_copy):
    """copy the mapfile to analysis dir
    Arguments:
        - `file_to_copy`: The mapfile from
        - ` file_copy`: a copy of mapfile
    """
    shutil.copyfile(file_to_copy, file_copy)
    return

def createQuality(input, output):
    """Check quality of the fastqfile

    Arguments:
        -`input`: The input fastq file
        -`output`: The output folder for the analysis
    """
    cmds = [
        'fastqc',
        input,
        '-o', output,
     ]
    cmds = '  '.join(cmds)
    cmds += " 2>&1 | tee -a  " + output + "/analysis_quality.log"
    runCommand(cmds, True)
    return


#ProbeName   AcceptorProbeSequence   DonorProbeSequence  AcceptorAdaptorSequence DonorAdaptorSequence    seq seq_len
#NM_000569.6_FCGR3A_2014 CAATGAACAAAGCTACACAG    GAATTAGATATTGAAGCAGA    GGAAGCCTTGGCTTTTG   AGATCGGAAGAGCACAC   CAATGAACAAAGCTACACAGGAATTAGATATTGAAGCAGA    40
def db_file(input,output):
    with open(output, 'w') as out, open(input, 'r') as infile:
        for line in infile:
            if line.startswith("ProbeName"):
                next
            else:
                line = line.strip()
                probName,accProbSeq, donProbSeq, accAdapSeq, donAdapSeq,seq,seqLen = line.split("\t")
                newline = ">" + probName + "\n" + seq + "\n"
                out.write(newline)
    return

def index_db_file(input, output, cpuNum):
    """Index the probe fastfile to use as db file"""
    cmds = [
        'STAR',
        '--runMode genomeGenerate',
        '--genomeDir', output,
        '--genomeFastaFiles', input,
        '--runThreadN', str(cpuNum),
        '--genomeSAindexNbases 2',

    ]
    cmds = '  '.join(cmds)
    cmds += " 2>&1 | tee -a " + output + "/index_STAR_genomeFile.log"
    runCommand(cmds, True)
    return
def prepare_barcode_file(barcodeFile, outFile):
    """docstring for prepare_bar_code_file"""
    with open(barcodeFile, 'r') as inFile, open(outFile[0], 'w') as plate, open(outFile[1], 'w') as wall:
        for line in inFile:
            if line.startswith("#"):
                next
            else:
                plateBarcode, wallBarcode, con = line.split()
                platLine = "PL_" + plateBarcode  + "\t" + plateBarcode + "\n"
                plate.write(platLine)
                wallLine = "WA_" + wallBarcode + "\t" + wallBarcode + "\n"
                wall.write(wallLine)

def split_plate_barcode(barcodes,fastqFile, outDir, prefixPlate,suffix):
    """split fastq based on plate barcode"""
    platebc = barcodes[0]
    #wallbc = barcodes[1]
    cmds = [
        'cat', fastqFile, '|',
        'fastx_barcode_splitter.pl',
        '--bcfile', platebc,
        '--prefix', prefixPlate,
        '--suffix', suffix,
        '--eol',
        '--partial', str(1),
        '--mismatches', str(1),
    ]
    plateLog =  prefixPlate + "platesplit_barcode.log"
    cmds ='  '.join(cmds)
    cmds +=" 2>&1 | tee   " + plateLog
    runCommand(cmds, True)
    return

def split_well_barcode(wellbarcode, fastqFile, inputDir, prefixWell, suffix):
    """split fastq based on plate barcode"""
    #wallbc = barcodes[1]
    cmds = [
        'cat', fastqFile, '|',
        'fastx_barcode_splitter.pl',
        '--bcfile',wellbarcode,
        '--prefix', prefixWell,
        '--suffix', suffix,
        '--bol',
        '--partial', str(1),
        '--mismatches', str(1),
    ]
    welllog =  prefixWell + "wellsplit_barcode.log"
    cmds ='  '.join(cmds)
    cmds +=" 2>&1 | tee   " + welllog
    runCommand(cmds, True)
    return
    # Combine wall Barcode splitted files

def plot_summary(logWall,directory,expt_id_wall):
    #TODO: The lebel of reversed, fix that in a plot

    #with open(logPlate, 'r') as inFile:
        #barcodes = []
        #counts = []
        #matches = []
        #for line in inFile:
            #line.strip()
            #if line.startswith("Barcode") or line.startswith("total"):
                #next
            #else:
                #barcode, count, match = line.split()
                #barcodes.append(barcode)
                #counts.append(count)
                #matches.append(match)

    #df = DataFrame({'barcode': barcodes,
                    #'count': counts,
                    #'matched': matches})
    #df = df.ix[:, 0:2]
    #p = ggplot2.ggplot(df) + \
        #ggplot2.aes_string(x='factor(barcode)', y='count') + \
        #ggplot2.geom_bar(position="dodge",stat="identity") + \
        #ggplot2.geom_jitter() + ggplot2.coord_flip() + \
        #ggplot2.ggtitle(label = expt_id_plate) + \
        #ggplot2.ggplot2.xlab(label = "") +  ggplot2.theme_bw()
        ##ggplot2.scale_y_continuous(name = "Count\n(million reads)")

    #filename = "{0}/{1}.png".format(directory, expt_id_plate)
    #print filename
    #grdevices.png(file=filename, width=4, height=5, unit='in', res=300)
    #p.plot()
    #grdevices.dev_off()
    with open(logWall, 'r') as inFile:
        plates = []
        barcodes = []
        counts = []
        matches = []
        for line in inFile:
            line.strip()
            if line.startswith("Plate"):
                next
            else:
                plate, well, count, match = line.split("\t")
                plates.append(plate)
                barcodes.append(well)
                counts.append(count)
                matches.append(match)

    df = DataFrame({'platebarcode':plates,
                    'wellbarcode': barcodes,
                    'count': counts,
                    'matched': matches})
    df = df.ix[:, 0:4]
    print df
    p = ggplot2.ggplot(df) + \
        ggplot2.aes_string(x='wellbarcode', y='count') + \
        ggplot2.geom_bar(position="dodge",stat="identity") + \
        ggplot2.coord_flip() + \
        ggplot2.ggtitle(label = expt_id_wall) + \
        ggplot2.ggplot2.xlab(label = "") +  ggplot2.theme_bw()
        #ggplot2.scale_y_continuous(name = "Count\n(million reads)")
    filename = "{0}".format(expt_id_wall)
    print filename
    grdevices.png(file=filename, width=4, height=5, unit='in', res=300)
    p.plot()
    grdevices.dev_off()
    return

def trim_Ad1_Ad2(input_fq, trimleft, trimright, output_fq):
    """Trim TEMPOseq adaptors from the fastq file, both 3' and 5' adaptors are 17 nc"""
    cmds = [
        'seqtk trimfq',
        '-b ', str(trimleft),
        '-e ', str(trimright),
        input_fq,
        '> ', output_fq,
    ]
    cmds = '  '.join(cmds)
    runCommand(cmds, True)

def combine_wellsplit_logfiles(input_file_names,output_file):
    """Combine the log files from the well splitting routine"""
    with open(output_file, "w") as oo:
        oo.write("Plate_Barcode\tWell_Barcode\tCount\tLocation\n")
        for input_file in input_file_names:
            infile=input_file.split("_")
            plateBarcode = infile[3]
            print "   Recombine %s -> %s " %(input_file, output_file)
            for line in open(input_file):
                if line.startswith("Barcode") or line.startswith("total"):
                    next
                else:
                    lines = line.split()
                    newline = plateBarcode + "\t" + lines[0] +"\t" + lines[1] + "\t" + lines[2] + "\n"
                    oo.write(newline)
    return


def map_seq_to_probes(fastq, genomeDir, numCPU, outPrefix):
    """Map the sequence to the probes genome file using STAR"""
    cmds = [
        'STAR',
        '--genomeDir', genomeDir,
        '--readFilesIn', fastq,
        '--runThreadN ', str(numCPU),
        '--outFileNamePrefix', outPrefix,
        '--twopassMode Basic',
        ' --genomeLoad NoSharedMemory',
    ]
    cmds = '  '.join(cmds)
    runCommand(cmds, True)




# index genome
#STAR --runMode genomeGenerate --genomeDir $WRKDIR/star-genome --genomeFastaFiles /path/to/genome/genome.fasta --runThreadN 2

# map seq to genome
#STAR --genomeDir $WRKDIR/star-genomes --readFilesIn my_reads.fastq
def comment():
    return "*" * 80
