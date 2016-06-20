"""This will be factored out into different functions (and possibly libraries) 
but I wanted to start with a catch all place for simplicity's sake

#testing implemenation of native (registered) support for pandas 
catagorical dataframe objects 
"""

import unittest

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
spec = importlib.util.spec_from_file_location("matplotlib.categorical", 
                                              "../categorical.py")
cat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat)

import pandas as pd
import pandas.util.testing as tm

def checkdep_pandas():
    return importlib.util.find_spec("pandas") is None

#@knownfailureif(checkdep_pandas())
class TestCategoricalConverter(unittest.TestCase):
    """
    Based on the pandas conversion and factorization tests:
    
    ref: /pandas/tseries/tests/test_converter.py
         /pandas/tests/test_algos.py:TestFactorize
    """

    def setUp(self):
        self.cc = cat.CategoricalConverter()
        class Axis(object):
            pass
        self.axis = Axis()
    
    def test_convert_accepts_unicode(self):
        c1 = self.cc.convert("a", None, None)
        c2 = self.cc.convert(u"a", None, None)
        self.assertEqual(c1, c2)
        
        c1 = self.cc.convert(["a"], None, None)
        c2 = self.cc.convert([u"a"], None, None)
        self.assertEqual(c1, c2)
        
    def test_conversion_single(self):
        act = self.cc.convert("a", None, None)
        exp = 0
        self.assertEqual(act, exp)

    def test_conversion_basic(self):
        cats = ['a', 'b', 'b', 'a', 'a', 'c', 'c','c']
        exp = [0, 1, 1, 0, 0, 2, 2, 2]
        act = self.cc.convert(cats, None, None)
        np.testing.assert_array_equal(act, exp)

           
    def test_conversion_mixed(self):
        # doc example reshaping.rst
        cats = ['A', 'A', np.nan, 'B', -np.inf, 3.14, np.inf]       
        exp = [1, 1, -1, 2, 4, 0, 3]
        act = self.cc.convert(cats, None, None)
        np.testing.assert_array_equal(act, exp)

    def test_axisinfo(self):
        """inspect that labeling and positions are where expected"""
        pass



@SkipTest
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
        nose.tools.assertEqual(cc.convert.called)
        nose.tools.assertEqual(cc.axisinfo.called)
        nose.tools.assertEqual(cc.default_units.called)
        
        

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
