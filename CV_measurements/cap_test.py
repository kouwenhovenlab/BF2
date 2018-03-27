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
station = qc.Station(SR1)#, Keith_1, Keith_2)
lockin = SR1
ampl = lockin.amplitude()
delay = 5*lockin.time_constant()
fs = np.linspace(100, 500e3, 101)

names = {1: (100, 'pF'),
         2: (68, 'pF'),
         3: (47, 'pF'),
         4: (33, 'pF'),
         5: (10, 'pF'),
         9: (1, 'pF'),
         8: (20, 'kOhm'),
         10:('open', '')}
channel = 10
name = 'ch{}_{}{}'.format(channel, *names[channel])
Is = np.zeros(len(fs), dtype = np.complex128)
dat = {'name': name,
       'V_ac': ampl,
       'table': names,
       'channel': channel,
       'settings': station.snapshot(),
       'f (Hz)': fs,
       'I (A)': Is}
lockin.frequency(fs[0])
time.sleep(4*delay)
for kk,f in enumerate(fs):
    lockin.frequency(f)
    time.sleep(delay)
    Is[kk] = lockin.X() + 1.j*lockin.Y()

plt.figure('Cap')

plt.subplot(211)
plt.plot(fs, Is.real, label = name)
plt.legend()
plt.subplot(212)
plt.plot(fs, Is.imag)
plt.figure('Cap_cmplx')
plt.plot(Is.real, Is.imag, '.', label = name)
plt.legend()
pickle.dump(dat, open(name + '.pickle', 'wb'))
