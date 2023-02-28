import logging
import subprocess
import os
import shutil
# from main import log_path
from logger import setup_logging
from mqtt import publish_mqtt_status

# Set up the logger with the log path
# log_path = '/home/pgregg/timelapse/logs/shouldnotbehere.log'
# logger = setup_logging(log_path)

def publish_video(video_path, json_path, logger):
    logger.info('Publishing Video')
    publish_mqtt_status("timelapse/status",'Publishing Video')
    try:
        result = subprocess.run(['/home/pgregg/timelapse/youtubeuploader', '-filename', video_path, '-metaJSON', json_path, '-cache', '/home/pgregg/timelapse/request.token', '-secrets', '/home/pgregg/timelapse/client_secrets.json'], capture_output=True)

        if result.returncode == 0:
            logger.info("Publishing: %s", result.stdout.decode())
            publish_mqtt_status("timelapse/status","Publishing: %s", result.stdout.decode())
            logger.info("Video Published")
            publish_mqtt_status("timelapse/status","Video Published")
            # Archive video
            logger.info("Archiving published video")
            publish_mqtt_status("timelapse/status","Archiving published video")
            video_archive_path = '/media/timelapse_storage/videos'
            isExist = os.path.exists(video_archive_path)
            if not isExist:
                os.makedirs(video_archive_path)
                logger.info('Archive path directory created')
                publish_mqtt_status("timelapse/status",'Archive path directory created')
            try:
                shutil.move(video_path,video_archive_path)
                shutil.move(json_path,video_archive_path)
                logger.info(f'Video and JSON archived: {video_archive_path}' )
                publish_mqtt_status("timelapse/status",f'Video and JSON archived: {video_archive_path}' )
            except Exception as e:
                logger.error(f'Error archiving video and JSON file', exc_info=e)
                publish_mqtt_status("timelapse/error",f'Error archiving video and JSON file', exc_info=e)
                publish_mqtt_status("timelapse/status",f'Error archiving video and JSON file', exc_info=e)
            return video_archive_path
        else:
            logger.error("Video Publish failed: %s", result.stderr.decode())
            publish_mqtt_status("timelapse/status","Video Publish failed: %s", result.stderr.decode())
            publish_mqtt_status("timelapse/error","Video Publish failed: %s", result.stderr.decode())
        
    except Exception as e:
        logger.error('Error publishing Video', exc_info=e)
        publish_mqtt_status("timelapse/error",'Error publishing Video', exc_info=e)
        publish_mqtt_status("timelapse/status",'Error publishing Video', exc_info=e)
   
