# pio_avrda
Script to import avrda definition files to PlatformIO

# Prerequisites
- Windows 10 (untested on other versions).
- Python3, Platformio and Platformio's atmelavr platform.
- Atmel Studio 7.0 and AVR-Dx_DFP package (from Atmel Studio: Tools -> Device Pack Manager).

# How it works
Run `patchpio.py`. This file will:
- attempt to find your platformio and atmel studio installation paths,
- find all files related to AVR-DA compilation,
- copy them in the platformio installation directory
- generator automagically all the board definition files
- all the boards should now be available in platformio


# Supported controllers
As of AVR-Dx_DFP version 1.6.76:

| ID | MCU | Frequency | Flash | RAM | Name |
| --- | --- | --- | --- | --- | --- |
| avr32da28 | AVR32DA28 | 24MHz | 32KB | 4KB | AVR32DA28 |
| avr32da32 | AVR32DA32 | 24MHz | 32KB | 4KB | AVR32DA32 |
| avr32da48 | AVR32DA48 | 24MHz | 32KB | 4KB | AVR32DA48 |
| avr32db28 | AVR32DB28 | 24MHz | 32KB | 4KB | AVR32DB28 |
| avr32db32 | AVR32DB32 | 24MHz | 32KB | 4KB | AVR32DB32 |
| avr32db48 | AVR32DB48 | 24MHz | 32KB | 4KB | AVR32DB48 |
| avr64da28 | AVR64DA28 | 24MHz | 64KB | 8KB | AVR64DA28 |
| avr64da32 | AVR64DA32 | 24MHz | 64KB | 8KB | AVR64DA32 |
| avr64da48 | AVR64DA48 | 24MHz | 64KB | 8KB | AVR64DA48 |
| avr64da64 | AVR64DA64 | 24MHz | 64KB | 8KB | AVR64DA64 |
| avr64db28 | AVR64DB28 | 24MHz | 64KB | 8KB | AVR64DB28 |
| avr64db32 | AVR64DB32 | 24MHz | 64KB | 8KB | AVR64DB32 |
| avr64db48 | AVR64DB48 | 24MHz | 64KB | 8KB | AVR64DB48 |
| avr64db64 | AVR64DB64 | 24MHz | 64KB | 8KB | AVR64DB64 |
| avr128da28 | AVR128DA28 | 24MHz | 128KB | 16KB | AVR128DA28 |
| avr128da32 | AVR128DA32 | 24MHz | 128KB | 16KB | AVR128DA32 |
| avr128da48 | AVR128DA48 | 24MHz | 128KB | 16KB | AVR128DA48 |
| avr128da64 | AVR128DA64 | 24MHz | 128KB | 16KB | AVR128DA64 |
| avr128db28 | AVR128DB28 | 24MHz | 128KB | 16KB | AVR128DB28 |
| avr128db32 | AVR128DB32 | 24MHz | 128KB | 16KB | AVR128DB32 |
| avr128db48 | AVR128DB48 | 24MHz | 128KB | 16KB | AVR128DB48 |
| avr128db64 | AVR128DB64 | 24MHz | 128KB | 16KB | AVR128DB64 |
