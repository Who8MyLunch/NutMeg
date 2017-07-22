
from __future__ import division, print_function, unicode_literals, absolute_import

import os
import sys
import json
import time

import sarge

from ordered_namespace import Struct

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

def safe_number(value):
    """Attempt to convert supplied object to an integer or float.  Return original value if unsucessful.
    """
    try:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    except TypeError:
        return value


#------------------------------------------------

class Proc():
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
        self._stdout = []
        self._stderr = []
        self._results = None
        self.command = ''
        self.verbose = verbose

    def __repr__(self):
        if self.is_running:
            msg = 'Nutmeg process running with PID {}'.format(self.pid)
        else:
            msg = 'Nutmeg process not running'
        return str(msg)

    def run(self):
        """User should override this method to setup their application-specific work command string
        """
        raise NotImplementedError('Please override this method in your subclass implementation.')

    def _start(self):
        """Start work task running in the background.  User should not need to call this directly.
        Work with your subclasses `run` method instead.
        """
        self._results = None

        if not self.command:
            raise ValueError('command not defined')

        # Pre-existing process ID?
        if self.is_running:
            if self.verbose:
                print('\nProcess already running with PID: {:d}'.format(self.pid))
            return self.pid

        # Instantiate command and run it
        self._proc = sarge.Command(self.command, stdout=sarge.Capture(), stderr=sarge.Capture())
        self._proc.run(async=True)

        time.sleep(0.01)

        if not self.is_running:
           raise ValueError('Problem starting process: {}'.format(self.fname_exe))

    def wait(self):
        """Block until background process finishes
        """
        if self._proc:
            self._proc.wait()

    def stop(self):
        """Halt the process
        """
        if self.is_running:
            self._proc.kill()
            self._proc.wait()
            self._proc = None
            self._stdout = None
            self._stderr = None
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
    def is_running(self):
        """Return True if process is running, otherwise False.
        """
        if self._proc:
            return self._proc.poll() is None
        else:
            return False

    @property
    def results(self):
        """Make available any post-processing results upon task completion.
        Block if process is still running in the background.
        """
        if self.is_running:
            self._proc.wait()

        if not self._proc:
            return None

        if not self._results:
            self._capture_stdout_stderr()

        return self._results

    def _capture_stdout_stderr(self):
        """Internal function to capture all lines of text from stdout and stderr.
        Method does nothing if process is still running.
        """
        if self.is_running:
            return

        lines_stdout = []
        for l in self._proc.stdout.text.split('\n'):
            lines_stdout.extend(l.split('\r'))

        lines_stderr = []
        for l in self._proc.stderr.text.split('\n'):
            lines_stderr.extend(l.split('\r'))

        self._stdout = lines_stdout
        self._stderr = lines_stderr
        self._results = self.post_process()

    def post_process(self):
        """do something with self._stdout and self._stderr
        """
        # raise NotImplementedError('Please override this method in your subclass implementation.')
        return True

#------------------------------------------------
#------------------------------------------------


