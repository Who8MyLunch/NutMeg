
from __future__ import division, print_function, unicode_literals, absolute_import

import os
import sys
import contextlib
import time
import json

import numpy as np
import sarge
# import shortuuid

try:
    from .namespace import Struct
except SystemError:
    from namespace import Struct

"""
This is a collection of classes and function for doing useful work with video files via ffmpeg.
"""

#------------------------------------------------
# Helper functions

def find_executable(executable, path=None):
    """
    This function was originally inspired by the public-domain function `find_executable`
    by Anatoly Techtonik <techtonik@gmail.com> at https://gist.github.com/4368898.

    Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']).

    Checks for all executable extensions. Returns full path if found otherwise None.
    """
    if path is None:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)

    extlist = ['']
    if sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext

    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None

#------------------------------------------------

class Proc(object):
    """Base class for asynchronously running an external commandline application.
    """
    def __init__(self, fname_exe, verbose=False):
        """Initialize new Processor instance.
        """
        self.fname_exe = find_executable(fname_exe)

        if not os.path.isfile(self.fname_exe):
            raise ValueError('Executable not found: {}'.format(self.fname_exe))

        # if not path_work:
        #     path_work = os.path.curdir
        # self.path_work = os.path.normpath(os.path.abspath(path_work))

        self._proc = None
        self._results = None
        self.command = None
        self.verbose = verbose

    def __repr__(self):
        if self.running:
            msg = 'Nutmeg process running with PID {}'.format(self.pid)
        else:
            msg = 'Nutmeg process not running'
        return str(msg)

    def start(self):
        """Run task process via Sarge package.
        """
        self._results = None

        if not self.command:
            raise ValueError('command not defined')

        # Pre-existing process ID?
        if self.running:
            if self.verbose:
                print('\nProcess already running with PID: {:d}'.format(self.pid))
            return self.pid

        # Instantiate command and run it
        self._proc = sarge.Command(self.command, stdout=sarge.Capture(), stderr=sarge.Capture())
        self._proc.run(async=True)

        if not self.running:
           raise ValueError('Problem starting process: {}'.format(self.fname_exe))

    def wait(self):
        """Wait until child process finishes, then process any results.
        """
        if self._proc:
            self._proc.wait()
            self.process_results()

    def stop(self):
        """Halt the process.
        """
        if self.running:
            self._proc.kill()
            self._proc.wait()
            self._proc = None
            self._results = None

            if self.verbose:
                print('\nProcess stopped.')
        else:
            if self.verbose:
                print('\nProcess not running.  Nothing to stop.')

    @property
    def pid(self):
        """Process ID
        """
        if self._proc:
            return self._proc.process.pid
        else:
            return None

    @property
    def running(self):
        """Return True if process is running, otherwise False.
        """
        if self._proc:
            return self._proc.poll() is None
        else:
            return False

    @property
    def results(self):
        """Return any processing results upon completion.
        """
        if self.running:
            self._proc.wait()

        if not self._proc:
            return None

        if not self._results:
            lines_stdout, lines_stderr = self._capture_stdout_stderr()
            new_results = Struct()
            new_results.lines_stdout = lines_stdout
            new_results.lines_stderr = lines_stderr

            self.process_results(new_results)
            self._results = new_results

        return self._results

    def _capture_stdout_stderr(self):
        """Internal function to capture all lines of text from stdout and stderr.
        This method returns None if process is still running.
        """
        if self.running:
            return None

        lines_stdout = []
        for l in self._proc.stdout.text.split('\n'):
            lines_stdout.extend(l.split('\r'))

        lines_stderr = []
        for l in self._proc.stderr.text.split('\n'):
            lines_stderr.extend(l.split('\r'))

        return lines_stdout, lines_stderr

    def process_results(self, lines_out, lines_err):
        raise NotImplementedError('Please override this method in your implementation.')



