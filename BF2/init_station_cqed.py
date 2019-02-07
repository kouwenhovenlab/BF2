from importlib import reload

import qcodes as qc
import broadbean as bb
from pytopo.qctools import instruments as instools
from pytopo.qctools.instruments import create_inst, add2station

from init_station import *

# set some station configuration variables
qc.config['user']['instruments'] = {
    'awg_name': 'awg',
    'alazar_name': 'alazar',
    'default_acquisition_controller': 'post_iq_acq',
}


# init instruments lives in a function (to be able to import without loading instruments.)
def init_instruments():
    inst_list = []

    # Create all instruments

    # create and setup Alazar
    from qcodes.instrument_drivers.AlazarTech import utils
    from qcodes.instrument_drivers.AlazarTech.ATS9360 import AlazarTech_ATS9360
    alazar = instools.create_inst(
        AlazarTech_ATS9360, 'alazar', force_new_instance=True)
    inst_list.append(alazar)

    from pytopo.rf.alazar import acquisition_tools
    acquisition_tools.simple_alazar_setup_ext_trigger(256, 1, 1)

    # create and setup AWG
    from qcodes.instrument_drivers.tektronix.AWG5014 import Tektronix_AWG5014
    awg = instools.create_inst(
        Tektronix_AWG5014, 'awg',
        address='TCPIP0::169.254.183.196::inst0::INSTR',
        force_new_instance=True)
    inst_list.append(awg)

    # specific to QT2 to use the AWG. Designates the correct path for the AWG files.
    # We cannot remember the password for the AWG5208 at this setup, so John made a new account
    # that we are using here.
    #awg.wfmxFileFolder = "\\Users\\MSFTE\\Documents"
    #awg.seqxFileFolder = "\\Users\\MSFTE\\Documents"

    # RF sources
    from qcodes.instrument_drivers.rohde_schwarz.SGS100A import RohdeSchwarz_SGS100A
    LO = instools.create_inst(RohdeSchwarz_SGS100A, 'LO',
                              address="TCPIP0::169.254.29.126", force_new_instance=True)
    inst_list.append(LO)

    TWPA = instools.create_inst(RohdeSchwarz_SGS100A, 'TWPA',
                                address="TCPIP0::169.254.167.18", force_new_instance=True)
    inst_list.append(TWPA)
    # TWPA.pulsemod_source('EXT')
    # TWPA.pulsemod_state('On')

    RF = instools.create_inst(RohdeSchwarz_SGS100A, 'RF',
                              address="TCPIP0::169.254.2.20", force_new_instance=True)
    inst_list.append(RF)
    # RF.pulsemod_source('EXT')
    # RF.pulsemod_state('On')

    qubsrc = instools.create_inst(RohdeSchwarz_SGS100A, 'qubsrc',
                                  address="TCPIP0::169.254.238.193", force_new_instance=True)
    inst_list.append(qubsrc)
    # qubsrc.pulsemod_source('EXT')
    # qubsrc.pulsemod_state('On')

    # from qcodes.instrument_drivers.agilent.E8267C import E8267
    # qubsrc = instools.create_inst(
    #     E8267, 'qubsrc', address='GPIB0::19::INSTR', force_new_instance=True)
    # inst_list.append(qubsrc)

    from pytopo.rf.sources import HeterodyneSource
    hetsrc = instools.create_inst(
        HeterodyneSource, 'hetsrc', RF=RF, LO=LO, force_new_instance=True)
    inst_list.append(hetsrc)

    # add IVVI
    from qcodes.instrument_drivers.QuTech.IVVI import IVVI
    ivvi = create_inst(IVVI, 'ivvi', address='ASRL4',
                       numdacs=16, force_new_instance=True)
    inst_list.append(ivvi)

    # Yoko for flux bias line
    from qcodes.instrument_drivers.yokogawa.GS200 import GS200
    yoko = create_inst(
        GS200, 'yoko', address='TCPIP::169.254.1.9::inst0::INSTR', force_new_instance=True)
    inst_list.append(yoko)

    # Magnet
    # from qcodes.instrument_drivers.oxford.MercuryiPS_VISA import MercuryiPS
    # mgnt = create_inst(
    #     MercuryiPS, 'mgnt', address='TCPIP0::169.254.111.111::7020::SOCKET', force_new_instance=True)
    # inst_list.append(mgnt)

    from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430, AMI430_3D
    # x_mgnt = create_inst(AMI430, 'x_mgnt', address='169.254.223.86',
    #                     port=7180, has_current_rating=True, force_new_instance=True)
    # y_mgnt = create_inst(AMI430, 'y_mgnt', address='169.254.189.19',
    #                      port=7180, has_current_rating=True, force_new_instance=True)
    # inst_list.append(y_mgnt)
    # z_mgnt = create_inst(AMI430, 'z_mgnt', address='169.254.209.84',
    #                      port=7180, has_current_rating=True, force_new_instance=True)
    #mgnt = create_inst(AMI430_3D, "mgnt", x_mgnt, y_mgnt, z_mgnt, 2)
    # inst_list.append(z_mgnt)

    # function generator (to trigger the AWG)
    from qcodes.instrument_drivers.rigol.DG1062 import DG1062
    fg = create_inst(
        DG1062, 'fg', address='TCPIP0::169.254.202.99', force_new_instance=True)
    inst_list.append(fg)

    # done
    station = qc.Station(*inst_list)
    return station


# Execute the script to load all instruments
if __name__ == '__main__':
    station = init_instruments()
