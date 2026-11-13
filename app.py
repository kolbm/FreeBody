"""Bilingual, live free-body diagrams with self-contained .fbd projects."""
import base64
import copy
import io
import json
import math
import textwrap
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import patches, transforms, font_manager, patheffects
from PIL import Image
import physics
import equations

COLORS = {'Green': '#008000', 'Red': '#FF0000', 'Blue': '#0000FF', 'Purple': '#800080', 'Orange': '#FFA500', 'Black': '#000000', 'White': '#FFFFFF'}
ES = {'Green':'Verde','Red':'Rojo','Blue':'Azul','Purple':'Morado','Orange':'Naranja','Black':'Negro','White':'Blanco','Rectangle':'Rectángulo','Square':'Cuadrado','Circle':'Círculo','Triangle':'Triángulo','General':'General','Advanced':'Avanzado'}
NAMES = [('Normal Force','Fuerza normal'),('Gravitational Force','Fuerza gravitacional'),('Applied Force','Fuerza aplicada'),('Frictional Force','Fuerza de fricción')]
DEFAULT = dict(forces=[dict(label=n[0], magnitude=m, angle=a, color=c) for n,m,a,c in zip(NAMES,[100.,100.,100.,50.],[90.,270.,0.,180.],list(COLORS)[:4])], shape='Rectangle', mode='General', inclined_angle=30., arrow_thickness=2., arrowhead_size=16., arrow_offset=1.2, font_size=12, show_ground=True, show_grid=False, show_axes=False, show_polar=False, show_box=False, box_color='#808080', image=None, show_net=False, show_components=False, font='Sans')
DEFAULT['physics']=copy.deepcopy(physics.SETTINGS)
LIMITS = {'inclined_angle':(-45,45),'arrow_thickness':(1,5),'arrowhead_size':(8,30),'arrow_offset':(0,4),'font_size':(8,24)}

DIRECTIONS = {'Up':90., 'Down':270., 'Left':180., 'Right':0.}
RELATIVE = {'Up the surface of the ramp':0., 'Down the surface of the ramp':180., 'Perpendicular to the surface of the ramp':90.}
ES.update({'Up':'Arriba','Down':'Abajo','Left':'Izquierda','Right':'Derecha',
 'Degrees':'Grados','Relative to the surface of the ramp':'Con respecto a la superficie del plano',
 'Up the surface of the ramp':'Hacia arriba del plano','Down the surface of the ramp':'Hacia abajo del plano',
 'Perpendicular to the surface of the ramp':'Perpendicular a la superficie del plano'})
# All presets have bundled fallbacks so exports remain portable across computers.
FONTS = {
 'Sans':(['DejaVu Sans'],'normal','normal'),
 'Sans bold':(['DejaVu Sans'],'normal','bold'),
 'Sans italic':(['DejaVu Sans'],'oblique','normal'),
 'Sans condensed':(['DejaVu Sans'],'normal','normal'),
 'Serif':(['DejaVu Serif'],'normal','normal'),
 'Serif bold':(['DejaVu Serif'],'normal','bold'),
 'Serif italic':(['DejaVu Serif'],'italic','normal'),
 'Serif condensed':(['DejaVu Serif'],'normal','normal'),
 'Courier / typewriter':(['Courier New','Nimbus Mono PS','Liberation Mono','DejaVu Sans Mono'],'normal','normal'),
 'Typewriter bold':(['Courier New','Nimbus Mono PS','Liberation Mono','DejaVu Sans Mono'],'normal','bold'),
 'Typewriter italic':(['Courier New','Nimbus Mono PS','Liberation Mono','DejaVu Sans Mono'],'italic','normal'),
 'Monospace':(['DejaVu Sans Mono'],'normal','normal'),
 'Monospace bold':(['DejaVu Sans Mono'],'normal','bold'),
 'Monospace italic':(['DejaVu Sans Mono'],'oblique','normal'),
 'Book serif':(['STIXGeneral','DejaVu Serif'],'normal','normal'),
 'Book serif italic':(['STIXGeneral','DejaVu Serif'],'italic','normal'),
 'Humanist sans':(['FreeSans','DejaVu Sans'],'normal','normal'),
 'Classic serif':(['FreeSerif','DejaVu Serif'],'normal','normal'),
}

ES.update({'Sans':'Sans','Sans bold':'Sans negrita','Sans italic':'Sans cursiva','Sans condensed':'Sans condensada','Serif':'Serif','Serif bold':'Serif negrita','Serif italic':'Serif cursiva','Serif condensed':'Serif condensada','Courier / typewriter':'Courier / máquina de escribir','Typewriter bold':'Máquina de escribir negrita','Typewriter italic':'Máquina de escribir cursiva','Monospace':'Monoespaciada','Monospace bold':'Monoespaciada negrita','Monospace italic':'Monoespaciada cursiva','Book serif':'Serif de libro','Book serif italic':'Serif de libro cursiva','Humanist sans':'Sans humanista','Classic serif':'Serif clásica'})

def advanced_starting_forces():
    forces=copy.deepcopy(DEFAULT['forces'])
    normal,gravity,applied,friction=forces
    normal['magnitude']=100.*math.cos(math.radians(30.))
    friction['magnitude']=applied['magnitude']/4.
    gravity.update(angle=270.,angle_mode='Degrees')
    for f,d in [(normal,'Perpendicular to the surface of the ramp'),(applied,'Up the surface of the ramp'),(friction,'Down the surface of the ramp')]:
        f.update(angle_mode='Relative to the surface of the ramp',relative=d)
    return [gravity,normal,applied,friction]

