import copy, json, math, unittest
from pathlib import Path
import app, physics
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).parent
class PhysicsTests(unittest.TestCase):
 def test_legacy_files(self):
  for file in (ROOT/'fixtures').glob('released-*.fbd'):
   raw=json.loads(file.read_bytes()); old=raw['diagram'];new=app.validate_project(raw)
   self.assertEqual(new['forces'],old['forces']);self.assertEqual(new['image'],old['image'])
   self.assertFalse(new['physics']['auto_gravity']);self.assertFalse(new['physics']['show_acceleration'])
   self.assertEqual(app.vector_forces(new),app.vector_forces(old))
   self.assertEqual(app.validate_project(json.loads(app.export_project(new))),new)
 def test_gravity_acceleration(self):
  p=copy.deepcopy(app.DEFAULT);p['physics'].update(auto_gravity=True,mass=20.,show_acceleration=True)
  r=app.evaluated(p);self.assertEqual(r.project['forces'][1]['magnitude'],200.)
  self.assertEqual(r.project['forces'][1]['angle'],270.)
  self.assertAlmostEqual(r.acceleration[0],2.5);self.assertAlmostEqual(r.acceleration[1],-5.)
  self.assertEqual(p['forces'][1]['magnitude'],100.)
  p['mode']='Advanced';p['forces']=app.advanced_starting_forces()
  self.assertEqual(app.evaluated(p).project['forces'][0]['angle'],270.)
 def test_settings_validation(self):
  for key,value in [('mass',0),('mass',float('inf')),('gravity',-1),('auto_gravity',1),('gravity_force',9)]:
   p=copy.deepcopy(app.DEFAULT);p['physics'][key]=value
   with self.assertRaises(ValueError): app.validate_project(dict(format='FreeBody',version=2,diagram=p))
 def test_mass_ui(self):
  a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
  a.toggle(key='0auto_gravity').set_value(True).run()
  a.number_input(key='0mass').set_value(20.).run()
  calculated=[x for x in a.number_input if '🧮' in x.label]
  self.assertEqual(calculated[0].value,200.);self.assertTrue(calculated[0].disabled)
  a.toggle(key='0acceleration').set_value(True).run();self.assertFalse(a.exception)
  a.toggle(key='0auto_gravity').set_value(False).run()
  self.assertEqual(a.session_state['project']['forces'][1]['magnitude'],100.)
if __name__=='__main__':unittest.main()
