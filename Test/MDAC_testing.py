from data_storage import datapickling as dp
import time
def set_zero_supersafe():
    lockin.set_sine_outdc(0)
    set_all_zero()

def set_all_zero(nmax= 64):
    for ch in mdac.channels[:nmax]:
        ch.voltage(0)
    for ch in mdac.channels[:nmax]:
        ch.dac_output('open')
        ch.bus('open')
        ch.gnd('open')
        ch.smc('open')
        ch.microd('open')
        ch.divider('off')

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
        self.keithley_2 = station['Keith_2']
        self.sources = [self.mdac.channels[source-1] for source in sources]
        self.drain = self.mdac.channels[drain-1]
        self.gate = self.mdac.channels[gate-1]
        self.smc_state = 'close'
        self.bias_voltages = np.linspace(-1e-3, 1e-3, 11)
        self.gate_voltages = np.linspace(0,-4, 30)
        self.data = {}
        self.last_data = {}
        self.name = device_name
        self.delay = min(0.02,self.lockin.time_constant()*4)
        self.data = dp.init_data_pickle(device_name)
        self.multiplier_bias = 1e-3  #ISO-in attenuation + voltage source scale
        self.multiplier_gate = 1
        self.frequency = 21
        self.DC_exc_sample = 1e-3
        self.DC_exc = self.DC_exc_sample/self.multiplier_bias
        self.AC_exc_sample = 1e-5
        self.AC_exc = self.AC_exc_sample/self.multiplier_bias
        self.AC_exc_zero = 1e-8
        #self.AC_exc = 2*self.AC_exc_sample*np.sqrt(2) #account for RMS and peak-to-peak
        self.rate = 2 #V/s
        set_all_zero()
    
    
    def check_beepR(self):
        self.drain.voltage(0)
        self.drain.dac_output('open')
        self.drain.gnd('close')
        self.drain.bus('open')
        self.drain.microd('close')     
        self.drain.smc('open')     
        
        self.gate.voltage(0)
        self.gate.limit_rate(self.rate)
        self.gate.gnd('open')
        self.gate.smc('close')       
        self.gate.microd('close')    
        self.gate.dac_output('open')
        
        for s in self.sources:
            s.voltage(0)
            s.limit_rate(self.rate)
            s.divider('off')
            s.gnd('open')
            s.microd('close')  
            s.smc('close')     
            s.dac_output('open')
        
    def initialize(self):
        self.drain.voltage(0)
        self.drain.dac_output('open')
        self.drain.gnd('open')
        self.drain.bus('close')
        self.drain.microd('close')     #open for RT tests, close for sample excitation in the fridge
        self.drain.smc('open')         #close for RT tests, open for sample excitation in the fridge
        
        
        self.gate.voltage(0)
        self.gate.limit_rate(self.rate)
        self.gate.gnd('open')
        self.gate.smc('open')       #close for RT tests, open for sample excitation in the fridge
        self.gate.microd('close')    #open for RT tests, close for sample excitation in the fridge
        self.gate.dac_output('close')
        
        
        for s in self.sources:
            s.voltage(0)
            s.limit_rate(self.rate)
            s.divider('off')
            s.gnd('open')
            s.microd('close')  #open for RT tests, close for sample excitation in the fridge
            s.smc('open')     #close for RT tests, open for sample excitation in the fridge
            s.dac_output('open')
            
        self.mdac.bus('close')
        
#        self.mdac.ch01.voltage(0)
#        self.mdac.ch01.dac_output('open')
#        self.mdac.ch01.attach_trigger()
#        self.mdac.ch01.awg_sine(self.frequency,1e-3,0)
    
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
            s.smc('close')    #close for RT tests, open for sample excitation in the fridge
            s.microd('close') #open for RT tests, close for sample excitation in the fridge
            self.measure_IVbias(s, 'source_{}'.format(kk))
            
            
            s.dac_output('open')
            s.smc('open')
            s.microd('open')
            
    def measure_IVbias(self, source, source_name):
        '''
        use MDAC DAC to generate signal (bypasses IVVI)
        '''
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
        
        
    def meas_float_lockin(self, bias_check = True):
        self.initialize()
        self.drain.smc('open')    #close for RT tests, open for sample excitation in the fridge
        self.drain.microd('close') #open for RT tests, close for sample excitation in the fridge
        self.drain.dac_output('open')
        
        for kk,s in enumerate(self.sources):
            s.gnd('close')
            if bias_check:
                self.sweep_bias(s, 'source_{}'.format(kk))
                s.gnd('open')
            else:
                self.sweep_gate(s, 'source_{}'.format(kk))
                s.gnd('open')
    
            
    def sweep_bias(self, source, source_name):
        '''
        use lockin to generate signal (uses IVVI)
        '''
        
        Vb = self.bias_voltages/self.multiplier_bias
        self.lockin.frequency(self.frequency)
        self.lockin.amplitude(self.AC_exc)
        sets = self.station.snapshot()
        self.data[source_name] = {'IVbias':dp.init_single_trace(['V_bias (V)'], ['I_lockin (A)','Keithley_1 (A)'], len(Vb), settings = sets)}
        for kk, voltage in enumerate(Vb):
            self.lockin.sine_outdc(voltage)
            time.sleep(self.delay+1.)
            self.data[source_name]['IVbias']['vals'][kk,:] = voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6
            print(voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6)
        self.lockin.sine_outdc(0)
        self.lockin.amplitude(self.AC_exc_zero)
        dp.save_data_pickle(self.data)
        self.last_data = self.data[source_name]['IVbias']
        
    def sweep_gate(self, source, source_name):
        Vg = self.gate_voltages/self.multiplier_gate
        self.lockin.frequency(self.frequency)
        self.lockin.amplitude(self.AC_exc)
        self.lockin.sine_outdc(self.DC_exc)
        sets = self.station.snapshot()
        self.data[source_name] = {'IVgate':dp.init_single_trace(['V_gate (V)'], ['I_lockin (A)','Keithley_1 (A)','Keithley_2_Leakage (A)'], len(Vg), settings = sets)}
        for kk, voltage in enumerate(Vg):
            self.gate.voltage(voltage)
            time.sleep(self.delay+1.)
            self.data[source_name]['IVgate']['vals'][kk,:] = voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6, self.keithley_2.amplitude()/1e6
            #print(voltage, self.lockin.X(), self.keithley_1.amplitude()/1e6)
        self.gate.voltage(0)
        self.lockin.sine_outdc(0)
        self.lockin.amplitude(self.AC_exc_zero)
        dp.save_data_pickle(self.data)
        self.last_data = self.data[source_name]['IVgate']
                
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
            
#smd = StdMobilityDevice('test_device', [9], 3, 10, station)
#sample = StdMobilityDevice('Test_sample', [43], 46, 2, station)
sample2 = StdMobilityDevice('Test_sample', 
                            [27],  #sources 
                            10, # drain
                            28, # gate
                            station)