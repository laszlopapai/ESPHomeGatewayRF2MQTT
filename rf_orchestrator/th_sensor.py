from enum import Enum

# https://manual.pilight.org/protocols/433.92/weather/alecto_ws1700.html
# 0  - 3  Header
# 4  - 11 ID
# 12 - 12 Battery
# 13 - 13 TX Mode
# 14 - 15 Channel
# 16 - 27 Temperature
# 28 - 35 Humidity


class Bit(Enum):
    ZERO = 0
    ONE = 1
    TooLong = 2
    TooShort = 3
    SyncLoss = 4

class THSensor:
    def __init__(self):
        self.first = True
        self.contigous = False
        self.buffer = 0
        self.messageCount = 0


    def getHeader(self):
        return self.extractBits(0, 3)
    
    def getID(self):
        return self.extractBits(4, 11)
    
    def getBattery(self):
        return self.extractBits(12, 12)
    
    def getTXMode(self):
        return self.extractBits(13, 13)
    
    def getChannel(self):
        return self.extractBits(14, 15)
    
    def getTemperature(self):
        return round(self.extractBits(16, 27) * 0.1, 1)
    
    def getHumidity(self):
        return self.extractBits(28, 35)

    def isValid(self):
        if self.getHeader() == 5:
            return self.messageCount
        return -1

    def extractBits(self, first: int, last: int) -> int:
        """
        Extracts bits from `buffer` between bit positions `first` and `last` (inclusive),
        where 0 is the most significant bit (MSB) of a 36-bit value.

        :param buffer: The 36-bit integer buffer.
        :param first: The index of the first bit (MSB side, 0-35).
        :param last: The index of the last bit (MSB side, 0-35).
        :return: Extracted integer value.
        """
        if not (0 <= first <= 35 and 0 <= last <= 35 and first <= last):
            raise ValueError("Bit positions must be between 0 and 35, and first <= last")

        # Calculate number of bits in the slice
        width = last - first + 1

        # Shift left to drop leading bits, then right to align to LSB
        shift = 35 - last
        mask = (1 << width) - 1
        return (self.buffer >> shift) & mask

    def pushBit(self, bit):
        if bit != Bit.ZERO and bit != Bit.ONE:
            self.buffer = 0
            return

        bitNum = 0 if bit == Bit.ZERO else 1
        self.buffer = ((self.buffer << 1) | bitNum) & ((1 << 36) - 1)  # Keep only 36 bits
        #print(f"Message {self.messageCount}: {self.buffer:036b} {bit}")

        if self.isValid() >= 0:
            self.messageCount += 1

    def pushPulse(self, pulseLength):
        MIN = 200
        MAX = 4200
        MINSHORT = 1200
        MINLONG = 3200

        tooLong = pulseLength > MAX
        tooShort = pulseLength < MIN
        resetPulse = pulseLength < MINSHORT and (not tooShort)
        shortPulse = pulseLength < MINLONG and pulseLength >= MINSHORT
        longPulse = pulseLength >= MINLONG and (not tooLong)

        
        if tooLong or tooShort:
            if (self.contigous and tooLong):
                self.pushBit(Bit.TooLong)
            if (self.contigous and tooShort):
                self.pushBit(Bit.TooShort)

            self.first = True
            self.contigous = False
            return

        if (shortPulse and (not self.first)):
            self.pushBit(Bit.ZERO)
            self.contigous = True
            self.first = True
        
        elif (longPulse and (not self.first)):
            self.pushBit(Bit.ONE)
            self.contigous = True
            self.first = True

        elif (resetPulse and self.first):
            self.first = False
		
        else:
            self.pushBit(Bit.SyncLoss)
            self.contigous = False
		