def default_project(mode='General'):
    project=copy.deepcopy(DEFAULT)
    project['mode']=mode
    if mode=='Advanced': project['forces']=advanced_starting_forces()
    asset=Path(__file__).with_name('assets')/('advanced-object.png' if mode=='Advanced' else 'general-object.png')
    project['image']=base64.b64encode(asset.read_bytes()).decode('ascii')
    return project


def sync_numeric(source, target):
    st.session_state[target]=float(st.session_state[source])

def adjustable_slider(label, low, high, value, key, help, spanish=False, step=1.):
    """One value, controlled by dragging, +/- buttons, or exact numeric entry."""
    skey=key+'_slider'; nkey=key+'_number'
    if skey not in st.session_state: st.session_state[skey]=float(value)
    if nkey not in st.session_state: st.session_state[nkey]=float(value)
    left,right=st.columns([3,2])
    left.slider(label,float(low),float(high),step=float(step),key=skey,help=help,
                on_change=sync_numeric,args=(skey,nkey))
    exact=label+(' · valor exacto / − +' if spanish else ' · exact value / − +')
    right.number_input(exact,float(low),float(high),step=float(step),key=nkey,
        help=('Escribe un valor exacto o usa − y +; el deslizador se actualiza al instante.' if spanish else 'Type an exact value or use − and +; the slider updates immediately.'),
        on_change=sync_numeric,args=(nkey,skey))
    return float(st.session_state[skey])

def evaluated(p):
    return physics.resolve(p,force_angle)

def resultant(p):
    if not p.get('_resolved'): p=evaluated(p).project
    x=sum(f['magnitude']*math.cos(math.radians(force_angle(p,f))) for f in p['forces'])
    y=sum(f['magnitude']*math.sin(math.radians(force_angle(p,f))) for f in p['forces'])
    if abs(x)<1e-8: x=0.
    if abs(y)<1e-8: y=0.
    magnitude=math.hypot(x,y)
    angle=(math.degrees(math.atan2(y,x))%360) if magnitude>1e-8 else None
    return x,y,magnitude,angle


def force_angle(p, f):
    if p['mode']=='General':
        direction=f.get('direction')
        if direction not in DIRECTIONS:
            direction=min(DIRECTIONS,key=lambda k:abs((f['angle']-DIRECTIONS[k]+180)%360-180))
        return DIRECTIONS[direction]
    if f.get('angle_mode')=='Relative to the surface of the ramp':
        relative=f.get('relative','Up the surface of the ramp')
        offset=RELATIVE[relative]
        if p['inclined_angle']<0 and relative!='Perpendicular to the surface of the ramp': offset=(offset+180)%360
        return (p['inclined_angle']+offset)%360
    return f['angle']

def vector_forces(p, spanish=False):
    if not p.get('_resolved'): p=evaluated(p).project
    vectors=[]
    for index,f in enumerate(p['forces']):
        a=math.radians(force_angle(p,f)); label=f['label']
        for en,es in NAMES:
            if spanish and label==en: label=es
        if index in p.get('_calculated',{}): label+=' ◆'
        vectors.append(dict(label=label,x=f['magnitude']*math.cos(a),y=f['magnitude']*math.sin(a),color=COLORS[f['color']]))
    if p['show_net']:
        vectors=[dict(label='Fuerza neta ◆' if spanish else 'Net force ◆',x=sum(v['x'] for v in vectors),y=sum(v['y'] for v in vectors),color='#007C91')]
    if p['show_components']:
        vectors=[dict(label=v['label']+' · '+axis+' ◆', x=v['x'] if axis=='x' else 0., y=v['y'] if axis=='y' else 0.,color=v['color']) for v in vectors for axis in ['x','y']]
    for v in vectors:
        for axis in ['x','y']:
            if abs(v[axis])<1e-8: v[axis]=0.
    return vectors

def object_geometry(p):
    """Geometry in ramp coordinates; lower edge y=-height contacts the plane."""
    image=None
    if p['image']:
        with Image.open(io.BytesIO(base64.b64decode(p['image']))) as im:
            image=im.convert('RGBA')
        bounds=image.getchannel('A').getbbox()
        if bounds: image=image.crop(bounds)
        scale=max(image.size); w=image.width/scale; h=image.height/scale
        # Downsample only the plot preview; .fbd files retain the full image bytes.
        image.thumbnail((600,600),Image.Resampling.LANCZOS)
    else:
        w=1.; h=.65 if p['shape'] in ['Rectangle','Triangle'] else 1.
    return w,h,image


