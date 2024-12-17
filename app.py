# File: fbd_creator_app_v7.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# Function to draw Free Body Diagram with resultant vector
def draw_fbd(forces, directions, labels, colors, label_distance, show_resultant):
    """
    Draw a Free Body Diagram with proportional vector scaling and resultant vector.
    
    Args:
        forces: List of force magnitudes.
        directions: List of (dx, dy) directions.
        labels: List of labels for each force.
        colors: List of colors for each force.
        label_distance: Distance to place the labels away from the arrow tips.
        show_resultant: Boolean to display the resultant vector.
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes for a clean diagram

    # Determine scaling factor
    max_force = max(forces)
    scale_factor = 2.0 / max_force  # Ensures vectors are scaled appropriately
    
    # Object size (half the smallest force)
    object_size = min(forces) / 2.0

    # Draw rectangle with thicker border
    center_x, center_y = 0, 0
    rect_size = object_size * 1.5
    ax.add_patch(plt.Rectangle((-rect_size/2, -rect_size/2), rect_size, rect_size, 
                 fill=False, linewidth=4, color="black"))

    # Draw forces and compute resultant components
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    resultant_x, resultant_y = 0, 0

    for i in range(len(forces)):
        # Scale the forces to fit nicely in the diagram
        force = forces[i] * scale_factor
        dx = force * direction_map[directions[i]][0]
        dy = force * direction_map[directions[i]][1]

        # Update resultant components
        resultant_x += dx
        resultant_y += dy

        # Draw vector arrow
        ax.arrow(center_x, center_y, dx, dy, head_width=0.05 * scale_factor, 
                 head_length=0.1 * scale_factor, fc=colors[i], ec=colors[i], linewidth=2)

        # Add labels at the arrow's tip
        label_x = center_x + dx * (1 + label_distance)
        label_y = center_y + dy * (1 + label_distance)
        plt.text(label_x, label_y, labels[i], fontsize=12, fontweight='bold', color=colors[i], ha='center')

    # Draw resultant vector (offset to avoid overlap)
    if show_resultant:
        resultant_x_offset = resultant_x + 0.3
        resultant_y_offset = resultant_y + 0.3
        ax.arrow(center_x, center_y, resultant_x_offset, resultant_y_offset, 
                 head_width=0.05 * scale_factor, head_length=0.1 * scale_factor, 
                 fc='purple', ec='purple', linewidth=3, linestyle='--')
        plt.text(resultant_x_offset * (1 + label_distance), resultant_y_offset * (1 + label_distance), 
                 "Resultant", fontsize=12, fontweight='bold', color='purple', ha='center')

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    plt.title("Free Body Diagram", fontsize=14)
    plt.close(fig)
    return fig

# Streamlit UI
def main():
    st.title("Free Body Diagram Creator (Resultant Force)")
    st.write("Create a Free Body Diagram (FBD) with customizable labels and forces.")

    # Label distance adjustment
    label_distance = st.slider("Label distance from arrow tip (multiplier):", min_value=0.1, max_value=2.0, step=0.1, value=0.3)

    # Option to show resultant vector
    show_resultant = st.checkbox("Show resultant force vector", value=True)

    # Number of forces
    num_forces = st.number_input("Number of forces:", min_value=1, max_value=10, value=3, step=1)

    # User inputs for forces
    st.subheader("Input Forces")
    forces = []
    directions = []
    labels = []
    colors = []

    direction_options = ["Up", "Down", "Left", "Right"]

    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            magnitude = st.number_input(f"Magnitude (N):", min_value=0.1, step=0.1, key=f"force_{i}")
        with col2:
            direction = st.selectbox("Direction:", direction_options, key=f"dir_{i}")
        with col3:
            label = st.text_input(f"Custom Label:", value=f"Force {i+1}", key=f"label_{i}")
        with col4:
            color = st.color_picker("Pick arrow color:", "#ff0000", key=f"color_{i}")

        forces.append(magnitude)
        directions.append(direction)
        labels.append(label)
        colors.append(color)

    # Generate the Free Body Diagram
    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, directions, labels, colors, label_distance, show_resultant)
        st.pyplot(fig)

        # Download as SVG
        buf = BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="Download FBD as SVG",
            data=buf,
            file_name="free_body_diagram.svg",
            mime="image/svg+xml"
        )

if __name__ == "__main__":
    main()
