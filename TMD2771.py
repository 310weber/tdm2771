#!/usr/bin/python

import time
import smbus

# ===========================================================================
# TAOS TMD2771 proximity/ALS Class
#
# Written by A. Weber
# https://bitbucket.org/310weber/tmd2771
# ===========================================================================


class TMD2771:
    i2c = None

    __TMD2771_ENABLE                                = 0xA0
    __TMD2771_ALS_TIME                              = 0xA1
    __TMD2771_PROX_TIME                             = 0xA2
    __TMD2771_WAIT_TIME                             = 0xA3
    __TMD2771_ALS_INTERRUPT_LOW_THRESH_LOW_BYTE     = 0xA4
    __TMD2771_ALS_INTERRUPT_LOW_THRESH_HIGH_BYTE    = 0xA5
    __TMD2771_ALS_INTERRUPT_HIGH_THRESH_LOW_BYTE    = 0xA6
    __TMD2771_ALS_INTERRUPT_HIGH_THRESH_HIGH_BYTE   = 0xA7
    __TMD2771_PROX_INTERRUPT_LOW_THRESH_LOW_BYTE    = 0xA8
    __TMD2771_PROX_INTERRUPT_LOW_THRESH_HIGH_BYTE   = 0xA9
    __TMD2771_PROX_INTERRUPT_HIGH_THRESH_LOW_BYTE   = 0xAA
    __TMD2771_PROX_INTERRUPT_HIGH_THRESH_HIGH_BYTE  = 0xAB
    __TMD2771_PROX_INTERRUPT_PERSISTENCE_FILTERS    = 0xAC
    __TMD2771_CONFIGURATION                         = 0xAD
    __TMD2771_PROX_PULSE_COUNT                      = 0xAE
    __TMD2771_CONTROL_REGISTER                      = 0xAF
    __TMD2771_DEVICE_ID                             = 0xB2  # 0x20 = TMD27711; 0x29 = TMD27713
    __TMD2771_DEVICE_STATUS                         = 0xB3
    __TMD2771_ALS_CH0_DATA_LOW_BYTE                 = 0xB4  # 2 byte register, read in one operation
    __TMD2771_ALS_CH0_DATA_HIGH_BYTE                = 0xB5
    __TMD2771_ALS_CH1_DATA_LOW_BYTE                 = 0xB6  # 2 byte register, read in one operation
    __TMD2771_ALS_CH1_DATA_HIGH_BYTE                = 0xB7
    __TMD2771_PROX_DATA_LOW_BYTE                    = 0xB8  # 2 byte register, read in one operation
    __TMD2771_PROX_DATA_HIGH_BYTE                   = 0xB9

    __ENABLE_PIEN           = 0x20  # Prox interrupt mask.  When asserted, permits proximity interrupts
    __ENABLE_AIEN           = 0x10  # ALS interrupt mask. When asserted, permits ALS interrupts
    __ENABLE_WEN            = 0x08  # Wait enable. 1 enables wait timer; 0 disables
    __ENABLE_PEN            = 0x04  # Proximity enable. 1 enables proximity; 0 disables
    __ENABLE_AEN            = 0x02  # ALS enable. 1 enables ALS; 0 disables
    __ENABLE_PON            = 0x01  # Power ON. This bit activates internal oscillator. 1 enables; 0 disables

    __ALS_TIME_2_72         = 0xFF  # ALS integration time 2.72 ms
    __ALS_TIME_27_2         = 0xF6  # ALS integration time 27.2 ms
    __ALS_TIME_101          = 0xDB  # ALS integration time 101 ms
    __ALS_TIME_174          = 0xC0  # ALS integration time 174 ms
    __ALS_TIME_696          = 0x00  # ALS integration time 696 ms (Default)

    __PROX_TIME_2_72        = 0xFF  # 2.72 ms (Default) --DO NOT CHANGE--

    # Wait time in ms - multiply by 12 if WLONG is set
    __WAIT_TIME_2_72        = 0xFF  # Wait time 2.72 ms (32 ms if WLONG = 1)
    __WAIT_TIME_200         = 0xB6  # Wait time 200 ms  (2.4 s if WLONG = 1)
    __WAIT_TIME_700         = 0x00  # Wait time 700 ms  (8.3 s if WLONG = 1)

    __PERSISTENCE_PROX_ALL  =0x00   # Every prox cycle generates an interrupt
    __PERSISTENCE_PROX_1    =0x10   # Prox int. when 1 value out of range
    __PERSISTENCE_PROX_2    =0x20   # Prox int. when 2 consecutive out of range
    __PERSISTENCE_PROX_3    =0x30   # " "
    __PERSISTENCE_PROX_4    =0x40   # " "
    __PERSISTENCE_PROX_5    =0x50   # " "
    __PERSISTENCE_PROX_6    =0x60   # " "
    __PERSISTENCE_PROX_7    =0x70   # " "
    __PERSISTENCE_PROX_8    =0x80   # " "
    __PERSISTENCE_PROX_9    =0x90   # " "
    __PERSISTENCE_PROX_10   =0xA0   # " "
    __PERSISTENCE_PROX_11   =0xB0   # " "
    __PERSISTENCE_PROX_12   =0xC0   # " "
    __PERSISTENCE_PROX_13   =0xD0   # " "
    __PERSISTENCE_PROX_14   =0xE0   # " "
    __PERSISTENCE_PROX_15   =0xF0   # Prox int. when 15 consecutive out of range

    __PERSISTENCE_ALS_ALL   =0x00   # Every ALS cycle generates an interrupt
    __PERSISTENCE_ALS_1     =0x01   # ALS int. when 1 value out of range
    __PERSISTENCE_ALS_2     =0x02   # ALS int. when 2  consecutive out of range
    __PERSISTENCE_ALS_3     =0x03   # ALS int. when 3  consecutive out of range
    __PERSISTENCE_ALS_5     =0x04   # ALS int. when 5  consecutive out of range
    __PERSISTENCE_ALS_10    =0x05   # ALS int. when 10 consecutive out of range
    __PERSISTENCE_ALS_15    =0x06   # ALS int. when 15 consecutive out of range
    __PERSISTENCE_ALS_20    =0x07   # ALS int. when 20 consecutive out of range
    __PERSISTENCE_ALS_25    =0x08   # ALS int. when 25 consecutive out of range
    __PERSISTENCE_ALS_30    =0x09   # ALS int. when 30 consecutive out of range
    __PERSISTENCE_ALS_35    =0x0A   # ALS int. when 35 consecutive out of range
    __PERSISTENCE_ALS_40    =0x0B   # ALS int. when 40 consecutive out of range
    __PERSISTENCE_ALS_45    =0x0C   # ALS int. when 45 consecutive out of range
    __PERSISTENCE_ALS_50    =0x0D   # ALS int. when 50 consecutive out of range
    __PERSISTENCE_ALS_55    =0x0E   # ALS int. when 55 consecutive out of range
    __PERSISTENCE_ALS_60    =0x0F   # ALS int. when 60 consecutive out of range

    __CONFIGURATION_WLONG   =0x02   # Enable long wait time (12x normal)

    __CONTROL_PDRIVE_100    = 0x00  # LED drive strength 100%
    __CONTROL_PDRIVE_50     = 0x40  # LED drive strength 50%
    __CONTROL_PDRIVE_25     = 0x80  # LED drive strength 25%
    __CONTROL_PDRIVE_12_5   = 0xB0  # LED drive strength 12.5%
    __CONTROL_PDIODE_CH0    = 0x10  # Proximity uses channel 0 diode
    __CONTROL_PDIODE_CH1    = 0x20  # Proximity uses channel 1 diode
    __CONTROL_PDIODE_BOTH   = 0x30  # Proximity uses both diodes
    __CONTROL_AGAIN_1       = 0x00  # ALS gain 1x
    __CONTROL_AGAIN_8       = 0x01  # ALS gain 8x
    __CONTROL_AGAIN_16      = 0x02  # ALS gain 16x
    __CONTROL_AGAIN_120     = 0x03  # ALS gain 120x

    __ID_TMD27711           = 0x20  # Model with i2c voltage = VDD
    __ID_TMD27713           = 0x29  # Model with i2c voltage = 1.8 V

    __STATUS_PROX_INT       = 0x20  # Proximity interrupt asserted
    __STATUS_ALS_INT        = 0x10  # ALS interrupt asserted
    __STATUS_ALS_VALID      = 0x01  # ALS channels completed integration cycle

    # Dictionaries with the valid gain/timing values
    # These simplify and clean the code (avoid abuse of if/elif/else clauses)
    ALS_GAIN_ACTUAL = {
        __CONTROL_AGAIN_1:      1,
        __CONTROL_AGAIN_8:      8,
        __CONTROL_AGAIN_16:     16,
        __CONTROL_AGAIN_120:    120
    }

    ALS_TIME_ACTUAL = {
        __ALS_TIME_2_72:    2.72,
        __ALS_TIME_27_2:    27.2,
        __ALS_TIME_101:     101,
        __ALS_TIME_174:     174,
        __ALS_TIME_696:     696
    }

    def __init__(self, address=0x39, debug=False):
        # Depending on if you have an old or a new Raspberry Pi, you
        # may need to change the I2C bus.  Older Pis use SMBus 0,
        # whereas new Pis use SMBus 1.  If you see an error like:
        # 'Error accessing 0x39: Check your I2C address '
        # change the SMBus number in the initializer below!

        # setup i2c bus and SFR address
        self.i2c = smbus.SMBus(1)
        self.address = address
        self.debug = debug

        # Check module identification to verify proper communication
        self.idModel = self.get_register(self.__TMD2771_DEVICE_ID)
        if self.idModel in (self.__ID_TMD27711, self.__ID_TMD27713):
            print "Prox/ALS sensor is ready. Model:", self.idModel
            self.ready = True
        else:
            print "Prox/ALS sensor error."
            self.ready = False

    def start(self):
        # Recommended settings from application note
        # http://ams.com/eng/content/view/download/145120

        # ALS integration time = 100 ms
        self.set_register(self.__TMD2771_ALS_TIME, self.__ALS_TIME_101)
        # Proximity integration time = 2.72 ms
        self.set_register(self.__TMD2771_PROX_TIME, self.__PROX_TIME_2_72)
        # Proximity pulses = 4
        self.set_register(self.__TMD2771_PROX_PULSE_COUNT, 0x04)
        # Control register: LED drive = 100 mA, prox. diode = CH1, ALS Gain = 1x
        self.set_register(self.__TMD2771_CONTROL_REGISTER,
                          (self.__CONTROL_PDRIVE_100 |
                           self.__CONTROL_PDIODE_CH1 |
                           self.__CONTROL_AGAIN_1)
                          )
        # Enable register:
        # Enable prox and ALS interrupts, wait, prox and ALS, power on
        self.set_register(self.__TMD2771_ENABLE,
                          (self.__ENABLE_PIEN |
                           self.__ENABLE_AIEN |
                           self.__ENABLE_WEN |
                           self.__ENABLE_PEN |
                           self.__ENABLE_AEN |
                           self.__ENABLE_PON)
                          )

        if self.debug:
            print "Default settings:"
            print "ALS integration time - %x" % \
                  self.get_register(self.__TMD2771_ALS_TIME)
            print "Proximity integration time - %x" % \
                  self.get_register(self.__TMD2771_PROX_TIME)
            print "Proximity pulse count - %x" % \
                  self.get_register(self.__TMD2771_PROX_PULSE_COUNT)
            control_register = self.get_register(self.__TMD2771_CONTROL_REGISTER)
            print "LED drive strength - %x" % \
                  ((control_register | 0xC0) >> 6)
            print "Proximity diode channel(s) - %x" % \
                  ((control_register | 0x30) >> 4)
            print "ALS gain - %x" % \
                  (control_register | 0x03)
            enable_register = self.get_register(self.__TMD2771_ENABLE)
            print "Prox. interrupt enable - %x" % \
                  ((enable_register | 0x20) >> 5)
            print "ALS interrupt enable - %x" % \
                  ((enable_register | 0x10) >> 4)
            print "Wait enable - %x" % \
                  ((enable_register | 0x08) >> 3)
            print "Prox. sensor enable - %x" % \
                  ((enable_register | 0x04) >> 2)
            print "ALS sensor enable - %x" % \
                  ((enable_register | 0x02) >> 1)
            print "Power on - %x" % \
                  (enable_register | 0x01)

    def stop(self):
        self.set_register(self.__TMD2771_ENABLE, 0x00)
        if self.debug:
            enable_register = self.get_register(self.__TMD2771_ENABLE)
            if (enable_register & 0x01) == 0x00:
                print "Sensor stopped. Enable register - %x" % enable_register
            else:
                print "Sensor failed ot stop. Enable register - %x" % \
                      enable_register

    def get_distance(self):
        prox_data = self.get_register_16bit(self.__TMD2771_PROX_DATA_LOW_BYTE)
        # Reverse bytes because low byte is read first
