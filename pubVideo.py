import logging
import time
import datetime
import subprocess

test_mode = False
log_level = logging.DEBUG

#setup logging
logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('/home/pgregg/timelapse/tl.log'),logging.StreamHandler()])



def publish_video(video_path, json_path):
    logging.info('Publishing Video')
    print('Publishing Video')
    result = subprocess.run(['/home/pgregg/timelapse/youtubeuploader', '-filename', video_path, '-metaJSON', json_path], capture_output=True)

    if result.returncode == 0:
        logging.info("Publishing: %s", result.stdout.decode())
        logging.info("Video Published")
        print('Video Published')
    else:
        logging.info("Video Publish failed: %s", result.stderr.decode())
        print('Video Publish failed: %s', result.stderr.decode())

if test_mode == True:
    video_path = '/media/timelapse_storage/videos/daily_uploadvideo2.mp4'
    json_path = '/home/pgregg/timelapse/json/2023-02-16.json'
    publish_video(video_path, json_path)