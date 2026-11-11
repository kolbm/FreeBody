import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms

COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#808080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00"
}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["Sans-serif", "Serif", "Monospace", "Fantasy", "Cursive", "Courier New", "Verdana", "Arial"]
TITLE_IMAGE_URL = "https://github.com/kolbm/FreeBody/blob/main/title.jpg?raw=true"

def draw_fbd(forces, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_val, angle_modes, custom_angles, show_grid, show_magnitudes, unit, mass_val, show_mass, arrow_offset, show_ground, motion_dir, motion_corner):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    
    rad = np.radians(inclined_angle) if advanced_mode else 0
    t_rot = transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)

    if show_grid:
        if advanced_mode:
            for i in np.arange(-5, 6, 1):
                p1 = t_rot.transform([i, -5]); p2 = t_rot.transform([i, 5])
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k--', alpha=0.1)
                p3 = t_rot.transform([-5, i]); p4 = t_rot.transform([5, i])
                ax.plot([p3[0], p4[0]], [p3[1], p4[1]], 'k--', alpha=0.1)
        else:
            ax.grid(True, linestyle='--', alpha=0.3)
    
    ax.axis('off')

    if show_ground and inclined_angle >= 0:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
        ax.fill_between([-5, 5], -6, [np.tan(rad)*-5, np.tan(rad)*5], color='sandybrown', alpha=0.3)
        ax.text(3, np.tan(rad)*3 + 0.5, f"Ramp: {inclined_angle}°", fontsize=10, color='brown', fontfamily=font_choice.lower(), bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    y_flush = 0.5
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, 0, 2], transform=t_rot + ax.transData)
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, 0), 2, 1, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Square": patch = patches.Rectangle((-1, 0), 2, 2, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Circle": patch = patches.Circle((0, 1), 1, color='gray', fill=True, transform=t_rot + ax.transData)
        else: patch = patches.Polygon([(-1, 0), (1, 0), (0, 2)], color='gray', fill=True, transform=t_rot + ax.transData)
        ax.add_patch(patch)
        
    if show_mass:
        ax.text(0, y_flush+0.5, f"m={mass_val}kg", fontsize=10, ha='center', color='black', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7))

    max_val = max(forces) if forces else 1
    scale = 2.0 / max_val if max_val > 0 else 1
    net_dx, net_dy = 0, 0
    off_x, off_y = arrow_offset * np.sin(rad), arrow_offset * np.cos(rad)
    
    for i in range(len(forces)):
        f = forces[i] * scale
        if advanced_mode:
            if angle_modes[i] == "Up the ramp": a = rad
            elif angle_modes[i] == "Down the ramp": a = rad + np.pi
            elif angle_modes[i] == "Perpendicular to ramp": a = rad + np.pi/2
            else: a = np.radians(custom_angles[i])
            dx, dy = f * np.cos(a), f * np.sin(a)
        else:
            dx, dy = 0, f
        
        net_dx += dx; net_dy += dy
        ax.arrow(off_x, y_flush+0.5+off_y, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        lbl = labels[i]
        if show_magnitudes: lbl += f" ({forces[i]}{unit[0]})"
        ax.text(off_x+dx*1.2, y_flush+0.5+off_y+dy*1.2, lbl, fontsize=12, fontweight='bold', fontfamily=font_choice.lower(), ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))

    if show_net_force:
        ax.arrow(off_x, y_flush+0.5+off_y, net_dx, net_dy, head_width=arrowhead_size*1.5, head_length=arrowhead_size*2, fc=net_color, ec=net_color, linewidth=arrow_thickness+1, linestyle='-', alpha=0.8)
        if show_net_val:
            ax.text(off_x+net_dx*1.2, y_flush+0.5+off_y+net_dy*1.2, f"Net: {np.hypot(net_dx, net_dy)/scale:.1f}{unit[0]}", color=net_color, fontweight='bold', fontfamily=font_choice.lower(), ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))

    if motion_dir != "None":
        corners = {"Top-Right": (4, 4), "Top-Left": (-4, 4), "Bottom-Right": (4, -4), "Bottom-Left": (-4, -4)}
        x, y = corners[motion_corner]
        ax.text(x, y, f"Motion: {motion_dir}", fontsize=12, fontweight='bold', bbox=dict(facecolor='yellow', alpha=0.5))

    plt.figtext(0.5, 0.05, "Generated using the Free Body Diagram Generator: freebody.streamlit.app", ha="center", fontsize=8, color='gray')
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    plt.tight_layout()
    return fig

