/*
* Copyright (c) 2017 Fabian Friedl
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*/

#define F_CPU 16000000UL
#define BAUD 38400

#include <avr/io.h>
#include <util/setbaud.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <math.h>

#define TIMER_START 1<<CS12
#define TIMER_STOP 0

void Timer1_init() 
{
	TCCR1B |= 1<<WGM12; // Enable CTC mode
	TCCR1A |= 1<<COM1A1 | 1<<COM1A0; //Set OC0A on Compare Mode

	// compare register
	OCR1AH = 0x7A; // high
	OCR1AL = 0x11; // low

	TCCR1B = TIMER_STOP; // Set prescale
	TIMSK1 |= 1<<OCIE1A; // Set Compare Match Interrupt
}

ISR(TIMER1_COMPA_vect)
{
	PORTD ^= (1<<PORTD4);
}

void LED_startBlinking()
{
	TCCR1B = TIMER_START; // Start blinking of status LED
}

void LED_stopBlinking()
{
	TCCR1B = TIMER_STOP; // Stop blinking of status LED
	PORTD |= 1<<PORTD4; // Set status LED to high
}

void UART_init() // TODO: Maybe add parity bit
{
	// Set baud rate 
	UBRR0H = UBRRH_VALUE;
	UBRR0L = UBRRL_VALUE;

	UCSR0A |= (1<<U2X0);

	// Enable receiver and transmitter 
	UCSR0B |= (1<<RXEN0)|(1<<TXEN0);

	// Set frame format: 8data, 2stop bit 
	UCSR0C |= (1<<USBS0)|(3<<UCSZ00);
}

void UART_sendByte(unsigned char data)
{
	// Wait for empty transmit buffer 
	while(!( UCSR0A & (1<<UDRE0)));

	// Put data into buffer, sends the data 
	UDR0 = data;
}

unsigned char UART_receiveByte()
{
	// Wait for data to be received 
	while(!(UCSR0A & (1<<RXC0)));

	// Get and return received data from buffer 
	return UDR0;
}

unsigned char GBC_readByte(const unsigned char addressH, const unsigned char addressL)
{
	DDRC = 0x00; // set PORTC to input

	// Write address to MBC
	PORTA = addressL;	// Write low address to PORTA
	PORTB = addressH;	// Write high address to PORTB

	_delay_us(50);

	// Get data from MBC
	return PINC;
}

void GBC_writeByte(const unsigned char addressH, const unsigned char addressL, const unsigned char data)
{
	DDRC = 0xFF; // set PORTC to output

	// Write address to MBC
	PORTA = addressL;
	PORTB = addressH;

	_delay_us(50);

	PORTC = data;
}

void GBC_setReadMode()
{
	PORTD |= (1<<PORTD2);	// Set !WR to 1
	PORTD &= ~(1<<PORTD3);	// Set !RD to 0
}

void GBC_setWriteMode()
{
	PORTD |= (1<<PORTD3);	// Set !RD to 1
	PORTD &= ~(1<<PORTD2);	// Set !WR to 0
}



/*
	A0-A7:	PORTA
	A8-A15:	PORTB
	D0-D7:	PORTC

	PD2:	!WR
	PD3:	!RD
*/
int main(void)
{
	/*
		Set DDR
	*/
	DDRA = 0xFF; // AdressLow
	DDRB = 0xFF; // AdressHigh
	DDRC = 0x00; // Input of data
	DDRD |= 1<<PORTD2 | 1<<PORTD3 | 1<<PORTD4; // PD2: !WR and PD3: !RD and PD4: Status LED

	Timer1_init();
	UART_init();
	sei();
	
	GBC_setReadMode();
	
	PORTD |= 1<<PORTD4; // Set status LED to high

	/*
		Start process loop
	*/
	unsigned char receivedByte, data, romSize, numberOfBanks;
    while (1) {

		if ((UCSR0A & (1<<RXC0))) {  // Check for serial transmission

			receivedByte = UART_receiveByte();

			switch(receivedByte) 
			{
			case 0x01: // Connection test -> response: 0xA0
				UART_sendByte(0xA0);
				break;
			case 0x02: // Read cartridge type (address: 0x0147) -> Documentation page 57
				data = GBC_readByte(0x01, 0x47);
				UART_sendByte(data);
				break;
			case 0x03: // Read ROM size (address: 0x0148)
				data = GBC_readByte(0x01, 0x48);
				UART_sendByte(data);
				break;
			case 0x04: // Read GBC flag (address: 0x0143)
				data = GBC_readByte(0x01, 0x43);
				UART_sendByte(data);
				break;
			case 0x05: // Read game title (address 0x0134-0x0143)
				LED_startBlinking();
				for(unsigned int i = 0x0134; i <= 0x0143; i++) {
					data = GBC_readByte((char) (i >> 8), (char) i);
					UART_sendByte(data);
				}

				LED_stopBlinking();
				break;
			case 0x06: // Read Nintendo logo (address 0x0104-0x0133)
				LED_startBlinking();
				
				for(unsigned int i = 0x0104; i <= 0x0133; i++) {
					data = GBC_readByte((char) (i >> 8), (char) i);
					UART_sendByte(data);
				}
				
				LED_stopBlinking();
				break;
			case 0x07: // Read game data (adress 0x0000-0x7FFF and n * 0x4000-0x7FFF) n = Number of banks
				LED_startBlinking();

				romSize = GBC_readByte(0x01, 0x48);
				if(romSize <= 7) {
					numberOfBanks = pow(2, romSize+1);
				} else if(romSize == 0x52) {
					numberOfBanks = 72;
				} else if(romSize == 0x53) {
					numberOfBanks = 80;
				} else if(romSize == 0x54) {
					numberOfBanks = 96;
				} else {
					break;
				}
				
				/*
					First read Bank00 and Bank01 (0x0000-0x7FFF)
				*/
				for(unsigned int i = 0x0000; i <= 0x3FFF; i++) // 0x7FFF
				{
					data = GBC_readByte((char) (i >> 8), (char) i);
					UART_sendByte(data);
				}

				/*
					Second read BanXX (0x4000-0x7FFF) n times
				*/
				for(unsigned char bank = 1; bank <= numberOfBanks; bank++) {
					// perform bank switch
					GBC_writeByte(0x20, 0x00, bank);
					GBC_setWriteMode();	

					_delay_us(50);

					GBC_setReadMode();
					// read bank
					for(unsigned int i = 0x4000; i <= 0x7FFF; i++) {
						data = GBC_readByte((char) (i >> 8), (char) i);
						UART_sendByte(data);
					}
				}
				
				LED_stopBlinking();
				break;
			case 0x08: // read checksum
				LED_startBlinking();

				for(unsigned int i = 0x014E; i <= 0x014F; i++) {
					data = GBC_readByte((char) (i >> 8), (char) i);
					UART_sendByte(data);
				}

				LED_stopBlinking();
				break;
			}
		}
    }
}

