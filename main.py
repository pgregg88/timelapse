import os
import logging
import concurrent.futures
from takePhotos import take_photos
from createVideo import create_video
from pubVideo import publish_video
from datetime import datetime
from logger import setup_logging
import paho.mqtt.client as mqtt

# Set up the logger with the log path
now = datetime.now()
log_date = now.strftime("%Y-%m-%d_%H%M%S")
project_name = 'lt_daily'
log_path = f'/home/pgregg/timelapse/logs/tl_{project_name}_{log_date}.log'
logger = setup_logging(log_path)

# Define the MQTT broker settings
broker_address = "10.0.10.41"
broker_port = 1883
broker_username = "hass"
broker_password = "monstermash1"
# Define the MQTT topic for status updates
status_topic = "timelapse/status"

def publish_mqtt_status(status):
    """Publish an MQTT message with the specified status."""
    client = mqtt.Client()
    client.username_pw_set(broker_username, broker_password)
    client.connect(broker_address, broker_port)
    try:
        result = client.publish(status_topic, status)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"Failed to publish MQTT message: {result.rc}")
    except Exception as e:
        logger.error(f"Error publishing MQTT message: {e}")
    finally:
        client.disconnect()

# define function for starting a task
def start_task(task_func, task_name):
    logger.info(f'Starting task {task_name}')
    publish_mqtt_status(f'Task {task_name} started')
    try:
        task_func()
        logger.info(f'Finished task {task_name}')
        publish_mqtt_status(f'Task {task_name} started')
    except Exception as e:
        logger.error(f'Error in task {task_name}: {e}')
        publish_mqtt_status(f'Task {task_name} failed: {e}')
        raise ValueError(f'Error in task {task_name}: {e}')

# define main function
def main():
    current_time = datetime.now()
    dir_name = current_time.strftime("%Y-%m-%d_%H%M%S")

    run_hours = 7
    #photo_count = run_hours * 1200 #1200 per hour
    photo_count = 16400
    delay_sec = 3
    photo_path = f"/media/photos/2/{dir_name}"

    if not os.path.exists(photo_path):
        os.makedirs(photo_path)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit take_pictures task to the thread pool and get its future object
        tp_future = executor.submit(take_photos, photo_count, delay_sec, photo_path, logger)

        # wait for the take_pictures future to complete
        try:
            photo_path, srt_path = tp_future.result()
            logger.debug(f'take_photos: Received photo_path: {photo_path}, srt_path: {srt_path}')
        except Exception as e:
            logger.error(f'Error receiving result from take_photos: {e}')
            raise ValueError(f'Error receiving result from take_photos: {e}')

        # submit create_video task to the thread pool and get its future object
        cv_future = executor.submit(create_video, photo_path, srt_path, logger)

        # wait for the create_video future to complete
        try:
            video_path, json_path = cv_future.result()
            logger.debug(f'create_video: Received video_path: {video_path}, json_path: {json_path}')
        except Exception as e:
            logger.error(f'Error receiving result from create_video: {e}')
            raise ValueError(f'Error receiving result from create_video: {e}')

        # submit publish_video task to the thread pool
        pv_future = executor.submit(publish_video, video_path, json_path, logger)

        # wait for the publish_video future to complete
        try:
            pv_future.result()
        except Exception as e:
            logger.error(f'Error in publish_video task: {e}')
            raise ValueError(f'Error in publish_video task: {e}')
    # shutdown the executor after all tasks have completed
    executor.shutdown()
# run main function
if __name__ == '__main__':
    main()
