from __future__ import print_function
import redis
import json
import time
import math
import Phidget22.Devices.VoltageOutput
import Phidget22.PhidgetException 
import Phidget22.Phidget


class FicTracAoutDemo(object):

    DefaultParam = {
            'rate_to_volt_const': 0.01, 
            'aout_channel': 0,
            'aout_max_volt': 5.0,
            'aout_min_volt': -5.0,
            'lowpass_cutoff': 0.5,
            }


    def __init__(self, param = DefaultParam):

        self.param = param
        self.time_start = time.time()
        self.heading_rate_calc = AngleRateCalc(self.time_start,0.0)
        self.heading_rate_lowpass = LowpassFilter(0.0, cutoff_freq=self.param['lowpass_cutoff'])

        # Setup redis subscriber
        self.redis_client = redis.StrictRedis()
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('fictrac')

        # Setup analog output
        self.aout = Phidget22.Devices.VoltageOutput.VoltageOutput()
        self.aout.setChannel(self.param['aout_channel'])
        self.aout.openWaitForAttachment(5000)
        self.aout.setVoltage(0.0)

    def run(self):
        """ 
        Loop forever listening for new messages on "fictrac" channel and output an 
        analog voltage proportional to heading rate for each new message
        """
        while True:

            for item in self.pubsub.listen():

                # New message from fictrac - convert from json to python dictionary
                message = item['data']
                try:
                    data = json.loads(message)
                except TypeError:
                    continue
        
                # Take action based on message type

                if data['type'] == 'reset':
                    # This is a reset message which indicates that FicTrac has been restarted 
                    self.time_start = time.time()
                    self.heading_rate_calc.reset(self.time_start)
                    self.aout.setVoltage(0.0)
                else:
                    # This is a Data message  - compute heading rate
                    time_curr = time.time()
                    heading_rate = self.heading_rate_calc.update(time_curr, data['heading'])
                    heading_rate_filt = self.heading_rate_lowpass.update(time_curr, heading_rate)

                    # Set analog output voltage and print message
                    output_voltage = self.param['rate_to_volt_const']*heading_rate_filt
                    output_voltage = clamp(output_voltage, self.param['aout_min_volt'], self.param['aout_max_volt']) 
                    self.aout.setVoltage(output_voltage)

                    # Display status message 
                    time_elapsed = time_curr - self.time_start
                    print('frame:  {0}'.format(data['frame']))
                    print('time:   {0:1.3f}'.format(time_elapsed))
                    print('rate:   {0:1.3f}'.format(heading_rate))
                    print('volt:   {0:1.3f}'.format(output_voltage))
                    print()



# Utilities
# ---------------------------------------------------------------------------------------
class AngleRateCalc(object):
    """
    Angular rate calculator
    """

    def __init__(self,t,value_init=0.0):
        self.value_init = value_init
        self.reset(t)

    def reset(self,t):
        self.rate = 0.0
        self.save_prev_state(t,self.value_init)

    def save_prev_state(self,t,value):
        self.time_prev = t
        self.value_prev = value

    def update(self, t, value):
        # Calculate rate
        dt = t - self.time_prev
        self.rate = angle_dist(self.value_prev, value)/dt
        self.save_prev_state(t,value)
        return self.rate


class LowpassFilter(object):
    """
    Simple first order lowpass filter
    """

    def __init__(self,t,cutoff_freq=1.0,value_init=0.0):
        self.value_init = value_init
        self.cutoff_freq = cutoff_freq
        self.reset(t)

    def reset(self,t):
        self.time_prev = t
        self.value_filt = self.value_init

    def get_alpha(self,dt):
        tmp = 2.0*math.pi*self.cutoff_freq*dt
        alpha = tmp/(tmp +1.0)
        return alpha

    def update(self,t,value):
        dt = t - self.time_prev
        self.time_prev = t
        alpha = self.get_alpha(dt)
        self.value_filt = (1.0-alpha)*self.value_filt + alpha*value
        return self.value_filt


def clamp(x, min_val, max_val):
    """
    Clamp value between min_val and max_val
    """
    return max(min(x,max_val),min_val)


def angle_dist(angle0,angle1,angle_type='deg'):
    """
    Calculate distance between two angles - always smallest value.
    """
    # Get max angle value based on angle type 'deg' or 'rad'
    if angle_type == 'deg':
        max_angle = 360.0
    elif angle_type == 'rad':
        max_angle = 2.0*math.pi
    else:
        raise ValueError, 'unknown angle type'
    # Compute shortest distance between angles
    value = (angle1%max_angle) - (angle0%max_angle)
    if value >  0.5*max_angle:
        value = value - max_angle 
    if value < -0.5*max_angle:
        value = max_angle + value 
    return value





