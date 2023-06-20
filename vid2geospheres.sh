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