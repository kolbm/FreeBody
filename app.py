import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms

# Configuration
COLOR_OPTIONS = {"Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500", "Purple": "#800080", "Black": "#000000", "White": "#FFFFFF"}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, arrow_thickness, arrowhead_size, arrow_offset, show_ground):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    rad = np.radians(inclined_angle) if advanced_mode else 0
    t_rot = transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)
    
    # Ground
    if show_ground:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
    
    # Object
    y_pos = 0 
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, y_pos, y_pos+2], transform=t_rot + ax.transData)
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, y_pos), 2, 1, color='gray', transform=t_rot + ax.transData)
        elif shape == "Square": patch = patches.Rectangle((-1, y_pos), 2, 2, color='gray', transform=t_rot + ax.transData)
        elif shape == "Circle": patch = patches.Circle((0, y_pos+1), 1, color='gray', transform=t_rot + ax.transData)
        else: patch = patches.Polygon([(-1, y_pos), (1, y_pos), (0, y_pos+2)], color='gray', transform=t_rot + ax.transData)
        ax.add_patch(patch)
        
    # Forces
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    for i in range(len(forces)):
        dx, dy = [c * (forces[i]/5) for c in direction_map[directions[i]]]
        ax.arrow(0, y_pos+0.5, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        ax.text(dx*1.2, y_pos+0.5+dy*1.2, labels[i], fontsize=12, fontweight='bold', color=colors[i])
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 2])
    with col1:
        num_forces = st.number_input("Number of Forces:", 1, 10, 2)
        forces, labels, colors, directions = [], [], [], []
        # Pre-fill defaults
        defaults = [("Normal", "Up"), ("Gravity", "Down")]
        for i in range(num_forces):
            with st.expander(f"Force {i+1}"):
                forces.append(st.number_input("Mag", value=5, key=f"m{i}"))
                labels.append(st.text_input("Lbl", defaults[i][0] if i < 2 else f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox("Col", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
                directions.append(st.selectbox("Dir", DIRECTION_OPTIONS, index=DIRECTION_OPTIONS.index(defaults[i][1] if i < 2 else "Up"), key=f"d{i}"))
        
    with col2:
        fig = draw_fbd(forces, directions, labels, colors, False, 0, "Rectangle", None, 2.0, 0.3, 0.0, True)
        st.pyplot(fig)

if __name__ == "__main__": main()
