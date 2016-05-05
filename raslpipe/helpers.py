import os
import sys
import time
import datetime
import logging
import logging.handlers
from argparse import ArgumentParser
import StringIO
from ruffus.proxy_logger import *
from ruffus import *

from collections import Counter
#from pandas import DataFrame
#from rpy2 import robjects
#import rpy2
#from rpy2.robjects import pandas2ri
#from rpy2.robjects.lib import ggplot2
#from rpy2.robjects.packages import importr
#from tabulate import tabulate
#grdevices = importr('grDevices')
#pandas2ri.activate()

class Result(object):
    def __init__(self, infiles, outfiles, log=None, stdout=None, stderr=None,
                 desc=None, failed=False, cmds=None):
        """
        A Result object encapsulates the information going to and from a task.
        Each task is responsible for determining the following arguments, based
        on the idiosyncracies of that particular task:

            `infiles`: Required list of input files to the task
            `outfiles`: Required list of output files to the task
            `failed`: Optional (but recommended) boolean indicating whether the
                      task failed or not.  Default is False, implying that the
                      task will always work
            `log`: Optional log file from running the task's commands
            `stdout`: Optional stdout that will be printed in the report if the
                      task failed
            `stderr`: Optional stderr that will be printed in the report if the
                      task failed
            `desc`: Optional description of the task
            `cmds`: Optional string of commands used by the task. Can be very
                    useful for debugging.
        """
        if isinstance(infiles, basestring):
            infiles = [infiles]
        if isinstance(outfiles, basestring):
            outfiles = [outfiles]
        self.infiles = infiles
        self.outfiles = outfiles
        self.log = log
        self.stdout = stdout
        self.stderr = stderr
        self.elapsed = None
        self.failed = failed
        self.desc = desc
        self.cmds = cmds

    def report(self, logger_proxy, logging_mutex):
        """
        Prints a nice report
        """
        with logging_mutex:
            if not self.desc:
                self.desc = ""
            logger_proxy.info(' Task: %s' % self.desc)
            logger_proxy.info('     Time: %s' % datetime.datetime.now())
            if self.elapsed is not None:
                logger_proxy.info('     Elapsed: %s' % nicetime(self.elapsed))
            if self.cmds is not None:
                logger_proxy.debug('     Commands: %s' % str(self.cmds))
            for output_fn in self.outfiles:
                output_fn = os.path.normpath(os.path.relpath(output_fn))
                logger_proxy.info('     Output:   %s' % output_fn)
            if self.log is not None:
                logger_proxy.info('     Log:      %s' % self.log)
            if self.failed:
                logger_proxy.error('=' * 80)
                logger_proxy.error('Error in %s' % self.desc)
                if self.cmds:
                    logger_proxy.error(str(self.cmds))
                if self.stderr:
                    logger_proxy.error('====STDERR====')
                    logger_proxy.error(self.stderr)
                if self.stdout:
                    logger_proxy.error('====STDOUT====')
                    logger_proxy.error(self.stdout)
                if self.log is not None:
                    logger_proxy.error('   Log: %s' % self.log)
                logger_proxy.error('=' * 80)
                sys.exit(1)
            logger_proxy.info('')