#        prox_data = ((prox_data << 8) & 0xFF00) | (prox_data >> 8)
        if self.debug:
            print "Proximity data - %d" % prox_data
        return prox_data

    def get_ambient_light(self):
        ch0_data = self.get_register_16bit(self.__TMD2771_ALS_CH0_DATA_LOW_BYTE)
        ch1_data = self.get_register_16bit(self.__TMD2771_ALS_CH1_DATA_LOW_BYTE)
        # Reverse bytes because low byte is read first
#        ch0_data = ((ch0_data << 8) & 0xFF00) | (ch0_data >> 8)
#        ch1_data = ((ch1_data << 8) & 0xFF00) | (ch1_data >> 8)
        if self.debug:
            print "ALS Ch0 data - %x; Ch1 data - %x" % (ch0_data, ch1_data)

        als_gain_actual = self.ALS_GAIN_ACTUAL.get(
                self.get_register(self.__TMD2771_CONTROL_REGISTER) & 0x03)
        als_time_actual = self.ALS_TIME_ACTUAL.get(
                self.get_register(self.__TMD2771_ALS_TIME))
        if als_gain_actual is None:
            als_gain_actual = 1
        if als_time_actual is None:
            als_time_actual = 2.72

        if self.debug:
            print "ALS gain - %d; ALS time - %d" % (als_gain_actual, als_time_actual)

        scaling_factor = 1.0  # 1.0 for open air (other factors for under glass)

        counts_per_lux = (als_time_actual * als_gain_actual) / \
                         (scaling_factor*24)
        lux_1 = (ch0_data - (2 * ch1_data)) / counts_per_lux
        lux_2 = ((0.6 * ch0_data) - ch1_data) / counts_per_lux
        lux_calculated = max(lux_1, lux_2, 0)
        if self.debug:
            print"ALS CPS - %.3d; Lux1 - %.1d; Lux2 - %.1d; Lux - %.1d" % \
                 (counts_per_lux, lux_1, lux_2, lux_calculated)

        return lux_calculated

    def get_register(self, register_address):
        # Reads an unsigned 8-bit value from the I2C device
        result = self.i2c.read_byte_data(self.address, register_address)
        if self.debug:
            print "I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % \
                  (self.address, result & 0xFF, register_address)
        return result

    def get_register_16bit(self, register_address):
        # Reads an unsigned 16-bit value from the I2C device
        result = self.i2c.read_word_data(self.address, register_address)
        if self.debug:
            print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % \
                  (self.address, result & 0xFFFF, register_address)
        return result

    def set_register(self, register_address, data):
        # Writes an unsigned 8-bit value from the I2C device
        self.i2c.write_byte_data(self.address, register_address, data)
        if self.debug:
            read_back = self.i2c.read_byte_data(self.address, register_address)
            if read_back == data:
                print "Success - I2C: Device 0x%02X returned 0x%02X from reg " \
                      "0x%02X" \
                      % (self.address, read_back & 0xFF, register_address)
            else:
                print "Failed - I2C: Device 0x%02X returned 0x%02X from reg " \
                      "0x%02X" \
                      % (self.address, read_back & 0xFF, register_address)

    def set_register_16bit(self, register_address, data):
        # Writes an unsigned 16-bit value from the I2C device
        self.i2c.write_word_data(self.address, register_address, data)
        if self.debug:
            read_back = self.i2c.read_word_data(self.address, register_address)
            if read_back == data:
                print "Success - I2C: Device 0x%02X returned 0x%04X from reg " \
                      "0x%02X" \
                      % (self.address, read_back & 0xFF, register_address)
            else:
                print "Failed - I2C: Device 0x%02X returned 0x%04X from reg " \
                      "0x%02X" \
                      % (self.address, read_back & 0xFF, register_address)