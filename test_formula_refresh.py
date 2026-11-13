import copy,io,unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image
from streamlit.testing.v1 import AppTest
import app,equations
class FormulaRefreshTests(unittest.TestCase):
 def test_plain_arithmetic_and_symbols(self):
  p=copy.deepcopy(app.DEFAULT);rows,_=app.equations.rows(p,app.force_angle)
  self.assertIn(r'\mathrm{N}',rows[0]);self.assertNotIn(r'\mathrm{NF}',rows[0])
  self.assertTrue(any('Horizontal' in r and r'100.00\,\mathrm{N} - 50.00\,\mathrm{N} = 50.00' in r for r in rows))
  self.assertTrue(any('Vertical' in r and r'100.00\,\mathrm{N} - 100.00\,\mathrm{N} = 0.00' in r for r in rows))
  self.assertFalse(any('pmatrix' in r for r in rows))
  self.assertEqual(Image.open(io.BytesIO(app.equations.png_bytes(rows))).format,'PNG')
 def test_ignores_stale_imported_module(self):
  with patch.object(equations,'rows',return_value=([r'\begin{pmatrix}50\\0\end{pmatrix}'],[])),patch.object(equations,'symbols',return_value=['NF','GF','AF','FF']):
   fresh=app.load_equations_module()
   self.assertEqual(fresh.symbols(app.DEFAULT['forces']),['N','G','A','F'])
   a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
   math=[x.value for x in a.latex]
   self.assertTrue(any('Horizontal' in r for r in math));self.assertFalse(any('pmatrix' in r for r in math))
   self.assertFalse(any(r'\mathrm{NF}' in r or r'\mathrm{GF}' in r for r in math))
   self.assertFalse(a.exception)
if __name__=='__main__':unittest.main()
