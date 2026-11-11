"""Bilingual, live free-body diagrams with self-contained .fbd projects."""
import base64
import copy
import io
import json
import math
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import patches
from PIL import Image

COLORS = {'Green': '#008000', 'Red': '#FF0000', 'Blue': '#0000FF', 'Purple': '#800080', 'Orange': '#FFA500', 'Black': '#000000', 'White': '#FFFFFF'}
ES = {'Green':'Verde','Red':'Rojo','Blue':'Azul','Purple':'Morado','Orange':'Naranja','Black':'Negro','White':'Blanco','Rectangle':'Rectángulo','Square':'Cuadrado','Circle':'Círculo','Triangle':'Triángulo','General':'General','Advanced':'Avanzado'}
NAMES = [('Normal Force','Fuerza normal'),('Gravitational Force','Fuerza gravitacional'),('Applied Force','Fuerza aplicada'),('Frictional Force','Fuerza de fricción')]
DEFAULT = dict(forces=[dict(label=n[0], magnitude=m, angle=a, color=c) for n,m,a,c in zip(NAMES,[100.,100.,100.,50.],[90.,270.,0.,180.],list(COLORS)[:4])], shape='Rectangle', mode='General', inclined_angle=0., arrow_thickness=2., arrowhead_size=16., arrow_offset=1.2, font_size=12, show_ground=True, show_grid=False, show_box=False, box_color='#808080', image=None)
LIMITS = {'inclined_angle':(-45,45),'arrow_thickness':(1,5),'arrowhead_size':(8,30),'arrow_offset':(0,4),'font_size':(8,24)}

def validate_project(data):
    if not isinstance(data,dict) or data.get('format') != 'FreeBody' or data.get('version') != 1:
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
    for k in ['show_ground','show_grid','show_box']:
        if not isinstance(p[k],bool): raise ValueError('Invalid '+k)
    def valid_color(c):
        return isinstance(c,str) and len(c)==7 and c[0]=='#' and all(x in '0123456789abcdefABCDEF' for x in c[1:])
    if not valid_color(p['box_color']): raise ValueError('Invalid color')
    if not isinstance(p['forces'],list) or not 1<=len(p['forces'])<=10: raise ValueError('Use 1–10 forces / Usa 1–10 fuerzas')
    for f in p['forces']:
        if not isinstance(f,dict) or not isinstance(f.get('label'),str) or len(f['label'])>80 or f.get('color') not in COLORS: raise ValueError('Invalid force / Fuerza inválida')
        for k,lo,hi in [('magnitude',0,10000),('angle',0,360)]:
            v=f.get(k)
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError('Invalid '+k)
    if p['image'] is not None:
        raw=base64.b64decode(p['image'],validate=True)
        if len(raw)>5*1024*1024: raise ValueError('Image exceeds 5 MB / Imagen mayor de 5 MB')
        with Image.open(io.BytesIO(raw)) as im:
            if im.width*im.height>16000000: raise ValueError('Image too large / Imagen demasiado grande')
            im.verify()
    return p

def export_project(p):
    return json.dumps({'format':'FreeBody','version':1,'diagram':p},ensure_ascii=False,allow_nan=False).encode('utf-8')

