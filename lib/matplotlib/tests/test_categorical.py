"""Catch all for categorical functions
"""
import unittest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import nose.tools
from nose.plugins.skip import SkipTest

import six
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('agg')
import matplotlib
import matplotlib.units as munits
import matplotlib.pyplot as plt

import importlib.util
spec = importlib.util.spec_from_file_location("matplotlib.categorical",
                                              "../categorical.py")
cat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat)

class FakeAxis(object):
    def __init__(self):
        pass


class TestCategoricalConverter(unittest.TestCase):
    """
    Based on the pandas conversion and factorization tests:

    ref: /pandas/tseries/tests/test_converter.py
         /pandas/tests/test_algos.py:TestFactorize
    """

    def setUp(self):
        self.cc = cat.CategoricalConverter()
        self.axis = FakeAxis()

    def test_convert_accepts_unicode(self):
        self.axis.unit_data = {'a':0}
        c1 = self.cc.convert("a", None, self.axis)
        c2 = self.cc.convert(u"a", None, self.axis)
        self.assertEqual(c1, c2)

        c1 = self.cc.convert(["a"], None, self.axis)
        c2 = self.cc.convert([u"a"], None, self.axis)
        self.assertEqual(c1, c2)

    def test_conversion_single(self):
        act = self.cc.convert("a", None, self.axis)
        exp = 0
        self.assertEqual(act, exp)

    def test_conversion_basic(self):
        cats = ['a', 'b', 'b', 'a', 'a', 'c', 'c', 'c']
        exp = [0, 1, 1, 0, 0, 2, 2, 2]
        self.axis.unit_data = {'a':0, 'b':1, 'c':2}
        act = self.cc.convert(cats, None, self.axis)
        np.testing.assert_array_equal(act, exp)

    def test_conversion_mixed(self):
        cats = ['A', 'A', np.nan, 'B', -np.inf, 3.14, np.inf]
        exp = [1, 1, -1, 2, 3, 0, 4]
        self.axis.unit_data = {'nan':-1, '3.14':0, 'A':1, 'B':2, 
                               '-inf':3, 'inf':4}
        act = self.cc.convert(cats, None, self.axis)
        np.testing.assert_array_equal(act, exp)

    def test_axisinfo(self):
        """inspect that labeling and positions are where expected"""
        pass

    def test_default_units(self):
        """At the moment, no nesting so only unit is base level"""
        self.assertEqual(self.cc.default_units(["a"], self.axis), None)


class testCategoricalLocator(unittest.TestCase):
    def setUp(self):
        self.locs = list(range(10))

    def test_CategoricalLocator(self):
        ticks = cat.CategoricalLocator(self.locs)
        np.testing.assert_equal(ticks.tick_values(None, None), 
                                self.locs)


class testCategoricalFormatter(unittest.TestCase):
    def setUp(self):
        self.seq = ["hello", "world", "hi"]
    
    def test_CategoricalFormatter(self):
        labels = cat.CategoricalFormatter(self.seq)
        self.assertEqual(labels('a',1), "world")

class TestPlot(unittest.TestCase):
    """Use mock to check that plot calls the conversion
    interface that will eventually live in pandas"""
    @classmethod
    def setupClass(cls):
        cls.cc = munits.ConversionInterface()

        def default_units(data, axis):
            axis.unit_data = {'a': 0, 'b':1, 'c':2}
            return None

        cls.cc.convert = MagicMock(return_value = np.array([0, 1, 2, 0]))
        cls.cc.axisinfo = MagicMock(return_value=None)
        cls.cc.default_units = MagicMock(side_effect=default_units)

        if six.PY2:
            munits.registry[basestring] = cls.cc
        elif six.PY3:
            munits.registry[str] = cls.cc

    def setUp(self):
        self.x = ["a", "b", "c", "a"]
        self.y = [2, 3, 4, 5]

    def tearDown(self):
        pass

    def test_plot(self):
        fig, ax = plt.subplots(1, 1)
        l, = plt.plot(self.x, self.y)
        self.assertTrue(TestPlot.cc.convert.called)
        self.assertTrue(TestPlot.cc.axisinfo.called)
        self.assertTrue(TestPlot.cc.default_units.called)
