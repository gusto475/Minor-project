


import rebar_2 as rb2

import handcalcs
import forallpeople 
from handcalcs.decorator import handcalc

import forallpeople as si
si.environment("structural")

calc_renderer = handcalc()
# decorator for varisous functions
ew = calc_renderer(rb2.calculate_effective_width)
d = calc_renderer(rb2.calculate_effective_depth)
space = calc_renderer(rb2.calculate_bar_spacing)












