import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.patches as patches

# Translation Dictionary
TRANSLATIONS = {
    "English": {
        "title": "Free Body Diagram Generator",
        "tech": "Technical Settings",
        "forces": "Forces",
        "mag": "Magnitude",
        "lbl": "Label",
        "col": "Color",
        "upload": "Upload Image",
        "diagram": "Diagram",
        "aes": "Aesthetic Settings",
        "at": "Arrow Thickness",
        "ao": "Arrow Offset",
        "fs": "Font Size",
        "box": "Show Box",
        "bc": "Box Color",
        "gen": "Generate"
    },
    "Spanish": {
        "title": "Generador de Diagramas de Cuerpo Libre",
        "tech": "Configuración Técnica",
        "forces": "Fuerzas",
        "mag": "Magnitud",
        "lbl": "Etiqueta",
        "col": "Color",
        "upload": "Subir Imagen",
        "diagram": "Diagrama",
        "aes": "Configuración Estética",
        "at": "Grosor de Flecha",
        "ao": "Desplazamiento de Flecha",
        "fs": "Tamaño de Fuente",
        "box": "Mostrar Caja",
        "bc": "Color de Caja",
        "gen": "Generar"
    }
}

COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#800080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF", "None": "none"
}

def main():
    st.set_page_config(layout="wide")
    lang = st.sidebar.radio("Language / Idioma", ["English", "Spanish"])
    t = TRANSLATIONS[lang]
    
    st.title(t["title"])
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header(t["tech"])
        num_forces = st.number_input(t["forces"], 1, 10, 2)
        forces, labels, colors = [], [], []
        for i in range(num_forces):
            with st.expander(f"{t['forces']} {i+1}"):
                forces.append(st.number_input(t["mag"], value=5, key=f"m{i}"))
                labels.append(st.text_input(t["lbl"], f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox(t["col"], list(COLOR_OPTIONS.keys()), key=f"c{i}")])
        uploaded_file = st.file_uploader(t["upload"])
        
    with col2:
        st.header(t["diagram"])
        
        # Link logic for aesthetics
        at_val = st.slider(t["at"], 1.0, 5.0, 2.0, key="at_s")
        ao_val = st.slider(t["ao"], 0.0, 2.0, 0.0, key="ao_s")
        fs_val = st.slider(t["fs"], 8, 24, 12, key="fs_s")
        
        show_box = st.checkbox(t["box"])
        box_color = COLOR_OPTIONS[st.selectbox(t["bc"], list(COLOR_OPTIONS.keys()), index=10)]
        
        if st.button(t["gen"]):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
            ax.set_aspect('equal', adjustable='box')
            ax.axis('off')
            patch = patches.Rectangle((-1, 0), 2, 1, color='gray', fill=True)
            ax.add_patch(patch)
            for i in range(len(forces)):
                ax.arrow(0, 0.5, 0, forces[i]/5, head_width=0.2, head_length=0.3, fc=colors[i], ec=colors[i], linewidth=at_val)
                ax.text(0.2, 0.5+forces[i]/5, labels[i], fontsize=fs_val, color=colors[i])
            ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
            st.pyplot(fig)

if __name__ == "__main__": main()
