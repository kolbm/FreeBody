import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms

# Configuration
COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#800080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF", "None": "none"
}

def draw_fbd(forces, labels, colors, arrow_thickness, arrow_offset, font_size, show_box, box_color, uploaded_file):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    # Object
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, 0, 2])
    else:
        patch = patches.Rectangle((-1, 0), 2, 1, color='gray', fill=True)
        ax.add_patch(patch)
    
    # Forces
    center_y = 0.5
    for i in range(len(forces)):
        f = forces[i]
        dx, dy = 0, f/5  # Simplified direction for now
        tx, ty = 0, arrow_offset
        ax.arrow(0, center_y, dx, dy, head_width=0.2, head_length=0.3, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box and box_color != "none" else None
        ax.text(dx*1.2, center_y+dy*1.2, labels[i], fontsize=font_size, ha='center', color=colors[i], bbox=bbox)
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Technical Settings")
        num_forces = st.number_input("Forces:", 1, 10, 2)
        forces, labels, colors = [], [], []
        for i in range(num_forces):
            with st.expander(f"Force {i+1}"):
                forces.append(st.number_input("Mag", value=5, key=f"m{i}"))
                labels.append(st.text_input("Lbl", f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox("Col", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
        uploaded_file = st.file_uploader("Upload Image")
        
    with col2:
        st.header("Diagram")
        # Linked Sliders & Number inputs
        a_t = st.columns(2)
        arrow_thickness = a_t[0].slider("Arrow Thickness", 1.0, 5.0, 2.0, key="at_s")
        arrow_thickness = a_t[1].number_input("Arrow Thickness", 1.0, 5.0, arrow_thickness, key="at_n")
        
        a_o = st.columns(2)
        arrow_offset = a_o[0].slider("Arrow Offset", 0.0, 2.0, 0.0, key="ao_s")
        arrow_offset = a_o[1].number_input("Arrow Offset", 0.0, 2.0, arrow_offset, key="ao_n")
        
        f_s = st.columns(2)
        font_size = f_s[0].slider("Font Size", 8, 24, 12, key="fs_s")
        font_size = f_s[1].number_input("Font Size", 8, 24, font_size, key="fs_n")
        
        show_box = st.checkbox("Show Box")
        box_color = COLOR_OPTIONS[st.selectbox("Box Color", list(COLOR_OPTIONS.keys()), index=10)]
        
        fig = draw_fbd(forces, labels, colors, arrow_thickness, arrow_offset, font_size, show_box, box_color, uploaded_file)
        st.pyplot(fig)

if __name__ == "__main__": main()
