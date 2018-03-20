from __future__ import print_function, absolute_import, division

import os
import unittest
from numpy.testing import assert_almost_equal

from parameterized import parameterized
from itertools import product

import dymos.examples.brachistochrone.ex_brachistochrone as ex_brachistochrone

from openmdao.utils.general_utils import set_pyoptsparse_opt
OPT, OPTIMIZER = set_pyoptsparse_opt('SNOPT')


class TestBrachistochroneExample(unittest.TestCase):

    def tearDown(self):
        for filename in ['phase0_sim.db', 'brachistochrone_sim.db']:
            if os.path.exists(filename):
                os.remove(filename)

    def run_asserts(self, p, transcription):
        t_initial = p.model.phase0.get_values('time')[0]
        tf = p.model.phase0.get_values('time')[-1]

        x0 = p.model.phase0.get_values('x')[0]
        xf = p.model.phase0.get_values('x')[-1]

        y0 = p.model.phase0.get_values('y')[0]
        yf = p.model.phase0.get_values('y')[-1]

        v0 = p.model.phase0.get_values('v')[0]
        vf = p.model.phase0.get_values('v')[-1]

        thetaf = p.model.phase0.get_values('theta')[-1]

        assert_almost_equal(t_initial, 0.0)
        assert_almost_equal(x0, 0.0)
        assert_almost_equal(y0, 10.0)
        assert_almost_equal(v0, 0.0)

        assert_almost_equal(tf, 1.8016, decimal=4)
        assert_almost_equal(xf, 10.0, decimal=3)
        assert_almost_equal(yf, 5.0, decimal=3)
        assert_almost_equal(vf, 9.902, decimal=3)

        if transcription != 'radau-ps':
            assert_almost_equal(thetaf, 100.12, decimal=0)

    @parameterized.expand(['gauss-lobatto', 'radau-ps'])
    def test_ex_brachistochrone(self, transcription='radau-ps'):
        ex_brachistochrone.SHOW_PLOTS = False
        p = ex_brachistochrone.brachistochrone_min_time(transcription=transcription)
        self.run_asserts(p, transcription)
        self.tearDown()

    @parameterized.expand(product(
        ['optimizer-based', 'solver-based', 'time-marching'],
        ['RK4'],
    ))
    @unittest.skip('GLM only works with SNOPT at the moment')
    # @unittest.skipIf(OPTIMIZER is None, 'GLM only works with SNOPT at the moment')
    def test_ex_brachistochrone_glm(self, glm_formulation='solver-based', glm_integrator='RK4'):
        transcription = 'glm'
        ex_brachistochrone.OPTIMIZER = 'SNOPT'
        ex_brachistochrone.SHOW_PLOTS = False
        p = ex_brachistochrone.brachistochrone_min_time(
            transcription=transcription, run_driver=True,
            glm_formulation=glm_formulation, glm_integrator=glm_integrator,
        )
        self.run_asserts(p, transcription)
        self.tearDown()
