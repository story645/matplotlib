"""
catch all for categorical functions
"""

import numpy as np

import matplotlib.units as units
import matplotlib.ticker as ticker
import matplotlib.dates as dates

import pandas as pd
from pandas.core.algorithms import _get_data_algo
from pandas.compat import string_types

def register():
    """conversation with pandas dev on what specifically gets
    registered"""
    #units.registry[str] = CategoricalConverter()
    #units.registry[pandas.Categorical] = CategoricalConverter()

#can probably be reimplemented less efficiently without pandas support
import pandas.hashtable as htable
from pandas.core.algorithms import _hashtables, _get_data_algo
import pandas.core.common as com

import six

class CategoricalConverter(units.ConversionInterface):
    @staticmethod
    def convert(value, unit, axis):
        if isinstance(value, six.string_types):
            return 0

        vals = np.asarray(value, dtype='str')
        uniq = np.unique(vals)
        print (uniq)

        if 'nan' in uniq:
            vals[vals=='nan'] = - 1
            uniq = uniq[uniq!='nan']

        if '-inf' in uniq:
            vals[vals=='-inf'] = uniq.shape[0]-1
            uniq = uniq[uniq!='-inf']
    
        if 'inf' in uniq:
            vals[vals=='inf'] = uniq.shape[0] - 1
            uniq = uniq[uniq!='inf']
        
        vmap = dict(zip(uniq,list(range(uniq.shape[0])))) 
        print(vmap)
        for u in uniq:
            vals[vals==u] = vmap[u]
    
        return vals.astype('int')

        
    @staticmethod
    def axisinfo(unit, axis):
        majloc = CategoricalFormatter()
        majfmt = CategoricalLocator()
        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label=None)

    @staticmethod
    def default_units(x,axis):
        """Default unit for categories is none"""
        """but if x is a dictionary then the default is a key"""
        return None

"""Staring as thin wrapper on existing locaters/formatters
probably supposed to eventually get fleshed out to support nesting
/heirarchy
"""
class CategoricalLocator(ticker.FixedLocator):
    """Starting with fixed because all catagories should be shown
    """
    pass

class CategoricalFormatter(ticker.FixedFormatter):
    """Probably a wrapper on one of the string formatters"""
    pass



