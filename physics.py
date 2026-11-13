"""Pure physics calculations. Source/manual force values are never overwritten."""
from dataclasses import dataclass, field
import copy
import math
import numpy as np

EPS=1e-8
SETTINGS=dict(mass=10.,gravity=10.,auto_gravity=False,show_acceleration=False,gravity_force=None,show_equations=True,equilibrium=False,unknown_force=None,auto_normal=False,normal_force=None,auto_friction=False,friction_force=None,friction_coefficient=.25,motion='Not moving',precision=2,component_basis='Horizontal / vertical')

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
           'unknown':['Applied Force','Fuerza aplicada'], 'normal':['Normal Force','Fuerza normal'], 'friction':['Frictional Force','Friction','Fuerza de fricción','Fricción']}
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

def component_axes(project):
    if project['mode']=='Advanced' and settings(project)['component_basis']=='Ramp parallel / perpendicular':
        theta=math.radians(project['inclined_angle']);sign=1. if theta>=0 else -1.
        return [(r'\parallel',np.array([sign*math.cos(theta),sign*math.sin(theta)])),(r'\perp',np.array([-math.sin(theta),math.cos(theta)]))]
    return [('x',np.array([1.,0.])),('y',np.array([0.,1.]))]


def resolve(project, angle_fn):
    p=copy.deepcopy(project); result=Evaluation(p); cfg=settings(p)
    def message(level,en,es): result.messages.append((level,en,es))
    def record(index,en,es):
        result.calculated[index]=(en,es);result.steps.append((en,es))
    if cfg['auto_gravity']:
        index=role_index(p,'gravity')
        if index is None: message('error','Select a gravitational force to calculate its value.','Selecciona una fuerza gravitacional para calcular su valor.')
        else:
            f=p['forces'][index];f.update(magnitude=cfg['mass']*cfg['gravity'],angle=270.,direction='Down',angle_mode='Degrees')
            record(index,f"Calculated: F = mg = {cfg['mass']:g} × {cfg['gravity']:g} = {f['magnitude']:g} N; vertically downward.",f"Calculado: F = mg = {cfg['mass']:g} × {cfg['gravity']:g} = {f['magnitude']:g} N; verticalmente hacia abajo.")
    roles={role:role_index(p,role) for role,enabled in [('normal',cfg['auto_normal']),('friction',cfg['auto_friction']),('unknown',cfg['equilibrium'])] if enabled}
    valid=True
    for role,index in roles.items():
        if index is None:
            message('error',f'Select the {role} force in Physics tools.',f'Selecciona la fuerza ({role}) en Herramientas de física.');valid=False
    selected=[i for i in roles.values() if i is not None]+list(result.calculated)
    if len(set(selected))!=len(selected):
        message('error','A force cannot be controlled by both calculations. Choose different forces for gravity, normal, friction and the unknown.','Una fuerza no puede tener dos cálculos automáticos. Elige fuerzas diferentes para gravedad, normal, fricción e incógnita.');valid=False
    slope=p['inclined_angle'] if p['mode']=='Advanced' else 0.
    rad=math.radians(slope);tangent=np.array([math.cos(rad),math.sin(rad)]);normal=np.array([-math.sin(rad),math.cos(rad)])
    normal_index=role_index(p,'normal');normal_value=0.
    if cfg['auto_friction'] and not cfg['auto_normal']:
        if normal_index is None or normal_index==roles.get('friction') or normal_index==roles.get('unknown'):
            message('error','Select a separate normal force, or turn on automatic normal force.','Selecciona una fuerza normal separada, o activa el cálculo automático de la normal.');valid=False
        else:
            nvector=np.array(vector(p['forces'][normal_index],angle_fn(p,p['forces'][normal_index])))
            normal_value=float(nvector@normal)
            if normal_value < -EPS or abs(float(nvector@tangent))>1e-7*max(1.,float(np.linalg.norm(nvector))):
                message('error','The normal force must point perpendicular to and away from the surface.','La fuerza normal debe apuntar perpendicularmente hacia fuera de la superficie.');valid=False
    if roles and valid:
        names=list(roles);basis=[]
        for name in names:
            if name=='normal':basis.append(normal)
            elif name=='friction':basis.append(tangent)
            else:
                a=math.radians(angle_fn(p,p['forces'][roles[name]]));basis.append(np.array([math.cos(a),math.sin(a)]))
        known=np.zeros(2)
        for i,f in enumerate(p['forces']):
            if i not in roles.values(): known+=np.array(vector(f,angle_fn(p,f)))
        rows=[];rhs=[]
        def balance(axis):
            rows.append([float(b@axis) for b in basis]);rhs.append(-float(known@axis))
        if cfg['auto_normal']: balance(normal)
        moving=cfg['motion']!='Not moving'
        motion_sign=1.
        if cfg['motion']=='Left':motion_sign=-1.
        elif cfg['motion']=='Up the surface of the ramp':motion_sign=1. if slope>=0 else -1.
        elif cfg['motion']=='Down the surface of the ramp':motion_sign=-1. if slope>=0 else 1.
        if cfg['auto_friction']:
            if moving:
                row=[0.]*len(names);row[names.index('friction')]=1.
                if cfg['auto_normal']:
                    row[names.index('normal')]=motion_sign*cfg['friction_coefficient'];constant=0.
                else:constant=-motion_sign*cfg['friction_coefficient']*normal_value
                rows.append(row);rhs.append(constant)
            else:balance(tangent)
        if cfg['equilibrium']:
            balance(np.array([1.,0.]));balance(np.array([0.,1.]))
        matrix=np.array(rows);values,_,rank,_=np.linalg.lstsq(matrix,np.array(rhs),rcond=None)
        tolerance=1e-7*max(1.,float(np.linalg.norm(rhs)))
        residual=float(np.linalg.norm(matrix@values-rhs))
        if rank<len(names):
            message('error','No unique solution: these automatic settings leave more unknowns than independent equations. For equilibrium with static friction, enter a force manually or specify motion.','No hay solución única: hay más incógnitas que ecuaciones independientes. Para equilibrio con fricción estática, introduce una fuerza manualmente o especifica movimiento.')
        elif residual>tolerance:
            message('error',f'No equilibrium solution in both axes (residual {residual:.3g} N). Entered forces are shown; change the unknown direction or other forces.',f'No hay solución de equilibrio en ambos ejes (residuo {residual:.3g} N). Se muestran las fuerzas introducidas; cambia la dirección de la incógnita u otras fuerzas.')
        else:
            solved=dict(zip(names,[0. if abs(v)<EPS else float(v) for v in values]));allowed=True
            if solved.get('unknown',0.) < -tolerance:
                message('error','No equilibrium solution in the selected direction. Reverse the unknown force direction.','No hay solución de equilibrio en la dirección elegida. Invierte la dirección de la fuerza desconocida.');allowed=False
            if solved.get('normal',normal_value) < -tolerance:
                if cfg['equilibrium']:
                    message('error','Equilibrium would require a negative normal force: contact cannot be maintained.','El equilibrio requeriría una fuerza normal negativa: no se puede mantener el contacto.');allowed=False
                else:
                    solved['normal']=0.
                    if 'friction' in solved:solved['friction']=0.
                    message('warning','Contact is lost: normal force and surface friction are zero.','Se pierde el contacto: la fuerza normal y la fricción son cero.')
            n=max(0.,solved.get('normal',normal_value));limit=cfg['friction_coefficient']*n
            if 'friction' in solved and not moving and abs(solved['friction'])>limit+tolerance:
                if cfg['equilibrium']:
                    message('error','Static friction cannot provide the force required for equilibrium. Increase the static coefficient or change the forces.','La fricción estática no puede proporcionar la fuerza necesaria para el equilibrio. Aumenta el coeficiente estático o cambia las fuerzas.');allowed=False
                else:
                    required=abs(solved['friction']);solved['friction']=math.copysign(limit,solved['friction'])
                    message('warning',f'Static friction limit exceeded: {required:.3g} N needed, {limit:.3g} N available. Rest is impossible; the diagram shows limiting static friction. Select motion and μk to model sliding.',f'Se supera el límite estático: se necesitan {required:.3g} N y hay {limit:.3g} N disponibles. No puede permanecer en reposo; se muestra la fricción estática límite. Selecciona movimiento y μk para modelar deslizamiento.')
            if allowed:
                for name,value in solved.items():
                    index=roles[name];f=p['forces'][index]
                    if name=='normal':
                        f.update(magnitude=max(0.,value),angle=(slope+90)%360,angle_mode='Degrees',direction='Up')
                        record(index,f'Calculated normal force: N = −Σ(other force components perpendicular to the surface) = {max(0.,value):g} N; assumes no perpendicular acceleration.',f'Normal calculada: N = −Σ(componentes de otras fuerzas perpendiculares al plano) = {max(0.,value):g} N; supone aceleración perpendicular nula.')
                    elif name=='friction':
                        f.update(magnitude=abs(value),angle=(slope+(180 if value<0 else 0))%360,angle_mode='Degrees',direction='Left' if value<0 else 'Right')
                        if moving:
                            en=f'Calculated kinetic friction: f = μk N = {cfg["friction_coefficient"]:g} × {n:g} = {abs(value):g} N, opposite motion.'
                            es=f'Fricción cinética calculada: f = μk N = {cfg["friction_coefficient"]:g} × {n:g} = {abs(value):g} N, contra el movimiento.'
                        else:
                            en=f'Calculated static friction: balances tangential tendency, capped at μs N = {limit:g} N; f = {abs(value):g} N.'
                            es=f'Fricción estática calculada: equilibra la tendencia tangencial, limitada a μs N = {limit:g} N; f = {abs(value):g} N.'
                        record(index,en,es)
                    else:
                        f['magnitude']=max(0.,value)
                        record(index,f'Calculated equilibrium force: {max(0.,value):g} N. Both x and y force balances verified; coupled automatic forces are solved together.',f'Fuerza de equilibrio calculada: {max(0.,value):g} N. Se verificaron ambos ejes; las fuerzas automáticas acopladas se resuelven juntas.')
                if cfg['auto_friction'] and not cfg['auto_normal']:
                    perpendicular=float(np.array(total(p,angle_fn)[:2])@normal)
                    if abs(perpendicular)>1e-6:
                        message('warning','The entered normal force does not balance perpendicular forces. Enable automatic normal force to impose surface contact without perpendicular acceleration.','La normal introducida no equilibra las fuerzas perpendiculares. Activa la normal automática para imponer contacto sin aceleración perpendicular.')
    x,y,mag,angle=total(p,angle_fn)
    result.acceleration=(x/cfg['mass'],y/cfg['mass'],mag/cfg['mass'],angle)
    p['_resolved']=True;p['_calculated']=result.calculated
    return result

