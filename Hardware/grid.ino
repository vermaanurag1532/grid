#include <WiFi.h>
#include <WiFiUdp.h>

// Define motor and IR sensor pins
#define MOTOR1_IN1 13   // Motor 1 IN1
#define MOTOR1_IN2 12   // Motor 1 IN2
#define MOTOR1_ENA 14   // Motor 1 Enable Pin for PWM (Speed Control)

#define MOTOR2_IN1 15   // Motor 2 IN1
#define MOTOR2_IN2 2   // Motor 2 IN2
#define MOTOR2_ENA 4  // Motor 2 Enable Pin for PWM (Speed Control)

#define IR_SENSOR_PIN 34

// Wi-Fi credentials
const char* ssid = "om";
const char* password = "12344321";

// UDP settings
WiFiUDP udp;
const char* udpAddress = "192.168.26.73";  // Target IP for UDP packet
const int udpPort = 8888;                 // Target port for UDP packet

bool ir_detected = false;
int motor_speed = 200;  // Initial motor speed (max 255 for full speed)

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);

  // Initialize motor control pins
  pinMode(MOTOR1_IN1, OUTPUT);
  pinMode(MOTOR1_IN2, OUTPUT);
  pinMode(MOTOR1_ENA, OUTPUT);  // PWM pin for motor 1 speed control
  
  pinMode(MOTOR2_IN1, OUTPUT);
  pinMode(MOTOR2_IN2, OUTPUT);
  pinMode(MOTOR2_ENA, OUTPUT);  // PWM pin for motor 2 speed control
  
  pinMode(IR_SENSOR_PIN, INPUT);

  // Set the motors to run in forward direction with full speed initially
  digitalWrite(MOTOR1_IN1, HIGH);
  digitalWrite(MOTOR1_IN2, LOW);
  analogWrite(MOTOR1_ENA, motor_speed);  // Set motor 1 speed using PWM

  digitalWrite(MOTOR2_IN1, HIGH);
  digitalWrite(MOTOR2_IN2, LOW);
  analogWrite(MOTOR2_ENA, motor_speed);  // Set motor 2 speed using PWM

  // Connect to Wi-Fi
  connectToWiFi();

  // Print UDP target info
  Serial.printf("UDP target IP: %s, port: %d\n", udpAddress, udpPort);
}

void loop() {
  // Read IR sensor state (object detected if LOW)
  ir_detected = digitalRead(IR_SENSOR_PIN) == HIGH;

  if (ir_detected) {
    // Stop both motors
    digitalWrite(MOTOR1_IN1, LOW);
    digitalWrite(MOTOR1_IN2, LOW);
    analogWrite(MOTOR1_ENA, 0);  // Set motor 1 speed to 0 (stop)

    digitalWrite(MOTOR2_IN1, LOW);
    digitalWrite(MOTOR2_IN2, LOW);
    analogWrite(MOTOR2_ENA, 0);  // Set motor 2 speed to 0 (stop)

    // Send UDP message: IR object detected
    sendUdpMessage("IR object detected");

    // Wait for 3 seconds
    delay(3000);

    // Restart both motors with full speed after the delay
    digitalWrite(MOTOR1_IN1, HIGH);
    digitalWrite(MOTOR1_IN2, LOW);
    analogWrite(MOTOR1_ENA, motor_speed);  // Set motor 1 speed using PWM

    digitalWrite(MOTOR2_IN1, HIGH);
    digitalWrite(MOTOR2_IN2, LOW);
    analogWrite(MOTOR2_ENA, motor_speed);  // Set motor 2 speed using PWM
    delay(2000);
  }// else {
    // Send UDP message: No object detected
    //sendUdpMessage("No object detected");
  //}

  // Small delay to avoid flooding
  delay(100);
}

void connectToWiFi() {
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  Serial.println("Connected to Wi-Fi");
}

void sendUdpMessage(const char* message) {
  // Send a UDP message
  udp.beginPacket(udpAddress, udpPort);
  udp.print(message);
  udp.endPacket();
}
