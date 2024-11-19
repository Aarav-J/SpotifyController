#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi credentials
const char* ssid = "alwar";
const char* password = "arihant11";

// Server URL
String serverURL = "http://localhost:5000";

// Button Pins
const int PLAY_BUTTON_PIN = 12;
const int PAUSE_BUTTON_PIN = 14;
const int NEXT_BUTTON_PIN = 27;
const int PREV_BUTTON_PIN = 26;
// Add more buttons as needed

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
  
  // Initialize button pins
  pinMode(PLAY_BUTTON_PIN, INPUT_PULLUP);
  pinMode(PAUSE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(NEXT_BUTTON_PIN, INPUT_PULLUP);
  pinMode(PREV_BUTTON_PIN, INPUT_PULLUP);
  // Initialize more buttons as needed
}

void loop() {
  if (digitalRead(PLAY_BUTTON_PIN) == LOW) {
    sendCommand("/play");
    delay(300); // Debounce delay
  }
  if (digitalRead(PAUSE_BUTTON_PIN) == LOW) {
    sendCommand("/pause");
    delay(300);
  }
  if (digitalRead(NEXT_BUTTON_PIN) == LOW) {
    sendCommand("/next");
    delay(300);
  }
  if (digitalRead(PREV_BUTTON_PIN) == LOW) {
    sendCommand("/previous");
    delay(300);
  }
  // Add more button checks as needed
}

void sendCommand(String command) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL + command);
    int httpResponseCode = http.GET();
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error sending command");
    }
    http.end();
  } else {
    Serial.println("Wi-Fi Disconnected");
  }
}