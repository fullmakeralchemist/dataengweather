import paho.mqtt.client as mqtt
import csv
import json
import datetime

topic = "sensors/all"  # Replace with the topic used by your Arduino

# CSV file configuration
csv_file_path = "sensor_data.csv" #Change the name of the file

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

# Callback when a message is received from the MQTT broker
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    received_temperature = payload["temperature"]
    received_humidity = payload["humidity"]
    received_pressure = payload["pressure"]

    # Save data to CSV file
    save_to_csv(datetime.datetime.now(), received_temperature, received_humidity, received_pressure)

    # Print the received data in the terminal
    print("Received Sensor Data:")
    print(f"Timestamp: {datetime.datetime.now()}")
    print(f"Temperature: {received_temperature:.2f} °C") #Be carefull with this line in Raspberry Pi Thonny 
    # is not acccepted this simbol °C" in the Wormbook Pi OS new version April 2024
    print(f"Humidity: {received_humidity:.2f} %")
    print(f"Pressure: {received_pressure:.2f} KPa")
    print()

def save_to_csv(timestamp, temperature, humidity, pressure):
    # Open the CSV file in append mode
    with open(csv_file_path, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Check if the file is empty, write headers if needed
        if csv_file.tell() == 0:
            csv_writer.writerow(["Timestamp", "Temperature (C)", "Humidity (%)", "Pressure (KPa)"])

        # Write the sensor data to the CSV file
        csv_writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), temperature, humidity, pressure])

# Create and configure the MQTT client

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.num.num", 1883, 60) #change the IP by your Raspberry Pi IP to obtain the IP run: -hostname

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()