def validate_project(data):
    if not isinstance(data,dict) or data.get('format') != 'FreeBody' or data.get('version') not in (1,2):
        raise ValueError('Unsupported .fbd format / Formato .fbd no compatible')
    p = copy.deepcopy(DEFAULT)
    source = data.get('diagram')
    if not isinstance(source,dict): raise ValueError('Missing diagram / Falta el diagrama')
    for k in p:
        if k in source: p[k]=source[k]
    if p['shape'] not in ['Rectangle','Square','Circle','Triangle'] or p['mode'] not in ['General','Advanced']: raise ValueError('Invalid settings / Configuración inválida')
    for k,(lo,hi) in LIMITS.items():
        v=p[k]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError('Invalid '+k)
    for k in ['show_ground','show_grid','show_axes','show_polar','show_box','show_net','show_components']:
        if not isinstance(p[k],bool): raise ValueError('Invalid '+k)
    if p['font'] not in FONTS: raise ValueError('Invalid font / Fuente inválida')
    def valid_color(c):
        return isinstance(c,str) and len(c)==7 and c[0]=='#' and all(x in '0123456789abcdefABCDEF' for x in c[1:])
    if not valid_color(p['box_color']): raise ValueError('Invalid color')
    if not isinstance(p['forces'],list) or not 1<=len(p['forces'])<=10: raise ValueError('Use 1–10 forces / Usa 1–10 fuerzas')
    for f in p['forces']:
        if not isinstance(f,dict) or not isinstance(f.get('label'),str) or len(f['label'])>80 or f.get('color') not in COLORS: raise ValueError('Invalid force / Fuerza inválida')
        for k,lo,hi in [('magnitude',0,10000),('angle',0,360)]:
            v=f.get(k)
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError('Invalid '+k)
        if f.get('direction','Up') not in DIRECTIONS or f.get('angle_mode','Degrees') not in ['Degrees','Relative to the surface of the ramp'] or f.get('relative','Up the surface of the ramp') not in RELATIVE: raise ValueError('Invalid direction / Dirección inválida')
    p['physics']=physics.validate_settings(source.get('physics',{}),len(p['forces']))
    if p['image'] is not None:
        raw=base64.b64decode(p['image'],validate=True)
        if len(raw)>5*1024*1024: raise ValueError('Image exceeds 5 MB / Imagen mayor de 5 MB')
        with Image.open(io.BytesIO(raw)) as im:
            if im.width*im.height>16000000: raise ValueError('Image too large / Imagen demasiado grande')
            im.verify()
    return p

def export_project(p):
    return json.dumps({'format':'FreeBody','version':2,'diagram':p},ensure_ascii=False,allow_nan=False).encode('utf-8')

def draw_diagram(p, spanish=False):
    if not p.get('_resolved'): p=evaluated(p).project
    vectors=vector_forces(p,spanish)
    fig,ax=plt.subplots(figsize=(8,7),dpi=150)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    ax.set_aspect('equal'); ax.set_axis_off()
    # Keep the same N-to-length scale when switching between source, net, and component views.
    offset=p['arrow_offset']; maxmag=max([f['magnitude'] for f in p['forces']]+[1.])
    longest=max([math.hypot(v['x'],v['y']) for v in vectors]+[0.])
    reach=offset+max(4.5,3.*longest/maxmag+1.5)
    angle=p['inclined_angle'] if p['mode']=='Advanced' else 0.
    r=math.radians(angle); w,h,image=object_geometry(p)
    rotation=transforms.Affine2D().rotate_deg(angle)+ax.transData
    if p['show_ground']:
        # n·position=-h, so the object's entire lower edge lies on the ramp.
        ax.plot([-reach,reach],[(-h-math.sin(r)*reach)/math.cos(r),(-h+math.sin(r)*reach)/math.cos(r)],color='saddlebrown',lw=2,zorder=0)
    if p['show_grid']:
        for x in range(-int(reach),int(reach)+1):
            ax.axhline(x,color='gray',alpha=.2,lw=.5,zorder=0); ax.axvline(x,color='gray',alpha=.2,lw=.5,zorder=0)
    if p['show_polar']:
        radius=reach-.7
        for ring in range(1,int(radius)+1):
            ax.add_patch(patches.Circle((0,0),ring,fill=False,color='#888888',alpha=.28,lw=.7,zorder=0))
        for degree in range(0,360,30):
            theta=math.radians(degree); dx=math.cos(theta); dy=math.sin(theta)
            ax.plot([0,radius*dx],[0,radius*dy],color='#888888',alpha=.35,lw=.7,zorder=0)
            ax.text((radius+.3)*dx,(radius+.3)*dy,f'{degree}°',ha='center',va='center',fontsize=9,color='#222222',bbox=dict(facecolor='white',edgecolor='none',alpha=.95,pad=1),zorder=4)
    if p['show_axes']:
        ax.axhline(0,color='#888888',lw=1.,ls='--',zorder=0)
        ax.axvline(0,color='#888888',lw=1.,ls='--',zorder=0)
        for text,x,y in [('+x',reach-.2,.65),('+y',.65,reach-.2)]:
            ax.text(x,y,text,ha='center',va='center',fontsize=10,color='#222222',bbox=dict(facecolor='white',edgecolor='none',alpha=.95,pad=1),zorder=4)
    if image is not None:
        ax.imshow(image,extent=(-w,w,-h,h),transform=rotation,zorder=1)
    else:
        kw=dict(facecolor=p['box_color'],edgecolor='#555555',alpha=.8,zorder=1,transform=rotation)
        if p['shape']=='Circle': obj=patches.Circle((0,0),1,**kw)
        elif p['shape']=='Triangle': obj=patches.Polygon([(-w,-h),(w,-h),(0,1)],**kw)
        else: obj=patches.Rectangle((-w,-h),2*w,2*h,**kw)
        ax.add_patch(obj)
    used=[]
    for v in vectors:
        mag=math.hypot(v['x'],v['y']); a=math.atan2(v['y'],v['x'])
        u=(math.cos(a),math.sin(a)); perp=(-u[1],u[0])
        same=sum(abs((a-old+math.pi)%(2*math.pi)-math.pi)<.14 for old in used); used.append(a)
        lane=.25*same; start=(offset*u[0]+lane*perp[0],offset*u[1]+lane*perp[1])
        length=3*mag/maxmag
        end=(start[0]+length*u[0],start[1]+length*u[1])
        if mag>1e-8:
            # An outline keeps force colors visible against light or dark themes.
            arrow=patches.FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=p['arrowhead_size'],lw=p['arrow_thickness'],color=v['color'],shrinkA=0,shrinkB=0,zorder=3)
            arrow.set_path_effects([patheffects.Stroke(linewidth=p['arrow_thickness']+1.5,foreground='#999999'),patheffects.Normal()])
            ax.add_patch(arrow)
        if p['mode']=='General' and not p['show_net']:
            directions=[]
            if abs(v['x'])>1e-8: directions.append('Right' if v['x']>0 else 'Left')
            if abs(v['y'])>1e-8: directions.append('Up' if v['y']>0 else 'Down')
            direction=' + '.join(ES.get(d,d) if spanish else d for d in directions)
        else: direction=f'{math.degrees(a)%360:.1f}°'
        detail=f'{mag:.1f} N'+(' · '+direction if mag>1e-8 else '')
        label='\n'.join(textwrap.wrap(v['label'],width=45))+ '  ·  '+detail
        ax.plot([],[],color=v['color'],lw=3,label=label)
    if physics.settings(p)['show_acceleration']:
        x,y,mag,angle=physics.total(p,force_angle); mass=physics.settings(p)['mass']
        if mag>physics.EPS:
            unit=(x/mag,y/mag)
            ax.add_patch(patches.FancyArrowPatch((0,0),(2.7*unit[0],2.7*unit[1]),arrowstyle='->',mutation_scale=18,lw=2,linestyle='--',color='#DD8800',zorder=5))
        label=('Aceleración' if spanish else 'Acceleration')+f' ◆ · {mag/mass:.2f} m/s²'
        if angle is not None: label+=f' · {angle:.1f}°'
        ax.plot([],[],color='#DD8800',lw=2,ls='--',label=label)
    ax.set_xlim(-reach,reach); ax.set_ylim(-reach,reach)
    families,style,weight=FONTS[p['font']]
    available={f.name for f in font_manager.fontManager.ttflist}
    family=next((f for f in families if f in available),'DejaVu Sans')
    font=font_manager.FontProperties(family=[family,'DejaVu Sans'],style=style,weight=weight,size=p['font_size'],stretch='condensed' if 'condensed' in p['font'] else 'normal')
    # Opaque light legend panel guarantees legibility on dark and light pages.
    legend=ax.legend(loc='upper center',bbox_to_anchor=(.5,-.02),frameon=True,prop=font,ncol=1,facecolor='white',edgecolor='#666666' if p['show_box'] else 'white',framealpha=1.,labelcolor='#111111')
    for text in legend.get_texts(): text.set_parse_math(False)
    return fig

