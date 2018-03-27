# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:56:54 2018

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:26:02 2018

@author: Administrator
"""

import time
import sys
import os
from collections import OrderedDict
from importlib import reload
from stationq.qctools import instruments as instr
import h5py
import numpy as np
from matplotlib import pyplot as plt
from qcodes.instrument_drivers.stanford_research.SR860 import SR860
from qcodes.instrument_drivers.tektronix.Keithley_2000  import Keithley_2000
from MDAC import MDAC
import qcodes as qc

sys.path.append(r'D:\Code\StationQ')


#mdac = MDAC.MDAC('MDAC1', 'ASRL4::INSTR', debug = True)
#mdac = instr.create_inst(MDAC.MDAC, 'MDAC1', 'ASRL4::INSTR', debug = True, force_new_instance=True)
#mdac.ch01.awg_sine(1000.,0.1,0.2)
SR1 = SR860('SR1', 'GPIB0::4::INSTR')
#Keith_1 = Keithley_2000('Keith_1', 'GPIB0::15::INSTR') # for DC
#Keith_2 = None # for leakage
#station = qc.Station(mdac, SR1, Keith_1)#, Keith_1, Keith_2)
def check_relays(ch):
    print('%s (dac, smc, microd, gnd, bus) = (%s, %s, %s, %s, %s)'%(ch.name, ch.dac_output(), ch.smc(), ch.microd(), ch.gnd(), ch.bus()))
#check_relays(mdac.ch01)
#check_relays(mdac.ch09)