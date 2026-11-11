import base64,copy,io,json,math,unittest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from streamlit.testing.v1 import AppTest
import app
class DiagramTests(unittest.TestCase):
 def test_file_roundtrip(self):
  p=copy.deepcopy(app.DEFAULT); p.update(show_net=True,show_components=True,font='Courier / typewriter')
  p['forces'][0].update(angle_mode='Relative to the surface of the ramp',relative='Perpendicular to the surface of the ramp')
  im=io.BytesIO();Image.new('RGBA',(80,40),(255,0,0,255)).save(im,format='PNG');p['image']=base64.b64encode(im.getvalue()).decode()
  self.assertEqual(p,app.validate_project(json.loads(app.export_project(p))))
 def test_vectors(self):
  p=copy.deepcopy(app.DEFAULT);p['show_net']=True
  v=app.vector_forces(p);self.assertEqual(len(v),1);self.assertAlmostEqual(v[0]['x'],50);self.assertAlmostEqual(v[0]['y'],0)
  p['show_components']=True;v=app.vector_forces(p);self.assertEqual(len(v),2);self.assertAlmostEqual(v[0]['x'],50);self.assertEqual(v[1]['y'],0)
  p['show_net']=False;self.assertEqual(len(app.vector_forces(p)),8)
 def test_ramp_directions(self):
  p=copy.deepcopy(app.DEFAULT);p.update(mode='Advanced',inclined_angle=30.)
  f=p['forces'][0];f['angle_mode']='Relative to the surface of the ramp'
  for direction,expected in zip(app.RELATIVE,[30,210,120]):
   f['relative']=direction;self.assertEqual(app.force_angle(p,f),expected)
  p['inclined_angle']=-30.;f['relative']='Up the surface of the ramp';self.assertEqual(app.force_angle(p,f),150)
 def test_geometry_and_render(self):
  for shape in ['Rectangle','Square','Circle','Triangle']:
   for angle in [-45,0,30,45]:
    p=copy.deepcopy(app.DEFAULT);p.update(shape=shape,mode='Advanced',inclined_angle=float(angle))
    fig=app.draw_diagram(p);ax=fig.axes[0];w,h,_=app.object_geometry(p)
    # The ground passes through the rotated lower corners (circle: tangent).
    r=math.radians(angle)
    x=w*math.cos(r)+h*math.sin(r);y=w*math.sin(r)-h*math.cos(r)
    if shape!='Circle': self.assertAlmostEqual(y,math.tan(r)*x-h/math.cos(r))
    ground=ax.lines[0];self.assertAlmostEqual(ground.get_ydata()[0],math.tan(r)*ground.get_xdata()[0]-h/math.cos(r))
    legend=ax.get_legend();self.assertEqual(legend.get_frame().get_alpha(),1.)
    for text in legend.get_texts(): self.assertEqual(tuple(matplotlib.colors.to_rgba(text.get_color())),matplotlib.colors.to_rgba('#111111'))
    fig.canvas.draw();plt.close(fig)
  p=copy.deepcopy(app.DEFAULT);p.update(mode='Advanced',inclined_angle=30.,show_net=True,show_components=True,font='Courier / typewriter')
  fig=app.draw_diagram(p,True);fig.savefig(io.BytesIO(),format='png',transparent=True,bbox_inches='tight');plt.close(fig)
 def test_ui(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py'))).run(timeout=30)
  self.assertFalse(a.exception)
  self.assertFalse(any('°' in x.label for x in a.number_input))
  directions=[x for x in a.selectbox if x.label=='Direction'];self.assertEqual(len(directions),4)
  a.toggle[0].set_value(True).run();a.toggle[1].set_value(True).run();self.assertFalse(a.exception)
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run();self.assertFalse(a.exception)
  self.assertTrue(any(x.label=='Ramp angle (°)' for x in a.slider))
  [x for x in a.radio if x.label=='Force direction method'][0].set_value('Relative to the surface of the ramp').run()
  self.assertFalse(a.exception);self.assertTrue(any(x.label=='Relative direction' for x in a.selectbox))
  [x for x in a.radio if x.label=='Language / Idioma'][0].set_value('Español').run();self.assertFalse(a.exception)
  [x for x in a.radio if x.label=='Funciones'][0].set_value('General').run();self.assertFalse(a.exception)
  self.assertFalse(any('°' in x.label for x in a.number_input))
if __name__=='__main__':unittest.main()
