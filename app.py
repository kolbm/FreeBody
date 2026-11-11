import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import json

# Translation Dictionary
TRANSLATIONS = {
    "English": {"title": "Free Body Diagram Generator", "tech": "Technical Settings", "aes": "Aesthetic Settings", "gen": "Generate", "export": "Export FBD", "import": "Import FBD", "mode": "Mode", "angle": "Inclined Plane Angle", "forces": "Number of Forces", "shape": "Object Shape", "upload": "Upload Image", "at": "Arrow Thickness", "ao": "Arrow Offset", "fs": "Font Size"},
    "Spanish": {"title": "Generador de Diagramas", "tech": "Configuración Técnica", "aes": "Configuración Estética", "gen": "Generar", "export": "Exportar FBD", "import": "Importar FBD", "mode": "Modo", "angle": "Ángulo del Plano Inclinado", "forces": "Número de Fuerzas", "shape": "Forma del Objeto", "upload": "Subir Imagen", "at": "Grosor de Flecha", "ao": "Desplazamiento", "fs": "Tamaño de Fuente"}
}

COLOR_OPTIONS = {"Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500", "Purple": "#800080", "Black": "#000000", "White": "#FFFFFF"}
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]

def draw_fbd(forces, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, arrow_thickness, arrowhead_size, arrow_offset, show_ground, font_size, show_box, box_color, show_grid):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    # Ramp
    if show_ground:
        rad = np.radians(inclined_angle) if advanced_mode else 0
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
    # Ground line function
    def ramp_y(x): return np.tan(rad) * x

    
    # Object
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, ramp_y(0), ramp_y(0)+1])
    else:
        patch = patches.Rectangle((-1, ramp_y(0)), 2, 1, color='gray')
        ax.add_patch(patch)
        
    # Forces
    for i in range(len(forces)):
        ax.arrow(0, 1, 0, forces[i]/5, head_width=0.2, head_length=0.3, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        ax.text(0.1, 1+forces[i]/5, labels[i], fontsize=font_size, color=colors[i])
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    lang = st.sidebar.radio("Language / Idioma", ["English", "Spanish"])
    t = TRANSLATIONS[lang]
    st.title(t["title"])
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header(t["tech"])
        import_f = st.file_uploader(t["import"], type=["fbd"])
        mode = st.radio(t["mode"], ["Regular", "Advanced"])
        inclined_angle = st.number_input(t["angle"], 0, 45, 0)
        num_forces = st.number_input(t["forces"], 1, 10, 2)
        shape = st.selectbox(t["shape"], SHAPE_OPTIONS)
        uploaded_file = st.file_uploader(t["upload"], type=["png", "jpg"])
        
        forces, labels, colors = [], [], []
        for i in range(num_forces):
            forces.append(st.number_input(f"F{i+1} Mag", value=5, key=f"m{i}"))
            labels.append(st.text_input(f"F{i+1} Label", f"F{i+1}", key=f"l{i}"))
            colors.append(COLOR_OPTIONS[st.selectbox(f"F{i+1} Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
        
        if st.button(t["gen"]): st.session_state.generate = True
        if st.button(t["export"]): pass

    with col2:
        st.header(t["aes"])
        a_t = st.columns(2)
        arrow_thickness = a_t[0].slider(t["at"], 1.0, 5.0, 2.0)
        a_t[1].number_input("Input", 1.0, 5.0, arrow_thickness, key="at_n")
        
        a_o = st.columns(2)
        arrow_offset = a_o[0].slider(t["ao"], 0.0, 2.0, 0.0)
        a_o[1].number_input("Input ", 0.0, 2.0, arrow_offset, key="ao_n")
        
        fig = draw_fbd(forces, labels, colors, mode=="Advanced", inclined_angle, shape, uploaded_file, arrow_thickness, 0.3, arrow_offset, True, 12, False, "none", False)
        st.pyplot(fig)

if __name__ == "__main__": main()
