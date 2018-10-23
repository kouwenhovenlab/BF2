from importlib import reload

import qcodes as qc
import broadbean as bb
from pytopo.qctools import instruments as instools
from pytopo.qctools.instruments import create_inst, add2station
from pytopo.rf.alazar.acquisition_tools import simple_alazar_setup_ext_trigger

from init_station import *


# set some station configuration variables
qc.config['user']['instruments'] = {
    'awg_name' : 'awg',
    'alazar_name' : 'alazar',
    'default_acquisition_controller' : 'post_iq_acq',
    }

# init instruments lives in a function (to be able to import without loading instruments.)
def init_instruments():
    inst_list = []

    # Create all instruments

    # create and setup Alazar
    from qcodes.instrument_drivers.AlazarTech import utils
    from qcodes.instrument_drivers.AlazarTech.ATS9360 import AlazarTech_ATS9360
    alazar = instools.create_inst(AlazarTech_ATS9360, 'alazar', force_new_instance=True)
    inst_list.append(alazar)

    simple_alazar_setup_ext_trigger(256, 1, 1)
    
    # create and setup AWG
    from qcodes.instrument_drivers.tektronix.AWG5208 import AWG5208
    awg = instools.create_inst(
        AWG5208, 'awg', 
        address='TCPIP0::169.254.121.32::inst0::INSTR',
        force_new_instance=True)
    inst_list.append(awg)

    awg.wfmxFileFolder = "\\Users\\MSFTE\\Documents"
    awg.seqxFileFolder = "\\Users\\MSFTE\\Documents"

    # done
    station = qc.Station(*inst_list)
    return station

# Execute the script to load all instruments
if __name__ == '__main__':
    station = init_instruments()
