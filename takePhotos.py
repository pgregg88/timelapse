import os
import logging
import requests
from datetime import datetime, timedelta
import time

def take_photos(num_photos, delay_sec, photo_path):
    srt_path = '/media/videos/srt/02162023_b.srt'
    url = "http://10.0.30.100/cgi-bin/api.cgi?cmd=Snap&channel=md=Snap&channel=0&rs=123&user=admin&password=pg12345678"

    if not os.path.exists(photo_path):
        os.makedirs(photo_path)

    start_time = datetime.now()
    logging.info(f"Photo taking started. Estimated end time: {start_time + timedelta(seconds=num_photos*delay_sec)}")
    
    for i in range(num_photos):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"laketravis_{timestamp}.jpg"
        response = None
        
        try:
            response = requests.get(url)
            with open(os.path.join(photo_path, filename), "wb") as f:
                f.write(response.content)
        except Exception as e:
            logging.error(str(e))
        
        remaining_photos = num_photos - i - 1
        if (i + 1) % 10 == 0 or remaining_photos == 0:
            elapsed_time = datetime.now() - start_time
            avg_time_per_photo = elapsed_time / (i + 1)
            remaining_time = avg_time_per_photo * remaining_photos
            completion_time = datetime.now() + remaining_time
            logging.info(f"Photos taken: {i + 1}, Remaining photos: {remaining_photos}, Estimated completion time: {completion_time}")
        
        if response is not None:
            response.close()
        
        # Use time.sleep() to account for the time taken to make the API call and write the image file.
        sleep_time = delay_sec - (datetime.now() - start_time).total_seconds() % delay_sec
        time.sleep(sleep_time)

    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"Photo taking complete. Duration: {duration}")
    return photo_path, srt_path
