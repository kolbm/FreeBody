import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import json
import base64
import io

# Configuration
COLOR_OPTIONS = {"Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500", "Purple": "#800080", "Black": "#000000", "White": "#FFFFFF", "Gray": "#D3D3D3"}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, arrow_thickness, arrowhead_size, arrow_offset, show_ground, font_size, show_box, box_color):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    rad = np.radians(inclined_angle) if advanced_mode else 0
    t_rot = transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)
    
    # Ground
    if show_ground:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
    
    # Object flush with ground
    y_pos = 0
    if uploaded_file:
        img = Image.open(io.BytesIO(base64.b64decode(uploaded_file)))
        ax.imshow(img, extent=[-1, 1, y_pos, y_pos+2], transform=t_rot + ax.transData)
    else:
        patch = patches.Rectangle((-1, y_pos), 2, 1, color='gray', transform=t_rot + ax.transData)
        ax.add_patch(patch)
        
    # Forces
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    for i in range(len(forces)):
        dx, dy = [c * (forces[i]/20) for c in direction_map[directions[i]]]
        ax.arrow(0, y_pos+0.5, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box else None
        ax.text(dx*1.2, y_pos+0.5+dy*1.2, labels[i], fontsize=font_size, color=colors[i], bbox=bbox)
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 2])
    
    # Preset Defaults
    defaults = [(100, "Normal Force", "Up", "Green"), (100, "Gravitational Force", "Down", "Red"), 
                (100, "Applied Force", "Right", "Blue"), (50, "Friction Force", "Left", "Purple")]
    
    with col1:
        st.header("Technical Settings")
        import_f = st.file_uploader("Import FBD", type=["fbd"])
        
        # Default to 4 forces
        num_forces = st.number_input("Number of Forces:", 1, 10, 4)
        forces, labels, colors, directions = [], [], [], []
        for i in range(num_forces):
            with st.expander(f"Force {i+1}"):
                forces.append(st.number_input("Mag", value=defaults[i][0] if i<4 else 5, key=f"m{i}"))
                labels.append(st.text_input("Lbl", defaults[i][1] if i<4 else f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox("Col", list(COLOR_OPTIONS.keys()), index=list(COLOR_OPTIONS.keys()).index(defaults[i][3]) if i<4 else 0, key=f"c{i}")])
                directions.append(st.selectbox("Dir", DIRECTION_OPTIONS, index=DIRECTION_OPTIONS.index(defaults[i][2] if i<4 else "Up"), key=f"d{i}"))
                
    with col2:
        # Drawing
        fig = draw_fbd(forces, directions, labels, colors, False, 0, "Rectangle", None, 2.0, 0.3, 0.0, True, 12, True, "Gray")
        st.pyplot(fig)

if __name__ == "__main__": main()