def draw_diagram(p, spanish=False):
    fig,ax=plt.subplots(figsize=(8,8),dpi=150)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    ax.set_aspect('equal'); ax.set_axis_off()
    offset=p['arrow_offset']; maxmag=max((f['magnitude'] for f in p['forces']),default=1) or 1
    reach=offset+3.5
    angle=p['inclined_angle'] if p['mode']=='Advanced' else 0
    if p['show_ground']:
        r=math.radians(angle)
        ax.plot([-reach,reach],[-1-math.tan(r)*reach,-1+math.tan(r)*reach],color='saddlebrown',lw=2,zorder=0)
    if p['show_grid']:
        for x in range(-int(reach),int(reach)+1):
            ax.axhline(x,color='gray',alpha=.15,lw=.5,zorder=0); ax.axvline(x,color='gray',alpha=.15,lw=.5,zorder=0)
    if p['image']:
        with Image.open(io.BytesIO(base64.b64decode(p['image']))) as im:
            ax.imshow(im.copy(),extent=(-1,1,-1,1),zorder=1)
    else:
        kw=dict(facecolor=p['box_color'],edgecolor='black',alpha=.55,zorder=1)
        if p['shape']=='Circle': obj=patches.Circle((0,0),1,**kw)
        elif p['shape']=='Triangle': obj=patches.RegularPolygon((0,0),3,radius=1,**kw)
        else: obj=patches.Rectangle((-1,-.65 if p['shape']=='Rectangle' else -1),2,1.3 if p['shape']=='Rectangle' else 2,angle=angle,rotation_point='center',**kw)
        ax.add_patch(obj)
    # Separate parallel arrows sideways; tails always advance along their own direction.
    used=[]
    for i,f in enumerate(p['forces']):
        r=math.radians(f['angle']); u=(math.cos(r),math.sin(r)); perp=(-u[1],u[0])
        same=sum(abs(((f['angle']-a+180)%360)-180)<8 for a in used); used.append(f['angle'])
        lane=.22*same; start=(offset*u[0]+lane*perp[0],offset*u[1]+lane*perp[1])
        length=3*f['magnitude']/maxmag
        end=(start[0]+length*u[0],start[1]+length*u[1])
        if length>0: ax.add_patch(patches.FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=p['arrowhead_size'],lw=p['arrow_thickness'],color=COLORS[f['color']],shrinkA=0,shrinkB=0,zorder=3))
        # Labels live in a separate key, so they cannot cover arrows or each other.
        label=f['label']
        for en,es in NAMES:
            if label==en and spanish: label=es
        ax.plot([],[],color=COLORS[f['color']],lw=3,label=f'{i+1}. {label}  ·  {f["magnitude"]:g} N  ·  {f["angle"]:g}°')
    ax.set_xlim(-reach-1,reach+1); ax.set_ylim(-reach-1,reach+1)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.02),frameon=p['show_box'],fontsize=p['font_size'],ncol=1)
    return fig

