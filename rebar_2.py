
from handcalcs.decorator import handcalc        
import plotly.graph_objects as go
from typing import List, Tuple


def calculate_effective_width(beam_width: float, concrete_cover: float, link_diam: float, bar_diam: float) :
    """
    Calculates width available for bar placement, considering concrete cover and link size
    """
    effective_width = beam_width - 2 * (concrete_cover + link_diam + bar_diam/2)
    return effective_width
def calculate_effective_depth(beam_depth: float, concrete_cover: float, link_diam: float, bar_diam: float, bar_y_offset: float = 0) :
    """
    Calculates the effective depth of row of bars. For 1st row, bar_y_offset =0
    """
    d = beam_depth - (concrete_cover + link_diam + bar_diam / 2 + bar_y_offset)
    return d

def calculate_bar_spacing(effective_width: float, num_of_bars: int, bar_diam: float, agg_size: float, concrete_cover: float) :
    """
    Calculates the spacing of bars in layers. Also considers the minimum bar spacing rules 
    per CSA A23-1 Clause 6.6.5.2
    """
   
    bar_space = (effective_width - (num_of_bars*bar_diam))/ (num_of_bars - 1) #gap between bars
    min_spacing = max(1.4 * bar_diam, 1.4 * agg_size, concrete_cover)
    bar_spacing = max(bar_space, min_spacing)
    
    return bar_spacing

def setup_concrete_section(beam_width: float, beam_depth: float, concrete_cover: float, link_diam: float) -> go.Figure:
    """
    Creates a plot of the outline of the concrete section along with the tie/link
    """
    fig = go.Figure()
    
    # Create figure layout
    fig.update_layout(
        width=beam_width + 500,
        height=beam_depth + 500,
        xaxis=dict(range=[-beam_width * 0.5, beam_width * 1.5]),
        yaxis=dict(range=[-beam_depth * 0.5, beam_depth * 1.5]),
        title=f"Concrete Section Distribution: {beam_depth} x {beam_width}",
        title_x=0.5,
        title_y=0.95
    )
    fig.layout.xaxis.scaleanchor = 'y'
    fig.layout.xaxis.scaleratio = 1
    
    # Add concrete section
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=beam_width, y1=beam_depth,
        line=dict(color="RoyalBlue"),
        fillcolor="lightgrey"
    )
    
    # Add inner rectangle
    fig.add_shape(
        type="rect",
        x0=concrete_cover, y0=concrete_cover,
        x1=beam_width - concrete_cover, y1=beam_depth - concrete_cover,
        line=dict(color="RoyalBlue", width=link_diam),
        fillcolor="lightgrey"
    )
    
    return fig  
def check_bar_placement_with_effective_width(bar_x_coords: List[float], effective_width: float, beam_width: float, concrete_cover: float, link_diam: float, bar_diam: float):
    """
    This function checks if the placement of the bars is within the effective width 
    """
    max_bar_position = max(bar_x_coords)
    link_limit = beam_width - concrete_cover - link_diam - bar_diam / 2  # Adjusted to match max bar placement
    
    if max_bar_position > link_limit:
        raise ValueError(f"The placement of bars exceeds the available effective width. Max bar position: {max_bar_position:.2f}, Effective width limit: {link_limit:.2f}")
