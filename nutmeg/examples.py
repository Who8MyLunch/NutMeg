
import os

import IPython.display

from processor import NutmegProbe, NutmegClip


def example_probe():
    f = '/home/pierre/Videos/GoPro/Malibu/GOPR6248.MP4'

    p = NutmegProbe()
    p.probe(f)

    print('\nContainer:')
    IPython.display.display(p.results.container)

    for s in p.results.streams:
        print('\nStream {}:'.format(s.index))
        IPython.display.display(s)


def example_clip():
    f = '/home/pierre/Videos/GoPro/Malibu/GOPR6248.MP4'

    p = NutmegProbe()
    p.probe(f)

    print('\nOriginal file: {}'.format(os.path.basename(f)))
    print('Original duration: {}'.format(p.results.container.duration))

    time_start = 0
    time_stop = 0.5*p.results.container.duration

    c = NutmegClip()
    c.clip(f, time_start, time_stop)

    print('\nClip file: {}'.format(os.path.basename(c.results.fname_out)))

    p = NutmegProbe()
    p.probe(c.results.fname_out)

    print('Clip duration: {}'.format(p.results.container.duration))


if __name__ == '__main__':
    example_clip()
