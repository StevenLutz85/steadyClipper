# steadyClipper
A simple tool for exporting steady sections of a video file as separate clips. 
The originating use case is for cutting drone and go-pro footage into useable clips while omitting shaky frames, and otherwise useless sections of footage. This should allow for faster content generation for social media, especially when creating Instagram Reels based on templates that require lots of precut video clips. 

Note: When exporting to x264 or x265, compiling opencv from source with python support will be required. 



$ ./steadyClipper.py --help
usage: steadyClipper.py [-h] [--min_duration_seconds MIN_DURATION_SECONDS] [--deviation_mult DEVIATION_MULT]
                        video_file

Extract steady sections from a video file.

positional arguments:
  video_file            Input video file (MP4 format)

optional arguments:
  -h, --help            show this help message and exit
  --min_duration_seconds MIN_DURATION_SECONDS
                        Minimum duration in seconds for exported sections, Default 1
  --deviation_mult DEVIATION_MULT
                        Multiplier of Standard Deviation which is added to the frames average difference value for
                        Clipping Threshold, Default 1
