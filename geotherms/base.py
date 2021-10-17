import numpy as np
import pandas as pd
from collections import OrderedDict

class Layer():

    def __init__(self, label='', top=0, bottom=None, heat_production=1.0563, density=2850):
        self.label = label
        self.top = top
        self.bottom = bottom
        self.thickness = bottom-top
        self.heat_production = heat_production
        self.density = density

    def __str__(self):
        return "<br>".join([f"{k}: {v}" for k,v in self.to_dict().items()])

    def to_dict(self):
        return {prop:getattr(self,prop) for prop in ['top','bottom','thickness','heat_production','density']}

class Geotherm():
    
    def __init__(self, layers, surface_hf=65, surface_temp=273, adiabat={}):
        self.layers=layers
        self._layers = self._layers_dict()
        self.surface_hf = surface_hf
        self.surface_temp = surface_temp

        self.adiabat = self.get_adiabat(adiabat)
        self.moho = self.get_moho_depth()
        self.max_depth = self.get_max_model_depth()
        
    def get_moho_depth(self):
        mantle = [l.top for l in self.layers if l.label.lower() == 'mantle'][0]
        return mantle

    def get_max_model_depth(self):
        return self.layers[-1].bottom

    def get_adiabat(self,adiabat):
        return dict(
            potential = adiabat.get('potential',1573),
            gradient = adiabat.get('gradient',0.3),
        )

    def _layers_dict(self):
        return OrderedDict({layer.label:layer for layer in self.layers})

    def get_layer_values(self,prop):
        return OrderedDict({layer.label:getattr(layer,prop) for layer in self.layers})

    def get_layer(self, label):
        return self._layers.get(label,None)

    def get_layer_by_depth(self, depth):
        return [layer for layer in self.layers if layer.top <= depth < layer.bottom][0]

    def bulk_crustal_density(self):
        dens = self.get_layer_values('density')
        return sum([v for k,v in dens.items() if k != "mantle"]) / (len(dens)-1)


    def compute(self,dz):
        depths = np.arange(0, self.max_depth+dz, dz)
        adiabat = self.adiabat['potential'] + depths*self.adiabat['gradient']
        data = pd.DataFrame(dict(
            z_upper = depths[:-1],
            z_lower = depths[1:],
            adiabat_upper = adiabat[:-1],
            adiabat_lower = adiabat[1:],
            ))

        # assign categories to each layer
        data['layer'] = pd.cut(data['z_lower'],
            bins = [0] + list(self.get_layer_values('bottom').values()),
            include_lowest = True,
            labels = self.get_layer_values('label').keys()
            )

        # assign heat production
        data['hp'] = data['layer'].map(self.get_layer_values('heat_production'))

        #map each layer density value to correct depths in dataframe
        data['density'] = data['layer'].map(self.get_layer_values('density'))

        #cumulative mean density - average density of current row and above
        data['density_cummean'] = data['density'].cumsum() / range(1,len(data)+1)

        #calculate basal heat flow for each interval
        data['hf_lower'] = self.surface_hf - (data['hp'].cumsum() * dz)
        data['hf_upper'] = data['hf_lower'].shift(1)
        data['hf_upper'].iat[0] = self.surface_hf
        return data

