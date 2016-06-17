"""This will be factored out into different functions (and possibly libraries) 
but I wanted to start with a catch all place for simplicity's sake

#testing implemenation of native (registered) support for pandas 
catagorical dataframe objects 
"""

try:
    # mock in python 3.3+
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import nose.tools
from nose.plugins.skip import SkipTest


import numpy as np

import matplotlib
matplotlib.use('Agg') #backend framework error
from matplotlib.testing.decorators import knownfailureif
import matplotlib.units as munits

#scaffolding, will be taken out 
import importlib.util
spec = importlib.util.spec_from_file_location("matplotlib.categorical", "../categorical.py")
cat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat)

import pandas as pd
import pandas.util.testing as tm

def checkdep_pandas():
    return importlib.util.find_spec("pandas") is None


@knownfailureif(checkdep_pandas())
class TestCategoricalConverter(tm.TestCase):
#ref: https://github.com/pydata/pandas/blob/master/pandas/tseries/tests/test_converter.py
    def setUp(self):
        self.cc = cat.CategoricalConverter()
        class Axis(object):
            self.axis = Axis()
    
    def test_convert_accepts_unicode(self):
        c1 = self.cc.convert(["a","b","c"], None, self.axis)
        #unicode version

    def test_conversion(self):
        #conversion only works on one axis at a time
        pass
    
    



class TestPlotting(object):
    """Use mock to check that plot calls the conversion 
    interface that will eventually live in pandas"""
    @classmethod
    def setup_class(cls):
        cc = munits.CategoricalInterface()
        
        def convert(value, unit, axis):
            #figure out what actually needs to be
            #pulled out
            return cat.convert(value, unit, axis)
        
        cc.convert = MagicMock(side_effect=convert)
        cc.axisinfo = MagicMock(return_value=None)
        cc.default_units - MagicMock(return_value=None)

        munits.registry[pd.DataFrame] = cc
    
    def setup(self):
        self.df = df = pd.DataFrame({"A":["a","b","c","a"],
                                     "B":["d","d", "e","g"]})
        

    def teardown(self):
        pass
    def test_plot(self):
        fig, ax = plt.subplots(1,1)
        l, = plt.plot(self.df)
        nose.tools.assert(cc.convert.called)
        nose.tools.assert(cc.axisinfo.called)
        nose.tools.assert(cc.default_units.called)
        
        

@knownfailureif(checkdep_pandas())
def test_factorize():
    index, labels = cat.factorize([1,1,2,2,1,1,4,5,6])
    np.testing.assert_equal(index, np.array([0, 0, 1, 1, 0, 0, 2, 3, 4]))
    np.testing.assert_equal(labels, np.array([1, 2, 4, 5, 6]))

@SkipTest
def test_CategoricalLocator():
    loc = cat.CategoricalLocator()
    

@SkipTest
def test_CategoricalFormatter():
    class FakeAxis(object):
        """Allow Formatter to be called without having a "full" plot set up."""
        def __init__(self, vmin=1, vmax=10):
            self.vmin = vmin
            self.vmax = vmax

        def get_view_interval(self):
            return self.vmin, self.vmax
    
    formatter = cat.CategoricalFormatter()
    formatter.axis = FakeAxis()