class NutmegProbe(Proc):
    """Extract information from video using ffprobe command
    """
    def __init__(self, fname_in=None, fname_exe='ffprobe', verbose=False):
        """
        Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)
        if fname_in:
            self.probe(fname_in)

    def probe(self, fname_in):
        """Query video file for detailed information
        """
        if not os.path.isfile(fname_in):
            raise ValueError('File not found: {}'.format(fname_in))

        parts = [self.fname_exe,
                 '-hide_banner',
                 '-show_format',
                 '-show_streams',
                 # '-unit -prefix -pretty',
                 '-print_format json',
                 '-i ' + fname_in]
                 # '-show_pixel_formats',

        self.command = ' '.join(parts)
        self.start()

    def process_results(self, results):
        """Parse lines of JSON text from stdout, extract container and stream information
        """
        text = ' '.join(results.lines_stdout)
        parsed = json.loads(text)

        streams = [Struct(s) for s in parsed['streams']]
        results.streams = streams
        results.num_streams = len(streams)

        results.container = Struct(parsed['format'])




class NutmegIntra(Proc):
    """Convert a video file to an intermediate formate suitable for editing.
    """
    def __init__(self, fname_in=None, fname_exe='ffmpeg', verbose=True):
        """
        Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)
        if fname_in:
            self.intra(fname_in)

    def intra(self, fname_in):
        """
        Convert video file.

        Nice terse description of pseudo AVC-I via ffmpeg
        https://vimeo.com/194400625

        intra
        https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping

        https://trac.ffmpeg.org/wiki/Encode/H.264
        """
        if not os.path.isfile(fname_in):
            raise ValueError('File does not exist: {}'.format(fname_in))

        b, e = os.path.splitext(fname_in)
        self.fname_out = b + '.intra.mp4'

        # Command parts
        parts = [self.fname_exe,
                 '-y',
                 '-hide_banner',
                 '-loglevel info',
                 # '-report',   # lots of good debug info from ffmpeg
                 '-i {}'.format(fname_in),
                 '-codec:a aac',
                 '-codec:v libx264',
                 '-tune fastdecode',
                 '-preset ultrafast',
                 '-pix_fmt yuvj420p',
                 '-crf 23',
                 # '-profile:v baseline -level 3.0',
                 # '-me_method tesa
                 # '-subq 9',
                 '-partitions all -direct-pred auto -psy 0',
                 # '-b:v 960M -bufsize 960M -level 5.1',
                 '-g 0 -keyint_min 0',
                 '-x264opts filler -x264opts colorprim=bt709 -x264opts transfer=bt709',
                 '-x264opts colormatrix=bt709 -x264opts force-cfr',
                 '-movflags +faststart+rtphint+disable_chpl+separate_moof+default_base_moof',
                 self.fname_out]

        self.command = ' '.join(parts)
        self.start()


    def process_results(self, results):
        """Return video processing results.
        """
        if not os.path.isfile(self.fname_out):
            raise ValueError('Output file not found: {}'.format(self.fname_out))

        results.fname_out = self.fname_out




class NutmegClip(Proc):
    """Extract clip from video file.
    """
    def __init__(self, fname_exe='ffmpeg', verbose=False):
        """
        Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)

    def clip(self, fname_in, time_start, time_stop=None, duration=None):
        """Extract clip from video file between two specified times.
        """
        if not time_stop and not duration:
            raise ValueError('Must specify at least one of `time_stop` or `duration`')

        if duration:
            time_stop = time_start + duration

        b, e = os.path.splitext(fname_in)
        self.fname_out = '{}.clip-{:.2f}-{:.2f}.mp4'.format(b, time_start, time_stop)

        # Command parts
        parts = [self.fname_exe,
                 '-y',
                 '-hide_banner',
                 '-loglevel warning',
                 # '-report',   # lots of good debug info from ffmpeg
                 '-i {}'.format(fname_in),
                 '-codec:a copy',
                 '-codec:v copy',
                 '-ss {}'.format(time_start),
                 '-to {}'.format(time_stop),
                 self.fname_out]

        self.command = ' '.join(parts)
        self.start()

    def process_results(self, results):
        """Return video processing results.
        """
        if not os.path.isfile(self.fname_out):
            raise ValueError('Output file not found: {}'.format(self.fname_out))

        results.fname_out = self.fname_out

#################################################
# Convenience functions

def probe(fname_video):
    p = NutmegProbe(fname_video)
    return p.results

def intra(fname_video):
    i = NutmegIntra(fname_video)
    return i.results

#------------------------------------------------


if __name__ == '__main__':

    print(1)
    f = '/home/pierre/Videos/GoPro/Malibu/GOPR6250.MP4'
    intra = NutmegIntra(f)
    print(2)
    probe = NutmegProbe(intra.results.fname_out)

    print(3)
    clip = NutmegClip()

