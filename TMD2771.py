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
    __TMD2771_DEVICE_ID                             = 0xB2      # 0x20 = TMD27711; 0x29 = TMD27713
    __TMD2771_DEVICE_STATUS                         = 0xB3
    __TMD2771_ALS_CH0_DATA_LOW_BYTE                 = 0xB4      # 2 byte register, read in one operation
    __TMD2771_ALS_CH0_DATA_HIGH_BYTE                = 0xB5
    __TMD2771_ALS_CH1_DATA_LOW_BYTE                 = 0xB6      # 2 byte register, read in one operation
    __TMD2771_ALS_CH1_DATA_HIGH_BYTE                = 0xB7
    __TMD2771_PROX_DATA_LOW_BYTE                    = 0xB8      # 2 byte register, read in one operation
    __TMD2771_PROX_DATA_HIGH_BYTE                   = 0xB9

    __ENABLE_PIEN           = 0x20  # Proximity interrupt mask.  When asserted, permits proximity interrupts.
    __ENABLE_AIEN           = 0x10  # ALS interrupt mask. When asserted, permits ALS interrupts.
    __ENABLE_WEN            = 0x08  # Wait enable. 1 enables wait timer; 0 disables.
    __ENABLE_PEN            = 0x04  # Proximity enable. 1 enables proximity; 0 disables.
    __ENABLE_AEN            = 0x02  # ALS enable. 1 enables ALS; 0 disables
    __ENABLE_PON            = 0x01  # Power ON. This bit activates internal oscillator. 1 enables; 0 disables.

    __ALS_TIME_2_72         = 0xFF  # ALS integration time 2.72 ms
    __ALS_TIME_27_2         = 0xF6  # ALS integration time 27.2 ms
    __ALS_TIME_101          = 0xDB  # ALS integration time 101 ms
    __ALS_TIME_174          = 0xC0  # ALS integration time 174 ms
    __ALS_TIME_696          = 0x00  # ALS integration time 696 ms (Default)

    __PROX_TIME_2_72        = 0xFF  # Proximity integration time 2.72 ms - default value; do not change

    # Wait time in ms - multiply by 12 if WLONG is set
    __WAIT_TIME_2_72        = 0xFF  # Wait time 2.72 ms (32 ms if WLONG = 1)
    __WAIT_TIME_200         = 0xB6  # Wait time 200 ms  (2.4 s if WLONG = 1)
    __WAIT_TIME_700         = 0x00  # Wait time 700 ms  (8.3 s if WLONG = 1)

    __PERSISTENCE_PROX_ALL  =0x00   # Every proximity cycle generates an interrupt
    __PERSISTENCE_PROX_1    =0x10   # Proximity interrupt only when 1 value out of range
    __PERSISTENCE_PROX_2    =0x20   # Proximity interrupt only when 2 consecutive values out of range
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
    __PERSISTENCE_PROX_15   =0xF0   # Proximity interrupt only when 15 consecutive values out of range

    __PERSISTENCE_ALS_ALL   =0x00   # Every ALS cycle generates an interrupt
    __PERSISTENCE_ALS_1     =0x01   # ALS interrupt only when 1 value out of range
    __PERSISTENCE_ALS_2     =0x02   # ALS interrupt only when 2  consecutive values out of range
    __PERSISTENCE_ALS_3     =0x03   # ALS interrupt only when 3  consecutive values out of range
    __PERSISTENCE_ALS_5     =0x04   # ALS interrupt only when 5  consecutive values out of range
    __PERSISTENCE_ALS_10    =0x05   # ALS interrupt only when 10 consecutive values out of range
    __PERSISTENCE_ALS_15    =0x06   # ALS interrupt only when 15 consecutive values out of range
    __PERSISTENCE_ALS_20    =0x07   # ALS interrupt only when 20 consecutive values out of range
    __PERSISTENCE_ALS_25    =0x08   # ALS interrupt only when 25 consecutive values out of range
    __PERSISTENCE_ALS_30    =0x09   # ALS interrupt only when 30 consecutive values out of range
    __PERSISTENCE_ALS_35    =0x0A   # ALS interrupt only when 35 consecutive values out of range
    __PERSISTENCE_ALS_40    =0x0B   # ALS interrupt only when 40 consecutive values out of range
    __PERSISTENCE_ALS_45    =0x0C   # ALS interrupt only when 45 consecutive values out of range
    __PERSISTENCE_ALS_50    =0x0D   # ALS interrupt only when 50 consecutive values out of range
    __PERSISTENCE_ALS_55    =0x0E   # ALS interrupt only when 55 consecutive values out of range
    __PERSISTENCE_ALS_60    =0x0F   # ALS interrupt only when 60 consecutive values out of range

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
    __STATUS_ALS_VALID      = 0x01  # Indicates the ALS channels have completed an integration cycle

    # Dictionaries with the valid gain/timing values
    # These simplify and clean the code (avoid abuse of if/elif/else clauses)
    ALS_GAIN_ACTUAL = {
        1:      __CONTROL_AGAIN_1,
        8:      __CONTROL_AGAIN_8,
        16:     __CONTROL_AGAIN_16,
        120:    __CONTROL_AGAIN_120,
    }
    ALS_TIME_ACTUAL = {
        2.72:   __ALS_TIME_2_72,
        27.2:   __ALS_TIME_27_2,
        101:    __ALS_TIME_101,
        174:    __ALS_TIME_174,
        696:    __ALS_TIME_696
    }

    PROX_TIME_ACTUAL = {
        2.72:   __PROX_TIME_2_72
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
        if self.idModel == (self.__ID_TMD27711 or self.__ID_TMD27713):
            print "Prox/ALS sensor is ready. Model:", self.idModel
            self.ready = True
        else:
            print "Prox/ALS sensor error."
            self.ready = False

    def enable(self):
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
        # Enable register: Enable prox and ALS interrupts, wait, prox and ALS, power on
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

    def get_distance(self):
        # Start Single shot mode
        self.set_register(self.__TMD2771_SYSRANGE_START, 0x01)
        time.sleep(0.010)
        if self.debug:
            print "Range status: %x" % \
                  self.get_register(self.__TMD2771_RESULT_RANGE_STATUS) & 0xF1
        distance = self.get_register(self.__TMD2771_RESULT_RANGE_VAL)
        self.set_register(self.__TMD2771_SYSTEM_INTERRUPT_CLEAR, 0x07)
        return distance

    def get_ambient_light(self, als_gain):
        # First load in Gain we are using, do it every time in case someone
        # changes it on us.
        # Note: Upper nibble should be set to 0x4 i.e. for ALS gain
        # of 1.0 write 0x46

        # Set the ALS gain, defaults to 20.
        # If gain is in the dictionary (defined in init()) it returns the value
        # of the constant otherwise it returns the value for gain 20.
        # This saves a lot of if/elif/else code!
        if als_gain not in self.ALS_GAIN_ACTUAL:
            print "Invalid gain setting: %d.  Setting to 20." % als_gain
        als_gain_actual = self.ALS_GAIN_ACTUAL.setdefault(als_gain, 20)
        self.set_register(
            self.__TMD2771_SYSALS_ANALOGUE_GAIN,
            (0x40 | self.ALS_GAIN_REG.setdefault(als_gain, self.__ALS_GAIN_20)))

        # Start ALS Measurement
        self.set_register(self.__TMD2771_SYSALS_START, 0x01)

        time.sleep(0.100)   # give it time...

        # Retrieve the Raw ALS value from the sensor
        if self.debug:
            print "ALS status: %x" % \
                  self.get_register(self.__TMD2771_RESULT_ALS_STATUS) & 0xF1
        als_raw = self.get_register_16bit(self.__TMD2771_RESULT_ALS_VAL)
        self.set_register(self.__TMD2771_SYSTEM_INTERRUPT_CLEAR, 0x07)

        # Get Integration Period for calculation, we do this every time in case
        # someone changes it on us.
        als_integration_period_raw = self.get_register_16bit(
            self.__TMD2771_SYSALS_INTEGRATION_PERIOD)

        als_integration_period = 100.0 / als_integration_period_raw

        # Calculate actual LUX from application note
        als_calculated = \
            0.32 * (als_raw / als_gain_actual) * als_integration_period

        return als_calculated

    def get_register(self, register_address):
        self.i2c.write_i2c_block_data(self.address, register_address)
        data = self.i2c.read_byte(self.address)
        return data

    def get_register_16bit(self, register_address):
        # Reads an unsigned 16-bit value from the I2C device
        try:
            result = self.bus.read_word_data(self.address, register_address)
            if self.debug:
                print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % \
                      (self.address, result & 0xFFFF, register_address)
            return result
        except IOError, err:
            return self.errMsg()

    def set_register(self, register_address, data):
        a1 = (register_address >> 8) & 0xFF
        a0 = register_address & 0xFF
        self.i2c.write_i2c_block_data(self.address, a1, [a0, (data & 0xFF)])

    def set_register_16bit(self, register_address, data):
        a1 = (register_address >> 8) & 0xFF
        a0 = register_address & 0xFF
        d1 = (data >> 8) & 0xFF
        d0 = data & 0xFF
        self.i2c.write_i2c_block_data(self.address, a1, [a0, d1, d0])