def generate_bar_coordinates(bar_properties: List[List[int]], beam_width: float, beam_depth: float, 
                             concrete_cover: float, link_diam: float, agg_size: float) -> List[List]:
    """
    Generates a nested list of x and y coordinates for each layer of bars.
    
    Parameters:
    - bar_properties: List of lists, where each sublist contains [layer_number, bar_size, num_of_bars].
    - beam_width: Width of the beam.
    - beam_depth: Depth of the beam.
    - concrete_cover: Concrete cover thickness.
    - link_diam: Diameter of the links.
    - agg_size: Aggregate size for bar spacing calculation.
    
    Returns:
    - A nested list where each sublist contains [layer_number, bar_size, num_of_bars, x_coords, y_coords].
    """
    coordinates_list = []
    previous_depth = 0  # Start from the concrete cover + link diameter
    
    for i, layer in enumerate(bar_properties):
        layer_number, bar_diam, num_of_bars = layer
        
        # Calculate effective width for bar placement
        effective_width = calculate_effective_width(beam_width, concrete_cover, link_diam, bar_diam)
        
        # Calculate the effective depth (y-coordinate) for this layer
        effective_depth = calculate_effective_depth(beam_depth, concrete_cover, link_diam, bar_diam, previous_depth)
        
        # Calculate bar spacing for this layer (should be 0 for bars touching)
        bar_spacing = calculate_bar_spacing(effective_width, num_of_bars, bar_diam, agg_size, concrete_cover)
        
 # Generate x coordinates for each bar in this layer
        x_coords = []
        start_x = concrete_cover + link_diam + bar_diam / 2
        
        for bar_idx in range(num_of_bars):
            if bar_idx == 0:
                x_coord = start_x
            else:
                # Adjust x coordinate considering the diameter of the previous bar
                previous_bar_diam = bar_properties[i][1]
                x_coord = x_coords[bar_idx - 1] + previous_bar_diam / 2 + bar_spacing + bar_diam / 2
            x_coords.append(x_coord)
            print(f"x_coords: {x_coords}")
        
        # Check if bar placement is within effective width
        check_bar_placement_with_effective_width(x_coords, effective_width, beam_width, concrete_cover, link_diam, bar_diam)
        
        # Generate y coordinates (same for all bars in the layer)
        y_coords = [effective_depth] * num_of_bars
        
        # Append the layer details and coordinates to the list
        coordinates_list.append([layer_number, bar_diam, num_of_bars, x_coords, y_coords])
        
        # Update previous_depth for the next layer
        if i < len(bar_properties) - 1:  # Skip update for the last layer
            previous_bar_diam = bar_properties[i][1]
            previous_depth = bar_spacing + previous_bar_diam  # Update for the next layer
    
    return coordinates_list

def plot_bars(fig: go.Figure, coordinates_list: List[List], beam_depth: float, bar_color: str = "black"):
    """
    Plot bars on the given figure using the coordinates list.

    Parameters:
    - fig: The Plotly figure to add bars to.
    - coordinates_list: A nested list where each sublist contains [layer_number, bar_size, num_of_bars, x_coords, y_coords].
    - beam_depth: The depth of the beam to adjust y-coordinates.
    - bar_color: Color of the bars.
    """
    for layer in coordinates_list:
        _, bar_diam, _, x_coords, y_coords = layer
        for x, y in zip(x_coords, y_coords):
            # Adjust y-coordinate to account for the bottom origin
            adjusted_y = beam_depth - y
            fig.add_shape(
                type="circle",
                x0=x - bar_diam / 2, y0=adjusted_y - bar_diam / 2,
                x1=x + bar_diam / 2, y1=adjusted_y + bar_diam / 2,
                line=dict(color=bar_color),
                fillcolor=bar_color
            )
def add_legend(fig: go.Figure, concrete_cover: float, agg_size: float, bar_properties, beam_width: float, link_diam: float):
    """
    Adds a legend to the figure showing provided cover, minimum cover, and aggregate size.
    
    Parameters:
    - fig: The Plotly figure to add the legend to.
    - concrete_cover: Provided concrete cover.
    - min_cover: Minimum cover calculated based on 1.4 * bar diameter, 1.4 * aggregate size, and provided cover.
    - agg_size: Aggregate size used in calculations.
    """
    #Extract key data from the first layer of bars
    if len(bar_properties) == 0:
        bar_leg_dia = bar_properties[1]
        bar_leg_num = bar_properties[2]
    else:
        bar_leg_dia = bar_properties[0][1]
        bar_leg_num = bar_properties[0][2]

    min_spacing = max(1.4 * bar_leg_dia, 1.4 * agg_size, concrete_cover)
    effective_width = calculate_effective_width(beam_width, concrete_cover, link_diam, bar_leg_dia)
    bar_spacing = calculate_bar_spacing(effective_width, bar_leg_num, bar_leg_dia, agg_size, concrete_cover)
    #Items to be placed in the legend
    legend_text = (
        f"<b>Legend</b><br>"
        f"Concrete Cover: {concrete_cover} mm<br>"
        f"1.4*Aggregate Size: {1.4*agg_size} mm<br>"
        f"1.4*Bar Size: {1.4*bar_leg_dia} mm<br>"
        f"Minimum Spacing: {min_spacing} mm<br>"
        f"Calculated Spacing Provided: {round(bar_spacing, 1)} mm"
    )
    
    # Add the legend as a text annotation
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=0.95,  # Centered position
        xanchor="center",  # Horizontal center anchor
        yanchor="top",  # Vertical center anch
        text=legend_text,
        showarrow=False,
        font=dict(size=12),
        align="left",
        bordercolor="black",
        borderwidth=1,
        borderpad=4,
        bgcolor="white",
        opacity=0.8
    )
