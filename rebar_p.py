


import rebar_2 as rb2

import handcalcs
import forallpeople 
from handcalcs.decorator import handcalc

import forallpeople as si
calc_renderer = handcalc()
# decorator for varisous functions
ew = calc_renderer(rb2.calculate_effective_width)
d = calc_renderer(rb2.calculate_effective_depth)
space = calc_renderer(rb2.calculate_bar_spacing)





si.environment("structural")





# new_latex, new_value = gen.sim_b_M(beam_length, w_b)




# st.latex(new_latex)

