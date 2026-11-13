import copy, math, unittest
from pathlib import Path
import app, physics
from streamlit.testing.v1 import AppTest
class FrictionTests(unittest.TestCase):
 def project(self,mode='General'):
  p=copy.deepcopy(app.DEFAULT);p['mode']=mode
  if mode=='Advanced':p['forces']=app.advanced_starting_forces()
  p['physics'].update(auto_gravity=True,auto_normal=True,auto_friction=True)
  return p
 def test_kinetic_and_static(self):
  p=self.project();p['physics']['motion']='Right'
  r=app.evaluated(p);self.assertFalse(r.messages);self.assertAlmostEqual(r.project['forces'][3]['magnitude'],25.)
  self.assertAlmostEqual(app.force_angle(r.project,r.project['forces'][3]),180.)
  p['physics']['motion']='Left';r=app.evaluated(p);self.assertAlmostEqual(app.force_angle(r.project,r.project['forces'][3]),0.)
  p['physics']['motion']='Not moving';p['forces'][2]['magnitude']=10.
  r=app.evaluated(p);self.assertFalse(r.messages);self.assertAlmostEqual(r.project['forces'][3]['magnitude'],10.)
  self.assertLess(app.resultant(p)[2],1e-7)
  p['forces'][2]['magnitude']=100.;r=app.evaluated(p)
  self.assertTrue(any('limit exceeded' in m[1] for m in r.messages));self.assertAlmostEqual(r.project['forces'][3]['magnitude'],25.)
  self.assertAlmostEqual(app.resultant(p)[2],75.)
 def test_ramp_motion_and_normal(self):
  for slope,motion,expected in [(30.,'Up the surface of the ramp',210.),(30.,'Down the surface of the ramp',30.),(-30.,'Up the surface of the ramp',330.),(-30.,'Down the surface of the ramp',150.)]:
   p=self.project('Advanced');p.update(inclined_angle=slope);p['physics']['motion']=motion
   r=app.evaluated(p);self.assertFalse(r.messages)
   self.assertAlmostEqual(app.force_angle(r.project,r.project['forces'][3]),expected)
   self.assertAlmostEqual(r.project['forces'][1]['magnitude'],100*math.cos(math.radians(30)))
  p=self.project('Advanced');p['physics']['motion']='Up the surface of the ramp'
  p['forces'][2].update(angle_mode='Degrees',angle=45.)
  r=app.evaluated(p);self.assertAlmostEqual(r.project['forces'][1]['magnitude'],100*math.cos(math.pi/6)-100*math.sin(math.pi/12))
 def test_coupled_equilibrium_and_friction(self):
  p=self.project('Advanced');p['physics'].update(motion='Up the surface of the ramp',equilibrium=True,show_acceleration=True)
  r=app.evaluated(p);self.assertFalse(r.messages)
  self.assertAlmostEqual(r.project['forces'][2]['magnitude'],50+25*math.cos(math.pi/6))
  self.assertLess(app.resultant(p)[2],1e-7);self.assertLess(r.acceleration[2],1e-7)
  p['forces'][2].update(angle_mode='Degrees',angle=45.)
  r=app.evaluated(p);self.assertFalse(r.messages);self.assertLess(app.resultant(p)[2],1e-7)
  expected=(50+25*math.cos(math.pi/6))/(math.cos(math.pi/12)+.25*math.sin(math.pi/12))
  self.assertAlmostEqual(r.project['forces'][2]['magnitude'],expected)
  p['physics']['motion']='Not moving'
  self.assertTrue(any('No unique solution' in m[1] for m in app.evaluated(p).messages))
 def test_contact_loss_and_no_double_writers(self):
  p=self.project();p['physics']['motion']='Right';p['forces'][2].update(magnitude=150.,direction='Up')
  r=app.evaluated(p);self.assertTrue(any('Contact is lost' in m[1] for m in r.messages))
  self.assertEqual(r.project['forces'][0]['magnitude'],0.);self.assertEqual(r.project['forces'][3]['magnitude'],0.)
  p['physics']['friction_force']=0
  self.assertTrue(any(m[0]=='error' for m in app.evaluated(p).messages))
 def test_static_and_equilibrium_with_fixed_normal(self):
  p=self.project();p['physics'].update(auto_normal=False,equilibrium=True,motion='Not moving',friction_coefficient=2.)
  p['forces'][2].update(direction='Up')
  p['forces'][0]['magnitude']=80.
  r=app.evaluated(p);self.assertFalse(r.messages)
  self.assertAlmostEqual(r.project['forces'][2]['magnitude'],20.);self.assertLess(app.resultant(p)[2],1e-7)
 def test_friction_ui(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
  a.toggle(key='0auto_normal').set_value(True).run();a.toggle(key='0auto_friction').set_value(True).run()
  [x for x in a.selectbox if x.label=='Direction of motion'][0].set_value('Right').run()
  p=a.session_state['project'];r=app.evaluated(p);self.assertAlmostEqual(r.project['forces'][3]['magnitude'],25.)
  self.assertFalse(a.exception)
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  self.assertFalse(a.exception)
  [x for x in a.selectbox if x.label=='Direction of motion'][0].set_value('Up the surface of the ramp').run()
  a.toggle(key='0equilibrium').set_value(True).run();a.toggle(key='0components').set_value(True).run()
  self.assertFalse(a.exception);self.assertLess(app.resultant(a.session_state['project'])[2],1e-7)
  [x for x in a.radio if x.label=='Language / Idioma'][0].set_value('Español').run();self.assertFalse(a.exception)
 def test_older_live_settings(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30)
  p=copy.deepcopy(app.DEFAULT);p['physics']={'mass':20.}
  a.session_state['project']=p;a.run();self.assertFalse(a.exception)
 def test_bad_coefficient(self):
  for value in [-1.,float('inf'),True]:
   p=self.project();p['physics']['friction_coefficient']=value
   with self.assertRaises(ValueError):app.validate_project(dict(format='FreeBody',version=2,diagram=p))
if __name__=='__main__':unittest.main()
