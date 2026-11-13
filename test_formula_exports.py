import copy,io,itertools,unittest
from pathlib import Path
from PIL import Image,ImageChops
from streamlit.testing.v1 import AppTest
import app,equations
class FormulaExportTests(unittest.TestCase):
 def test_ignore_force_words(self):
  for label,expected in [('Normal Force','N'),('FORCE Applied Force','A'),('Fuerza normal','N'),('Fuerzas Aplicadas','A'),('Reinforcement','R'),('Force','1')]:
   self.assertEqual(equations.symbols([dict(label=label)]),[expected])
 def test_exports_all_equation_views(self):
  for mode,components,acceleration in itertools.product(['General','Advanced'],[False,True],[False,True]):
   p=copy.deepcopy(app.DEFAULT);p.update(mode=mode,show_components=components)
   if mode=='Advanced':p['forces']=app.advanced_starting_forces()
   p['physics'].update(auto_gravity=True,show_acceleration=acceleration,component_basis='Ramp parallel / perpendicular',precision=4)
   rows,_=equations.rows(p,app.force_angle)
   self.assertFalse(any('pmatrix' in row for row in rows))
   png=equations.png_bytes(rows,title='Ecuaciones de fuerzas')
   with Image.open(io.BytesIO(png)) as image:
    self.assertEqual(image.format,'PNG');self.assertGreater(image.width,200)
    rgb=image.convert('RGB');self.assertIsNotNone(ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).getbbox())
    self.assertEqual(rgb.getpixel((0,0)),(255,255,255));self.assertEqual(rgb.getpixel((rgb.width-1,rgb.height-1)),(255,255,255))
   tex=equations.latex_document(rows,True).decode()
   self.assertIn('\\begin{document}',tex);self.assertIn('Ecuaciones de fuerzas',tex)
   for row in rows:self.assertIn(row,tex)
 def test_long_labels_and_tex_safety(self):
  p=copy.deepcopy(app.DEFAULT)
  p['forces']=[dict(label=('Force '+'A '*37).strip(),magnitude=100.,angle=0.,color='Blue') for _ in range(10)]
  rows,_=equations.rows(p,app.force_angle)
  image=Image.open(io.BytesIO(equations.png_bytes(rows)));self.assertGreater(image.width,200)
  p['forces'][0]['label']=r'\input{secrets}'
  rows,_=equations.rows(p,app.force_angle);self.assertNotIn(r'\input',equations.latex_document(rows).decode())
 def test_formula_download_ui(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
  labels=[x.proto.label for x in a.get('download_button')]
  self.assertIn('Save formulas as PNG',labels);self.assertIn('Save formulas as LaTeX (.tex)',labels)
  self.assertTrue(any('ΣFx and ΣFy' in x.value for x in a.caption))
  [x for x in a.radio if x.label=='Language / Idioma'][0].set_value('Español').run()
  self.assertIn('Guardar fórmulas como PNG',[x.proto.label for x in a.get('download_button')]);self.assertFalse(a.exception)
  a.checkbox(key='0equations').uncheck().run()
  self.assertNotIn('Guardar fórmulas como PNG',[x.proto.label for x in a.get('download_button')])
if __name__=='__main__':unittest.main()
