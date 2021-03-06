import unittest

import openmdao.api as om
from openmdao.utils.assert_utils import assert_rel_error

import dymos as dm
from dymos.examples.brachistochrone.brachistochrone_ode import BrachistochroneODE


class TestTimeseriesOutput(unittest.TestCase):

    def test_timeseries_gl(self):
        p = om.Problem(model=om.Group())

        p.driver = om.ScipyOptimizeDriver()
        p.driver.declare_coloring()

        phase = dm.Phase(ode_class=BrachistochroneODE,
                         transcription=dm.GaussLobatto(num_segments=8, order=3, compressed=True))

        p.model.add_subsystem('phase0', phase)

        phase.set_time_options(fix_initial=True, duration_bounds=(.5, 10))

        phase.add_state('x', rate_source=BrachistochroneODE.states['x']['rate_source'],
                        units=BrachistochroneODE.states['x']['units'],
                        fix_initial=True, fix_final=True, solve_segments=False)

        phase.add_state('y', rate_source=BrachistochroneODE.states['y']['rate_source'],
                        units=BrachistochroneODE.states['y']['units'],
                        fix_initial=True, fix_final=True, solve_segments=False)

        phase.add_state('v', rate_source=BrachistochroneODE.states['v']['rate_source'],
                        targets=BrachistochroneODE.states['v']['targets'],
                        units=BrachistochroneODE.states['v']['units'],
                        fix_initial=True, fix_final=False, solve_segments=False)

        phase.add_control('theta', continuity=True, rate_continuity=True, opt=True,
                          targets=BrachistochroneODE.parameters['theta']['targets'],
                          units='deg', lower=0.01, upper=179.9, ref=1, ref0=0)

        phase.add_design_parameter('g', targets=BrachistochroneODE.parameters['g']['targets'],
                                   opt=True, units='m/s**2', val=9.80665)

        # Minimize time at the end of the phase
        phase.add_objective('time_phase', loc='final', scaler=10)

        p.model.linear_solver = om.DirectSolver()
        p.setup(check=True)

        p['phase0.t_initial'] = 0.0
        p['phase0.t_duration'] = 2.0

        p['phase0.states:x'] = phase.interpolate(ys=[0, 10], nodes='state_input')
        p['phase0.states:y'] = phase.interpolate(ys=[10, 5], nodes='state_input')
        p['phase0.states:v'] = phase.interpolate(ys=[0, 9.9], nodes='state_input')
        p['phase0.controls:theta'] = phase.interpolate(ys=[5, 100], nodes='control_input')
        p['phase0.design_parameters:g'] = 9.80665

        p.run_driver()

        gd = phase.options['transcription'].grid_data
        state_input_idxs = gd.subset_node_indices['state_input']
        control_input_idxs = gd.subset_node_indices['control_input']
        col_idxs = gd.subset_node_indices['col']

        assert_rel_error(self,
                         p.get_val('phase0.time'),
                         p.get_val('phase0.timeseries.time')[:, 0])

        assert_rel_error(self,
                         p.get_val('phase0.time_phase'),
                         p.get_val('phase0.timeseries.time_phase')[:, 0])

        for state in ('x', 'y', 'v'):
            assert_rel_error(self,
                             p.get_val('phase0.states:{0}'.format(state)),
                             p.get_val('phase0.timeseries.states:'
                                       '{0}'.format(state))[state_input_idxs])

            assert_rel_error(self,
                             p.get_val('phase0.state_interp.state_col:{0}'.format(state)),
                             p.get_val('phase0.timeseries.states:'
                                       '{0}'.format(state))[col_idxs])

        for control in ('theta',):
            assert_rel_error(self,
                             p.get_val('phase0.controls:{0}'.format(control)),
                             p.get_val('phase0.timeseries.controls:'
                                       '{0}'.format(control))[control_input_idxs])

        for dp in ('g',):
            for i in range(gd.subset_num_nodes['all']):
                assert_rel_error(self,
                                 p.get_val('phase0.design_parameters:{0}'.format(dp))[0, :],
                                 p.get_val('phase0.timeseries.design_parameters:{0}'.format(dp))[i])

    def test_timeseries_radau(self):
        p = om.Problem(model=om.Group())

        p.driver = om.ScipyOptimizeDriver()
        p.driver.declare_coloring()

        phase = dm.Phase(ode_class=BrachistochroneODE,
                         transcription=dm.Radau(num_segments=8, order=3, compressed=True))

        p.model.add_subsystem('phase0', phase)

        phase.set_time_options(fix_initial=True, duration_bounds=(.5, 10))

        phase.add_state('x', rate_source=BrachistochroneODE.states['x']['rate_source'],
                        units=BrachistochroneODE.states['x']['units'],
                        fix_initial=True, fix_final=True, solve_segments=False)

        phase.add_state('y', rate_source=BrachistochroneODE.states['y']['rate_source'],
                        units=BrachistochroneODE.states['y']['units'],
                        fix_initial=True, fix_final=True, solve_segments=False)

        phase.add_state('v', rate_source=BrachistochroneODE.states['v']['rate_source'],
                        targets=BrachistochroneODE.states['v']['targets'],
                        units=BrachistochroneODE.states['v']['units'],
                        fix_initial=True, fix_final=False, solve_segments=False)

        phase.add_control('theta', continuity=True, rate_continuity=True, opt=True,
                          targets=BrachistochroneODE.parameters['theta']['targets'],
                          units='deg', lower=0.01, upper=179.9, ref=1, ref0=0)

        phase.add_design_parameter('g', targets=BrachistochroneODE.parameters['g']['targets'],
                                   opt=True, units='m/s**2', val=9.80665)

        # Minimize time at the end of the phase
        phase.add_objective('time_phase', loc='final', scaler=10)

        p.model.options['assembled_jac_type'] = 'csc'
        p.model.linear_solver = om.DirectSolver()
        p.setup(check=True)

        p['phase0.t_initial'] = 0.0
        p['phase0.t_duration'] = 2.0

        p['phase0.states:x'] = phase.interpolate(ys=[0, 10], nodes='state_input')
        p['phase0.states:y'] = phase.interpolate(ys=[10, 5], nodes='state_input')
        p['phase0.states:v'] = phase.interpolate(ys=[0, 9.9], nodes='state_input')
        p['phase0.controls:theta'] = phase.interpolate(ys=[5, 100], nodes='control_input')
        p['phase0.design_parameters:g'] = 9.80665

        p.run_driver()

        gd = phase.options['transcription'].grid_data
        state_input_idxs = gd.subset_node_indices['state_input']
        control_input_idxs = gd.subset_node_indices['control_input']

        assert_rel_error(self,
                         p.get_val('phase0.time'),
                         p.get_val('phase0.timeseries.time')[:, 0])

        assert_rel_error(self,
                         p.get_val('phase0.time_phase'),
                         p.get_val('phase0.timeseries.time_phase')[:, 0])

        for state in ('x', 'y', 'v'):
            assert_rel_error(self,
                             p.get_val('phase0.states:{0}'.format(state)),
                             p.get_val('phase0.timeseries.states:'
                                       '{0}'.format(state))[state_input_idxs])

        for control in ('theta',):
            assert_rel_error(self,
                             p.get_val('phase0.controls:{0}'.format(control)),
                             p.get_val('phase0.timeseries.controls:'
                                       '{0}'.format(control))[control_input_idxs])

        for dp in ('g',):
            for i in range(gd.subset_num_nodes['all']):
                assert_rel_error(self,
                                 p.get_val('phase0.design_parameters:{0}'.format(dp))[0, :],
                                 p.get_val('phase0.timeseries.design_parameters:'
                                           '{0}'.format(dp))[i])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
