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
 def test_advanced_defaults_and_resultant(self):
  p=copy.deepcopy(app.DEFAULT);p.update(mode='Advanced',inclined_angle=30.,forces=app.advanced_starting_forces())
  self.assertEqual([f['label'] for f in p['forces']],['Gravitational Force','Normal Force','Applied Force','Frictional Force'])
  self.assertEqual([app.force_angle(p,f) for f in p['forces']],[270,120,30,210])
  x,y,magnitude,angle=app.resultant(p)
  self.assertAlmostEqual(x,25*math.cos(math.radians(30)))
  self.assertAlmostEqual(y,12.5)
  self.assertAlmostEqual(magnitude,25.)
  self.assertAlmostEqual(angle,30.)
  self.assertEqual(p['forces'][3]['magnitude'],p['forces'][2]['magnitude']/4.)
  self.assertAlmostEqual(p['forces'][1]['magnitude'],100*math.cos(math.radians(30)))
  p['forces']=[dict(label='zero',magnitude=0.,angle=0.,color='Blue')]
  self.assertIsNone(app.resultant(p)[3])
 def test_precision_controls_and_overlays(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run(timeout=30)
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  self.assertFalse(a.exception)
  self.assertEqual([app.force_angle(a.session_state['project'],f) for f in a.session_state['project']['forces']],[270,120,30,210])
  # Every slider has its linked exact input; both update the same project value.
  for field,label in [('inclined_angle','Ramp angle (°)'),('arrow_offset','Arrow offset'),('arrow_thickness','Arrow thickness'),('arrowhead_size','Arrowhead size'),('font_size','Label size')]:
   slider=[x for x in a.slider if x.label==label][0]
   value=float(slider.value)+float(slider.step)
   slider.set_value(value).run()
   number=[x for x in a.number_input if x.label==label+' · exact value / − +'][0]
   self.assertAlmostEqual(number.value,value)
   number.set_value(value+float(number.step)).run()
   self.assertAlmostEqual(a.session_state['project'][field],value+float(number.step))
   self.assertAlmostEqual([x for x in a.slider if x.label==label][0].value,value+float(number.step))
  for label in ['Show grid','Show axes','Show polar coordinates (degrees)']:
   [x for x in a.checkbox if x.label==label][0].check().run()
  p=copy.deepcopy(a.session_state['project'])
  self.assertTrue(p['show_grid'] and p['show_axes'] and p['show_polar'])
  self.assertEqual(app.validate_project(json.loads(app.export_project(p))),p)
  fig=app.draw_diagram(p);fig.canvas.draw()
  labels=[x.get_text() for x in fig.axes[0].texts]
  self.assertIn('330°',labels);self.assertIn('+x',labels);self.assertIn('+y',labels)
  bounds=[t.get_window_extent(fig.canvas.get_renderer()) for t in fig.axes[0].texts]
  for i,box in enumerate(bounds):
   self.assertFalse(any(box.overlaps(other) for other in bounds[i+1:]))
  fig.savefig(io.BytesIO(),format='png',transparent=True,bbox_inches='tight');plt.close(fig)
  # Switching modes restores edited force sets rather than erasing student work.
  [x for x in a.number_input if x.label=='Magnitude (N)'][0].set_value(120.).run()
  [x for x in a.radio if x.label=='Features'][0].set_value('General').run()
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  self.assertEqual(a.session_state['project']['forces'][0]['magnitude'],120.)
  self.assertFalse(a.exception)
 def test_net_arrow_scale(self):
  p=copy.deepcopy(app.DEFAULT)
  source=app.draw_diagram(p)
  p['show_net']=True
  net=app.draw_diagram(p)
  def length(arrow):
   start,end=arrow._posA_posB
   return math.hypot(end[0]-start[0],end[1]-start[1])
  individual=[q for q in source.axes[0].patches if isinstance(q,app.patches.FancyArrowPatch)]
  result=[q for q in net.axes[0].patches if isinstance(q,app.patches.FancyArrowPatch)]
  self.assertAlmostEqual(length(result[0])/length(individual[0]),.5)
  self.assertEqual(source.axes[0].get_xlim(),net.axes[0].get_xlim())
  plt.close(source);plt.close(net)
  p.update(mode='Advanced',forces=app.advanced_starting_forces())
  p['forces'][3]['magnitude']=50.
  fig=app.draw_diagram(p)
  self.assertFalse(any(isinstance(q,app.patches.FancyArrowPatch) for q in fig.axes[0].patches))
  plt.close(fig)
 def test_restore_advanced(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run(timeout=30)
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  [x for x in a.number_input if x.label=='Magnitude (N)'][1].set_value(100.).run()
  [x for x in a.button if x.label=='Restore starting forces'][0].click().run()
  self.assertEqual(a.session_state['project']['mode'],'Advanced')
  self.assertAlmostEqual(a.session_state['project']['forces'][1]['magnitude'],86.6025403784)
  self.assertAlmostEqual(app.resultant(a.session_state['project'])[2],25.)
  [x for x in a.number_input if x.label=='Magnitude (N)'][3].set_value(50.).run()
  [x for x in a.toggle if x.label=='Display net force'][0].set_value(True).run()
  self.assertTrue(any('Balanced forces' in x.value for x in a.info))
  self.assertFalse(a.exception)
 def test_mode_default_images(self):
  general=app.default_project('General');advanced=app.default_project('Advanced')
  for mode,project in [('general',general),('advanced',advanced)]:
   self.assertEqual(base64.b64decode(project['image']),(Path(__file__).parent/'assets'/f'{mode}-object.png').read_bytes())
   self.assertEqual(project,app.validate_project(json.loads(app.export_project(project))))
   fig=app.draw_diagram(project);fig.canvas.draw();plt.close(fig)
  self.assertNotEqual(general['image'],advanced['image'])
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run(timeout=30)
  self.assertEqual(a.session_state['project']['image'],general['image'])
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  self.assertEqual(a.session_state['project']['image'],advanced['image'])
  [x for x in a.radio if x.label=='Features'][0].set_value('General').run()
  self.assertEqual(a.session_state['project']['image'],general['image'])
  [x for x in a.button if x.label=='Remove image'][0].click().run()
  self.assertIsNone(a.session_state['project']['image'])
  [x for x in a.radio if x.label=='Features'][0].set_value('Advanced').run()
  [x for x in a.radio if x.label=='Features'][0].set_value('General').run()
  self.assertIsNone(a.session_state['project']['image'])
  [x for x in a.button if x.label=='Restore starting forces'][0].click().run()
  self.assertEqual(a.session_state['project']['image'],general['image'])
  self.assertFalse(a.exception)
 def test_ui(self):
  a=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run(timeout=30)
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
