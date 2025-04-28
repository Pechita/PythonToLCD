
// LCD Serial Display Handler
// Receives serial data and displays 2-line text chunks on 16x2 LCD.

#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600);
  lcd.clear();
}

void loop() {
  static int row = 0;

  if (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      row++;
      if (row > 1) {
        delay(1500);
        lcd.clear();
        row = 0;
      }
      lcd.setCursor(0, row);
    } else {
      lcd.write(c);
    }
  }
}
