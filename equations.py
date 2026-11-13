"""Safe LaTeX symbols and signed force equations for student-created labels."""
import collections
import math
import re
import unicodedata
import physics

def symbols(forces):
    bases=[]
    for f in forces:
        words=re.findall(r'[^\W\d_]+',f['label'],re.UNICODE)
        initial=''.join(w[0].upper() for w in words)
        base=unicodedata.normalize('NFKD',initial).encode('ascii','ignore').decode()
        bases.append(re.sub('[^A-Z]','',base) or 'F')
    counts=collections.Counter(bases);used=collections.Counter();result=[]
    for base in bases:
        used[base]+=1
        result.append(base+str(used[base]) if counts[base]>1 else base)
    return result

def force_symbol(initial,component=None,vector=False):
    sub=r'\mathrm{'+initial+'}'+(','+component if component else '')
    return (r'\vec F' if vector else 'F')+'_{'+sub+'}'

def rows(project,angle_fn):
    p=project if project.get('_resolved') else physics.resolve(project,angle_fn).project
    ids=symbols(p['forces']);cfg=physics.settings(p);digits=cfg.get('precision',2)
    def fmt(value):
        if abs(value)<.5*10**(-digits):value=0.
        return f'{value:.{digits}f}'
    vectors=[physics.vector(f,angle_fn(p,f)) for f in p['forces']]
    x,y,mag,angle=physics.total(p,angle_fn)
    out=[]
    if p['show_components']:
        for name,index,result in [('x',0,x),('y',1,y)]:
            symbolic=' + '.join(force_symbol(i,name) for i in ids)
            values=' + '.join(r'\left('+fmt(v[index])+r'\right)' for v in vectors)
            out.append(r'\sum F_'+name+' = '+symbolic)
            out.append(r'\sum F_'+name+' = '+values+' = '+fmt(result)+r'\,\mathrm{N}')
            if cfg['show_acceleration']:
                out.append(r'a_'+name+r'=\frac{\sum F_'+name+r'}{m}=\frac{'+fmt(result)+'}{'+fmt(cfg['mass'])+'}='+fmt(result/cfg['mass'])+r'\,\mathrm{m/s^2}')
    else:
        symbolic=' + '.join(force_symbol(i,vector=True) for i in ids)
        out.append(r'\sum\vec F = '+symbolic)
        out.append(r'\sum\vec F = \begin{pmatrix}'+fmt(x)+r'\\'+fmt(y)+r'\end{pmatrix}\,\mathrm{N}')
        out.append(r'\left|\sum\vec F\right| = '+fmt(mag)+r'\,\mathrm{N}')
        if cfg['show_acceleration']:
            out.append(r'\vec a=\frac{\sum\vec F}{m}=\begin{pmatrix}'+fmt(x/cfg['mass'])+r'\\'+fmt(y/cfg['mass'])+r'\end{pmatrix}\,\mathrm{m/s^2}')
    return out,list(zip(ids,[f['label'] for f in p['forces']]))
