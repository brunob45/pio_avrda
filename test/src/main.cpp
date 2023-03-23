#include <Arduino.h>

int main()
{
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);

    for(;;)
    {
        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("LOW");
        delay(500);

        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("HIGH");
        delay(500);
    }
}