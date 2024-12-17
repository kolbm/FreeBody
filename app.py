# File: fbd_creator_app_v2.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# Function to draw Free Body Diagram
def draw_fbd(forces, angles, positions, labels, colors, object_type, object_size):
    """
    Draw a Free Body Diagram using Matplotlib.
    
    Args:
        forces: List of force magnitudes.
        angles: List of force angles (in degrees).
        positions: List of (x, y) positions for force arrows.
        labels: List of labels for each force.
        colors: List of colors for each force.
        object_type: Type of object (rectangle or circle).
        object_size: Size of the object.
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Draw the object
    if object_type == 'Rectangle':
        ax.add_patch(plt.Rectangle((-object_size/2, -object_size/2), object_size, object_size, fill=False, linewidth=2))
    else:
        ax.add_patch(plt.Circle((0, 0), object_size/2, fill=False, linewidth=2))

    # Draw forces
    for i in range(len(forces)):
        x, y = positions[i]
        angle_rad = np.radians(angles[i])
        dx = forces[i] * np.cos(angle_rad)
        dy = forces[i] * np.sin(angle_rad)

        ax.arrow(x, y, dx, dy, head_width=0.2, head_length=0.2, fc=colors[i], ec=colors[i], linewidth=1.5)
        plt.text(x + dx, y + dy, f'{labels[i]} ({forces[i]}N)', fontsize=10, color=colors[i])

    ax.set_xlim(-object_size, object_size)
    ax.set_ylim(-object_size, object_size)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Free Body Diagram")
    plt.close(fig)
    return fig

# Preset Templates
templates = {
    "Simple Gravity": {
        "forces": [10],
        "angles": [270],
        "positions": [(0, 0)],
        "labels": ["Weight"],
        "colors": ["red"]
    },
    "Two Forces Balanced": {
        "forces": [10, 10],
        "angles": [0, 180],
        "positions": [(0, 0), (0, 0)],
        "labels": ["Force 1", "Force 2"],
        "colors": ["blue", "green"]
    },
    "Three Forces": {
        "forces": [10, 15, 20],
        "angles": [0, 120, 240],
        "positions": [(0, 0), (0, 0), (0, 0)],
        "labels": ["Force A", "Force B", "Force C"],
        "colors": ["orange", "purple", "cyan"]
    }
}

# Streamlit UI
def main():
    st.title("Enhanced Free Body Diagram Creator")
    st.write("Create a Free Body Diagram (FBD) with labels, custom arrow colors, and templates.")

    # Object selection
    object_type = st.selectbox("Select the object type:", ["Rectangle", "Circle"])
    object_size = st.slider("Select object size (units):", min_value=1, max_value=10, value=5)

    # Preset templates or custom input
    use_template = st.checkbox("Use a preset template")

    if use_template:
        template_name = st.selectbox("Select a template:", list(templates.keys()))
        template = templates[template_name]
        forces = template["forces"]
        angles = template["angles"]
        positions = template["positions"]
        labels = template["labels"]
        colors = template["colors"]
    else:
        # Number of forces
        num_forces = st.number_input("Number of forces:", min_value=1, max_value=10, value=2, step=1)

        # User inputs for forces
        st.subheader("Input Forces")
        forces = []
        angles = []
        positions = []
        labels = []
        colors = []
        for i in range(num_forces):
            st.write(f"### Force {i+1}")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                magnitude = st.number_input(f"Magnitude (N):", min_value=1.0, step=0.5, key=f"force_{i}")
            with col2:
                angle = st.number_input(f"Angle (degrees):", min_value=0, max_value=360, step=1, key=f"angle_{i}")
            with col3:
                x = st.number_input(f"X-position:", min_value=-10.0, max_value=10.0, step=0.5, key=f"x_{i}")
                y = st.number_input(f"Y-position:", min_value=-10.0, max_value=10.0, step=0.5, key=f"y_{i}")
            with col4:
                label = st.text_input(f"Label:", value=f"Force {i+1}", key=f"label_{i}")
            with col5:
                color = st.color_picker("Pick arrow color:", "#ff0000", key=f"color_{i}")
            forces.append(magnitude)
            angles.append(angle)
            positions.append((x, y))
            labels.append(label)
            colors.append(color)

    # Generate the Free Body Diagram
    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, angles, positions, labels, colors, object_type, object_size)
        st.pyplot(fig)

        # Download as Image
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="Download FBD as Image",
            data=buf,
            file_name="free_body_diagram.png",
            mime="image/png"
        )

if __name__ == "__main__":
    main()
