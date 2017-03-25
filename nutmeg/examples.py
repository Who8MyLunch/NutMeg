
import IPython.display

from processor import NutmegProbe


# f = '<path_to_video_file>/<your_video_file_name_here.mp4'
f = '/home/pierre/Videos/GoPro/Malibu/GOPR6248.MP4'

p = NutmegProbe()
p.probe(f)


print('\nContainer:')
IPython.display.display(p.results.container)

print('\nNumber of streams: {}'.format(p.results.num_streams))

for s in p.results.streams:
    print('\nStream {}:'.format(s.index))
    IPython.display.display(s)


