import numpy as np
import pandas as pd
from itertools import zip_longest
import warnings

rho_crust = 2850 #rhoc
rho_mantle = 3340 #rhom
g = 10

def geotherm(surface_hf,max_depth,dz,layers,layer_hp):
    """Based on Hasterok and Chapman (2011)"""

    # Temperature conditions
    T0 = 0 + 273     # degC      Surface Temperature
    Ta0 = 1300 + 273 # degC      Adiabatic Potential
    dT = 0.3       # degC/km   Adiabatic Gradient
    moho = layers[-1]

    depths = np.arange(0,max_depth+dz,dz)
    # df = pd.DataFrame(depth, columns=['depth'])
    surfaces = pd.DataFrame(dict(
        depth = depths,
        adiabat = Ta0 + depths*dT
        ))

    intervals = pd.DataFrame(dict(
        z_upper = depths[:-1],
        z_lower = depths[1:],
        adiabat = surfaces['adiabat'].iloc[1:],
        ))

    # assign categories to each layer
    intervals['layer'] = pd.cut(intervals['z_lower'],
        bins = [0] + layers + [max_depth],
        include_lowest = True,
        labels = ['upper', 'middle', 'lower', 'mantle']
        )

    # assign heat production
    intervals['hp'] = intervals.layer.map(layer_hp)

    #calculate basal heat flow for each interval
    intervals['hf_lower'] = surface_hf - (intervals['hp'].cumsum() * dz)
    intervals['hf_upper'] = intervals['hf_lower'].shift(1)
    intervals['hf_upper'].iat[0] = surface_hf

    # Compute Heat Flow
    surfaces['hf'] = (
        pd.Series([surface_hf])
        .append(surface_hf - (intervals['hp'].cumsum() * dz), ignore_index=True)
    )

    # Compute Temperature
    ik = 0
    T = [T0]
    alpha = [ empexpansivity(0,moho,0,T0) ]
    k = []
    for i, row in intervals.iterrows():
        zsg = (1.4209 + np.exp(3.9073e-3*T[-1] - 6.8041) - rho_crust*g*moho*1e-6) /(rho_mantle*g*1e-6)

        if row['z_upper'] - moho > zsg:
            ik = len(layers) + 1
        elif ik > len(layers):
            if layers[ik] < row['z_lower']:
                ik+=1

        if not T[-1] > row['adiabat']:
            T_bottom, k_layer = tccomp(
                ik, 
                zmoho = moho, 
                depth = row['z_lower'], 
                dz = dz, 
                tau = T[-1], 
                hf = row['hf_upper'], 
                tc = k[-1] if not i==1 else 3, 
                hp = row['hp'])

            T.append(T_bottom)
            k.append(k_layer)
            # alpha.append(empexpansivity(ik,moho,row['z_lower'],T[-1]))

        # If the geotherm has reached the adiabat
        else:
            T.append(row['adiabat'])
            k.append(thermcond(
                ik,
                moho,
                row['z_lower'],
                0.5*(T[-1] + Ta0 + (row['z_lower']+dz)*dT)
                )[0])
            # heat_flow[j] = heat_flow[j-1]
            # HP[j] = HP[j-1]

        alpha.append(empexpansivity(ik,moho,row['z_lower'],T[-1]))

    intervals['T_upper'] = pd.Series(T[:-1])-273
    intervals['T_lower'] =pd.Series(T[1:])-273

    intervals['alpha_upper'] = alpha[:-1]
    intervals['alpha_lower'] = alpha[1:]
    intervals['conductivity'] = k

    return intervals 
    # T-273, depths, k, HP, heat_flow, alpha, il

def tccomp(ik,zmoho,depth,dz,tau,hf,tc,hp):
    # Starting temperature guess
    dT0 = hf/tc*dz
    guess = tau + dT0

    c = 1
    tolerance = 1e-3
    maxit = 10

    gamma = (hf*dz - 0.5*hp*dz**2)

    while True:
        # thermal conductivity
        k, dk = thermcond(ik,zmoho,depth,0.5*(guess+tau))
        f = guess - (tau + gamma/k)
        df = 1 + gamma*dk/k**2
        result = guess - f/df

        # break if result within specified tolerance
        if abs(result - guess) < tolerance:
            break

        if c > maxit:
            warnings.warn('TCCOMP did not converge...') 
            break

        # New dT becomes guess dT0
        guess = result
        c+=1

    # Compute k
    k = thermcond(ik,zmoho,depth,0.5*(guess+tau))

    return guess, k[0]

def thermcond(ik,zmoho,z,T):
    k = kcoef(ik,T)
    if z < zmoho:
        P = 1e-6*rho_crust*g*z
    else:
        P = 1e-6*(rho_crust*g*zmoho + rho_mantle*g*(z - zmoho))


    HP = (k[0] + k[1]/T + k[2]*T**2)*(1 + k[3]*P)
    dHP = (2*k[2]*T - k[1]*T**-2)*(1 + k[3]*P)

    return HP, dHP

def kcoef(ik,T):
    ka = np.array([
        [1.496,  398.84,  4.573e-7, 0.0950],
        [1.733,  194.59,  2.906e-7, 0.0788],
        [1.723,  219.88,  1.705e-7, 0.0520],
        [2.271,  681.12, -1.259e-7, 0.0399],
        [2.371,  669.40, -1.288e-7, 0.0384]])

    kb = np.array([
        [2.964, -495.29,  0.866e-7, 0.0692],
        [2.717, -398.93,  0.032e-7, 0.0652],
        [2.320,  -96.98, -0.981e-7, 0.0463],])

    if ik <= 2 and T > 844:
        k = kb[ik,:]
    else:
        k = ka[ik,:]

    return k

def empexpansivity(ia,zmoho,z,T):
    a = acoef(ia,T)
    zmoho = 39

    if z < zmoho:
        P = 1e-6*rho_crust*g*z
    else:
        P = 1e-6*(rho_crust*g*zmoho + rho_mantle*g*(z - zmoho))

    alpha = (a[0] + a[1]*T + a[2]*T**-2)*(1 + a[3]*P)
    return alpha

def acoef(ia,T):
    aa = np.array([
        [2.355e-5, 3.208e-8, -0.7938, -0.1193],
        [2.020e-5, 2.149e-8, -0.6315, -0.1059],
        [2.198e-5, 0.921e-8, -0.1820, -0.0626],
        [3.036e-5, 0.925e-8, -0.2730, -0.0421],
        [3.026e-5, 0.906e-8, -0.3116, -0.0408],])

    ab = np.array([
        [1.741e-5, 0.500e-8, -0.3094, -0.0778],
        [1.663e-5, 0.602e-8, -0.3364, -0.0745],
        [2.134e-5, 0.711e-8, -0.1177, -0.0563]])

    if ia <= 3 and T > 844:
        a = ab[ia,:]
    else:
        a = aa[ia,:]

    return a

if __name__ == '__main__':
    geotherm(65,150,2,[16,24,40],
    dict(
        upper=1.0563,
        middle=0.4,
        lower=0.4,
        mantle=0.02
        ))
