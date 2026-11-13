import copy, math, json, unittest, itertools
from pathlib import Path
import app, equations, physics
from state_history import ProjectHistory
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).parent
class QualityTests(unittest.TestCase):
 def test_automatic_toggle_matrix(self):
  for mode,gravity,acceleration,equilibrium,normal,friction,moving in itertools.product(['General','Advanced'],[False,True],[False,True],[False,True],[False,True],[False,True],[False,True]):
   p=copy.deepcopy(app.DEFAULT);p['mode']=mode
   if mode=='Advanced':p['forces']=app.advanced_starting_forces()
   p['physics'].update(auto_gravity=gravity,show_acceleration=acceleration,equilibrium=equilibrium,auto_normal=normal,auto_friction=friction,motion=('Right' if mode=='General' else 'Up the surface of the ramp') if moving else 'Not moving')
   original=copy.deepcopy(p);r=app.evaluated(p)
   self.assertEqual(p,original)
   self.assertTrue(all(math.isfinite(v) for v in app.resultant(p)[:3]))
   for net,components in itertools.product([False,True],[False,True]):
    p.update(show_net=net,show_components=components)
    p['physics']['component_basis']='Ramp parallel / perpendicular'
    vectors=app.vector_forces(p)
    self.assertTrue(all(math.isfinite(v[axis]) for v in vectors for axis in ['x','y']))
    self.assertAlmostEqual(sum(v['x'] for v in vectors),app.resultant(p)[0])
    self.assertAlmostEqual(sum(v['y'] for v in vectors),app.resultant(p)[1])
    self.assertTrue(equations.rows(p,app.force_angle)[0])
   self.assertEqual(app.validate_project(json.loads(app.export_project(p))),p)
 def test_unrecognized_labels_require_selection(self):
  a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
  p=copy.deepcopy(app.DEFAULT)
  for i,f in enumerate(p['forces']):f['label']=str(i+1)
  a.session_state['project']=p;a.run()
  a.toggle(key='0auto_gravity').set_value(True).run()
  self.assertIsNone(a.session_state['project']['physics']['gravity_force'])
  self.assertTrue(a.error);self.assertFalse(a.exception)
  self.assertEqual(a.session_state['project']['forces'],p['forces'])
 def test_format_version_validation(self):
  for version in [True,2.0,3,'2']:
   with self.assertRaises(ValueError):app.validate_project(dict(format='FreeBody',version=version,diagram=app.DEFAULT))
 def test_component_basis(self):
  for slope in [30.,-30.,0.]:
   p=copy.deepcopy(app.DEFAULT);p.update(mode='Advanced',inclined_angle=slope,show_components=True)
   p['forces']=app.advanced_starting_forces();p['physics']['component_basis']='Ramp parallel / perpendicular'
   v=app.vector_forces(p);whole=physics.total(p,app.force_angle)
   self.assertAlmostEqual(sum(x['x'] for x in v),whole[0]);self.assertAlmostEqual(sum(x['y'] for x in v),whole[1])
   p['show_net']=True;v=app.vector_forces(p);self.assertEqual(len(v),2)
   self.assertAlmostEqual(sum(x['x'] for x in v),whole[0]);self.assertAlmostEqual(sum(x['y'] for x in v),whole[1])
   rows,_=equations.rows(p,app.force_angle)
   self.assertTrue(any(r'\mathrm{G},\parallel' in row for row in rows));self.assertTrue(any(r'\perp' in row for row in rows))
 def test_precision_and_history(self):
  p=copy.deepcopy(app.DEFAULT);p['forces'][0]['magnitude']=86.6025403784
  history=ProjectHistory(p,limit=2)
  for value in [1,2,3]:
   p['physics']['precision']=value;history.record(p)
  self.assertEqual(len(history.past),2)
  undone=history.undo();self.assertEqual(undone['physics']['precision'],2)
  self.assertEqual(history.redo()['physics']['precision'],3)
  p['physics']['precision']=6;history.record(p)
  self.assertFalse(history.future)
  q=app.validate_project(json.loads(app.export_project(p)))
  self.assertEqual(q['forces'][0]['magnitude'],86.6025403784)
  self.assertTrue(any('86.602540' in row for row in equations.rows({**q,'show_components':True},app.force_angle)[0]))
 def test_undo_redo_ui(self):
  a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
  a.number_input(key='0mass').set_value(20.).run()
  self.assertFalse([x for x in a.button if x.label=='Undo'][0].disabled)
  [x for x in a.button if x.label=='Undo'][0].click().run()
  self.assertEqual(a.session_state['project']['physics']['mass'],10.)
  [x for x in a.button if x.label=='Redo'][0].click().run()
  self.assertEqual(a.session_state['project']['physics']['mass'],20.)
  self.assertFalse(a.exception)
 def test_ramp_ui_precision_and_steps(self):
  a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  a.toggle(key='0components').set_value(True).run()
  a.selectbox(key='0component_basis').set_value('Ramp parallel / perpendicular').run()
  a.number_input(key='0precision').set_value(4).run()
  a.toggle(key='0auto_gravity').set_value(True).run()
  self.assertTrue(any(r'\parallel' in x.value for x in a.latex))
  self.assertTrue(any('Show calculation steps' in x.label for x in a.expander))
  self.assertFalse(a.exception)
 def test_history_does_not_bake_calculated_values(self):
  p=copy.deepcopy(app.DEFAULT);h=ProjectHistory(p)
  p['physics'].update(auto_gravity=True,mass=20.);h.record(p)
  self.assertEqual(app.evaluated(p).project['forces'][1]['magnitude'],200.)
  self.assertEqual(h.present['forces'][1]['magnitude'],100.)
  self.assertEqual(h.undo()['forces'][1]['magnitude'],100.)
if __name__=='__main__':unittest.main()
