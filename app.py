# File: fbd_creator_app_v10.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# Basic color options
COLOR_OPTIONS = {
    "Red": "#FF0000",
    "Blue": "#0000FF",
    "Green": "#00FF00",
    "Orange": "#FFA500",
    "Purple": "#800080",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Black": "#000000",
    "Gray": "#808080",
    "Yellow": "#FFFF00"
}

# Function to draw Free Body Diagram with resultant vector
def draw_fbd(forces, directions, labels, colors, label_distance, show_resultant, title, caption):
    """
    Draw a Free Body Diagram with proportional vector scaling and resultant vector.
    
    Args:
        forces: List of force magnitudes or None for unknowns.
        directions: List of (dx, dy) directions.
        labels: List of labels for each force.
        colors: List of colors for each force.
        label_distance: Distance to place the labels away from the arrow tips.
        show_resultant: Boolean to display the resultant vector.
        title: Title of the diagram.
        caption: Caption of the diagram.
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes for a clean diagram

    # Determine scaling factor
    known_forces = [f for f in forces if f is not None]
    min_force = min(known_forces) if known_forces else 1
    scale_factor = 2.0 / (max(known_forces) if known_forces else 1)

    # Object size scaled to half the smallest known vector
    object_size = min_force / 2.0 if known_forces else 0.5

    # Draw rectangle
    rect_size = object_size * 1.5
    ax.add_patch(plt.Rectangle((-rect_size/2, -rect_size/2), rect_size, rect_size, 
                 fill=False, linewidth=4, color="black"))

    # Draw forces and compute resultant components
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    resultant_x, resultant_y = 0, 0
    has_unknown = False

    # For legend items
    legend_items = []

    for i in range(len(forces)):
        force = forces[i]
        if force is None:
            has_unknown = True
            continue
        
        # Scale the forces
        scaled_force = force * scale_factor
        dx = scaled_force * direction_map[directions[i]][0]
        dy = scaled_force * direction_map[directions[i]][1]

        # Update resultant components
        resultant_x += dx
        resultant_y += dy

        # Draw vector arrow
        ax.arrow(0, 0, dx, dy, head_width=0.05 * scale_factor, 
                 head_length=0.1 * scale_factor, fc=colors[i], ec=colors[i], linewidth=2)

        # Add labels
        label_x = dx * (1 + label_distance)
        label_y = dy * (1 + label_distance)
        plt.text(label_x, label_y, labels[i], fontsize=12, fontweight='bold', color=colors[i], ha='center')

        # Add to legend items
        legend_items.append((labels[i], colors[i]))

    # Draw resultant vector (if enabled and no unknowns)
    if show_resultant and not has_unknown:
        resultant_x_offset = resultant_x + 0.3
        resultant_y_offset = resultant_y + 0.3
        ax.arrow(0, 0, resultant_x_offset, resultant_y_offset, 
                 head_width=0.05 * scale_factor, head_length=0.1 * scale_factor, 
                 fc='purple', ec='purple', linewidth=3, linestyle='--')
        plt.text(resultant_x_offset * (1 + label_distance), resultant_y_offset * (1 + label_distance), 
                 "Resultant", fontsize=12, fontweight='bold', color='purple', ha='center')
        legend_items.append(("Resultant", "purple"))

    # Add title and caption
    plt.title(title, fontsize=14, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    # Add legend
    legend_handles = [plt.Line2D([0], [0], color=color, lw=2, label=label) for label, color in legend_items]
    if legend_handles:
        ax.legend(handles=legend_handles, loc="lower right", fontsize=10)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    plt.close(fig)
    return fig, has_unknown

# Streamlit UI
def main():
    st.title("Free Body Diagram Creator (With Legend)")
    st.write("Create a Free Body Diagram with customizable labels, titles, and export formats.")

    # Title and caption input
    title = st.text_input("Enter diagram title:", "Free Body Diagram")
    caption = st.text_input("Enter diagram caption:", "Generated using the Free Body Diagram Creator.")

    # Label distance adjustment
    label_distance = st.slider("Label distance from arrow tip (multiplier):", min_value=0.1, max_value=2.0, step=0.1, value=0.3)

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
            magnitude = st.text_input("Magnitude (leave blank for unknown):", key=f"force_{i}")
            magnitude = float(magnitude) if magnitude.strip().replace('.', '', 1).isdigit() else None
        with col2:
            direction = st.selectbox("Direction:", direction_options, key=f"dir_{i}")
        with col3:
            label = st.text_input(f"Custom Label:", value=f"Force {i+1}", key=f"label_{i}")
        with col4:
            color = st.selectbox("Pick arrow color:", list(COLOR_OPTIONS.keys()), key=f"color_{i}")

        forces.append(magnitude)
        directions.append(direction)
        labels.append(label)
        colors.append(COLOR_OPTIONS[color])

    # Resultant vector toggle
    show_resultant = st.checkbox("Show resultant force vector", value=False)

    # Generate the Free Body Diagram
    if st.button("Generate Diagram"):
        fig, has_unknown = draw_fbd(forces, directions, labels, colors, label_distance, show_resultant, title, caption)

        if has_unknown and show_resultant:
            st.warning("Resultant vector cannot be calculated when any magnitudes are unknown.")

        st.pyplot(fig)

        # Export options
        export_format = st.selectbox("Select export format:", ["SVG", "PNG", "JPG"])
        buf = BytesIO()
        fig.savefig(buf, format=export_format.lower(), bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label=f"Download FBD as {export_format}",
            data=buf,
            file_name=f"free_body_diagram.{export_format.lower()}",
            mime=f"image/{export_format.lower()}"
        )

if __name__ == "__main__":
    main()
