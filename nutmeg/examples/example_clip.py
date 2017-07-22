
import os

import IPython.display

import nutmeg


def example():
    f = '/home/pierre/Projects/GoProHelper/notebooks/data/GOPR8802.intra.mp4'

    # command
    p = nutmeg.NutmegClip()

    p.run(f, 0.1, duration=2.5)




#------------------------------------------------

if __name__ == '__main__':
    example()