def nicetime(seconds):
    """Convert seconds to hours-minutes-seconds"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    elapsed = "%dh%02dm%02.2fs" % (h, m, s)
    return elapsed


def timeit(func):
    """Decorator to time a single run of a task"""
    def wrapper(*arg, **kw):
        t0 = time.time()
        res = func(*arg, **kw)
        t1 = time.time()
        res.elapsed = (t1 - t0)
        if not res.desc:
            res.desc = func.__name__
        return res
    return wrapper


def run(options):
    """
    Run the pipeline according to the provided options (which were probably
    created by get_options())
    """
    if options.just_print:
        pipeline_printout(sys.stdout,
                          options.target_tasks,
                          options.forced_tasks,
                          verbose=options.verbose)

    elif options.flowchart:
        pipeline_printout_graph(open(options.flowchart, "w"),
                                os.path.splitext(options.flowchart)[1][1:],
                                options.target_tasks,
                                options.forced_tasks,
                                no_key_legend=not options.key_legend_in_graph)
    else:
        pipeline_run(options.target_tasks,
                     options.forced_tasks,
                     multiprocess=options.jobs,
                     logger=stderr_logger,
                     verbose=options.verbose)


def get_options():
    """
    Standard set of options to be passed to the command line.  These can be in
    turn passed to run() to actually run the pipeline.
    """
    #config = parse_config()
    parser = ArgumentParser()
    '''
    parser = ArgumentParser(usage="\n\n    %(prog)s [arguments]")
    parser.add_argument("-v", "--verbose", dest="verbose",
                      action="count", default=0,
                      help="Print more verbose messages for each "
                           "additional verbose level.")
    parser.add_argument("-L", "--log_file", dest="log_file",
                      metavar="FILE",
                      type=str,
                      help="Name and path of log file")
    parser.add_argument("-t", "--target_tasks", dest="target_tasks",
                        action="append",
                        default=list(),
                        metavar="JOBNAME",
                        type=str,
                        help="Target task(s) of pipeline.")
    parser.add_argument("-j", "--jobs", dest="jobs",
                        default=6,
                        metavar="N",
                        type=int,
                        help="Allow N jobs (commands) to run "
                             "simultaneously.")
    parser.add_argument("-n", "--just_print", dest="just_print",
                        action="store_true", default=False,
                        help="Don't actually run any commands; just print "
                             "the pipeline.")
    parser.add_argument("--flowchart", dest="flowchart",
                        metavar="FILE",
                        type=str,
                        help="Don't actually run any commands; just print "
                             "the pipeline as a flowchart.")
    parser.add_argument("--key_legend_in_graph",
                        dest="key_legend_in_graph",
                        action="store_true",
                        default=False,
                        help="Print out legend and key for dependency "
                             "graph.")
    parser.add_argument("--forced_tasks", dest="forced_tasks",
                        action="append",
                        default=list(),
                        metavar="JOBNAME",
                        type=str,
                        help="Pipeline task(s) which will be included "
                             "even if they are up to date.")
    parser.add_argument('--config',
                        help='Meta YAML config')

    # get help string
    f = StringIO.StringIO()
    parser.print_help(f)
    helpstr = f.getvalue()
    options = parser.parse_args()

    mandatory_options = ['config']
'''
    parser.add_argument(
        '-o',
        '--outdir',
        required = True,
        help='output directory'

    )
    parser.add_argument(
        '-f',
        '--fastq_file',
        required = True,
        help="RASL-Seq fastq file name"

    )
    parser.add_argument(
        '-p',
        '--probe_file',
        required = True,
        help = " Specifies a tab delemeted  probes file containing the following columns: AcceptorProbeSequence \
                                DonorProbeSequence AcceptorAdaptorSequence DonorAdaptorSequence ProbeName, example \
                                probes.txt "
    )
    parser.add_argument(
        '-w',
        '--plate_well_bc',
        required = True,
        help = "Specifies a tab delemeted file of the input plate and well barcode file containing  the following columns: PlateBarcode and WellBarcode"
    )
    parser.add_argument(
        '-c',
        '--cpuNum',
        dest="cpuNum",
        default= 4,
        type=int,
        help = "Number of CPU to use [DEFAULT: %(default)s]"
    )
    parser.add_argument(
        '-l',
        '--trimleft',
        dest="trimleft",
        required = True,
        type=int,
        help = "Length of sequence  to trim from the 3' end, length of well bacode + adaptor 1 (AD1)"

    )
    parser.add_argument(
        '-r',
        '--trimright',
        dest='trimright',
        required =True,
        type = int,
        help = "lenght of sequence to trim from the 5' end, length of plate barcode + Adaptor 2 (AD2)"
    )
    parser.add_argument("-n", "--just_print", dest="just_print",
                        action="store_true", default=False,
                        help="Don't actually run any commands; just print "
                             "the pipeline.")
    parser.add_argument("--forced_tasks", dest="forced_tasks",
                        action="append",
                        default=list(),
                        metavar="JOBNAME",
                        type=str,
                        help="Pipeline task(s) which will be included "
                             "even if they are up to date.")
    parser.add_argument("-t", "--target_tasks", dest="target_tasks",
                        action="append",
                        default=list(),
                        metavar="JOBNAME",
                        type=str,
                        help="Target task(s) of pipeline.")
    parser.add_argument("--flowchart", dest="flowchart",
                        metavar="FILE",
                        type=str,
                        help="Don't actually run any commands; just print "
                             "the pipeline as a flowchart.")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        action="count", default=0,
                        help="Print more verbose messages for each "
                             "additional verbose level.")
    return parser.parse_args()

    def check_mandatory_options(options, mandatory_options, helpstr):
        """
        Check if specified mandatory options have been defined
        """
        missing_options = []
        for o in mandatory_options:
            if not getattr(options, o):
                missing_options.append("--" + o)

        if not len(missing_options):
            return

        raise Exception("Missing mandatory parameter%s: %s.\n\n%s\n\n" %
                        ("s" if len(missing_options) > 1 else "",
                         ", ".join(missing_options),
                         helpstr))
    check_mandatory_options(options, mandatory_options, helpstr)
    return options

def setup_shell_environment():
    """Set all the shell variables using config value"""
    installdir = sys.prefix
    rldpath = os.path.join(installdir, "lib", "R-3.2.3", "lib64","R", "lib")
    if 'LD_LIBRARY_PATH' not in os.environ:
        os.environ['LD_LIBRARY_PATH'] = rldpath
    else:
        os.environ['LD_LIBRARY_PATH'] += rldpath



def isGzip(input):
    if input.endswith(".gz"):
        return True
    else:
        return False

def symlink(src, dst):
    '''
    Create symlink src -> dst
    Overwrite dst if exists
    Do not create if src does not exist
    '''
    rel = relpath(src, dirname(dst))
    if exists(dst):
        os.unlink(dst)
    if not exists(src):
        return
    os.symlink(rel, dst)
def runCommand(cmd, printCMD):
    import subprocess
    if printCMD == 'T' or printCMD is True:
        print cmd
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    sout, serr = p.communicate()
    return sout,serr

def run_cmd(cmd_str):
    """
    Throw exception if run command fails
    """
    process = subprocess.Popen(cmd_str, stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE, shell = True)
    stdout_str, stderr_str = process.communicate()
    if process.returncode != 0:
        raise Exception("Failed to run '%s'\n%s%sNon-zero exit status %s" %
                            (cmd_str, stdout_str, stderr_str, process.returncode))

def which(program):
    """Check if the excutable exists in the users path
    """
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

    return None


#def plot_summary(barcodes_obs, barcode_table, directory, expt_id):
    #"""Plot barcode split stat
    #TODO: Modify this function to fit for my purpose
    #"""
    #barcodes, counts, matches = get_vectors(barcodes_obs, barcode_table)
    #df = DataFrame({'barcode': barcodes,
                    #'count': counts,
                    #'matched': matches})
    #p = ggplot2.ggplot(df) + \
        #ggplot2.aes_string(x='factor(matched)', y='count / 1000000') + \
        #ggplot2.geom_boxplot(outlier_size = 0) + \
        #ggplot2.geom_jitter() + \
        #ggplot2.ggtitle(label = expt_id) + \
        #ggplot2.ggplot2.xlab(label = "") + \
        #ggplot2.scale_y_continuous(name = "Count\n(million reads)")

    #filename = "{0}/{1}.png".format(directory, expt_id)
    #grdevices.png(filename=filename, width=4, height=5, unit='in', res=300)
    #p.plot()
    #grdevices.dev_off()

