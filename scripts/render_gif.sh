#!/bin/sh
set -eu
# Convert the existing recorded demo; no generated or simulated UI frames.
ffmpeg -y -i docs/demo.mp4 -filter_complex 'trim=start=0:end=60,setpts=PTS/2,fps=2,scale=1080:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[palette];[b][palette]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' -loop 0 docs/demo.gif
