import logging
import subprocess
import os
import shutil

#setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('/home/pgregg/timelapse/tl.log'), logging.StreamHandler()])



def publish_video(video_path, json_path):
    logging.info('Publishing Video')
    try:
        result = subprocess.run(['/home/pgregg/timelapse/youtubeuploader', '-filename', video_path, '-metaJSON', json_path], capture_output=True)

        if result.returncode == 0:
            logging.info("Publishing: %s", result.stdout.decode())
            logging.info("Video Published")
            # Archive video
            logging.info("Archiving published video")
            video_archive_path = '/media/timelapse_storage/videos'
            isExist = os.path.exists(video_archive_path)
            if not isExist:
                os.makedirs(video_archive_path)
                logging.info('Archive path directory created')
            try:
                shutil.move(video_path,video_archive_path)
                shutil.move(json_path,video_archive_path)
                logging.info(f'Video and JSON archived: {video_archive_path}' )
            except Exception as e:
                logging.error(f'Error archiving video and JSON file', exc_info=e)

        else:
            logging.info("Video Publish failed: %s", result.stderr.decode())
        
    except Exception as e:
        logging.error('Error publishing Video', exc_info=e)