def main():
    st.set_page_config(page_title='FreeBody',layout='wide')
    spanish=st.sidebar.radio('Language / Idioma',['English','Español'])=='Español'
    def t(en,es): return es if spanish else en
    def option(s): return ES.get(s,s) if spanish else s
    st.title(t('Free Body Diagram Generator','Generador de diagramas de cuerpo libre'))
    st.caption(t('Edit a value to update the diagram. Angles: 0° right, 90° up, 180° left, 270° down.','Cambia un valor para actualizar el diagrama. Ángulos: 0° derecha, 90° arriba, 180° izquierda, 270° abajo.'))
    if 'project' not in st.session_state: st.session_state.project=copy.deepcopy(DEFAULT)
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
        st.session_state.project=copy.deepcopy(DEFAULT); st.session_state.revision+=1
    p=st.session_state.project
    prefix=str(st.session_state.revision)
    controls,preview=st.columns([1,2])
    with controls:
        p['mode']=st.radio(t('Features','Funciones'),['General','Advanced'],index=['General','Advanced'].index(p['mode']),format_func=option,key=prefix+'mode',help=t('Advanced adds incline, grid, arrow styling, and label options.','Avanzado añade inclinación, cuadrícula y estilos de flechas y etiquetas.'))
        p['shape']=st.selectbox(t('Object shape','Forma del objeto'),['Rectangle','Square','Circle','Triangle'],index=['Rectangle','Square','Circle','Triangle'].index(p['shape']),format_func=option,key=prefix+'shape',help=t('Used when no image is attached.','Se usa cuando no hay imagen.'))
        upload=st.file_uploader(t('Object image (up to 5 MB)','Imagen del objeto (hasta 5 MB)'),type=['png','jpg','jpeg'],key=prefix+'image',help=t('The image is saved inside your .fbd file.','La imagen se guarda dentro del archivo .fbd.'))
        if upload is not None:
            try:
                candidate=copy.deepcopy(p); candidate['image']=base64.b64encode(upload.getvalue()).decode('ascii')
                p['image']=validate_project({'format':'FreeBody','version':1,'diagram':candidate})['image']
            except (ValueError,OSError,TypeError) as e: st.error(str(e))
        if p['image'] and st.button(t('Remove image','Quitar imagen')):
            p['image']=None; st.session_state.revision+=1; st.rerun()
        count=st.number_input(t('Number of forces','Número de fuerzas'),1,10,len(p['forces']),key=prefix+'count',help=t('Add up to 10 forces. A zero magnitude hides its arrow.','Añade hasta 10 fuerzas. Una magnitud de cero oculta la flecha.'))
        while len(p['forces'])<count: p['forces'].append(dict(label=f'F{len(p["forces"])+1}',magnitude=0.,angle=0.,color='Black'))
        p['forces']=p['forces'][:count]
        for i,f in enumerate(p['forces']):
            with st.expander(t(f'Force {i+1}',f'Fuerza {i+1}'),expanded=True):
                label=f['label']
                for en,es in NAMES:
                    if label==en and spanish: label=es
                entered=st.text_input(t('Name','Nombre'),label,max_chars=80,key=prefix+f'label{i}'+str(spanish),help=t('Give this force a descriptive name.','Escribe un nombre que describa la fuerza.'))
                f['label']=next((en for en,es in NAMES if entered in (en,es)),entered)
                f['magnitude']=st.number_input(t('Magnitude (N)','Magnitud (N)'),0.,10000.,float(f['magnitude']),key=prefix+f'm{i}',help=t('Force strength in newtons; arrow lengths use the same scale.','Intensidad en newtons; las flechas usan la misma escala.'))
                f['angle']=st.number_input(t('Direction (°)','Dirección (°)'),0.,360.,float(f['angle']),key=prefix+f'a{i}',help=t('Counterclockwise from right: 0 right, 90 up, 180 left, 270 down.','Desde la derecha, en sentido antihorario: 0 derecha, 90 arriba, 180 izquierda, 270 abajo.'))
                f['color']=st.selectbox(t('Color','Color'),list(COLORS),index=list(COLORS).index(f['color']),format_func=option,key=prefix+f'c{i}',help=t('Match the arrow to its entry in the key.','Relaciona la flecha con su entrada en la leyenda.'))
        p['arrow_offset']=st.slider(t('Arrow offset','Desplazamiento de flechas'),0.,4.,float(p['arrow_offset']),key=prefix+'offset',help=t('Distance from the center to each arrow tail, along its force direction.','Distancia del centro a la cola de cada flecha, en la dirección de la fuerza.'))
        p['show_ground']=st.checkbox(t('Show ground','Mostrar suelo'),p['show_ground'],key=prefix+'ground',help=t('Draw a ground or inclined-plane reference line.','Dibuja una línea de referencia para el suelo o plano inclinado.'))
        if p['mode']=='Advanced':
            for k,en,es,step in [('inclined_angle','Incline angle (°)','Ángulo del plano (°)',1.),('arrow_thickness','Arrow thickness','Grosor de flechas',.1),('arrowhead_size','Arrowhead size','Tamaño de puntas',1.),('font_size','Label size','Tamaño de etiquetas',1)]:
                lo,hi=LIMITS[k]
                p[k]=st.slider(t(en,es),float(lo),float(hi),float(p[k]),float(step),key=prefix+k,help=t('Adjust the appearance of the diagram; force magnitudes stay unchanged.','Ajusta la apariencia del diagrama; las magnitudes de las fuerzas se conservan.'))
            p['show_grid']=st.checkbox(t('Show grid','Mostrar cuadrícula'),p['show_grid'],key=prefix+'grid',help=t('Adds reference lines behind the object.','Añade líneas de referencia detrás del objeto.'))
            p['show_box']=st.checkbox(t('Frame the force key','Enmarcar la leyenda'),p['show_box'],key=prefix+'box',help=t('Adds a border around the force labels.','Añade un borde alrededor de las etiquetas.'))
            p['box_color']=st.color_picker(t('Object color','Color del objeto'),p['box_color'],key=prefix+'boxcolor',help=t('Changes the built-in shape color.','Cambia el color de la forma del objeto.'))
    with preview:
        st.subheader(t('Live diagram','Diagrama en vivo'))
        fig=draw_diagram(p,spanish)
        st.pyplot(fig,transparent=True,bbox_inches='tight')
        png=io.BytesIO(); fig.savefig(png,format='png',transparent=True,bbox_inches='tight'); plt.close(fig)
        st.download_button(t('Save diagram (.fbd)','Guardar diagrama (.fbd)'),export_project(p),'diagram.fbd','application/octet-stream',help=t('Reopen this file later; it includes the attached image.','Abre este archivo después; incluye la imagen adjunta.'))
        st.download_button(t('Download transparent PNG','Descargar PNG transparente'),png.getvalue(),'diagram.png','image/png',help=t('Use this picture in your lab report or slides.','Usa esta imagen en tu informe o presentación.'))
        fx=sum(f['magnitude']*math.cos(math.radians(f['angle'])) for f in p['forces']); fy=sum(f['magnitude']*math.sin(math.radians(f['angle'])) for f in p['forces'])
        st.caption(t(f'Net force: x = {fx:.1f} N; y = {fy:.1f} N',f'Fuerza neta: x = {fx:.1f} N; y = {fy:.1f} N'))

if __name__=='__main__': main()
