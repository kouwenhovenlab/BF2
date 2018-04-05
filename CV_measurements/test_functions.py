# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 17:44:20 2018

@author: gidelang
"""
fs = np.linspace(100,500e3, 11)
plt.figure('f')
plt.clf()
Rs =  np.logspace(1,4, 21)
C_Ds = np.linspace(1e-12,5e-11, 21)
for C_D in C_Ds:
    for R in Rs:
        Vs = cvm.V_out_cap_model(fs, 1e-3, C_D, 1e10 ,R,0,1e3,600e-12)
        plt.plot(Vs.real, Vs.imag, '-', label = '%s'%R)
plt.legend()
plt.figure('Rs')
plt.clf()

Vs = cvm.V_out_cap_model(100, 1e-3, 40e-12, Rs,1,0,1e3,500e-12)

plt.plot(Vs.real, Vs.imag, '.')
Vs = cvm.V_out_cap_model(500e3, 1e-3, 40e-12, Rs,1,0,1e3,500e-12)
plt.plot(Vs.real, Vs.imag, 'o', color = 'orange')