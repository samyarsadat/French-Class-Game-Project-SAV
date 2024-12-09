#include <USBComposite.h>

USBHID HID;
HIDKeyboard BootKeyboard(HID, 0);

#define button_1 PB6
#define button_2 PB7
#define button_3 PB8
#define button_4 PB9

void setup() 
{
  pinMode(button_1, INPUT_PULLUP);
  pinMode(button_2, INPUT_PULLUP);
  pinMode(button_3, INPUT_PULLUP);
  pinMode(button_4, INPUT_PULLUP);
  
  HID.begin(HID_BOOT_KEYBOARD);
  BootKeyboard.begin();
}


void loop() 
{
  if (digitalRead(button_1) == 0)
  {
    BootKeyboard.press(KEY_LEFT_CTRL);
    BootKeyboard.press(KEY_LEFT_ALT);
    BootKeyboard.press(KEY_KP_0);
    delay(500);
    BootKeyboard.releaseAll();
  }

  if (digitalRead(button_2) == 0)
  {
    BootKeyboard.press(KEY_LEFT_CTRL);
    BootKeyboard.press(KEY_LEFT_ALT);
    BootKeyboard.press(KEY_KP_1);
    delay(500);
    BootKeyboard.releaseAll();
  }

  if (digitalRead(button_3) == 0)
  {
    BootKeyboard.press(KEY_LEFT_CTRL);
    BootKeyboard.press(KEY_LEFT_ALT);
    BootKeyboard.press(KEY_KP_2);
    delay(500);
    BootKeyboard.releaseAll();
  }

  if (digitalRead(button_4) == 0)
  {
    BootKeyboard.press(KEY_LEFT_CTRL);
    BootKeyboard.press(KEY_LEFT_ALT);
    BootKeyboard.press(KEY_KP_3);
    delay(500);
    BootKeyboard.releaseAll();
  }
}