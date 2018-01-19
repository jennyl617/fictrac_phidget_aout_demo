## fictrac_phidget_aout_demo 

Demo Fictrac client (redis channel subscriber) which outputs an analog voltage proportional to 
the rate of change in heading. 

## Installation

Requirements: python-redis, Phidget22Python

```bash
$ python setup.py install 

```

## Hardware

Analog values are output on the [PhidgetAnalog 4-Output](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=1018) device.



## Example

``` python
from fictrac_phidget_aout_demo import FicTracAoutDemo

param = { 
        'rate_to_volt_const': 0.05,   # Constant for converting heading rate to voltage
        'aout_channel': 0,            # Analog output channel
        'aout_max_volt': 5.0,         # Maximum analog output value
        'aout_min_volt': -5.0,        # Minimum analog output value
        'lowpass_cutoff': 1.0,        # Lowpass filter cutoff frequency
        }

client = FicTracAoutDemo(param=param)
client.run()

```