def validate_settings(raw, force_count):
    if not isinstance(raw,dict): raise ValueError('Invalid physics settings / Configuración física inválida')
    cfg=copy.deepcopy(SETTINGS)
    for key in cfg:
        if key in raw: cfg[key]=raw[key]
    for key,lo,hi in [('mass',.001,1000000.),('gravity',0.,1000.),('friction_coefficient',0.,10.)]:
        value=cfg[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
            raise ValueError('Invalid '+key+' / Valor inválido')
    for key in ['auto_gravity','show_acceleration','show_equations','equilibrium','auto_normal','auto_friction']:
        if not isinstance(cfg[key],bool): raise ValueError('Invalid '+key)
    for key in ['gravity_force','unknown_force','normal_force','friction_force']:
        if cfg[key] is not None and (type(cfg[key]) is not int or not 0<=cfg[key]<force_count): raise ValueError('Invalid force selection / Selección de fuerza inválida')
    if cfg['motion'] not in ['Not moving','Right','Left','Up the surface of the ramp','Down the surface of the ramp']: raise ValueError('Invalid motion / Movimiento inválido')
    if type(cfg['precision']) is not int or not 0<=cfg['precision']<=6: raise ValueError('Invalid precision / Precisión inválida')
    if cfg['component_basis'] not in ['Horizontal / vertical','Ramp parallel / perpendicular']: raise ValueError('Invalid component basis / Ejes de componentes inválidos')
    return cfg
