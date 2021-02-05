""" Dictionaries of styles """
from pyx import *

def get_colors_symbols_lines():
    colour_strings=['black','dark','medium','light','blue','red','green']
    colours=[color.gray(0.0),color.gray(0.5),color.rgb.red,color.rgb.blue]
    symbols=[graph.style.symbol.plus,graph.style.symbol.circle,graph.style.symbol.cross,graph.style.symbol.triangle]
    linests=[style.linestyle.solid,style.linestyle.dashed,style.linestyle.dashdotted,style.linestyle.dotted]
    return {'colours': colours, 'symbols': symbols, 'linests': linests, 'colour_strings': colour_strings}

# Dictionaries
def get_dictionaries():
    col_dict= {
        'red' : color.rgb.red,
        'blue' : color.rgb.blue,
        'green' : color.rgb.green,
        'black' : color.gray(0.0),
        'dark' : color.gray(0.25),
        'medium' : color.gray(0.5),
        'light' : color.gray(0.75)
        }

    linst_dict={
        '_' : style.linestyle.solid,
        '-' : style.linestyle.solid,
        '.' : style.linestyle.dotted,
        '.-' : style.linestyle.dashdotted,
        '-.' : style.linestyle.dashdotted,
        '--' : style.linestyle.dashed
        }

    symst_dict={
        'x' : graph.style.symbol.cross,
        '*' : graph.style.symbol.cross,
        '+' : graph.style.symbol.plus,
        'o' : graph.style.symbol.circle,
        '>' : graph.style.symbol.triangle,
        '<' : graph.style.symbol.triangle
        }

    linw_dict={
        '1' :     style.linewidth.thin,
        '2' :     style.linewidth.thick,
        '3' :     style.linewidth.Thick,
        '4' :     style.linewidth.THIck,
        '5' :     style.linewidth.THICK
        }

    grad_dict={
        'rainbow'    :     color.gradient.Rainbow,
        'whitered'    :     color.gradient.WhiteRed,
        'wr'        :     color.gradient.WhiteRed,
        'redwhite'    :     color.gradient.RedWhite,
        'rw'        :     color.gradient.RedWhite,
        'gray'        :     color.gradient.Gray,
        'grey'        :     color.gradient.Gray,
        'gr'        :     color.gradient.Gray,
        'jet'        :     color.gradient.Jet,
        }

    return {'colors': col_dict, 'lines': linst_dict, 'symbols':symst_dict, 'widths': linw_dict, 'gradients': grad_dict}
