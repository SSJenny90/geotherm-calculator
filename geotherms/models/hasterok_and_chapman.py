import numpy as np
import pandas as pd
import warnings
from geotherms.base import Geotherm
g = 10

class Hasterok(Geotherm):

    def __init__(self, layers, **kwargs):
        return super().__init__(layers, **kwargs)

    def compute(self, dz):
        """Based on Hasterok and Chapman (2011)"""
        data = super().compute(dz)

        k_ind = 0
        T = [self.surface_temp]
        alpha = [ self.empexpansivity(0, depth=0, temp=self.surface_temp, density=data['density'][0]) ]
        k = []
        for i, row in data.iterrows():

            upper_T = T[-1]

            k_ind = self.kcoeff_ind(
                upper_depth=row['z_upper'],
                lower_depth=row['z_lower'], 
                temp=upper_T, 
                density=row['density'],
                k_ind=k_ind)

            if upper_T < row['adiabat_upper']:

                tc = k[-1] if not i==0 else 3

                # If the geotherm has not yet reached the mantle adiabat
                T_bottom, k_layer = self.temp_k_converger(
                    depth = row['z_lower'], 
                    temp = upper_T, 
                    guess = upper_T + row['hf_upper']/tc*dz,
                    gamma =  row['hf_upper']*dz - 0.5*row['hp']*dz**2,
                    density = row['density_cummean'],
                    k_ind = k_ind,                    
                    )

                if T_bottom >= row['adiabat_lower']:
                    T.append(row['adiabat_lower'])
                else:
                    T.append(T_bottom)
                k.append(k_layer)           
            else: # The geotherm has reached the adiabat
                T.append(row['adiabat_lower'])
                k.append(self.thermcond(
                    depth=row['z_lower'],
                    temp = 0.5*(upper_T + self.adiabat['potential'] + (row['z_lower']+dz)*self.adiabat['gradient']),
                    density = row['density'],
                    k_ind = k_ind,
                    )[0])
                # heat_flow[j] = heat_flow[j-1]
                # HP[j] = HP[j-1]

            alpha.append(self.empexpansivity(k_ind,row['z_lower'],upper_T, density=data['density_cummean']))

        #add the new layers and return
        return data.assign(
                    T_upper = pd.Series(T[:-1])-273,
                    T_lower = pd.Series(T[1:])-273,
                    alpha_upper = alpha[:-1],
                    alpha_lower = alpha[1:],
                    conductivity = k,
                    ) 

    def transition_depth(self, temp):
        """Eq 4 from Hasterok and Chapman (2011)"""
        return 1.4209 + np.exp(3.9073e-3 * temp - 6.8041)

    def kcoeff_ind(self, upper_depth, lower_depth, temp, density, k_ind):
        zsg = (self.transition_depth(temp) - density*g*self.moho*1e-6) / (self.get_layer('mantle').density*g*1e-6)

        if upper_depth - self.moho > zsg:
            return len(self.layers)
        elif k_ind > len(self.layers):
            if self.layers[k_ind].bottom < lower_depth:
                return k_ind+1

        return k_ind

    def temp_k_converger(self, k_ind, depth, temp, guess, gamma, density, max_iter=10, tolerance=1e-3):

        def within_tolerance(result, guess):
            return abs(result - guess) < tolerance

        for _ in range(max_iter):
            k, dk = self.thermcond(depth, np.mean([guess,temp]), density, k_ind,)

            f = guess - (temp + gamma/k)
            df = 1 + gamma*dk/k**2
            result = guess - f/df

            if within_tolerance(result, guess):
                return result, k

            guess = result

        warnings.warn('thermcond() did not converge...') 

        return result, k

    def thermcond(self, depth, temp, density, k_ind):
        
        if depth < self.moho:
            P = 1e-6*density*g*depth
        else:
            P = 1e-6*(density*g*self.moho + self.get_layer('mantle').density*g*(depth - self.moho))

        k = self.k_coef(k_ind,temp)
        HP = (k[0] + k[1]/temp + k[2]*temp**2)*(1 + k[3]*P)
        dHP = (2*k[2]*temp - k[1]*temp**-2)*(1 + k[3]*P)

        return HP, dHP

    def empexpansivity(self, ia, depth, temp, density):
        a = self.acoef(ia, temp)

        if depth <= self.moho:
            P = 1e-6*density*g*depth
        else:
            P = 1e-6*(self.bulk_crustal_density()*g*self.moho + self.get_layer('mantle').density*g*(depth - self.moho))

        return (a[0] + a[1]*temp + a[2]*temp**-2)*(1 + a[3]*P)

    def k_coef(self, k_ind, temp):
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

        if k_ind <= 2 and temp > 844:
            return kb[k_ind,:]
        else:
            return ka[k_ind,:]

    def acoef(self, ia, temp):
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

        if ia <= 3 and temp > 844:
            a = ab[ia,:]
        else:
            a = aa[ia,:]

        return a


