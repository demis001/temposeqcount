# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import time
import subprocess
from paver.easy import *
from os.path import islink, isfile,join,basename,dirname,exists,relpath,abspath
from paver.setuputils import setup
try:
    from paver.virtual import bootstrap, virtualenv
except ImportError, e:
    info(
        "VirtualEnv must be installed to enable 'paver bootstrap'. If you need this command, run: pip install virtualenv"
    )

# Import parameters from the setup file.
sys.path.append('.')
from setup import (
    setup_dict, get_project_files, print_success_message,
    print_failure_message, _lint, _test, _test_all,
    CODE_DIRECTORY, DOCS_DIRECTORY, TESTS_DIRECTORY, PYTEST_FLAGS)

from paver.easy import options, task, needs, consume_args
from paver.setuputils import install_distutils_tasks

options(setup=setup_dict,
        star=Bunch(
        sdir=path('raslpipe/download'),
        bindir=path('raslpipe/bin')
        ),
         FastQC=Bunch(
            url='http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.2.zip',
            downloads=path('raslpipe/download'),
            installdir=join(sys.prefix,'lib')
        ),
        fastx_lib=Bunch(
            url='https://github.com/agordon/libgtextutils/releases/download/0.7/libgtextutils-0.7.tar.gz',
            downloads=path('raslpipe/download'),
            installdir=join(sys.prefix, 'lib', 'libgtextutils')
        ),
        fastx=Bunch(
            url='https://github.com/agordon/fastx_toolkit/releases/download/0.0.14/fastx_toolkit-0.0.14.tar.bz2',
            downloads=path('raslpipe/download'),
            installdir=join(sys.prefix, 'lib', 'fastx_toolkit')

        ),
        ngsutils=Bunch(
            url='https://github.com/ngsutils/ngsutils/archive/ngsutils-0.5.7.tar.gz',
            downloads=path('raslpipe/download'),

        ),
        auto_barcode=Bunch(
            url='https://github.com/mfcovington/auto_barcode/archive/2.1.2.tar.gz',
            downloads=path('raslpipe/download')

        ),
        R=Bunch(
            url='https://cran.r-project.org/src/base/R-3/R-3.2.3.tar.gz',
            downloads=path('raslpipe/download'),
            installdir=join(sys.prefix, 'lib', "R-3.2.3")

        ),
        rpy2=Bunch(
            url='https://pypi.python.org/packages/source/r/rpy2/rpy2-2.7.8.tar.gz',
            downloads=path('raslpipe/download')

        ),
        seqtk=Bunch(
            url='https://github.com/lh3/seqtk.git',
            downloads=path('raslpipe/download')

        ),
        environ=Bunch(
            installdir=path('raslpipe/lib')

        ),
          settings=Bunch(
            shell_file=path('raslpipe/files/settings.sh')
        ),
        samtools=Bunch(
          sdir=path('raslpipe/download'),
          bindir=path('raslpipe/bin')
        ),
        help2man=Bunch(
        sdir=path('raslpipe/download'),
            url='http://ftp.gnu.org/gnu/help2man/help2man-1.43.3.tar.gz',
        ),
        libtool=Bunch(
        sdir=path('raslpipe/download'),
        url='http://mirror.easthsia.com/gnu/libtool/libtool-2.4.tar.gz'
        ),
        textinfo=Bunch(
        sdir=path('raslpipe/download'),
        url='http://ftp.gnu.org/gnu/texinfo/texinfo-6.1.tar.gz'
        ),
        graphviz=Bunch(
        sdir=path('raslpipe/download'),
        url='http://ftp.osuosl.org/pub/blfs/conglomeration/graphviz/graphviz-2.38.0.tar.gz'
        ),
        virtualenv=Bunch(
        packages_to_install=[],
        no_site_packages=True)
        )

INSTRUICTIONS = """
Run
    $ source raslpipe/bin/activate
to enter the virtual environment and
    $ deactivate
to exit the environment.

"""

