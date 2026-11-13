import copy, unittest
from pathlib import Path
import app, equations
from streamlit.testing.v1 import AppTest
class EquationTests(unittest.TestCase):
 def test_initials_and_duplicates(self):
  p=copy.deepcopy(app.DEFAULT)
  self.assertEqual(equations.symbols(p['forces']),['NF','GF','AF','FF'])
  p['forces'][1]['label']='Normal Force'
  self.assertEqual(equations.symbols(p['forces'])[:2],['NF1','NF2'])
  p['forces'][0]['label']=r'\\evil{<script>}';symbol=equations.symbols(p['forces'])[0]
  self.assertNotIn('\\',symbol);self.assertNotIn('{',symbol)
 def test_equations_components(self):
  p=copy.deepcopy(app.DEFAULT);p['show_components']=True
  rows,key=equations.rows(p,app.force_angle)
  self.assertIn(r'F_{\mathrm{NF},x}',rows[0]);self.assertIn(r'F_{\mathrm{GF},y}',rows[2])
  self.assertIn(r'\left(-100.00\right)',rows[3])
  p['physics'].update(auto_gravity=True,mass=20.,show_acceleration=True)
  rows,key=equations.rows(p,app.force_angle)
  self.assertTrue(any('a_x=' in row for row in rows));self.assertTrue(any('-200.00' in row for row in rows))
 def test_equations_ui_bilingual(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
  self.assertGreater(len(a.latex),0)
  a.toggle(key='0components').set_value(True).run()
  self.assertTrue(any(r'\mathrm{NF},x' in x.value for x in a.latex))
  [x for x in a.radio if x.label=='Language / Idioma'][0].set_value('Español').run()
  self.assertFalse(a.exception)
  self.assertTrue(any('Ecuaciones' in x.value for x in a.subheader))
if __name__=='__main__':unittest.main()
