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
import pandas as pd
#from tabulate import tabulate
import pandas as pd
from pandas import DataFrame


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


def db_file(input,output):
    with open(output, 'w') as out, open(input, 'r') as infile:
        for line in infile:
            if line.startswith("Probe"):
                next
            else:
                line = line.strip()
                print line
                probe_ID, Attenuation_Correction_Factor,Gene_Symbol,Probe_Sequence,Main_RefSeq,RefSeqs_Targeted,Distance_from_5_Prime_End_of_mRNA = line.split(",")
                newline = ">" + probe_ID + "\n" + Probe_Sequence + "\n"
                out.write(newline)
    return

def create_gtf(input, output):
    """Creating custom gtf file from the manifest file"""
    with open(output, 'w') as out, open(input, 'r') as infile:
        for line in infile:
            if line.startswith("Probe"):
                next
            else:
                line = line.strip()
                probe_ID, Attenuation_Correction_Factor,Gene_Symbol,Probe_Sequence,Main_RefSeq,RefSeqs_Targeted,Distance_from_5_Prime_End_of_mRNA = line.split(",")
                seqLen = len(Probe_Sequence)
                gene = probe_ID +"\tprocessed_transcript\t"+ "gene\t"+   str(1) +"\t" +str(seqLen) + "\t.\t.\t.\t" + "gene_id " +'"' + probe_ID+'"; '+"gene_name"+' "'+Gene_Symbol+'";\n'
                transcript = probe_ID +"\tprocessed_transcript\t"+ "transcript\t"  + str(1) +"\t" +str(seqLen) + "\t.\t.\t.\t" + "gene_id " +'"' + probe_ID+'"; '+"transcript_id"+' "'+probe_ID+'";'  + "gene_name " + '"'+Gene_Symbol+'";\n'
                exon = probe_ID +"\tprocessed_transcript\t"+ "exon\t"+  str(1) +"\t" +str(seqLen) + "\t.\t.\t.\t" + "gene_id "+ '"' + probe_ID+'"; '+"transcript_id"+' "'+probe_ID+'"; '+'exon_number "1"; ' + "gene_name " + '"'+Gene_Symbol+'";\n'
                out.write(gene)
                out.write(transcript)
                out.write(exon)
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
                platLine = "PL__" + plateBarcode  + "\t" + plateBarcode + "\n"
                plate.write(platLine)
                wallLine = "WA__" + wallBarcode + "\t" + wallBarcode + "\n"
                wall.write(wallLine)

def split_plate_barcode(barcodes,fastqFile, outDir, prefixPlate,suffix):
    """split fastq based on plate barcode"""
    platebc = barcodes[0]
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
            infile=input_file.split("__")
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


def map_seq_to_probes(fastq, genomeDir, numCPU, outPrefix, gtfFile):
    """Map the sequence to the probes genome file using STAR"""
    cmds = [
        'STAR',
        '--genomeDir', genomeDir,
        '--readFilesIn', fastq,
        '--readFilesCommand zcat',
        '--runThreadN ', str(numCPU),
        '--outFileNamePrefix', outPrefix,
        '--outSAMtype BAM SortedByCoordinate',
        '--quantMode GeneCounts',
        '--sjdbGTFfile', gtfFile,
        ' --genomeLoad NoSharedMemory',
    ]
    cmds = '  '.join(cmds)
    runCommand(cmds, True)

def convertSamToBam(samfile, bamfileout):
    """Convert sam file to bam file"""
    cmds = "samtools view -b -S %s > %s"%(samfile, bamfileout)
    runCommand(cmds, True)

def sortBamFile(bamfile, outSuffix):
    """docstring for sortBamFile"""
    cmds = "samtools  sort -m 1000000000  %s  %s" %(bamfile, outSuffix)
    runCommand(cmds, True)

def index_bam_file(bamfile):
    """Index bam files"""
    cmds = "samtools index %s" %(bamfile)
    runCommand(cmds, True)

def countReadsMappedToProbes(bamindex, outfile):
    """docstring for countReadsMappedToProbes"""
    cmds = "samtools idxstats %s > %s " %(bamindex, outfile)
    runCommand(cmds, True)

def formatCount(input_file, output_file):
    """Combine the log files from the well splitting routine"""
    with open(output_file, "w") as oo, open(input_file, "r") as ii:
        #oo.write("Plate_Barcode\tWell_Barcode\tCount\tLocation\n")
        for line in ii:
            if line.startswith("N_"):
                next
            else:
                lines = line.split("\t")
                newline = lines[0] +"\t" + lines[1] + "\n"
                oo.write(newline)
    return


def combineCount(input_file_names, output_file):
    """Combine Count files, merge multiple count files to a single dataframe"""
    # get string from file name
    dfs = []
    for filename in input_file_names:
        fileN = os.path.basename(filename)
        records = fileN.split("_")
        sampleName = records[0] + "_" + records[1] #A11C_S22
        ids = sampleName
        count = ids
        df = pd.read_table(filename, sep= '\t', names=["Genes",count]).set_index("Genes")
        dfs.append(df)
    import functools
    #dfs = [pd.read_table(filename, sep= '\t', names=["gene","len","count","loc"]).set_index("gene") for filename in input_file_names]
    mergefunc = functools.partial(pd.merge, left_index=True, right_index=True)
    merged =functools.reduce(mergefunc, dfs)
    #merged.columns = ['a', 'b']
    #print merged
    merged.to_csv(output_file, index=True)
    return