install_distutils_tasks()

## Miscellaneous helper functions


@task
def bootstrap(options):
    """Create virtualenv in ./bootstrap"""
    try:
        import virtualenv
    except ImportError, e:
        raise RuntimeError("Virtualenv is needed for bootstrap")
    options.virtualenv.no_site_packages=False
    options.bootstrap.no_site_packages=False
    call_task("paver.virtualenv.boostrap")

@task
def download_compile_star(options):
    """installs the current package"""
    starbin=join(sys.prefix,'bin','STAR')
    if not exists(starbin):
        info("Compiling STAR...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.star.sdir
        bdir = path(currwd) / options.star.bindir
        dist = join(sys.prefix, 'bin', 'STAR')
        if not islink(dist):
            sh('(cd %s; wget https://github.com/alexdobin/STAR/archive/2.5.2a.tar.gz -O- | tar xzf -; cd STAR-2.5.2a; make; ln -s %s/STAR-2.5.2a/bin/Linux_x86_64/STAR %s; cd %s)' % (sdir, sdir, bdir, sdir))

@task
def installggplot():
    """install ggplot"""
    try:
        import ggplot
    except ImportError:
        cmd = 'pip install git+https://github.com/yhat/ggplot'
        sh(cmd)

@task
def download_compile_seqtk(options):
    """Download and compile seqtk"""
    appbin=join(sys.prefix, 'bin', 'seqtk')
    srcdir = join(options.seqtk.downloads, "seqtk")
    if not exists(appbin):
        if exists(srcdir):
            sh('cd %s ; cd seqtk;make' %(options.seqtk.downloads))
        else:
            sh('cd %s ;git clone %s ; cd seqtk ; make' %(options.seqtk.downloads, options.seqtk.url))
@task
def download_compile_samtools(options):
    """installs the current package"""
    samtoolsbin=join(sys.prefix,'bin','samtools')
    if not exists(samtoolsbin):
        info("Compiling samtools....")
        currwd = os.getcwd()
        sdir = path(currwd) / options.samtools.sdir
        sh('(cd %s; wget https://github.com/samtools/htslib/archive/1.1.tar.gz -O- | tar xzf -; mv htslib-* htslib;wget https://github.com/samtools/samtools/archive/1.1.tar.gz -O- | tar xzf -; mv samtools-* samtools; cd samtools;make; cd %s)' % (sdir, sdir))

@task
def install_fastax_lib(options):
    """Install lib required for fastx"""
    info("Installing lib required for fastx ..." )
    installdir = abspath(options.fastx_lib.installdir)
    if not exists(installdir):
        lbcmd = 'cd %s   && wget %s && tar -xvf libgtextutils-0.7.tar.gz  && cd libgtextutils-0.7 && ./configure --prefix=%s && make &&  make install' %(options.fastx_lib.downloads, options.fastx_lib.url, installdir)
        sh(lbcmd)

@task
def install_fastx(options):
    """Install fastx toolkit ..."""
    info("Installing fastx toolkit ...")
    installdir = abspath(options.fastx.installdir)
    libdir = abspath(options.fastx_lib.installdir)
    if not exists(installdir):
        lbcmd = 'cd %s && wget %s && tar -xjvf fastx_toolkit-0.0.14.tar.bz2  && cd fastx_toolkit-0.0.14 && export PKG_CONFIG_PATH=%s/lib/pkgconfig:$PKG_CONFIG_PATH && ./configure --prefix=%s && make && make install' %(options.fastx.downloads, options.fastx.url,libdir, installdir)
        sh(lbcmd)

@task
def install_ngsutils(options):
    """Install ngsutils ..."""
    info ("Installing ngsutils ...")
    installdir = abspath(options.ngsutils.installdir)
    srcdir = abspath(options.ngsutils.installdir)
    if not exists(installdir):
        lbcmd = 'cd %s && wget %s && tar -xvf ngsutils-0.5.7.tar.gz && cd ngsutils-ngsutils-0.5.7 && make' %(options.ngsutils.downloads, options.ngsutils.url)
        sh(lbcmd)

@task
def install_R(options):
    """Install R64 ..."""
    info("Installing R ...")
    installdir=abspath(options.R.installdir)
    dist = join(sys.prefix, 'bin', "R")
    src = join(options.R.installdir, "bin", "R")
    if not exists(dist):
        lbcmd = 'cd %s && wget %s && tar -xvf R-3.2.3.tar.gz && cd R-3.2.3 && ./configure --enable-R-shlib --prefix=%s && make && make install ' %(options.R.downloads, options.R.url, installdir)
        sh(lbcmd)
        # make symbolic link to the bin dir
        os.symlink(src, dist)
        os.chmod(dist, 0755)
@task
@needs('install_R')
def setenviron(options):
    """Setup environment varaible"""
    src = options.environ.installdir
    rldpath = os.path.join(src, "R-3.2.3", "lib64", "R", "lib")
    if 'LD_LIBRARY_PATH' not in os.environ:
        os.environ['LD_LIBRARY_PATH']=rldpath
    else:
        os.environ['LD_LIBRARY_PATH']+=rldpath


@task
@needs('setenviron')
def install_rpy2(options):
    """Install rpy2 python package"""
    info("Install rpy2 python package, require dependencies ...")
    #rhome=join(sys.prefix, "lib", "R-2.12", "lib64", "R", "lib")
    rinclude=join(sys.prefix, "lib", "R-3.2.3", "lib64", "R", "include")
    dist = join(sys.prefix, 'download', 'rpy2-2.7.8')
    if not exists(dist):
        lbcmd = 'cd %s && wget %s && tar -xvf rpy2-2.7.8.tar.gz && cd rpy2-2.7.8 && export CFLAGS="-I%s" && python setup.py build  install ' %(options.rpy2.downloads, options.rpy2.url, rinclude)
        sh(lbcmd)
    else:
        lbcmd = 'cd %s  && export CFLAGS="-I%s" && python setup.py build  install ' %(dist,rinclude)
        sh(lbcmd)

@task
def download_compile_textinfo(options):
    """installs the textinfo, required by graphviz"""
    makeinfobin=join(sys.prefix,'bin','makeinfo')
    if not exists(makeinfobin):
        info("Installing textinfo...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.textinfo.sdir
        url=options.textinfo.url
        info(sdir)
        sh('(cd %s; wget %s; tar -xzvf texinfo-6.1.tar.gz;cd texinfo-6.1;./configure --prefix=%s/texinfo-6.1;make;make install)' %(sdir,url, sdir))

@task
def download_compile_help2man(options):
    """installs the help2man, required by graphviz"""
    help2manbin=join(sys.prefix,'bin','help2man')
    if not exists(help2manbin):
        info("Installing help2man...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.help2man.sdir
        url = options.help2man.url
        src = join(sys.prefix, "download",'help2man-1.43.3' )
        info(sdir)
        sh('cd %s; wget %s;tar -xzvf help2man-1.43.3.tar.gz; cd help2man-1.43.3; ./configure CC="cc" --prefix=%s;make;make install' %(sdir,url,src))

@task
#@needs('download_compile_help2man', 'download_compile_textinfo')
def download_compile_libtool(options):
    """installs libtool, needed by graphviz ... """
    libtoolbin=join(sys.prefix,'bin','libtool')
    if not exists(libtoolbin):
        info("Installing libtool, needed by graphviz ...")
        currwd = os.getcwd()
        sdir = path(currwd)  / options.libtool.sdir
        url = options.libtool.url
        info(sdir)
        sh('(cd %s; wget %s; tar -xzvf libtool-2.4.tar.gz;cd libtool-2.4;./configure CC="cc" --prefix=%s/libtool-2.4;make;make install)' %(sdir,url, sdir))

@task
#@needs('download_compile_libtool')
def download_compile_graphviz(options):
    """installs the current package"""
    graphvizbin=join(sys.prefix,'bin','dot')
    url = options.graphviz.url
    info(graphvizbin)
    if not exists(graphvizbin):
        info("Installing graphviz...")
        currwd=os.getcwd()
        sdir =path(currwd) / options.graphviz.sdir
        info(sdir)
        sh('(cd %s;wget %s -O- | tar xzf -; cd graphviz-2.38.0;./configure --prefix=%s/graphviz-2.38.0;make;make install)' %(sdir,url,sdir))
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:~/data/jimaprogramming/python/raslpipe/raslpipe/lib/R-3.2.3/lib64/R/lib/

@task
def insallRpackages(options):
    """Install R packages that cannot be installed using pip install ..."""
    #from rpy2.robjects.packages import importr
    src = join(sys.prefix, "lib", "R-3.2.3", "lib64", "R", "lib")
    spe = "$"
    cmd = 'export LD_LIBRARY_PATH=%sLD_LIBRARY_PATH:%s' %(spe,src)
    sh(cmd)
   # import rpy2.robjects as robjects
    import rpy2.robjects.packages as rpackages
    #from rpy2.robjects.vectors import StrVector
    packageNames = ('ggplot2')

    if all(rpackages.isinstalled(x) for x in packageNames):

        have_packages = True

    else:

        have_packages = False

    if not have_packages:

         #utils = rpackages.importr('utils')
         #utils.chooseCRANmirror(ind=1, useHTTPS=False)
         packnames_to_install = [x for x in packageNames if not rpackages.isinstalled(x)]
        # if len(packnames_to_install) > 0:
         #    utils.install_packages(StrVector(packnames_to_install))
         if len(packnames_to_install) > 0:
             # install biocondcutor package
            base = rpackages.importr('base')
            base.source("http://www.bioconductor.org/biocLite.R")
            biocinstaller = rpackages.importr("BiocInstaller")
            biocinstaller.biocLite("ggplot2", suppressUpdates=True)

@task
def download_install_fastqc(options):
    import zipfile
    from glob import glob
    dlpath = join(options.FastQC.downloads,'fastqc_v*.zip')
    fastqczip = glob(dlpath)
    # No need to redownload
    if not len(fastqczip):
        info("Downloading FastQC from %s" % options.FastQC.url)
        dlcmd = 'cd %s && [ ! -e fastqc*.zip ] && wget %s' % (options.FastQC.downloads,options.FastQC.url)
        sh(dlcmd)
    else:
        info("FastQC Already downloaded")
    fastqczip = glob(dlpath)
    fqcdir = join(options.FastQC.installdir,'FastQC')
    # Check to see if it is extracted already
    if not exists(fqcdir):
        info("Unpacking FastQC")
        zfh = zipfile.ZipFile(fastqczip[-1])
        zfh.extractall(options.FastQC.installdir)
        zfh.close()
    else:
        info("FastQC already unpacked")
    # Make symlink to bin
    src = relpath(join(fqcdir,'fastqc'),join(sys.prefix,'bin'))
    dst = join(sys.prefix,'bin','fastqc')
    if not exists(dst):
        info("Installing fastqc symlink")
        os.symlink(src,dst)
        os.chmod(dst, 0755)
    else:
        info("fastqc symlink already exists")

@task
def set_ld_path(options):
    """Create setting.sh file and source it"""
    src = options.settings.shell_file
    if exists(src):
        next
    else:
        with open(src, 'w') as myfile:
            installdir = sys.prefix
            rldpath = os.path.join(installdir, "lib", "R-3.2.3", "lib64","R", "lib")
            sep ="$"
            ldpath = "export LD_LIBRARY_PATH=%sLD_LIBRARY_PATH:%s\n"%(sep, rldpath)
            myfile.write(ldpath)
    info(src)
    sh('source %s' %(src))

def print_passed():
    # generated on http://patorjk.com/software/taag/#p=display&f=Small&t=PASSED
    print_success_message(r'''  ___  _   ___ ___ ___ ___
 | _ \/_\ / __/ __| __|   \
 |  _/ _ \\__ \__ \ _|| |) |
 |_|/_/ \_\___/___/___|___/
''')


def print_failed():
    # generated on http://patorjk.com/software/taag/#p=display&f=Small&t=FAILED
    print_failure_message(r'''  ___ _   ___ _    ___ ___
 | __/_\ |_ _| |  | __|   \
 | _/ _ \ | || |__| _|| |) |
 |_/_/ \_\___|____|___|___/
''')


class cwd(object):
    """Class used for temporarily changing directories. Can be though of
    as a `pushd /my/dir' then a `popd' at the end.
    """
    def __init__(self, newcwd):
        """:param newcwd: directory to make the cwd
        :type newcwd: :class:`str`
        """
        self.newcwd = newcwd

    def __enter__(self):
        self.oldcwd = os.getcwd()
        os.chdir(self.newcwd)
        return os.getcwd()

    def __exit__(self, type_, value, traceback):
        # This acts like a `finally' clause: it will always be executed.
        os.chdir(self.oldcwd)


## Task-related functions

def _doc_make(*make_args):
    """Run make in sphinx' docs directory.

    :return: exit code
    """
    if sys.platform == 'win32':
        # Windows
        make_cmd = ['make.bat']
    else:
        # Linux, Mac OS X, and others
        make_cmd = ['make']
    make_cmd.extend(make_args)

    # Account for a stupid Python "bug" on Windows:
    # <http://bugs.python.org/issue15533>
    with cwd(DOCS_DIRECTORY):
        retcode = subprocess.call(make_cmd)
    return retcode


## Tasks


@task
def init():
    """Initializing everything so you can start working"""
    info ("virtual environment successfully bootstrapped.")
    info (INSTRUICTIONS)

@task
@needs('install_python_dependencies','install_other_dependencies')
def install_dependencies():
    pass

@task
#@needs('download_compile_star', 'download_install_fastqc', 'download_compile_seqtk','download_compile_samtools','install_fastax_lib', 'install_fastx', 'in)
@needs('installggplot','download_compile_star', 'download_install_fastqc', 'download_compile_seqtk','download_compile_samtools','install_fastax_lib', 'install_fastx', 'download_compile_help2man', 'download_compile_textinfo','download_compile_libtool','download_compile_graphviz')
def install_other_dependencies():
    pass

@task
def install_python_dependencies():
    sh('pip install -r requirements-dev.txt  --download-cache raslpipe/download/.pip_cache')

@task
def install_python_dependencies_nodeps():
    """Install python package without installing dependencies"""
    sh('pip install -r requirements_nodeps.txt  --download-cache raslpipe/download/.pip_cache')

@task
@needs('install_dependencies')
def prepare():
    """Prepare complete environment
    """
    pass

@task
@needs('prepare','setuptools.command.install')
def install():
    pass

@task
@needs('install')
def develop():
    pass

@task
@needs('prepare','doc_html', 'setuptools.command.sdist')
def sdist():
    """Build the HTML docs and the tarball."""
    pass


@task
def test():
    """Run the unit tests."""
    raise SystemExit(_test())


@task
def lint():
    # This refuses to format properly when running `paver help' unless
    # this ugliness is used.
    ('Perform PEP8 style check, run PyFlakes, and run McCabe complexity '
     'metrics on the code.')
    raise SystemExit(_lint())


@task
def test_all():
    """Perform a style check and run all unit tests."""
    retcode = _test_all()
    if retcode == 0:
        print_passed()
    else:
        print_failed()
    raise SystemExit(retcode)


@task
@consume_args
def run(args):
    """Run the package's main script. All arguments are passed to it."""
    # The main script expects to get the called executable's name as
    # argv[0]. However, paver doesn't provide that in args. Even if it did (or
    # we dove into sys.argv), it wouldn't be useful because it would be paver's
    # executable. So we just pass the package name in as the executable name,
    # since it's close enough. This should never be seen by an end user
    # installing through Setuptools anyway.
    from raslpipe.main import main
    raise SystemExit(main([CODE_DIRECTORY] + args))


@task
def commit():
    """Commit only if all the tests pass."""
    if _test_all() == 0:
        subprocess.check_call(['git', 'commit'])
    else:
        print_failure_message('\nTests failed, not committing.')


@task
def coverage():
    """Run tests and show test coverage report."""
    try:
        import pytest_cov  # NOQA
    except ImportError:
        print_failure_message(
            'Install the pytest coverage plugin to use this task, '
            "i.e., `pip install pytest-cov'.")
        raise SystemExit(1)
    import pytest
    pytest.main(PYTEST_FLAGS + [
        '--cov', CODE_DIRECTORY,
        '--cov-report', 'term-missing',
        TESTS_DIRECTORY])


@task  # NOQA
def doc_watch():
    """Watch for changes in the docs and rebuild HTML docs when changed."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print_failure_message('Install the watchdog package to use this task, '
                              "i.e., `pip install watchdog'.")
        raise SystemExit(1)

    class RebuildDocsEventHandler(FileSystemEventHandler):
        def __init__(self, base_paths):
            self.base_paths = base_paths

        def dispatch(self, event):
            """Dispatches events to the appropriate methods.
            :param event: The event object representing the file system event.
            :type event: :class:`watchdog.events.FileSystemEvent`
            """
            for base_path in self.base_paths:
                if event.src_path.endswith(base_path):
                    super(RebuildDocsEventHandler, self).dispatch(event)
                    # We found one that matches. We're done.
                    return

        def on_modified(self, event):
            print_failure_message('Modification detected. Rebuilding docs.')
            # # Strip off the path prefix.
            # import os
            # if event.src_path[len(os.getcwd()) + 1:].startswith(
            #         CODE_DIRECTORY):
            #     # sphinx-build doesn't always pick up changes on code files,
            #     # even though they are used to generate the documentation. As
            #     # a workaround, just clean before building.
            doc_html()
            print_success_message('Docs have been rebuilt.')

    print_success_message(
        'Watching for changes in project files, press Ctrl-C to cancel...')
    handler = RebuildDocsEventHandler(get_project_files())
    observer = Observer()
    observer.schedule(handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


@task
@needs('doc_html')
def doc_open():
    """Build the HTML docs and open them in a web browser."""
    doc_index = os.path.join(DOCS_DIRECTORY, 'build', 'html', 'index.html')
    if sys.platform == 'darwin':
        # Mac OS X
        subprocess.check_call(['open', doc_index])
    elif sys.platform == 'win32':
        # Windows
        subprocess.check_call(['start', doc_index], shell=True)
    elif sys.platform == 'linux2':
        # All freedesktop-compatible desktops
        subprocess.check_call(['xdg-open', doc_index])
    else:
        print_failure_message(
            "Unsupported platform. Please open `{0}' manually.".format(
                doc_index))


@task
def get_tasks():
    """Get all paver-defined tasks."""
    from paver.tasks import environment
    for task in environment.get_tasks():
        print(task.shortname)

@task
@needs('install_python_dependencies')
def doc_man():
    """Build man page"""
    retcode=_doc_make('man')
    if retcode:
        raise SystemExit(retcode)


@task
def doc_html():
    """Build the HTML docs."""
    retcode = _doc_make('html')

    if retcode:
        raise SystemExit(retcode)


@task
def doc_clean():
    """Clean (delete) the built docs."""
    retcode = _doc_make('clean')

    if retcode:
        raise SystemExit(retcode)
