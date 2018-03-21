from data_storage import datapickling as dp
import time


def set_all_zero(nmax= 64):
    for ch in mdac.channels[:nmax]:
        ch.voltage(0)
    for ch in mdac.channels[:nmax]:
        ch.dac_output('open')
        ch.bus('open')
        ch.gnd('open')
        ch.smc('open')
        ch.microd('open')

def safe_mode(ch):
    mdac.channels[ch-1].voltage(0)
    mdac.channels[ch-1].dac_output('open')
    mdac.channels[ch-1].gnd('open')
    mdac.channels[ch-1].microd('open')
    mdac.channels[ch-1].smc('open')
    mdac.channels[ch-1].bus('open')

G0 = 2*1.6e-19**2/6.6e-34

class StdMobilityDevice:
    def __init__(self, device_name, sources, drain, gate, station):
        self.station = station
        self.mdac = station['MDAC1']
        self.lockin = station['SR1']
        self.keithley_1 = station['Keith_1']
        self.sources = [self.mdac.channels[source-1] for source in sources]
        self.drain = self.mdac.channels[drain-1]
        self.gate = self.mdac.channels[gate-1]
        self.smc_state = 'close'
        self.bias_voltages = np.linspace(-10e-3, 10e-3, 11)
        self.gate_voltages = np.linspace(10e-3,0, 11)
        self.data = {}
        self.name = device_name
        self.delay = min(0.02,self.lockin.time_constant()*4)
        self.data = dp.init_data_pickle(device_name)
        self.frequency = 21
        self.AC_exc_sample = 5e-5
        self.AC_exc = 2*self.AC_exc_sample*np.sqrt(2) #account for RMS and peak-to-peak
        self.rate = 2 #V/s
        set_all_zero(12)
        
        
    def initialize(self):
        self.drain.voltage(0)
        self.drain.dac_output('open')
        self.drain.gnd('open')
        self.drain.bus('close')
        self.drain.microd('close')
        self.drain.smc(self.smc_state)
        
        
        self.gate.voltage(0)
        self.gate.limit_rate(self.rate)
        self.gate.gnd('open')
        self.gate.smc(self.smc_state)
        self.gate.microd('close')
        self.gate.dac_output('close')
        
        
        for s in self.sources:
            s.voltage(0)
            s.limit_rate(self.rate)
            s.divider('on')
            s.gnd('open')
            s.microd('close')
            s.smc('close')
            s.dac_output('open')
        self.mdac.bus('close')
        
        self.mdac.ch01.voltage(0)
        self.mdac.ch01.dac_output('open')
        self.mdac.ch01.attach_trigger()
        self.mdac.ch01.awg_sine(self.frequency,1e-3,0)
    
    def excitation_on(self, ch_no, offset = 10e-3):
        self.initialize()
        s = self.mdac.channels[ch_no-1]
        s.gnd('open')
        s.dac_output('close')
        s.smc('close')
        s.microd('close')
        s.awg_sine(self.frequency, 10*self.AC_exc, offset)
        self.current_channel = s
    def excitation_off(self):
        s = self.current_channel
        s.voltage(0)
        s.dac_output('open')
        s.smc('open')
        s.microd('open')
    
    def measure_IVbias_all(self):
        self.initialize()
        for kk,s in enumerate(self.sources):
            s.gnd('open')
            s.dac_output('close')
            s.smc('close')
            s.microd('close')
            self.measure_IVbias(s, 'source_{}'.format(kk))
            
            
            s.dac_output('open')
            s.smc('open')
            s.microd('open')
            
    def measure_IVbias(self, source, source_name):
        Vs = self.bias_voltages
        sets = self.station.snapshot()
        self.data[source_name] = {'IV':dp.init_single_trace(['V_bias (V)'], ['I_lockin (A)','Keithley_1 (A)'], len(Vs), settings = sets)}
        
        
        for kk, voltage in enumerate(Vs):
            print(kk, voltage)
            source.awg_sine(self.frequency, self.AC_exc, voltage)
            time.sleep(self.delay+2.)
            self.data[source_name]['IV']['vals'][kk,:] = voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6
        source.voltage(0)
        dp.save_data_pickle(self.data)
        
        
    def sweep_bias(self):
        
        self.drain.smc('close')
        self.drain.microd('close')
        self.drain.dac_output('close')
        
        for kk,s in enumerate(self.sources):
            s.gnd('close')
            self.measure_sweep_bias(s, 'source_{}'.format(kk))
            s.gnd('open')
            
    def measure_sweep_bias(self, source, source_name):
        Vb = np.linspace(-10e-3, 10e-3, 11)
        self.lockin.frequency(13)
        self.lockin.amplitude(1e-5)
        sets = self.station.snapshot()
        self.data[source_name] = {'IVbias':dp.init_single_trace(['V_bias (V)'], ['I_lockin (A)','Keithley_1 (A)'], len(Vb), settings = sets)}
        for kk, voltage in enumerate(Vb):
            self.lockin.sine_outdc(voltage)
            time.sleep(self.delay+1.)
            self.data[source_name]['IVbias']['vals'][kk,:] = voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6
            print(voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6)
        self.lockin.sine_outdc(0)
        dp.save_data_pickle(self.data)
                
    def sweep_gate_all(self):
        self.initialize()
        for kk, s in enumerate(self.sources):
            s.gnd('open')
            s.smc('close')
            s.microd('close')
            s.dac_output('close')
            self.measure_sweep_gate(s, 'source_{}'.format(kk))
            s.dac_output('open')
            s.microd('open')
            s.smc('open')
            
    def measure_sweep_gate(self, s, source_name):
        Vg = self.gate_voltages
        sets = self.station.snapshot()
        self.data[source_name] = {'Gate_sweep':dp.init_single_trace(['V_gate (V)'], ['Keithley (A)','I_lockin (A)', 'Conductance (G0)'], len(Vg), settings = sets)}
        s.awg_sine(self.frequency, self.AC_exc, 10e-3)
        time.sleep(20.)
        for kk,voltage in enumerate(Vg):
            self.gate.voltage(voltage)
            time.sleep(self.delay+2.)
            self.data[source_name]['Gate_sweep']['vals'][kk,:] = voltage, self.keithley_1.amplitude()/1e6, self.lockin.X()/1e6, self.lockin.X()/1e6/self.AC_exc_sample/G0
        s.awg_off()
        s.voltage(0)
        self.gate.voltage(0)
        dp.save_data_pickle(self.data)
        
        
        

class AutoIV:
    '''
    Class for doing automated IVs with the MDACs
    
    '''
    def __init__(self, station, sources, drain, gate):
        
        self.mdac = station['MDAC1']
        self.chs = self.mdac.channels
        self.rate = 2 #V/s
    def set_dac_zero(self, ch):
        ch.limit_rate(self.rate)
        ch.voltage(0)
    def set_all_dacs_zero(self):
        for ch in self.channels:
            self.set_dac_zero(ch)
            
    def set_dac_state(ch, state):
        self.set_dac_zero(ch)
        #ch.
        
    def init_all_channels(self):
        '''
        first sets all dacs to zero
        
        opens all the dac relays
        closes all gnd relays
        
        '''
        
        for ch in chs:
            '''
            do not use ramp functions yet
            '''
            
            ch.limit_rate(self.rate)
            ch.voltage(0)
        for ch in chs:
            ch.dac_output('open')
            ch.bus('open')
            ch.gnd('close')
            ch.smc('close')
            ch.microd('close')
            
    def disable_all_dacs(self):
        
        
            
            ch.ramp(0)
            
smd = StdMobilityDevice('test_device', [9], 3, 10, station)