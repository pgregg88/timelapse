import logging
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from takePhotos import take_photos
from createVideo import create_video
from pubVideo import publish_video

# Constants
LOG_LEVEL = logging.DEBUG
LOG_FILE = '/home/pgregg/timelapse/tl.log'
PHOTO_COUNT = 30
DELAY_SEC = 3
PHOTO_PATH = '/media/photos/2/daily_photos'

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def main():
    try:
        # Create photo directory if it doesn't exist
        if not os.path.exists(PHOTO_PATH):
            os.makedirs(PHOTO_PATH)

        # Estimate end time of photo taking
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=PHOTO_COUNT * DELAY_SEC)
        logging.info(f"Photo taking started. Estimated end time: {end_time}")

        # Take photos
        with ThreadPoolExecutor() as executor:
            tp_future = executor.submit(take_photos, PHOTO_COUNT, DELAY_SEC, PHOTO_PATH)

        # Wait for photo taking to complete
        photo_path, srt_path = tp_future.result()
        if photo_path is None:
            raise ValueError('Error: no photo path received from take_photos')
        if srt_path is None:
            raise ValueError('Error: no srt path received from take_photos')
        logging.info(f"Photo taking complete. Photos saved to {photo_path}")

        # Create video
        with ThreadPoolExecutor() as executor:
            cv_future = executor.submit(create_video, photo_path, srt_path)

        # Wait for video creation to complete
        video_path, json_path = cv_future.result()
        if video_path is None:
            raise ValueError('Error: unable to create video')
        if json_path is None:
            raise ValueError('Error: unable to create JSON file')
        logging.info(f"Video creation complete. Video saved to {video_path}, JSON file saved to {json_path}")

        # Publish video
        with ThreadPoolExecutor() as executor:
            pv_future = executor.submit(publish_video, video_path, json_path)

        # Wait for video publishing to complete
        pv_future.result()
        logging.info("Video publishing complete")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()
