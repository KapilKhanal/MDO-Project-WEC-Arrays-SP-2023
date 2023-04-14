# Contains Functions to complets A3b
import scipy.optimize as scipy_opt
import numpy as np
import matplotlib.pyplot as plt

# import model for what you want to do...
#import modules.n2.model_2WECs as model

import modules.model_4WECs as model

'''def distance_check(wecx,wecy,r):
    n = len(wecx)
    for i in range(n):
        for j in range(i+1,n):
            d = ((wecx[i]-wecx[j])**2 + (wecy[i]-wecy[j])**2)**(1/2)
            if d<10*r:
                return True
    return False'''

def objective(x,*args):         #   Calculates LCOE
    p = args
    '''nwec = p[3]
    wecx = np.zeros(nwec)
    wecy = np.zeros(nwec)
    for i in range(nwec):
        wecx[i] = x[1+i*3]
        wecy[i] = x[2+i*3]
    if distance_check(wecx,wecy,x[0]):
        LCOE = np.Infinity
    else:'''
    Power_out,efficiency,LCOE = model.run(x,p)  #   runs the model
    print(f"This is LCOE {LCOE}")
    return LCOE

def objective1(x,args):         #   Calculates LCOE
    p = args
    '''nwec = p[3]
    wecx = np.zeros(nwec)
    wecy = np.zeros(nwec)
    for i in range(nwec):
        wecx[i] = x[1+i*3]
        wecy[i] = x[2+i*3]
    if distance_check(wecx,wecy,x[0]):
        LCOE = np.Infinity
    else:'''
    Power_out,efficiency,LCOE = model.run(x,p)  #   runs the model
    print(f"This is LCOE {LCOE}")
    return LCOE

def gradient_method(x0,p,bnds,opt):     #   Gradient Method Search Algorithm
    history = []
    def callback(x,p):
        fobj = objective1(x,p)
        history.append(fobj)
    res = scipy_opt.minimize(objective1, x0, method='slsqp', args=p, bounds=bnds, options=opt)
    print("The values at each iteration")
    
    plt.plot(range(len(history)),history)
    plt.show()
    plt.savefig('convergence.png')
    return res.x

def heuristic_method(p,bnds,opt):       #   GA method search algorithm
    res = scipy_opt.differential_evolution(objective, bounds=bnds, args=p)
    return res.x