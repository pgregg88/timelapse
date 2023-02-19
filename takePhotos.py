import os
import requests
import logging
import time
from datetime import datetime, timedelta

# setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# retry decorator with maximum number of retries
def retry_on_exception(max_retries):
    def decorator(func):
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f'Retrying... ({tries + 1}/{max_retries})')
                    logging.error(str(e))
                    tries += 1
            raise Exception(f'Maximum number of retries ({max_retries}) exceeded')
        return wrapper
    return decorator

# decorate take_photo function with retry decorator
@retry_on_exception(5)
def take_photo(url, photo_path):
    response = requests.get(url)
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"laketravis_{timestamp}.jpg"
        with open(os.path.join(photo_path, filename), "wb") as f:
            f.write(response.content)
        logging.debug(f"Photo saved: {filename}")
    else:
        raise Exception(f"Error taking photo: {response.status_code}")

def take_photos(num_photos, delay_sec, photo_path):
    srt_path = '/media/videos/srt/02162023_b.srt'
    url = "http://10.0.30.100/cgi-bin/api.cgi?cmd=Snap&channel=md=Snap&channel=0&rs=123&user=admin&password=pg12345678"
    if not os.path.exists(photo_path):
        os.makedirs(photo_path)
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=num_photos*delay_sec)
    logging.info(f"Photo taking started. Estimated end time: {end_time}")
    for i in range(num_photos):
        try:
            take_photo(url, photo_path)
        except Exception as e:
            logging.error(str(e))
        remaining_photos = num_photos - (i + 1)
        remaining_time = timedelta(seconds=remaining_photos*delay_sec)
        completion_time = datetime.now() + remaining_time
        logging.info(f"Photos taken: {i+1}, Remaining: {remaining_photos}, Estimated completion time: {completion_time}")
        time.sleep(delay_sec)
    end_time = datetime.now()
    duration = end_time - start_time
    duration_str = str(timedelta(seconds=duration.total_seconds()))
    logging.info(f"Photo taking complete. Duration: {duration_str}")
    return photo_path, srt_path
