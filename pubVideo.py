import logging
import subprocess
import os
import shutil
# from main import log_path
from logger import setup_logging

# Set up the logger with the log path
# log_path = '/home/pgregg/timelapse/logs/shouldnotbehere.log'
# logger = setup_logging(log_path)

def publish_video(video_path, json_path, logger):
    logger.info('Publishing Video')
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(['/home/pgregg/timelapse/youtubeuploader', '-filename', video_path, '-metaJSON', json_path], capture_output=True)
            
            if result.returncode == 0:
                logger.info("Publishing: %s", result.stdout.decode())
                logger.info("Video Published")
                # Archive video
                logger.info("Archiving published video")
                video_archive_path = '/media/timelapse_storage/videos'
                isExist = os.path.exists(video_archive_path)
                if not isExist:
                    os.makedirs(video_archive_path)
                    logger.info('Archive path directory created')
                try:
                    shutil.move(video_path,video_archive_path)
                    shutil.move(json_path,video_archive_path)
                    logger.info(f'Video and JSON archived: {video_archive_path}' )
                except Exception as e:
                    logger.error(f'Error archiving video and JSON file', exc_info=e)
                break  # exit the loop if successful
            
            else:
                logger.info("Video Publish failed: %s", result.stderr.decode())
                retries += 1  # increment the retries count
                
        except Exception as e:
            logger.error('Error publishing Video', exc_info=e)
            retries += 1  # increment the retries count
            
        logger.info(f"Retrying ({retries}/{max_retries})...")
    
    if retries == max_retries:
        logger.error(f"Max retries ({max_retries}) reached. Giving up.")
