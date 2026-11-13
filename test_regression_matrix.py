"""Exercise every pre-existing display category with physics tools enabled."""
import copy, io, itertools, unittest, warnings
import matplotlib.pyplot as plt
import app
class FeatureMatrix(unittest.TestCase):
 def test_display_interactions(self):
  for mode,net,components in itertools.product(['General','Advanced'],[False,True],[False,True]):
   p=copy.deepcopy(app.DEFAULT);p.update(mode=mode,show_net=net,show_components=components,show_grid=True,show_axes=True,show_polar=True,show_ground=False)
   if mode=='Advanced': p['forces']=app.advanced_starting_forces();p['inclined_angle']=-30.
   p['physics'].update(auto_gravity=True,show_acceleration=True,mass=15.)
   fig=app.draw_diagram(p,True);fig.canvas.draw()
   self.assertEqual(fig.patch.get_alpha(),0.);self.assertEqual(fig.axes[0].patch.get_alpha(),0.)
   fig.savefig(io.BytesIO(),format='png',transparent=True,bbox_inches='tight');plt.close(fig)
 def test_fonts_shapes_and_style(self):
  with warnings.catch_warnings(record=True) as seen:
   warnings.simplefilter('always')
   for font in app.FONTS:
    p=copy.deepcopy(app.DEFAULT);p.update(font=font,show_net=True,show_components=True,show_box=True,arrow_offset=0.,arrow_thickness=5.,arrowhead_size=30.,font_size=24)
    p['physics'].update(auto_gravity=True,show_acceleration=True)
    fig=app.draw_diagram(p);fig.canvas.draw();plt.close(fig)
   self.assertFalse(any('Glyph' in str(w.message) for w in seen))
  for shape in ['Rectangle','Square','Circle','Triangle']:
   p=copy.deepcopy(app.DEFAULT);p.update(shape=shape,mode='Advanced',inclined_angle=45.,show_ground=True)
   p['physics'].update(auto_gravity=True)
   fig=app.draw_diagram(p);fig.canvas.draw();plt.close(fig)
