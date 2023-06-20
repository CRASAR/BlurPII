# FEMA-DHS-Image-Sanitize

This repository does the following...
- Generates photospheres from 360 video
- Aligns those photospheres with GPX files
- Sanitizes the photospheres via bluring

FEMA/DHS has stated that all images that have all legible license plates and faces must be blurred out prior to viewing. We make a good faith effort at this in this repo. This repository also integrates with the Mapillary service so that imagery can be uploaded to their servers for remote inspection. 

***

Initial setup of this repository can be performed by simply running the `setup.sh` script. Here is the sample usage. 
```
./setup.sh
```

***

Example usage of how to perform the conversion of 360 videos to photosphers followed by sanitization can be found in the `vid2geospheres.sh` script.
You will need a 360 video and a GPX file that describes the geospatial coordinates of the video content. Examples of those files can be found [here](https://fsu-my.sharepoint.com/:f:/g/personal/jhadams_fsu_edu/Euo8BkX5A_xKpZT0dCMCTcsB18m3kUNQO3aztBYbPnjHOw?email=tom.m%40nzini.com&e=BdTubJ).

```
VIDEO_PATH="./input/vid/GS010017.mp4"
GPX_PATH="./input/vid/GS010017.gpx"
OUTPUT_PATH="./input/geospheres"
VIDEO_SAMPLE_INTERVAL=10
USER_NAME="tmanzini"

python ./src/vid2photosphere_sanitize.py $VIDEO_PATH $OUTPUT_PATH \
                                         --video_sample_distance -1 \
                                         --video_sample_interval $VIDEO_SAMPLE_INTERVAL \
                                         --geotag_source "gpx" \
                                         --geotag_source_path $GPX_PATH \
                                         --interpolation_use_gpx_start_time \
                                         --rerun
```

If you have any questions, or encounter any issues, please contact [tmanzini@tamu.edu](tmanzini@tamu.edu).
