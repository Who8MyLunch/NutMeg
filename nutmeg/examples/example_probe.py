
import os

import IPython.display

import nutmeg


def example():
    f = '/home/pierre/Projects/GoProHelper/notebooks/data/GOPR8802.MP4'

    # command
    p = nutmeg.NutmegProbe(f)
    # p.run(f)

    # display
    print('\nContainer:')
    IPython.display.display(p.results.container)

    for s in p.results.streams:
        print('\nStream {}:'.format(s.index))
        IPython.display.display(s)


#------------------------------------------------

if __name__ == '__main__':
    example()
