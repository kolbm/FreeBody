"""Safe LaTeX symbols and signed force equations for student-created labels."""
import collections
import math
import re
import unicodedata
import physics
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

def symbols(forces):
    bases=[]
    for index,f in enumerate(forces):
        words=re.findall(r'[^\W\d_]+',f['label'],re.UNICODE)
        words=[w for w in words if w.casefold() not in {'force','forces','fuerza','fuerzas'}]
        initial=''.join(w[0].upper() for w in words)
        base=unicodedata.normalize('NFKD',initial).encode('ascii','ignore').decode()
        bases.append(re.sub('[^A-Z]','',base) or str(index+1))
    counts=collections.Counter(bases);used=collections.Counter();result=[]
    for base in bases:
        used[base]+=1
        result.append(base+str(used[base]) if counts[base]>1 else base)
    return result

def force_symbol(initial,component=None,vector=False):
    sub=r'\mathrm{'+initial+'}'+(','+component if component else '')
    return (r'\vec{F}' if vector else 'F')+'_{'+sub+'}'

def rows(project,angle_fn,spanish=False):
    p=project if project.get('_resolved') else physics.resolve(project,angle_fn).project
    ids=symbols(p['forces']);cfg=physics.settings(p);digits=cfg.get('precision',2)
    def fmt(value):
        if abs(value)<.5*10**(-digits):value=0.
        return f'{value:.{digits}f}'
    def arithmetic(values):
        nonzero=[v for v in values if abs(v)>physics.EPS]
        if not nonzero:return fmt(0.)+r'\,\mathrm{N}'
        expression=fmt(nonzero[0])+r'\,\mathrm{N}'
        for value in nonzero[1:]:expression+=(' - ' if value<0 else ' + ')+fmt(abs(value))+r'\,\mathrm{N}'
        return expression
    vectors=[physics.vector(f,angle_fn(p,f)) for f in p['forces']]
    x,y,mag,angle=physics.total(p,angle_fn)
    out=[]
    if p['show_components']:
        for name,unit in physics.component_axes(p):
            result=x*unit[0]+y*unit[1]
            component_values=[v[0]*unit[0]+v[1]*unit[1] for v in vectors]
            symbolic=' + '.join(force_symbol(i,name) for i in ids)
            values=' + '.join(r'\left('+fmt(value)+r'\right)' for value in component_values)
            out.append(r'\sum F_'+name+' = '+symbolic)
            out.append(r'\sum F_'+name+' = '+values+' = '+fmt(result)+r'\,\mathrm{N}')
            if cfg['show_acceleration']:
                out.append(r'a_'+name+r'=\frac{\sum F_'+name+r'}{m}=\frac{'+fmt(result)+'}{'+fmt(cfg['mass'])+'}='+fmt(result/cfg['mass'])+r'\,\mathrm{m/s^2}')
    else:
        symbolic=' + '.join(force_symbol(i,vector=True) for i in ids)
        out.append(r'\sum\vec{F} = '+symbolic)
        horizontal='Horizontal';vertical='Vertical'
        net='Fuerza neta' if spanish else 'Net force'
        out.append(r'\mathrm{'+horizontal+r':}\quad '+arithmetic([v[0] for v in vectors])+' = '+fmt(x)+r'\,\mathrm{N}')
        out.append(r'\mathrm{'+vertical+r':}\quad '+arithmetic([v[1] for v in vectors])+' = '+fmt(y)+r'\,\mathrm{N}')
        out.append(r'\mathrm{'+net.replace(' ',r'\ ')+r':}\quad F_{\mathrm{net}} = '+fmt(mag)+r'\,\mathrm{N}')
        if cfg['show_acceleration']:
            out.append(r'a_x = '+fmt(x/cfg['mass'])+r'\,\mathrm{m/s^2}\qquad a_y = '+fmt(y/cfg['mass'])+r'\,\mathrm{m/s^2}')
    return out,list(zip(ids,[f['label'] for f in p['forces']]))

def latex_snippet(latex_rows):
    return '\n\n'.join('\\[\n'+row+'\n\\]' for row in latex_rows)

def latex_document(latex_rows,spanish=False):
    # Only app-generated math and a fixed title are emitted, never raw force labels.
    title='Ecuaciones de fuerzas' if spanish else 'Force equations'
    source=('\\documentclass{article}\n\\usepackage[T1]{fontenc}\n'
            '\\usepackage[utf8]{inputenc}\n\\usepackage{amsmath}\n'
            '\\pagestyle{empty}\n\\begin{document}\n\\section*{'+title+'}\n'
            +latex_snippet(latex_rows)+'\n\\end{document}\n')
    return source.encode('utf-8')

def png_bytes(latex_rows,title='Force equations',font_size=16,dpi=180):
    """Render the same formulas without a system LaTeX installation or matrix shorthand."""
    fig=Figure(figsize=(8,2),dpi=dpi,facecolor='white');canvas=FigureCanvasAgg(fig)
    items=[fig.text(0,0,title,fontsize=font_size+2,fontweight='bold',color='black',fontfamily='DejaVu Sans',ha='left',va='top')]
    for row in latex_rows:
        items.append(fig.text(0,0,'$'+row+'$',fontsize=font_size,color='black',fontfamily='DejaVu Sans',math_fontfamily='dejavusans',ha='left',va='top'))
    canvas.draw();renderer=canvas.get_renderer()
    boxes=[item.get_window_extent(renderer) for item in items]
    padding=dpi*.18;gap=dpi*.12
    width=max(box.width for box in boxes)+padding*2
    height=sum(box.height for box in boxes)+gap*(len(items)-1)+padding*2
    fig.set_size_inches(width/dpi,height/dpi,forward=True)
    top=height-padding
    for item,box in zip(items,boxes):
        item.set_position((padding/width,top/height));top-=box.height+gap
    output=io.BytesIO();fig.savefig(output,format='png',facecolor='white',transparent=False,dpi=dpi)
    return output.getvalue()
