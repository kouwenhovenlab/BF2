from importlib import reload

import qcodes as qc
import broadbean as bb
from pytopo.qctools import instruments as instools
from pytopo.qctools.instruments import create_inst, add2station

# set some station configuration variables
qc.config['core']['db_location'] = r"D:\OneDrive\BF2\Data\experiments.db"
qc.config['user']['instruments'] = {
    'awg_name' : 'awg',
    'alazar_name' : 'alazar',
    'default_acquisition_controller' : 'post_iq_acq',
    }

# simplified setting up and acquisition

def setup_alazar9360_ext_trigger(nsamples, nrecords, nbuffers, 
                                 allocated_buffers=2, 
                                 SR=2e8, int_time=None):
    """
    Simple setting up of the alazar. This is basically just setting some
    reasonable starting values when starting up the station.

    Parameters:
    -----------
    nsamples : int
        samples per record

    nrecords : int
        records per buffer

    nbuffers : int
        buffers per acquisition

    allocated_buffers : int (default: 2)
        allocated buffers

    SR : float (default: 2e8)
        sampling rate

    int_time : float (default: None)
        if not None, will try to compute number of samples that best corresponds
        to this measurement time (taking mod 128 into account, and that we need at
        least 256 samples per record). Overrrides nsamples if set.
    """
    
    alazar = qc.Instrument.find_instrument('alazar')
    
    SR = int(SR)
    if int_time is not None:
        SPR = max(256, int(int_time * SR // 128 * 128))
    else: 
        SPR = nsamples
    
    with alazar.syncing():
        alazar.clock_source('INTERNAL_CLOCK')
        alazar.sample_rate(SR)
        alazar.clock_edge('CLOCK_EDGE_RISING')
        alazar.decimation(1)
        alazar.coupling1('DC')
        alazar.coupling2('DC')
        alazar.channel_range1(0.4)
        alazar.channel_range2(0.4)
        alazar.impedance1(50)
        alazar.impedance2(50)
        alazar.trigger_source1('EXTERNAL')
        alazar.trigger_level1(128 + 5)
        alazar.external_trigger_coupling('DC')
        alazar.external_trigger_range('ETR_TTL')
        alazar.trigger_delay(0)
        # alazar.timeout_ticks(int(1e7))
        alazar.timeout_ticks(int(0))
        alazar.records_per_buffer(nrecords)
        alazar.buffers_per_acquisition(nbuffers)
        alazar.buffer_timeout(10000)
        alazar.samples_per_record(SPR)
        alazar.allocated_buffers(allocated_buffers)


# init instruments lives in a function (to be able to import without loading instruments.)
def init_instruments():
    inst_list = []

    # Create all instruments

    # create and setup Alazar
    from qcodes.instrument_drivers.AlazarTech import utils
    from qcodes.instrument_drivers.AlazarTech.ATS9360 import AlazarTech_ATS9360
    alazar = instools.create_inst(AlazarTech_ATS9360, 'alazar', force_new_instance=True)
    inst_list.append(alazar)

    setup_alazar9360_ext_trigger(256, 1, 1)
    
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
