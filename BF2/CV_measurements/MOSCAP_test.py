# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 20:37:33 2018

@author: Administrator
"""


import numpy as np
import matplotlib.pyplot as plt
import pickle
import time
import qcodes as qc
from qcodes.instrument_drivers.stanford_research.SR865 import SR865
from utils import data_storage as ds
from utils.data_storage import datapickling as dp
import sys
senses = [0.5, 1, 0.2, 2e-09, 5e-05, 1e-08, 2e-08, 0.0001, 0.05, 0.0002, 5e-06, 5e-08, 1e-06, 0.1, 1e-09, 5e-09, 2e-05, 0.02, 5e-07, 1e-05, 0.01, 2e-07, 0.005, 1e-07, 2e-06, 0.002, 0.001, 0.0005]
senses = np.array(senses)
senses.sort()

def ramp_lockin_dc(val):
    curval = lockin.sine_outdc()
    dv = 0.01
    nvals = np.abs((val - curval))/dv 
    #print(nvals)
    vals = np.linspace(curval, val, int(nvals))
    #print(vals)
    for nval in vals:
        lockin.sine_outdc(nval)
        time.sleep(0.02)
try:        
    SR1 = SR865('SR1', 'USB0::0xB506::0x2000::003225::INSTR')
except:
    pass
station = qc.Station(SR1)#, Keith_1, Keith_2)
lockin = SR1
ampl = lockin.amplitude()
delay = 5*lockin.time_constant()
fs = np.linspace(100, 500e3, 21)


names = {1: (750, 'um'),
         2: (300, 'um'),
         3: (200, 'um'),
         4: (150, 'um', 2),
         5: (100, 'um', 1),
         6: (50, 'um', 1),
         7:('open', '')}
channel = 6
V_gates = np.linspace(-5,5,21)
ramp_lockin_dc(V_gates[0])
name = 'MOSCAP_test_dev{}_{}{}'.format(channel, *names[channel])
dat = dp.init_data_pickle(name)

ds = {'name': name,
       'V_ac': ampl,
       'table': names,
       'channel': channel,
       'settings': station.snapshot(),
       'data': {
               'V_gates (V)': V_gates,
               'I (A)':  [],
               'f (Hz)': fs,}
       }
for d in ds.keys():
    dat[d] = ds[d]
gdat = dat['data']
ERASE_LINE = 200*'\b'#'\x1b[1M'#'\x1b[2K'
for nn, V_gate in enumerate(V_gates):
    ramp_lockin_dc(V_gate)
    time.sleep(1)
    Is = np.zeros(len(fs), dtype = np.complex128)
    gdat['I (A)'] += [Is]
    sys.stdout.write(ERASE_LINE + 'V_gate = {} V, {} of {}'.format(V_gate, nn, len(V_gates)))
    lockin.frequency(fs[0])
    time.sleep(4*delay)
    for kk,f in enumerate(fs):
        lockin.frequency(f)
        time.sleep(delay)
        Is[kk] = lockin.X() + 1.j*lockin.Y()
    sens = senses[(senses > 1.2*(np.max(np.abs(Is)))).tolist()][0]
    lockin.sensitivity(sens)
    plt.figure('Cap')
    
    plt.subplot(211)
    plt.plot(fs, Is.real, label = name)
    plt.legend()
    plt.subplot(212)
    plt.plot(fs, Is.imag)
    plt.figure('Cap_cmplx')
    plt.plot(Is.real, Is.imag, '.', label = name+'{V_gate}')
    plt.legend()
    dp.save_data_pickle(dat)
pickle.dump(dat, open(name + '.pickle', 'wb'))
