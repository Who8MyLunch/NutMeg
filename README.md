# NutMeg

A collection of simple video processing tools.  Nice Python classes and functions 
that wrap practical functionality predefined ffmpeg commands.


## Examples

- NutmegProbe

```py
f = '/home/Videos/GoPro/Malibu/GOPR6248.MP4'

p = NutmegProbe()
p.probe(f)


print('\nContainer:')
IPython.display.display(p.results.container)

print('\nNumber of streams: {}'.format(p.results.num_streams))

for s in p.results.streams:
    print('\nStream {}:'.format(s.index))
    IPython.display.display(s)
```

Running the above sample code yields the following output:

Container:
```python
{'bit_rate': '24243114',
 'duration': '40.323617',
 'filename': '/home/Videos/GoPro/Malibu/GOPR6248.MP4',
 'format_long_name': 'QuickTime / MOV',
 'format_name': 'mov,mp4,m4a,3gp,3g2,mj2',
 'nb_programs': 0,
 'nb_streams': 3,
 'probe_score': 100,
 'size': '122196256',
 'start_time': '0.000000',
 'tags': {'compatible_brands': 'avc1isom',
  'creation_time': '2014-07-06T15:20:02.000000Z',
  'major_brand': 'avc1',
  'minor_version': '0'}}
```
Number of streams: 3

Stream 0:
```python
{'avg_frame_rate': '60000/1001',
 'bit_rate': '23967131',
 'bits_per_raw_sample': '8',
 'chroma_location': 'left',
 'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10',
 'codec_name': 'h264',
 'codec_tag': '0x31637661',
 'codec_tag_string': 'avc1',
 'codec_time_base': '1001/120000',
 'codec_type': 'video',
 'coded_height': 1080,
 'coded_width': 1920,
 'color_primaries': 'bt709',
 'color_range': 'pc',
 'color_space': 'bt709',
 'color_transfer': 'bt709',
 'display_aspect_ratio': '16:9',
 'disposition': {'attached_pic': 0,
  'clean_effects': 0,
  'comment': 0,
  'default': 1,
  'dub': 0,
  'forced': 0,
  'hearing_impaired': 0,
  'karaoke': 0,
  'lyrics': 0,
  'original': 0,
  'visual_impaired': 0},
 'duration': '40.323617',
 'duration_ts': 2419417,
 'has_b_frames': 1,
 'height': 1080,
 'index': 0,
 'is_avc': 'true',
 'level': 42,
 'nal_length_size': '4',
 'nb_frames': '2417',
 'pix_fmt': 'yuvj420p',
 'profile': 'Main',
 'r_frame_rate': '60000/1001',
 'refs': 1,
 'sample_aspect_ratio': '1:1',
 'start_pts': 0,
 'start_time': '0.000000',
 'tags': {'creation_time': '2014-07-06T15:20:02.000000Z',
  'encoder': 'GoPro AVC encoder',
  'handler_name': '\rGoPro AVC',
  'language': 'eng',
  'timecode': '15:19:06:51'},
 'time_base': '1/60000',
 'width': 1920}
```

Stream 1:
```python
{'avg_frame_rate': '0/0',
 'bit_rate': '128040',
 'bits_per_sample': 0,
 'channel_layout': 'stereo',
 'channels': 2,
 'codec_long_name': 'AAC (Advanced Audio Coding)',
 'codec_name': 'aac',
 'codec_tag': '0x6134706d',
 'codec_tag_string': 'mp4a',
 'codec_time_base': '1/48000',
 'codec_type': 'audio',
 'disposition': {'attached_pic': 0,
  'clean_effects': 0,
  'comment': 0,
  'default': 1,
  'dub': 0,
  'forced': 0,
  'hearing_impaired': 0,
  'karaoke': 0,
  'lyrics': 0,
  'original': 0,
  'visual_impaired': 0},
 'duration': '40.320000',
 'duration_ts': 1935360,
 'index': 1,
 'nb_frames': '1890',
 'profile': 'LC',
 'r_frame_rate': '0/0',
 'sample_fmt': 'fltp',
 'sample_rate': '48000',
 'start_pts': 0,
 'start_time': '0.000000',
 'tags': {'creation_time': '2014-07-06T15:20:02.000000Z',
  'handler_name': '\rGoPro AAC',
  'language': 'eng',
  'timecode': '15:19:06:51'},
 'time_base': '1/48000'}
```

Stream 2:
```python
{'avg_frame_rate': '60/1',
 'codec_tag': '0x64636d74',
 'codec_tag_string': 'tmcd',
 'codec_type': 'data',
 'disposition': {'attached_pic': 0,
  'clean_effects': 0,
  'comment': 0,
  'default': 1,
  'dub': 0,
  'forced': 0,
  'hearing_impaired': 0,
  'karaoke': 0,
  'lyrics': 0,
  'original': 0,
  'visual_impaired': 0},
 'duration': '40.323617',
 'duration_ts': 2419417,
 'index': 2,
 'nb_frames': '1',
 'r_frame_rate': '0/0',
 'start_pts': 0,
 'start_time': '0.000000',
 'tags': {'creation_time': '2014-07-06T15:20:02.000000Z',
  'language': 'eng',
  'timecode': '15:19:06:51'},
 'time_base': '1/60000'}
```