#def get_vectors(barcodes_obs, barcode_table):
    #""" Utility function for plot_summary function"""
    #barcodes = []
    #counts = []
    #matches = []
    #for barcode in dict.keys(barcodes_obs):
        #barcodes.append(barcode)
        #counts.append(barcodes_obs[barcode])
        #match = "matched" if barcode_table.get(barcode) else "unmatched"
        #matches.append(match)
    #return barcodes, counts, matches

def make_logger(options, file_name):
    """
    Sets up logging for the pipeline so that messages are synchronized across
    multiple processes
    """

    MESSAGE = 15
    logging.addLevelName(MESSAGE, "MESSAGE")

    def setup_std_logging(logger, log_file, verbose):
        """
        set up logging using programme options
        """
        class debug_filter(logging.Filter):
            """
            Ignore INFO messages
            """
            def filter(self, record):
                return logging.INFO != record.levelno

        class NullHandler(logging.Handler):
            """
            for when there is no logging
            """
            def emit(self, record):
                pass

        # We are interested in all messages
        logger.setLevel(logging.DEBUG)
        has_handler = False

        # log to file if that is specified
        if log_file:
            handler = logging.FileHandler(log_file, delay=False)
            handler.setFormatter(
                logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)6s - %(message)s"))
            handler.setLevel(MESSAGE)
            logger.addHandler(handler)
            has_handler = True

        # log to stderr if verbose
        if verbose:
            stderrhandler = logging.StreamHandler(sys.stderr)
            stderrhandler.setFormatter(
                    logging.Formatter("    %(message)s")
                    )
            stderrhandler.setLevel(logging.DEBUG)
            if log_file:
                stderrhandler.addFilter(debug_filter())
            logger.addHandler(stderrhandler)
            has_handler = True

        # no logging
        if not has_handler:
            logger.addHandler(NullHandler())

    # set up log
    logger_name = os.path.splitext(os.path.basename(file_name))[0]
    logger = logging.getLogger(logger_name)
    setup_std_logging(logger, options.log_file, options.verbose)

    # Allow logging across Ruffus pipeline
    def get_logger(logger_name, args):
        return logger

    (logger_proxy,
     logging_mutex) = make_shared_logger_and_proxy(get_logger,
                                                   logger_name,
                                                   {})

    return logger_proxy, logging_mutex
