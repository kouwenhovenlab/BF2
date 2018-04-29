### Instrument settings
import qcodes as qc


### Init instruments
from pytopo.qctools import instruments as instools
from pytopo.rf.alazar_acquisition import RawAcqCtl, DemodAcqCtl, DemodRelAcqCtl, IQRelAcqCtl, IQAcqCtl

inst_list = []

from qcodes.instrument_drivers.AlazarTech.ATS9360 import AlazarTech_ATS9360
alazar = instools.create_inst(AlazarTech_ATS9360, 'alazar')
inst_list.append(alazar)

raw_acq = instools.create_inst(RawAcqCtl, 'raw_acq', 'alazar', force_new_instance=True)
inst_list.append(raw_acq)

demod_acq = instools.create_inst(DemodAcqCtl, 'demod_acq', 'alazar', force_new_instance=True)
inst_list.append(demod_acq)

demodrel_acq = instools.create_inst(DemodRelAcqCtl, 'rel_acq', 'alazar', force_new_instance=True)
inst_list.append(demodrel_acq)

iqrel_acq = instools.create_inst(IQRelAcqCtl, 'iqrel_acq', 'alazar', force_new_instance=True)
inst_list.append(iqrel_acq)

iq_acq = instools.create_inst(IQAcqCtl, 'iq_acq', 'alazar', force_new_instance=True)
inst_list.append(iq_acq)

from qcodes.instrument_drivers.tektronix.AWG5014 import Tektronix_AWG5014
awg5014 = instools.create_inst(Tektronix_AWG5014, 'awg5014', address="TCPIP0::169.254.220.147::inst0::INSTR")
inst_list.append(awg5014)

from qcodes.instrument_drivers.rohde_schwarz.SGS100A import RohdeSchwarz_SGS100A
LO = instools.create_inst(RohdeSchwarz_SGS100A, 'RF', address="TCPIP0::169.254.2.20")
inst_list.append(LO)
RF = instools.create_inst(RohdeSchwarz_SGS100A, 'LO', address="TCPIP0::169.254.231.38")
inst_list.append(RF)
qubit_gen = instools.create_inst(RohdeSchwarz_SGS100A, 'qubit_gen', address="TCPIP0::169.254.167.18")
inst_list.append(qubit_gen)

station = qc.Station(*inst_list)