def alignmentSummary(input_file_name, output_file_name):
    """Generate alignment summary alignmentSummary"""
    with open(output_file_name, 'w') as oo, open(input_file_name, 'r') as ii:
        rec = {}
        for line in ii:
            line = line.rstrip()
            #print line
            if line.endswith(":") or not line.strip():
                next
            else:
                myList = line.split("\t")
                key_line =myList[0].strip().split("|")
                key = key_line[0].strip()
                val =myList[1].strip()
                #print key
                #print val
                rec[str(key)]= val
        #print rec
        numSeq = "Number_of_input_reads\t" + rec['Number of input reads']+"\n"
        umapped = "Uniquely_mapped_reads_number\t" + rec['Uniquely mapped reads number'] + "\n"
        umperc = "Uniquely_mapped_reads%\t" + rec['Uniquely mapped reads %'].strip('%') + "\n"
        ave_map_length = "Average_mapped_length\t" + rec["Average mapped length"] + "\n"
        multi_map = "Number_of_reads_mapped_to_multiple_loci%\t" + str(float(rec["Number of reads mapped to multiple loci"]) / float(rec['Number of input reads']) * 100) + "\n"
        unmaped_perc = "Reads_unmapped_too_short%\t" + rec["% of reads unmapped: too short"].strip('%') + "\n"
        oo.write(numSeq)
        oo.write(umapped)
        oo.write(umperc)
        oo.write(ave_map_length)
        oo.write(multi_map)
        oo.write(unmaped_perc)

    return

def combineAlignmentSummary(input_file_names, output_file):
    """Combine Count files, merge multiple count files to a single dataframe"""
    # get string from file name
    dfs = []
    for filename in input_file_names:
        fileN = os.path.basename(filename)
        records = fileN.split("_")
        sampleName = records[0] + "_" + records[1] #A11C_S22
        ids = sampleName
        summary = ids
        df = pd.read_table(filename, sep= '\t', names=["category",summary]).set_index("category")
        dfs.append(df)


    import functools
    #dfs = [pd.read_table(filename, sep= '\t', names=["gene","len","count","loc"]).s
    mergefunc = functools.partial(pd.merge, left_index=True, right_index=True)
    merged =functools.reduce(mergefunc, dfs)
    #merged.columns = ['a', 'b']
    #print merged
    merged.to_csv(output_file, index=True)
    return

def plotAlignmentStat(input,output):
    """plot Alignment summary using ggplot"""
    df = pd.read_csv(input, thousands=",")
    # replace % with '' and convert the type to float
    #df.replace('%', '', regex=True)
    print df.dtypes
    # convert to numeric
    #df1=df.apply(pd.to_numeric, args=('coerce',))
    # Get certain rows
    print df
    df = df.iloc[[2,4,5],]
    #df = df.ix[['Uniquely mapped reads %', 'Number of reads mapped to multiple loci %', 'Reads unmapped: too short %']]
    dfm = pd.melt(df, id_vars=['category'], var_name='sampleName',value_name = 'Value')

    print dfm
    #from ggplot import *
    #import pandas as pd
    #df = pd.DataFrame({"x":[1,2,3,4], "y":[1,3,4,2]})
    #ggplot(aes(x="x", weight="y"), df) + geom_bar()
    #ggplot(diamonds, aes(x='price', fill='cut')) + geom_histogram() +  theme_bw() + scale_color_brewer(type='qual')

    from ggplot import *
    p = ggplot(dfm, aes(x='sampleName', weight='Value', fill='category')) + geom_bar(position = "stack") + theme_bw() + ggtitle("Alignment Summary") + scale_y_continuous(labels='comma') + coord_flip()
    #p = ggplot(df, aes(x = "category", y = "value", fill = "variable")) + \
        #geom_bar(stat="bar", labels=df["category"].tolist()) + \
        #theme(axis_text_x = element_text(angle=90))
    dirname, filename = os.path.split(output)
    print dirname
    print filename
    p.save(output)
    #ggsave(plot=p, filename=filename, path=dirname)
    return


def filterCombineCount(input, output):
    """extract count column only"""
    df = pd.read_csv(input[0])
    df =df.filter(like='Counts', axis=1)
    df = df.set_index("Counts")
    df.to_csv(output, index=True, sep='\t')
    return

# index genome
#STAR --runMode genomeGenerate --genomeDir $WRKDIR/star-genome --genomeFastaFiles /path/to/genome/genome.fasta --runThreadN 2

# map seq to genome
#STAR --genomeDir $WRKDIR/star-genomes --readFilesIn my_reads.fastq
def comment():
    return "*" * 80
