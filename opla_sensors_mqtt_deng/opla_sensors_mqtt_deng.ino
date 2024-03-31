#include <Arduino_MKRIoTCarrier.h>
#include "visuals.h"
#include <WiFiNINA.h>
#include <PubSubClient.h>
#include "secrets.h"

MKRIoTCarrier carrier;

WiFiClient wifi;
int status = WL_IDLE_STATUS;

IPAddress server(, , , );  // change this value for the Raspberry Pi IP
PubSubClient client(wifi);

String state = "start";
unsigned long previousMillis = 0;  // will store the last time sensors were updated
const long interval = 20000;        // interval at which to update sensors (milliseconds)

// Declare pages
void configure();
void sensorsPage();

void callback(char* topic, byte* payload, unsigned int length) {
  // handle incoming messages here
}

void setup() {
  CARRIER_CASE = false;
  Serial.begin(9600);
  delay(1500);

  if (!carrier.begin()) {
    Serial.println("Carrier not connected, check connections");
    while (1);
  }

  Serial.println("OK");
  Serial.print("Connessione...");
  while (status != WL_CONNECTED) {
    status = WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Connected to WiFi!\n");

  client.setServer(server, 1883);
  client.setCallback(callback);

  if (client.connect("arduinosub")) {
    Serial.println("mqtt connected");
    client.subscribe("sensors/all");
  } else {
    Serial.println("mqtt not connected");
    Serial.print("failed, rc=");
    Serial.println(client.state());
  }
}

void loop() {
  client.loop();  // fix: added parentheses
  unsigned long currentMillis = millis();  // get the current time

  // check if 20 seconds have passed since the last update
  if (currentMillis - previousMillis >= interval) {
    // save the last time you updated the sensors
    previousMillis = currentMillis;

    // update the sensors
    sensorsPage();
  }
}

// ... (configure function remains unchanged)

// Check the Env, IMU and light sensors
void sensorsPage() {
  carrier.display.fillScreen(0x0000);

  // displaying temperature
  carrier.display.setCursor(25, 60);
  carrier.display.setTextSize(3);
  carrier.display.print("Temperature");
  float temperature = carrier.Env.readTemperature();
  carrier.display.drawBitmap(80, 80, temperature_logo, 100, 100, 0xDAC9);
  carrier.display.setCursor(60, 180);
  carrier.display.print(temperature);
  carrier.display.print(" C");
  delay(2500);

  // displaying humidity
  carrier.display.fillScreen(0x0000);
  carrier.display.setCursor(54, 40);
  carrier.display.setTextSize(3);
  carrier.display.print("Humidity");
  carrier.display.drawBitmap(70, 70, humidity_logo, 100, 100, 0x0D14);
  float humidity = carrier.Env.readHumidity();
  carrier.display.setCursor(60, 180);
  carrier.display.print(humidity);
  carrier.display.print(" %");
  delay(2500);

  // displaying pressure
  carrier.display.fillScreen(0x0000);
  carrier.display.setCursor(54, 40);
  carrier.display.setTextSize(3);
  carrier.display.print("Pressure");
  carrier.display.drawBitmap(70, 60, pressure_logo, 100, 100, 0xF621);
  float press = carrier.Pressure.readPressure();
  carrier.display.setCursor(40, 160);
  carrier.display.println(press);
  carrier.display.setCursor(160, 160);
  carrier.display.print("KPa");
  delay(2500);

  // Publish all values to MQTT
  String payload = "{\"temperature\":" + String(temperature) +
                   ",\"humidity\":" + String(humidity) +
                   ",\"pressure\":" + String(press) + "}";
  client.publish("sensors/all", payload.c_str());

  // Delay for better readability in the display
  delay(2500);
}