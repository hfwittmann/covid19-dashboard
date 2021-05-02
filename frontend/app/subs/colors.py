
import streamlit as st
import numpy as np
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex
from string import ascii_lowercase
from subs.access_backend import get_countries

LETTERS = {letter: str(index) for index, letter in enumerate(ascii_lowercase, start=1)}


def getNumber(text, max_length = 3):
    base = 26
    try:
        text = text.lower().strip().replace(' ', '')[:max_length]
        mynumbers = [int(LETTERS.get(character))*base**(max_length-ix) for ix, character in enumerate(text)]
        return np.sum(mynumbers)

    except Exception as e:
        return 1


def relative_Number(number, max_length = 3):
    return number / getNumber('z'*max_length, max_length)



def rgba_to_rgb(x):
    assert len(x) == 4
    x=np.array(x)
    out = tuple(x[:3]*256/x[3])
    return out

# @st.cache()
def get_countries_colors(config):

    cmap_marker = config['cmap_marker']
    cmap_marker_line = config['cmap_marker_line']
    mymod = config['mymod']

    _, countries_colors = get_countries()

    color_mapping_marker = cm.get_cmap(cmap_marker)
    color_mapping_marker_line = cm.get_cmap(cmap_marker_line)

    countries_colors['country_number'] = countries_colors['COUNTRY'].apply(getNumber)
    countries_colors['country_relative_number'] = countries_colors['country_number'].apply(relative_Number)


    countries_colors['country_color_marker'] = countries_colors['country_relative_number'].apply(lambda x: color_mapping_marker(x)).apply(rgb2hex)
    countries_colors['country_color_marker_line'] = countries_colors['country_relative_number'].apply(lambda x: color_mapping_marker_line(x)).apply(rgb2hex)

    countries_colors['country_number_mod'] = countries_colors['country_number'].apply(lambda x: x % mymod)

    countries_colors = countries_colors.rename({'COUNTRY':'country'},axis=1)



    return countries_colors