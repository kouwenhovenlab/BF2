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

    # Yoko for flux bias line
    # from qcodes.instrument_drivers.yokogawa.GS200 import GS200
    # yoko = create_inst(
    #     GS200, 'yoko', address='TCPIP::169.254.1.9::inst0::INSTR', force_new_instance=True)
    # inst_list.append(yoko)

    # VNA
    from qcodes.instrument_drivers.rohde_schwarz.ZNB import ZNB
    vna = create_inst(
        ZNB, 'vna', address='TCPIP::169.254.82.128::inst0::INSTR', force_new_instance=True)
    # ZNB, 'vna', address='TCPIP::169.254.62.18::inst0::INSTR', force_new_instance=True)
    inst_list.append(vna)

    # RF sources
    from qcodes.instrument_drivers.rohde_schwarz.SGS100A import RohdeSchwarz_SGS100A
    # LO = instools.create_inst(RohdeSchwarz_SGS100A, 'LO',
    #                           address="TCPIP0::169.254.2.20", force_new_instance=True)
    # inst_list.append(LO)

    # TWPA = instools.create_inst(RohdeSchwarz_SGS100A, 'TWPA',
    #                             address="TCPIP0::169.254.167.18", force_new_instance=True)
    # inst_list.append(TWPA)
    # TWPA.pulsemod_source('EXT')
    # TWPA.pulsemod_state('On')

    # RF = instools.create_inst(RohdeSchwarz_SGS100A, 'RF',
    #                           address="TCPIP0::169.254.231.38", force_new_instance=True)
    # inst_list.append(RF)

    # Magnet

    # from qcodes.instrument_drivers.QuTech.IVVI import IVVI
    # ivvi = create_inst(IVVI, 'ivvi', address='ASRL4',
    #                    numdacs=16, force_new_instance=True)
    # inst_list.append(ivvi)

    # from qcodes.instrument_drivers.oxford.MercuryiPS_VISA import MercuryiPS
    # mgnt = create_inst(
    #     MercuryiPS, 'mgnt', address='TCPIP0::169.254.111.111::7020::SOCKET', force_new_instance=True)
    # inst_list.append(mgnt)

    # from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430, AMI430_3D
    # x_mgnt = create_inst(AMI430, 'x_mgnt', address='169.254.147.115',
    #                      port=7180, has_current_rating=True, force_new_instance=True)
    # y_mgnt = create_inst(AMI430, 'y_mgnt', address='169.254.189.19',
    #                      port=7180, has_current_rating=True, force_new_instance=True)
    # z_mgnt = create_inst(AMI430, 'z_mgnt', address='169.254.209.84',
    #                      port=7180, has_current_rating=True, force_new_instance=True)
    # mgnt = create_inst(AMI430_3D, "mgnt", x_mgnt, y_mgnt, z_mgnt, 2)
    # inst_list.append(mgnt)

    # done
    station = qc.Station(*inst_list)
    return station


# Execute the script to load all instruments
if __name__ == '__main__':
    station = init_instruments()
