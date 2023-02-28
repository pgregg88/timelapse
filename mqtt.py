from logger import setup_logging
import paho.mqtt.client as mqtt


# Define the MQTT broker settings
broker_address = "10.0.10.41"
broker_port = 1883
broker_username = "hass"
broker_password = "monstermash"
# Define the MQTT topic for status updates
status_topic = "timelapse/status"

def publish_mqtt_status(status_topic, status, exc_info=None):
    """Publish an MQTT message with the specified status."""
    client = mqtt.Client()
    client.username_pw_set(broker_username, broker_password)
    client.connect(broker_address, broker_port)
    try:
        result = client.publish(status_topic, status)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Failed to publish MQTT message: {result.rc}")
            publish_mqtt_status("timelapse/error",f"Failed to publish MQTT message: {result.rc}")
    except Exception as e:
        print(f"Error publishing MQTT message: {e}")
        publish_mqtt_status("timelapse/error",f"Error publishing MQTT message: {e}")
    finally:
        client.disconnect()
