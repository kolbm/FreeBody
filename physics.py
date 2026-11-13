"""Pure physics calculations. Source/manual force values are never overwritten."""
from dataclasses import dataclass, field
import copy
import math

EPS=1e-8
SETTINGS=dict(mass=10.,gravity=10.,auto_gravity=False,show_acceleration=False,gravity_force=None)

@dataclass
class Evaluation:
    project: dict
    calculated: dict=field(default_factory=dict)
    messages: list=field(default_factory=list)
    steps: list=field(default_factory=list)
    acceleration: tuple=(0.,0.,0.,None)

def settings(project):
    return {**SETTINGS,**project.get('physics',{})}

def role_index(project, role):
    explicit=settings(project).get(role+'_force')
    if explicit is not None and 0<=explicit<len(project['forces']): return explicit
    words={'gravity':['Gravitational Force','Gravity','Weight','Fuerza gravitacional','Peso'],
           'normal':['Normal Force','Fuerza normal'], 'friction':['Frictional Force','Friction','Fuerza de fricción','Fricción']}
    return next((i for i,f in enumerate(project['forces']) if f['label'].casefold() in [w.casefold() for w in words[role]]),None)

def vector(force, angle):
    rad=math.radians(angle)
    return force['magnitude']*math.cos(rad),force['magnitude']*math.sin(rad)

def total(project, angle_fn):
    vectors=[vector(f,angle_fn(project,f)) for f in project['forces']]
    x=sum(v[0] for v in vectors); y=sum(v[1] for v in vectors)
    x=0. if abs(x)<EPS else x; y=0. if abs(y)<EPS else y
    mag=math.hypot(x,y)
    return x,y,mag,math.degrees(math.atan2(y,x))%360 if mag>EPS else None

def resolve(project, angle_fn):
    p=copy.deepcopy(project); result=Evaluation(p); cfg=settings(p)
    if cfg['auto_gravity']:
        index=role_index(p,'gravity')
        if index is None:
            result.messages.append(('error','Select a gravitational force to calculate its value.','Selecciona una fuerza gravitacional para calcular su valor.'))
        else:
            f=p['forces'][index]
            f.update(magnitude=cfg['mass']*cfg['gravity'],angle=270.,direction='Down',angle_mode='Degrees')
            explanation=(f"Calculated: F = mg = {cfg['mass']:g} × {cfg['gravity']:g} = {f['magnitude']:g} N; vertically downward.",
                         f"Calculado: F = mg = {cfg['mass']:g} × {cfg['gravity']:g} = {f['magnitude']:g} N; verticalmente hacia abajo.")
            result.calculated[index]=explanation;result.steps.append(explanation)
    x,y,mag,angle=total(p,angle_fn)
    result.acceleration=(x/cfg['mass'],y/cfg['mass'],mag/cfg['mass'],angle)
    p['_resolved']=True;p['_calculated']=result.calculated
    return result

def validate_settings(raw, force_count):
    if not isinstance(raw,dict): raise ValueError('Invalid physics settings / Configuración física inválida')
    cfg=copy.deepcopy(SETTINGS)
    for key in cfg:
        if key in raw: cfg[key]=raw[key]
    for key,lo,hi in [('mass',.001,1000000.),('gravity',0.,1000.)]:
        value=cfg[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
            raise ValueError('Invalid '+key+' / Valor inválido')
    for key in ['auto_gravity','show_acceleration']:
        if not isinstance(cfg[key],bool): raise ValueError('Invalid '+key)
    for key in ['gravity_force']:
        if cfg[key] is not None and (type(cfg[key]) is not int or not 0<=cfg[key]<force_count): raise ValueError('Invalid force selection / Selección de fuerza inválida')
    return cfg
