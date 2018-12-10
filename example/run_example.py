from fictrac_phidget_aout_demo import aout_demo

param = { 
        'rate_to_volt_const': 0.05,   # Constant for converting heading rate to voltage
        'aout_channel': 0,            # Analog output channel
        'aout_max_volt': 5.0,         # Maximum analog output value
        'aout_min_volt': -5.0,        # Minimum analog output value
        'lowpass_cutoff': 1.0,        # Lowpass filter cutoff frequency
        }

client = aout_demo.FicTracAoutDemo(param=param)
client.run()