def main():
    st.set_page_config(page_title='FreeBody',layout='wide')
    splash=Path(__file__).with_name('title.jpg')
    if splash.exists(): st.sidebar.image(str(splash),width=160)
    spanish=st.sidebar.radio('Language / Idioma',['English','Español'])=='Español'
    def t(en,es): return es if spanish else en
    def option(s): return ES.get(s,s) if spanish else s
    st.title(t('Free Body Diagram Generator','Generador de diagramas de cuerpo libre'))
    st.caption(t('Edit a value to update the diagram. General uses Up, Down, Left, and Right.','Cambia un valor para actualizar el diagrama. General usa Arriba, Abajo, Izquierda y Derecha.'))
    if 'project' not in st.session_state: st.session_state.project=default_project()
    if 'revision' not in st.session_state: st.session_state.revision=0
    incoming=st.sidebar.file_uploader(t('Open .fbd diagram','Abrir diagrama .fbd'),type=['fbd'],help=t('Includes forces, settings, and the original image.','Incluye fuerzas, configuración y la imagen original.'))
    if st.sidebar.button(t('Load diagram','Cargar diagrama'),disabled=incoming is None):
        try:
            if incoming.size>8*1024*1024: raise ValueError('File exceeds 8 MB / Archivo mayor de 8 MB')
            loaded=validate_project(json.loads(incoming.getvalue()))
            st.session_state.project=loaded; st.session_state.revision+=1
            st.sidebar.success(t('Diagram loaded.','Diagrama cargado.'))
        except (ValueError,TypeError,KeyError,OSError) as e: st.sidebar.error(str(e))
    if st.sidebar.button(t('Restore starting forces','Restaurar fuerzas iniciales')):
        mode=st.session_state.project['mode']
        restored=default_project(mode)
        st.session_state.project=restored; st.session_state.revision+=1
    p=st.session_state.project
    for k,v in DEFAULT.items(): p.setdefault(k,copy.deepcopy(v))
    p['physics']=physics.settings(p)
    prefix=str(st.session_state.revision)
    controls,preview=st.columns([1,2])
    with controls:
        previous_mode=p['mode']
        p['mode']=st.radio(t('Features','Funciones'),['General','Advanced'],index=['General','Advanced'].index(p['mode']),format_func=option,key=prefix+'mode',help=t('Advanced adds incline, grid, arrow styling, and label options.','Avanzado añade inclinación, cuadrícula y estilos de flechas y etiquetas.'))
        cache_key=prefix+'mode_force_cache'
        if cache_key not in st.session_state: st.session_state[cache_key]={}
        image_cache_key=prefix+'mode_image_cache'
        if image_cache_key not in st.session_state: st.session_state[image_cache_key]={}
        role_cache_key=prefix+'mode_role_cache'
        if role_cache_key not in st.session_state: st.session_state[role_cache_key]={}
        if p['mode']!=previous_mode:
            role_cache=st.session_state[role_cache_key]
            role_cache[previous_mode]={k:v for k,v in p['physics'].items() if k.endswith('_force')}
            for k in p['physics']:
                if k.endswith('_force'): p['physics'][k]=role_cache.get(p['mode'],{}).get(k)
            cache=st.session_state[cache_key]
            cache[previous_mode]=copy.deepcopy(p['forces'])
            image_cache=st.session_state[image_cache_key]
            image_cache[previous_mode]=p['image']
            p['image']=image_cache[p['mode']] if p['mode'] in image_cache else default_project(p['mode'])['image']
            p['forces']=copy.deepcopy(cache.get(p['mode'],advanced_starting_forces() if p['mode']=='Advanced' else DEFAULT['forces']))
            st.session_state[prefix+'force_revision']=st.session_state.get(prefix+'force_revision',0)+1
        force_prefix=prefix+p['mode']+str(st.session_state.get(prefix+'force_revision',0))
        p['show_net']=st.toggle(t('Display net force','Mostrar fuerza neta'),value=p['show_net'],key=prefix+'net',help=t('Replaces all individual forces with their vector sum.','Sustituye las fuerzas individuales por su suma vectorial.'))
        p['show_components']=st.toggle(t('Horizontal and vertical components','Componentes horizontal y vertical'),value=p['show_components'],key=prefix+'components',help=t('Replaces each displayed force with its x and y components. With net force enabled, shows only the net components.','Sustituye cada fuerza por sus componentes x e y. Con fuerza neta activada, muestra solo sus componentes.'))
        p['physics']['show_equations']=st.checkbox(t('Show force equations','Mostrar ecuaciones de fuerzas'),p['physics']['show_equations'],key=prefix+'equations',help=t('Shows force symbols, signed component sums, and numerical substitutions.','Muestra símbolos de fuerzas, sumas de componentes con signo y sustituciones numéricas.'))
        p['font']=st.selectbox(t('Diagram font','Fuente del diagrama'),list(FONTS),index=list(FONTS).index(p['font']),format_func=option,key=prefix+'font',help=t('Choose sans, serif, Courier/typewriter, monospace, and more. Portable alternatives are used if a font is unavailable.','Elige sans, serif, Courier/máquina de escribir, monoespaciada y más. Se usa una alternativa si falta la fuente.'))
        p['shape']=st.selectbox(t('Object shape','Forma del objeto'),['Rectangle','Square','Circle','Triangle'],index=['Rectangle','Square','Circle','Triangle'].index(p['shape']),format_func=option,key=prefix+'shape',help=t('Used when no image is attached.','Se usa cuando no hay imagen.'))
        upload=st.file_uploader(t('Object image (up to 5 MB)','Imagen del objeto (hasta 5 MB)'),type=['png','jpg','jpeg'],key=force_prefix+'image',help=t('The image is saved inside your .fbd file.','La imagen se guarda dentro del archivo .fbd.'))
        if upload is not None:
            try:
                candidate=copy.deepcopy(p); candidate['image']=base64.b64encode(upload.getvalue()).decode('ascii')
                p['image']=validate_project({'format':'FreeBody','version':1,'diagram':candidate})['image']
            except (ValueError,OSError,TypeError) as e: st.error(str(e))
        if p['image'] and st.button(t('Remove image','Quitar imagen')):
            p['image']=None; st.session_state.revision+=1; st.rerun()
        if p['mode']=='Advanced':
            p['inclined_angle']=adjustable_slider(t('Ramp angle (°)','Ángulo del plano (°)'),-45.,45.,p['inclined_angle'],key=prefix+'inclined_angle',help=t('Tilts the ramp and object together. Relative force directions follow this slope.','Inclina el plano y el objeto juntos. Las direcciones relativas siguen esta inclinación.'),spanish=spanish)
        count=st.number_input(t('Number of forces','Número de fuerzas'),1,10,len(p['forces']),key=force_prefix+'count',help=t('Add up to 10 forces. A zero magnitude hides its arrow.','Añade hasta 10 fuerzas. Una magnitud de cero oculta la flecha.'))
        while len(p['forces'])<count: p['forces'].append(dict(label=f'F{len(p["forces"])+1}',magnitude=0.,angle=0.,color='Black'))
        p['forces']=p['forces'][:count]
        for k,v in p['physics'].items():
            if k.endswith('_force') and v is not None and v>=count: p['physics'][k]=None
        with st.expander(t('Physics tools','Herramientas de física'),expanded=True):
            cfg=p['physics']
            cfg['mass']=st.number_input(t('Mass (kg)','Masa (kg)'),.001,1000000.,float(cfg['mass']),key=prefix+'mass',help=t('Used for weight and acceleration. Mass must be positive.','Se usa para el peso y la aceleración. La masa debe ser positiva.'))
            if p['mode']=='Advanced':
                cfg['gravity']=st.number_input(t('Gravitational field g (m/s²)','Campo gravitacional g (m/s²)'),0.,1000.,float(cfg['gravity']),key=prefix+'g',help=t('Default 10 m/s² for classroom calculations.','Por defecto 10 m/s² para los cálculos en clase.'))
            cfg['auto_gravity']=st.toggle(t('Calculate gravity from mass','Calcular gravedad a partir de la masa'),cfg['auto_gravity'],key=prefix+'auto_gravity',help=t('Calculates mg vertically down; your manual value is retained when switched off.','Calcula mg verticalmente hacia abajo; conserva el valor manual al desactivarse.'))
            if cfg['auto_gravity']:
                indices=list(range(len(p['forces']))); chosen=physics.role_index(p,'gravity')
                cfg['gravity_force']=st.selectbox(t('Gravity force to calculate','Fuerza gravitacional a calcular'),indices,index=chosen if chosen is not None else 0,format_func=lambda i:f"{i+1}. {p['forces'][i]['label']}",key=force_prefix+'gravity_role',help=t('Choose the existing force representing weight.','Elige la fuerza existente que representa el peso.'))
            cfg['show_acceleration']=st.toggle(t('Show acceleration','Mostrar aceleración'),cfg['show_acceleration'],key=prefix+'acceleration',help=t('Uses a = net force / mass. The dashed orange arrow is acceleration, not another force.','Usa a = fuerza neta / masa. La flecha naranja discontinua es aceleración, no otra fuerza.'))
            cfg['auto_normal']=st.toggle(t('Calculate normal force automatically','Calcular fuerza normal automáticamente'),cfg['auto_normal'],key=prefix+'auto_normal',help=t('Balances all perpendicular force components; assumes no acceleration through the surface.','Equilibra todos los componentes perpendiculares; supone aceleración perpendicular nula.'))
            cfg['auto_friction']=st.toggle(t('Calculate friction automatically','Calcular fricción automáticamente'),cfg['auto_friction'],key=prefix+'auto_friction',help=t('Uses μN for sliding, or the required static friction up to μsN when not moving.','Usa μN al deslizar, o la fricción estática necesaria hasta μsN en reposo.'))
            if cfg['auto_normal'] or cfg['auto_friction']:
                indices=list(range(len(p['forces'])));chosen=physics.role_index(p,'normal')
                cfg['normal_force']=st.selectbox(t('Normal force','Fuerza normal'),indices,index=chosen if chosen is not None else 0,format_func=lambda i:f"{i+1}. {p['forces'][i]['label']}",key=force_prefix+'normal_role',help=t('Used as the contact force for μN.','Se usa como fuerza de contacto para μN.'))
            if cfg['auto_friction']:
                indices=list(range(len(p['forces'])));chosen=physics.role_index(p,'friction')
                cfg['friction_force']=st.selectbox(t('Friction force','Fuerza de fricción'),indices,index=chosen if chosen is not None else 0,format_func=lambda i:f"{i+1}. {p['forces'][i]['label']}",key=force_prefix+'friction_role',help=t('This existing force becomes calculated; its manual value is preserved.','Esta fuerza pasa a ser calculada; se conserva su valor manual.'))
                motions=['Not moving','Right','Left'] if p['mode']=='General' else ['Not moving','Up the surface of the ramp','Down the surface of the ramp']
                if cfg['motion'] not in motions: cfg['motion']='Not moving'
                cfg['motion']=st.selectbox(t('Direction of motion','Dirección del movimiento'),motions,index=motions.index(cfg['motion']),format_func=lambda v:t('Not moving','En reposo') if v=='Not moving' else option(v),key=force_prefix+'motion',help=t('Not moving selects static friction. Otherwise kinetic friction opposes motion along the surface.','En reposo selecciona fricción estática. En movimiento, la fricción cinética se opone al movimiento sobre el plano.'))
                cfg['friction_coefficient']=st.number_input(t('Coefficient μs' if cfg['motion']=='Not moving' else 'Coefficient μk','Coeficiente μs' if cfg['motion']=='Not moving' else 'Coeficiente μk'),0.,10.,float(cfg['friction_coefficient']),step=.01,key=prefix+'mu',help=t('Dimensionless. Static friction can be smaller than μsN; kinetic friction equals μkN.','Sin unidades. La fricción estática puede ser menor que μsN; la cinética es μkN.'))
            cfg['equilibrium']=st.toggle(t('Solve for equilibrium','Resolver para equilibrio'),cfg['equilibrium'],key=prefix+'equilibrium',help=t('Solves one force for zero net force in both axes. Dynamic equilibrium means constant velocity, not acceleration.','Resuelve una fuerza para fuerza neta cero en ambos ejes. Equilibrio dinámico significa velocidad constante, no aceleración.'))
            if cfg['equilibrium']:
                indices=list(range(len(p['forces']))); chosen=physics.role_index(p,'unknown')
                cfg['unknown_force']=st.selectbox(t('Unknown force','Fuerza desconocida'),indices,index=chosen if chosen is not None else 0,format_func=lambda i:f"{i+1}. {p['forces'][i]['label']}",key=force_prefix+'unknown_role',help=t('Set its direction in the force editor. The app checks whether one magnitude can balance both axes.','Define su dirección en el editor. La app verifica si una magnitud puede equilibrar ambos ejes.'))
        calculated_slots={}
        for i,f in enumerate(p['forces']):
            with st.expander(t(f'Force {i+1}',f'Fuerza {i+1}'),expanded=True):
                label=f['label']
                for en,es in NAMES:
                    if label==en and spanish: label=es
                entered=st.text_input(t('Name','Nombre'),label,max_chars=80,key=force_prefix+f'label{i}'+str(spanish),help=t('Give this force a descriptive name.','Escribe un nombre que describa la fuerza.'))
                f['label']=next((en for en,es in NAMES if entered in (en,es)),entered)
                gravity_controlled=p['physics']['auto_gravity'] and i==physics.role_index(p,'gravity')
                unknown_controlled=p['physics']['equilibrium'] and i==physics.role_index(p,'unknown')
                normal_controlled=p['physics']['auto_normal'] and i==physics.role_index(p,'normal')
                friction_controlled=p['physics']['auto_friction'] and i==physics.role_index(p,'friction')
                if gravity_controlled or unknown_controlled or normal_controlled or friction_controlled:
                    calculated_slots[i]=st.empty()
                else:
                    f['magnitude']=st.number_input(t('Magnitude (N)','Magnitud (N)'),0.,10000.,float(f['magnitude']),key=force_prefix+f'm{i}',help=t('Force strength in newtons; arrow lengths use the same scale.','Intensidad en newtons; las flechas usan la misma escala.'))
                if normal_controlled or friction_controlled:
                    st.caption(t('🧮 Direction follows the contact calculation','🧮 La dirección sigue el cálculo de contacto'))
                elif gravity_controlled:
                    st.caption(t('🧮 Direction: vertically downward','🧮 Dirección: verticalmente hacia abajo'))
                elif p['mode']=='General':
                    direction=f.get('direction',min(DIRECTIONS,key=lambda k:abs((f['angle']-DIRECTIONS[k]+180)%360-180)))
                    f['direction']=st.selectbox(t('Direction','Dirección'),list(DIRECTIONS),index=list(DIRECTIONS).index(direction),format_func=option,key=force_prefix+f'd{i}',help=t('Choose Up, Down, Left, or Right.','Elige Arriba, Abajo, Izquierda o Derecha.'))
                    f['angle']=DIRECTIONS[f['direction']]
                else:
                    modes=['Degrees','Relative to the surface of the ramp']
                    f['angle_mode']=st.radio(t('Force direction method','Método de dirección de la fuerza'),modes,index=modes.index(f.get('angle_mode','Degrees')),format_func=option,key=force_prefix+f'am{i}',help=t('Use an absolute angle or a direction that follows the ramp.','Usa un ángulo absoluto o una dirección que siga el plano.'))
                    if f['angle_mode']=='Degrees':
                        f['angle']=st.number_input(t('Force angle (°)','Ángulo de la fuerza (°)'),0.,360.,float(f['angle']),key=force_prefix+f'a{i}',help=t('Counterclockwise from right: 0 right, 90 up, 180 left, 270 down.','Desde la derecha, en sentido antihorario: 0 derecha, 90 arriba, 180 izquierda, 270 abajo.'))
                    else:
                        f['relative']=st.selectbox(t('Relative direction','Dirección relativa'),list(RELATIVE),index=list(RELATIVE).index(f.get('relative','Up the surface of the ramp')),format_func=option,key=force_prefix+f'r{i}',help=t('Perpendicular points away from the ramp. On a descending ramp, uphill points toward its higher end.','Perpendicular apunta hacia fuera del plano. En un plano descendente, subir apunta al extremo más alto.'))

                f['color']=st.selectbox(t('Color','Color'),list(COLORS),index=list(COLORS).index(f['color']),format_func=option,key=force_prefix+f'c{i}',help=t('Match the arrow to its entry in the key.','Relaciona la flecha con su entrada en la leyenda.'))
        calculation=evaluated(p)
        for i,slot in calculated_slots.items():
            value=calculation.project['forces'][i]['magnitude'] if i in calculation.calculated else None
            tip=calculation.calculated[i][int(spanish)] if i in calculation.calculated else t('No valid calculated value. See the calculation message.','No hay valor calculado válido. Consulta el mensaje del cálculo.')
            slot.number_input(t('Magnitude (N) 🧮','Magnitud (N) 🧮'),value=float(value) if value is not None else None,disabled=True,key=force_prefix+f'computed{i}{value}',help=tip)
        p['arrow_offset']=adjustable_slider(t('Arrow offset','Desplazamiento de flechas'),0.,4.,p['arrow_offset'],key=prefix+'offset',help=t('Distance from the center to each arrow tail, along its force direction.','Distancia del centro a la cola de cada flecha, en la dirección de la fuerza.'),spanish=spanish,step=.1)
        p['show_ground']=st.checkbox(t('Show ground','Mostrar suelo'),p['show_ground'],key=prefix+'ground',help=t('Draw a ground or inclined-plane reference line.','Dibuja una línea de referencia para el suelo o plano inclinado.'))
        p['show_grid']=st.checkbox(t('Show grid','Mostrar cuadrícula'),p['show_grid'],key=prefix+'grid',help=t('Adds a rectangular reference grid. Diagram distances are not meters.','Añade una cuadrícula rectangular de referencia. Las distancias del diagrama no son metros.'))
        p['show_axes']=st.checkbox(t('Show axes','Mostrar ejes'),p['show_axes'],key=prefix+'axes',help=t('Shows horizontal x and vertical y axes through the object center.','Muestra los ejes horizontal x y vertical y en el centro del objeto.'))
        p['show_polar']=st.checkbox(t('Show polar coordinates (degrees)','Mostrar coordenadas polares (grados)'),p['show_polar'],key=prefix+'polar',help=t('Shows circles and angle rays every 30°. Angles increase counterclockwise from the right. Circles are diagram reference distances.','Muestra círculos y rayos cada 30°. Los ángulos aumentan en sentido antihorario desde la derecha. Los círculos son distancias de referencia del diagrama.'))
        if p['mode']=='Advanced':
            for k,en,es,step in [('arrow_thickness','Arrow thickness','Grosor de flechas',.1),('arrowhead_size','Arrowhead size','Tamaño de puntas',1.),('font_size','Label size','Tamaño de etiquetas',1)]:
                lo,hi=LIMITS[k]
                p[k]=adjustable_slider(t(en,es),lo,hi,p[k],key=prefix+k,help=t('Adjust the appearance of the diagram; force magnitudes stay unchanged.','Ajusta la apariencia del diagrama; las magnitudes de las fuerzas se conservan.'),spanish=spanish,step=step)
            p['show_box']=st.checkbox(t('Frame the force key','Enmarcar la leyenda'),p['show_box'],key=prefix+'box',help=t('Adds a border around the force labels.','Añade un borde alrededor de las etiquetas.'))
            p['box_color']=st.color_picker(t('Object color','Color del objeto'),p['box_color'],key=prefix+'boxcolor',help=t('Changes the built-in shape color.','Cambia el color de la forma del objeto.'))
    with preview:
        st.subheader(t('Live diagram','Diagrama en vivo'))
        if p['show_net'] and resultant(p)[2]<1e-8:
            st.info(t('Balanced forces: net force is 0 N, so no resultant arrow is drawn.','Fuerzas equilibradas: la fuerza neta es 0 N, por lo que no se dibuja una flecha resultante.'))
        calculation=evaluated(p)
        for level,en,es in calculation.messages: getattr(st,level)(t(en,es))
        st.caption(t('◆ / 🧮 = app-calculated. Hover over a calculated value for its formula.','◆ / 🧮 = calculado por la app. Pasa el cursor sobre un valor calculado para ver su fórmula.'))
        if p['physics']['show_acceleration']:
            ax_,ay_,acceleration,acc_angle=calculation.acceleration
            direction=t('no direction (zero acceleration)','sin dirección (aceleración cero)') if acc_angle is None else f'{acc_angle:.1f}°'
            st.caption(t(f'🧮 Acceleration: {acceleration:.2f} m/s² · {direction}',f'🧮 Aceleración: {acceleration:.2f} m/s² · {direction}'),help=t('a = ΣF / m. Direction follows net force, not necessarily the direction of motion.','a = ΣF / m. La dirección sigue la fuerza neta, no necesariamente la dirección del movimiento.'))
        fig=draw_diagram(p,spanish)
        st.pyplot(fig,transparent=True,bbox_inches='tight')
        png=io.BytesIO(); fig.savefig(png,format='png',transparent=True,bbox_inches='tight'); plt.close(fig)
        st.download_button(t('Save diagram (.fbd)','Guardar diagrama (.fbd)'),export_project(p),'diagram.fbd','application/octet-stream',help=t('Reopen this file later; it includes the attached image.','Abre este archivo después; incluye la imagen adjunta.'))
        st.download_button(t('Download transparent PNG','Descargar PNG transparente'),png.getvalue(),'diagram.png','image/png',help=t('Use this picture in your lab report or slides.','Usa esta imagen en tu informe o presentación.'))
        fx,fy,magnitude,angle=resultant(p)
        direction=(f'{angle:.1f}°' if angle is not None else t('undefined (zero force)','indefinido (fuerza cero)'))
        st.caption(t(f'🧮 Resultant total force: {magnitude:.1f} N · angle = {direction} · x = {fx:.1f} N · y = {fy:.1f} N',f'🧮 Fuerza resultante total: {magnitude:.1f} N · ángulo = {direction} · x = {fx:.1f} N · y = {fy:.1f} N'))
        if p['physics']['show_equations']:
            st.subheader(t('🧮 Force equations','🧮 Ecuaciones de fuerzas'))
            st.caption(t('Calculated from the currently displayed forces. Component values are signed; a negative value points opposite the positive axis.','Calculadas a partir de las fuerzas actuales. Los componentes tienen signo; un valor negativo apunta contra el eje positivo.'),help=t('ΣF is the vector sum of every force, even when only the net arrow is displayed.','ΣF es la suma vectorial de todas las fuerzas, incluso cuando solo se muestra la flecha neta.'))
            latex_rows,key=equations.rows(calculation.project,force_angle)
            for row in latex_rows: st.latex(row)
            with st.expander(t('Force symbol key','Clave de símbolos de fuerzas')):
                for symbol,label in key:
                    for en,es in NAMES:
                        if spanish and label==en:label=es
                    st.write(f'F_{symbol}: {label}')
                st.caption(t('Subscripts use the initials of the saved force labels. Repeated initials receive numbers.','Los subíndices usan las iniciales de las etiquetas guardadas. Las iniciales repetidas reciben números.'))
        st.caption(t('Angles are measured counterclockwise from the right (+x).','Los ángulos se miden en sentido antihorario desde la derecha (+x).'))


if __name__=='__main__': main()
