#Main Code

#Our Modules
from modules.wec_dyn import wec_dyn as wec_dyn
from modules.time_avg_power import time_avg_power as time_avg_power
import Econ
import capy.notfinalbutworks as nfbw
import capy.geometry
import capy.hydrodyno
import capy.hydrostatics
import pandas as pd
#import capy1 

#Other packages:
import numpy as np


# Variables and Parameters:
#K_p = 100 #N/m : Proportional gain
#K_I = 10 #N/m.s : Integral Gain
#L = 100 #m : WEC spacing
#d = 0.36 #m : WEC diameter
#S= 0 # Spectral density function or array?
#k = 1000 # N/m : spring constant
#s = 10 #MPa : Nominal stiffness
#b = 10 #N.s/m : nominal damping

# Constraints --unused
#P_min = 10000 #W : minimum power Watts
#LCOE_max = 200 #$/MWhr

# Define design vector
#x=[L,d,k,s]
# Define parameters
p=[]
# Should some of these be internal variables determined during optimization? 
#...ex: control tuning parameters

#link modules together
def evaluate(dvs,p,omega,m,wave_amp):
    # dvs = [radius all wecs, spacing, damping wec 1, stiffness wec 1, damping 2, stiffness 2]
    #out1 = wec_dyn(x,p)
    #out2 = capy(x,p,out1)
    #out3 = time_avg_power(x,p,out2)
    wec_radius = dvs[0]
    wec_spacing = dvs[1]
    wec1hydro=nfbw.run(wec_radius,wec_spacing)[0]
    wec2hydro=nfbw.run(wec_radius,wec_spacing)[1]
    n_wec=2

    power_indv = [0,0]
    XI = [0,0]

    # for WEC 1
    F1,A1,B1,C1 = wec1hydro
    print(F1)
    pto_damping = dvs[2]
    pto_stiffness = dvs[3]
    XI[0] = wec_dyn(omega,F1,A1,B1,C1,m,pto_damping,pto_stiffness)
    power_indv[0] = time_avg_power(XI[0],pto_damping,omega,wave_amp)

    # for WEC 2
    F2,A2,B2,C2 = wec2hydro
    pto_damping = dvs[2]
    pto_stiffness = dvs[3]
    XI[1] = wec_dyn(omega,F2,A2,B2,C2,m,pto_damping,pto_stiffness)
    power_indv[1] = time_avg_power(XI[1],pto_damping,omega,wave_amp)

    power = sum(power_indv)
    #print("THIS IS POWER:")
    #print(power)
    Power_out,efficiency,LCOE = Econ.run([n_wec,dvs[0],dvs[1]],p,power)
    # Define order of modules. connect inputs and outputs
    return Power_out,efficiency,LCOE

# Build DoE input vectors
x1=[0,0,0,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1]
x2=[0,1,-1,0,0,-1,1,-1,1,1,-1,-1,1,1,-1,1,-1]
x3=[0,1,-1,1,1,0,0,-1,1,-1,1,1,-1,-1,1,1,-1]
x4=[0,1,-1,1,1,1,-1,0,0,-1,1,-1,1,1,-1,-1,1]
x=np.zeros([17,4])
r_doe=[2,3,4]
L_doe=[200,300,400]
k_doe=[100,200,300]
s_doe=[10,20,30]
print('DoE Conditions: ')

results = {'r_doe': [],
            'L_doe' : [], 'k_doe' : [],'s_doe' : [],'power':[],'efficiency':[],'LCOE':[]}

p = 0
omega = 1
m = 1
wave_amp = 1
for i in range(np.size(x1)):
    x[i]=[r_doe[x1[i]+1],L_doe[x2[i]+1],k_doe[x3[i]+1],s_doe[x4[i]+1]]
    Power_out,efficiency,LCOE=evaluate(x[i],p,omega,m,wave_amp)
    results['r_doe'].append(r_doe[x1[i]+1])
    results['L_doe'].append(L_doe[x2[i]+1])
    results['k_doe'].append(k_doe[x3[i]+1])
    results['s_doe'].append(s_doe[x4[i]+1])
    results['power'].append(Power_out)
    results['efficiency'].append(efficiency)
    results['LCOE'].append(LCOE)
    

#print(results)
data = pd.DataFrame.from_dict(results)
data.to_csv("data.csv")

