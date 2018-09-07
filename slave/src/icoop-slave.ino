#include <Wire.h>
#include <DHT.h>

#define SLAVE_ADDRESS       0x04

#define PIN_LIGHT_SENSOR    A0

#define PIN_DHT             5

#define PIN_OPEN            7
#define PIN_CLOSE           6

#define PIN_OPEN_SWITCH     15
#define PIN_CLOSE_SWITCH    14

#define NO_CMD              0
#define OPEN_DOOR_CMD       1
#define CLOSE_DOOR_CMD      2
#define GET_DOOR_STATUS_CMD 3
#define GET_LIGHT_LEVEL_CMD 4
#define GET_TEMP_CMD        5
#define GET_HUMIDITY_CMD    6

#define DOOR_OPEN           1
#define DOOR_CLOSE          2
#define DOOR_UNKNOWN        3

DHT dht(PIN_DHT, DHT22);

int dht_temp;
int dht_humidity;

int active_cmd;
int cmd_result;
int cmd_timer;

void setup()
{
  Serial.begin(9600);

  pinMode(PIN_OPEN, OUTPUT);
  pinMode(PIN_CLOSE, OUTPUT);
  pinMode(PIN_OPEN_SWITCH, INPUT_PULLUP);
  pinMode(PIN_CLOSE_SWITCH, INPUT_PULLUP);

  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData); 

  dht.begin();
}

void loop()
{
  delay(100);
  cmd_timer++;

  switch (active_cmd)
  {
  case OPEN_DOOR_CMD:
    if (!digitalRead(PIN_OPEN_SWITCH) || cmd_timer >= 300)
    {
      Serial.println("STOP OPEN_DOOR");
      digitalWrite(PIN_CLOSE, 0);
      digitalWrite(PIN_OPEN, 0);
      active_cmd = NO_CMD;
    }
    else
    {
      Serial.println("OPEN_DOOR");
      digitalWrite(PIN_CLOSE, 0);
      digitalWrite(PIN_OPEN, 1);
    }
    break;

  case CLOSE_DOOR_CMD:
    if (!digitalRead(PIN_CLOSE_SWITCH) || cmd_timer >= 300)
    {
      Serial.println("STOP CLOSE_DOOR");
      digitalWrite(PIN_CLOSE, 0);
      digitalWrite(PIN_OPEN, 0);
      active_cmd = NO_CMD;
    }
    else
    {
      Serial.println("CLOSE_DOOR");
      digitalWrite(PIN_CLOSE, 1);
      digitalWrite(PIN_OPEN, 0);
    }
    break;
  }

  if (dht.read())
  {
    dht_temp = dht.readTemperature(true);
    dht_humidity = dht.readHumidity();
  }
}

void receiveData(int byteCount)
{
  int cmd = Wire.read();
  while (Wire.available())
    Wire.read();

  cmd_timer = 0;

  switch (cmd)
  {
  case GET_DOOR_STATUS_CMD:
    if (!digitalRead(PIN_OPEN_SWITCH))
      cmd_result = DOOR_OPEN;
    else if (!digitalRead(PIN_CLOSE_SWITCH))
      cmd_result = DOOR_CLOSE;
    else
      cmd_result = DOOR_UNKNOWN;
    Serial.println("GET_DOOR_STATUS_CMD");
    Serial.println(cmd_result);
    break;

  case GET_LIGHT_LEVEL_CMD:
    cmd_result = analogRead(PIN_LIGHT_SENSOR) / 4;
    Serial.println("GET_LIGHT_LEVEL_CMD");
    Serial.println(cmd_result);
    break;

  case GET_TEMP_CMD:
    cmd_result = dht_temp;
    Serial.println("GET_TEMP_CMD");
    Serial.println(cmd_result);
    break;

  case GET_HUMIDITY_CMD:
    cmd_result = dht_humidity;
    Serial.println("GET_HUMIDITY_CMD");
    Serial.println(cmd_result);
    break;

  case OPEN_DOOR_CMD:
    cmd_result = 0;
    active_cmd = OPEN_DOOR_CMD;
    Serial.println("OPEN_DOOR_CMD");
    break;

  case CLOSE_DOOR_CMD:
    cmd_result = 0;
    active_cmd = CLOSE_DOOR_CMD;
    Serial.println("CLOSE_DOOR_CMD");
    break;

  default:
    cmd_result = 0;
    Serial.println("INVALID_CMD");
    Serial.println(cmd);
    break;
  }
}

void sendData()
{
  if (cmd_result > 255)
    cmd_result = 255;
  if (cmd_result < 0)
    cmd_result = 0;
  Wire.write(cmd_result);
}
