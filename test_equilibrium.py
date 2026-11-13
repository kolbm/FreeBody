import copy, unittest
from pathlib import Path
import app, physics
from streamlit.testing.v1 import AppTest
class EquilibriumTests(unittest.TestCase):
 def test_general_and_ramp(self):
  for mode,expected in [('General',50.),('Advanced',75.)]:
   p=copy.deepcopy(app.DEFAULT);p['mode']=mode
   if mode=='Advanced':p['forces']=app.advanced_starting_forces()
   p['physics'].update(equilibrium=True,auto_gravity=True,show_acceleration=True)
   r=app.evaluated(p)
   self.assertFalse(r.messages);self.assertAlmostEqual(r.project['forces'][2]['magnitude'],expected)
   self.assertLess(app.resultant(p)[2],1e-7);self.assertEqual(r.acceleration[2],0.)
   self.assertEqual(p['forces'][2]['magnitude'],100.)
 def test_impossible_and_conflicting(self):
  p=copy.deepcopy(app.DEFAULT);p['physics']['equilibrium']=True
  p['forces'][0]['magnitude']=150.
  r=app.evaluated(p);self.assertTrue(r.messages);self.assertNotIn(2,r.calculated)
  p['forces'][0]['magnitude']=100.;p['forces'][2]['direction']='Left'
  self.assertTrue(app.evaluated(p).messages)
  p['physics'].update(auto_gravity=True,unknown_force=1)
  self.assertTrue(any('both' in m[1] for m in app.evaluated(p).messages))
 def test_zero_unknown(self):
  p=copy.deepcopy(app.DEFAULT);p['forces'][3]['magnitude']=0.;p['physics']['equilibrium']=True
  r=app.evaluated(p);self.assertFalse(r.messages);self.assertEqual(r.project['forces'][2]['magnitude'],0.)
 def test_solver_ui(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
  a.toggle(key='0equilibrium').set_value(True).run()
  calculated=[x for x in a.number_input if '🧮' in x.label]
  self.assertAlmostEqual(calculated[0].value,50.);self.assertTrue(calculated[0].disabled)
  a.toggle(key='0components').set_value(True).run();a.toggle(key='0acceleration').set_value(True).run()
  self.assertFalse(a.exception);self.assertGreater(len(a.latex),0)
  a.toggle(key='0equilibrium').set_value(False).run()
  self.assertEqual(a.session_state['project']['forces'][2]['magnitude'],100.)
if __name__=='__main__':unittest.main()