def effective_depths(bar_properties: list[list], beam_depth: float, concrete_cover: float, link_diam: float, bar_y_offset: float = 0):
    # Initialize variables to calculate cumulative depth
    previous_depth = 0
    effective_depths = []

    # Calculate effective depth for each layer, accounting for the cumulative depth
    for i, layer in enumerate(bar_properties):
    # Calculate the depth from the top of the beam to the centroid of the current layer
        effective_depth = (
            beam_depth - (concrete_cover + link_diam + previous_depth + layer[1] / 2)
    )
    
    # Store the effective depth
    effective_depths.append(effective_depth)
    
    # Update the previous_depth to include the current layer's full diameter
    previous_depth += layer[1]
    return effective_depths
def add_dimension(fig: go.Figure, beam_width: float, beam_depth: float, dimension_text: str, 
                  orientation: str = 'horizontal', line_offset: float = 50):
    """
    Adds an engineering-style dimension with arrowheads, dimension lines, and extension lines.
    
    Parameters:
    - fig: The Plotly figure to add the dimension to.
    - beam_width: Width of the concrete section.
    - beam_depth: Depth of the concrete section.
    - dimension_text: Text for the dimension (e.g., "300 mm").
    - orientation: 'horizontal' for width, 'vertical' for height/depth.
    - line_offset: Offset distance for the dimension line from the section.
    """
    arrow_size = 15  # Arrowhead size
    text_offset = 10  # Offset for dimension text from the dimension line

    if orientation == 'horizontal':
        # Horizontal dimension (width)
        x0, y0 = 0, 0
        x1, y1 = beam_width, 0
        
        # Extension lines
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x0, y1=y0 - line_offset, line=dict(color="black"))
        fig.add_shape(type="line", x0=x1, y0=y1, x1=x1, y1=y1 - line_offset, line=dict(color="black"))
        
        # Dimension line
        fig.add_shape(type="line", x0=x0, y0=y0 - line_offset, x1=x1, y1=y1 - line_offset, line=dict(color="black"))
        
        # Arrowheads
        fig.add_annotation(x=x0, y=y0 - line_offset, ax=x0 + arrow_size, ay=y0 - line_offset, xref="x", yref="y",
                           axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
        fig.add_annotation(x=x1, y=y1 - line_offset, ax=x1 - arrow_size, ay=y1 - line_offset, xref="x", yref="y",
                           axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
        
        # Dimension text
        fig.add_annotation(x=(x0 + x1) / 2, y=y0 - line_offset - text_offset, text=dimension_text,
                           showarrow=False, font=dict(size=12), xanchor="center", yanchor="top")

    elif orientation == 'vertical':
        # Vertical dimension (depth)
        x0, y0 = 0, 0
        x1, y1 = 0, beam_depth
        
        # Extension lines
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x0 - line_offset, y1=y0, line=dict(color="black"))
        fig.add_shape(type="line", x0=x1, y0=y1, x1=x1 - line_offset, y1=y1, line=dict(color="black"))
        
        # Dimension line
        fig.add_shape(type="line", x0=x0 - line_offset, y0=y0, x1=x1 - line_offset, y1=y1, line=dict(color="black"))
        
        # Arrowheads
        fig.add_annotation(x=x0 - line_offset, y=y0, ax=x0 - line_offset, ay=y0 + arrow_size, xref="x", yref="y",
                           axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
        fig.add_annotation(x=x1 - line_offset, y=y1, ax=x1 - line_offset, ay=y1 - arrow_size, xref="x", yref="y",
                           axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
        
        # Dimension text
        fig.add_annotation(x=x0 - line_offset - text_offset, y=(y0 + y1) / 2, text=dimension_text,
                           showarrow=False, font=dict(size=12), xanchor="right", yanchor="middle")

# def add_effd_dims(fig:go.Figure, effective_depths: list[list], beam_width, beam_depth):
#     # Add dimensions for each effective depth
#     if len(effective_depths) == 1:
#         # If there's only one layer, add a single dimension line
#         add_dimension(
#             fig=fig,
#             beam_width=beam_width,
#             beam_depth=beam_depth - effective_depths[0],
#             dimension_text=f"{round(effective_depths[0], 1)} mm",
#             orientation='vertical',
#             line_offset=500  # Adjust offset as needed
#         )
#     else:
#         # If there are multiple layers, add a dimension line for each effective depth
#         for i, depth in enumerate(effective_depths):
#             add_dimension(
#                 fig=fig,
#                 beam_width=beam_width,
#                 beam_depth=beam_depth - depth,
#                 dimension_text=f"Layer {i + 1}: {round(depth, 1)} mm",
#                 orientation='vertical',
#                 line_offset=50 + i * 20  # Adjust offset to avoid overlap
#             )





