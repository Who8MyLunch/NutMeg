
import os

import IPython.display

from processor import NutmegProbe, NutmegClip


def example():
    f = '/home/pierre/Videos/GoPro/Malibu/GOPR6248.MP4'

    p = NutmegProbe()
    p.probe(f)

    print('\nContainer:')
    IPython.display.display(p.results.container)

    for s in p.results.streams:
        print('\nStream {}:'.format(s.index))
        IPython.display.display(s)



#------------------------------------------------

if __name__ == '__main__':
    example()