class NutmegProbe(Proc):
    """Extract information from video using ffprobe command
    """
    def __init__(self, fname_in=None, fname_exe='ffprobe', verbose=False):
        """Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)
        if fname_in:
            self.run(fname_in)

    def run(self, fname_in):
        """Query video file for detailed information
        """
        if not os.path.isfile(fname_in):
            raise ValueError('File not found: {}'.format(fname_in))

        parts = [self.fname_exe,
                 '-hide_banner',
                 '-show_format',
                 '-show_streams',
                 '-print_format json',
                 # '-unit -prefix -pretty',
                 '-i ' + fname_in]

        self.command = ' '.join(parts)
        self._start()

    def post_process(self):
        """Parse lines of JSON text from stdout, extract container and stream information.
        """
        text = ' '.join(self._stdout)
        parsed = json.loads(text)

        # Convert any string numerical values to int or float.  Safely.
        container = {k: safe_number(v) for k,v in parsed['format'].items()}
        streams =  [{k: safe_number(v) for k,v in s.items()} for s in parsed['streams']]

        # Store final results in handy namespace structures.  Same as a dict, but access items
        # via attributes.  Includes support for IPython tab-completion.
        results = Struct()
        results.container = Struct(container)
        results.num_streams = len(streams)
        results.streams = [Struct(s) for s in streams]

        return results

#------------------------------------------------


class NutmegIntra(Proc):
    """Convert a video file to an intermediate formate suitable for editing.
    """
    def __init__(self, fname_in=None, fname_exe='ffmpeg', crf=23, verbose=True):
        """Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)
        if fname_in:
            self.run(fname_in, crf=crf)

    def run(self, fname_in, crf=23, block=True):
        """Convert video file to intra-frames only, more suitable for editing.

        Nice terse description of pseudo AVC-I via ffmpeg: https://vimeo.com/194400625

        intra stuff:
        - https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping
        - https://trac.ffmpeg.org/wiki/Encode/H.264
        """
        if not os.path.isfile(fname_in):
            raise ValueError('File not found: {}'.format(fname_in))

        self.fname_in = fname_in
        b, e = os.path.splitext(fname_in)
        self.fname_out = b + '.intra.mp4'

        # Command parts
        # https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping
        # https://ffmpeg.org/ffmpeg-formats.html#Options-8
        parts = [self.fname_exe,
                 '-y',
                 '-hide_banner',
                 '-loglevel info',
                 '-report',   # lots of good debug info from ffmpeg
                 '-i {}'.format(self.fname_in),
                 '-codec:a aac',
                 '-strict -2',      # enable experimental aac
                 '-codec:v libx264',
                 '-preset ultrafast',
                 '-tune fastdecode',
                 '-pix_fmt yuvj420p',
                 '-crf {}'.format(crf),
                 # '-profile:v baseline -level 3.0',
                 # '-direct-pred spatial',
                 '-g 0 -keyint_min 0 -intra',
                 '-x264opts colormatrix=bt709 -x264opts force-cfr',
                 '-movflags +faststart+rtphint+disable_chpl+separate_moof+default_base_moof',
                 self.fname_out]

        self.command = ' '.join(parts)
        self._start()

        if block:
            self.wait()

    def post_process(self):
        """Return video processing results
        """
        if not os.path.isfile(self.fname_out):
            raise ValueError('Output file not found: {}'.format(self.fname_out))

        results = Struct()
        results.probe_in = NutmegProbe(self.fname_in).results
        results.probe_out = NutmegProbe(self.fname_out).results
        results.fname_out = self.fname_out

        return results



class NutmegClip(Proc):
    """Extract clip from video file.
    """
    def __init__(self, fname_exe='ffmpeg', verbose=False):
        """Initialize new Processor instance.
        """
        super().__init__(fname_exe, verbose=verbose)

    def run(self, fname_in, time_start, time_stop=None, duration=None, block=True):
        """Extract clip from video file between two specified times.
        """
        if not time_stop and not duration:
            raise ValueError('Must specify at least one of `time_stop` or `duration`')

        if duration:
            time_stop = time_start + duration

        if not os.path.isfile(fname_in):
            raise ValueError('File not found: {}'.format(fname_in))

        self.fname_in = fname_in
        b, e = os.path.splitext(self.fname_in)
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
        self._start()

        if block:
            self.wait()

    def post_process(self):
        """Return video processing results
        """
        if not os.path.isfile(self.fname_out):
            raise ValueError('Output file not found: {}'.format(self.fname_out))

        results = Struct()
        results.probe_in = NutmegProbe(self.fname_in).results
        results.probe_out = NutmegProbe(self.fname_out).results
        results.fname_out = self.fname_out

        return results

#################################################
# Convenience functions

def probe(fname_video):
    """Probe supplied video file for detailed information
    """
    p = NutmegProbe(fname_video)
    return p.results

def intra(fnames_video):
    """Process supplied file(s) to intra frames for easier editing
    """
    if isinstance(fnames_video, str):
        fnames_video = [fnames_video]

    p = NutmegIntra()
    results = []
    for f in fnames_video:
        print('Processing: {}'.format(os.path.basename(f)))

        p.run(f, block=True)
        results.append(p.results)

    return results

#------------------------------------------------

if __name__ == '__main__':
    pass
