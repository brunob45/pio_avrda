#include <avr/io.h>
#include <util/delay.h>

int main()
{
    PORTC.DIRSET = PIN6_bm;

    while (1)
    {
        PORTC.OUTTGL = PIN6_bm;
        _delay_ms(500);
    }
}