def main():
    st.sidebar.image(TITLE_IMAGE_URL, use_container_width=True)
    mode = st.radio("Mode", ["Regular", "Advanced"])
    inclined_angle = st.slider("Inclined Plane Angle", 0, 45, 0) if mode == "Advanced" else 0
    num_forces = st.number_input("Number of Forces:", 1, 10, 2)
    shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
    uploaded_file = st.file_uploader("Insert Picture", type=["png", "jpg", "jpeg"])
    
    st.sidebar.header("Settings")
    show_ground = st.sidebar.checkbox("Display Ground/Ramp", True)
    arrow_thickness = st.sidebar.slider("Arrow Line Thickness", 1.0, 5.0, 2.0)
    arrowhead_size = st.sidebar.slider("Arrowhead Size", 0.1, 1.0, 0.3)
    arrow_offset = st.sidebar.slider("Arrow Center Offset", 0.0, 2.0, 0.0)
    font_choice = st.sidebar.selectbox("Font Style", FONT_OPTIONS)
    show_grid = st.sidebar.checkbox("Show Grid/Axes")
    show_magnitudes = st.sidebar.checkbox("Show Magnitudes in Labels")
    show_mass = st.sidebar.checkbox("Show Object Mass")
    mass_val = st.number_input("Object Mass (kg)", value=1.0)
    
    st.sidebar.subheader("Motion Indicator")
    motion_dir = st.sidebar.selectbox("Motion Direction", ["None", "Up", "Down", "Left", "Right"])
    motion_corner = st.sidebar.selectbox("Indicator Corner", ["Top-Right", "Top-Left", "Bottom-Right", "Bottom-Left"])
    
    st.sidebar.subheader("Net Force")
    show_net_force = st.sidebar.checkbox("Show Net Force")
    net_color = COLOR_OPTIONS[st.sidebar.selectbox("Net Force Color", list(COLOR_OPTIONS.keys()))]
    show_net_val = st.sidebar.checkbox("Show Net Force Value")
    
    forces, labels, colors, angle_modes, custom_angles = [], [], [], [], []
    for i in range(num_forces):
        with st.expander(f"Force {i+1}"):
            c1, c2, c3, c4 = st.columns(4)
            forces.append(c1.number_input("Magnitude", value=5, key=f"m{i}"))
            if mode == "Advanced":
                angle_modes.append(c2.selectbox("Angle Mode", ["Custom Angle", "Up the ramp", "Down the ramp", "Perpendicular to ramp"], key=f"am{i}"))
                custom_angles.append(c3.number_input("Angle", value=0, key=f"a{i}") if angle_modes[-1] == "Custom Angle" else 0)
            else:
                angle_modes.append("Custom Angle"); custom_angles.append(0)
            labels.append(c3.text_input("Label", f"F{i+1}", key=f"l{i}"))
            colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])

    if st.button("Generate"):
        fig = draw_fbd(forces, labels, colors, mode=="Advanced", inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_val, False, angle_modes, custom_angles, show_grid, show_magnitudes, "Newtons (N)", mass_val, show_mass, arrow_offset, show_ground, motion_dir, motion_corner)
        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True, dpi=200)
        st.image(buf)
        st.download_button("Download", buf, "fbd.png", "image/png")

if __name__ == "__main__": main()
