import streamlit as st
import plotly.graph_objects as go
import rebar_p as rp
import handcalcs
import forallpeople 
from handcalcs.decorator import handcalc
import rebar_2 as rb
import forallpeople as si

si.environment("structural")
st.write("# Rebar Placment App")    
st.subheader("Scope and Assumptions")

text =''' This basic app is aimed at plotting the distribution of main bars in a concrete section,  
            to ensure main bars are placed adequately within a section  
            It takes user input including:  
            section width $b$, section depth $h$, and concrete cover $b'_c$;  
            link bar size;    
            number of main bars and diameter, for up to two layers  
            (an error is raised if number of bars in both layers are not the same per CSA23-1 Cl 6.6.5.3  
            Note: For spacings calculated, the spacing in the horizontal is applied to the vertical in  
            the second layer '''
text_2 = r''' The outputs are:  
            A plot of the section and bars,  
            Calculations for:  
            Effective Width for Bar Placement,  
            Spacing of the bars in the assigned layer(s) in alignment with with CSA23-1 Cl 6.6.5.2, 
            
             '''



st.markdown(text)
st.markdown(text_2)

#input of geometric props
st.sidebar.subheader("Concrete Section Properties")
beam_width = st.sidebar.number_input("Width(mm)", value=300)
beam_depth = st.sidebar.number_input("Depth(mm)", value=300)
concrete_cover = st.sidebar.number_input("Concrete Cover(mm)", value=30)

agg_size = st.sidebar.number_input("Aggregate size(mm)", value=20)


#input of link props
st.sidebar.subheader("Link Properties")
allowed_link_sizes = [11, 16, 20]
link_diam = st.sidebar.selectbox("Link diameter(mm)", allowed_link_sizes)

#input of repar props
st.sidebar.subheader("Rebar Layer properties")
num_layers = st.sidebar.number_input("Number of Layers", min_value=1, max_value=2, value=1)
## generate a list containing: layer number, bar size and number of bars per layer
bar_properties = []
allowed_bar_sizes = [11, 16, 20, 25, 30, 36, 44, 56]
for i in range(num_layers):
    with st.sidebar.expander(f"Layer {i + 1} Properties"):
        cols = st.columns(3)
        bar_size = cols[0].selectbox(f"Bar Size (Layer {i + 1})", allowed_bar_sizes)
        num_bars = cols[1].number_input(f"Number of Bars (Layer {i + 1})", min_value=1, max_value=10, value=4)
        layer_number = cols[2].number_input(f"Layer Number", min_value=1, max_value=num_layers, value=i + 1)
        
        bar_properties.append([layer_number, bar_size, num_bars])
    #Check conditions after the second layer is defined
    if i == 1:  # 2nd layer (index 1)
        if bar_properties[1][1] != bar_properties[0][1]:  # Check bar size
            st.warning("Warning: Bar size in the 2nd layer differs from the 1st layer. They should match per code requirements.")
        
        if bar_properties[1][2] != bar_properties[0][2]:  # Check number of bars
            st.warning("Warning: Number of bars in the 2nd layer differs from the 1st layer. They should match per code requirements.")


#Implement the plot function
fig = rb.setup_concrete_section(beam_width, beam_depth,concrete_cover,link_diam)
#generate coordinates for the bars
coordinates_list = rb.generate_bar_coordinates(bar_properties, beam_width, beam_depth, concrete_cover, link_diam, agg_size)

#plot the bars and add dimensions
rb.plot_bars(fig, coordinates_list, beam_depth)

rb.add_legend(fig,concrete_cover,agg_size,bar_properties,beam_width,link_diam)
rb.add_dimension(fig,beam_width, beam_depth,f"{beam_width} mm","horizontal")
rb.add_dimension(fig,beam_width, beam_depth,f"{beam_depth} mm","vertical")
#obtian values to be used for rendered calculations from the bar layer(s) input
effective_depths = []
for coord in coordinates_list:
    effective_depth = coord[4][1]# effective depth to bar layer
    bars = coord[1] #diameter of bars in layer
    num_bars = coord[2] # number of bars in layer
    effective_depths.append([effective_depth, bars, num_bars])
# implement rendered calculation for effective width and spacing
ew_latex_5, ew_value_5 = rp.ew(beam_width,concrete_cover,link_diam,max(effective_depths)[1])
# d_latex, d_value = rp.d(beam_depth,concrete_cover,link_diam,max(effective_depths)[1])
space_latex, space_value = rp.space(ew_value_5,max(effective_depths)[2],max(effective_depths)[1],agg_size,concrete_cover)

#Show plot
st.plotly_chart(fig)
st.markdown("## Calculations")
st.markdown("### Effective Width for Bar Placement")
st.latex(ew_latex_5)
st.markdown("### Bar Spacing")
st.latex(space_latex)

