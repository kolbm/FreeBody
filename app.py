# File: fbd_creator_app_v3.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# Function to draw Free Body Diagram
def draw_fbd(forces, directions, labels, colors, object_type, object_size, use_axes):
    """
    Draw a Free Body Diagram using Matplotlib.
    
    Args:
        forces: List of force magnitudes.
        directions: List of angles or (dx, dy) directions.
        labels: List of labels for each force.
        colors: List of colors for each force.
        object_type: Type of object (rectangle or circle).
        object_size: Size of the object.
        use_axes: If True, directions are treated as (up/down, left/right) axes.
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Draw the object
    if object_type == 'Rectangle':
        ax.add_patch(plt.Rectangle((-object_size/2, -object_size/2), object_size, object_size, fill=False, linewidth=2))
    else:
        ax.add_patch(plt.Circle((0, 0), object_size/2, fill=False, linewidth=2))

    # Draw forces from the center of the object
    center_x, center_y = 0, 0

    for i in range(len(forces)):
        if use_axes:
            dx = forces[i] * directions[i][0]  # Left-right axis
            dy = forces[i] * directions[i][1]  # Up-down axis
        else:
            angle_rad = np.radians(directions[i])
            dx = forces[i] * np.cos(angle_rad)
            dy = forces[i] * np.sin(angle_rad)

        ax.arrow(center_x, center_y, dx, dy, head_width=0.2, head_length=0.2, fc=colors[i], ec=colors[i], linewidth=1.5)
        plt.text(center_x + dx, center_y + dy, f'{labels[i]} ({forces[i]}N)', fontsize=10, color=colors[i])

    ax.set_xlim(-object_size, object_size)
    ax.set_ylim(-object_size, object_size)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Free Body Diagram")
    plt.close(fig)
    return fig

# Streamlit UI
def main():
    st.title("Free Body Diagram Creator (Enhanced)")
    st.write("Create a Free Body Diagram (FBD) with options for angles or up/down and left/right axes.")

    # Object selection
    object_type = st.selectbox("Select the object type:", ["Rectangle", "Circle"])
    object_size = st.slider("Select object size (units):", min_value=1, max_value=10, value=5)

    # Use angles or axes
    use_axes = st.radio("Select input method for forces:", ["Use Angles", "Use Axes"]) == "Use Axes"

    # Number of forces
    num_forces = st.number_input("Number of forces:", min_value=1, max_value=10, value=2, step=1)

    # User inputs for forces
    st.subheader("Input Forces")
    forces = []
    directions = []
    labels = []
    colors = []

    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            magnitude = st.number_input(f"Force {i+1} Magnitude (N):", min_value=1.0, step=0.5, key=f"force_{i}")
        with col2:
            if use_axes:
                left_right = st.selectbox("Left-Right Axis:", ["Left (-1)", "None (0)", "Right (1)"], key=f"lr_{i}")
                up_down = st.selectbox("Up-Down Axis:", ["Down (-1)", "None (0)", "Up (1)"], key=f"ud_{i}")
                directions.append((float(left_right.split()[1][1]), float(up_down.split()[1][1])))
            else:
                angle = st.number_input(f"Angle (degrees):", min_value=0, max_value=360, step=1, key=f"angle_{i}")
                directions.append(angle)
        with col3:
            label = st.text_input(f"Label:", value=f"Force {i+1}", key=f"label_{i}")
        with col4:
            color = st.color_picker("Pick arrow color:", "#ff0000", key=f"color_{i}")

        forces.append(magnitude)
        labels.append(label)
        colors.append(color)

    # Generate the Free Body Diagram
    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, directions, labels, colors, object_type, object_size, use_axes)
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
