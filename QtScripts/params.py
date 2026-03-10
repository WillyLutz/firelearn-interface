import os
import sys

from matplotlib import font_manager


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))


name = 'FireLearn GUI'
version = "1.0.11-beta"
last_version_compatible = "1.0.10-beta"
last_version_compatible_spike = "1.0.10-beta"
last_version_compatible_learning = "1.0.10-beta"
last_version_compatible_processing = "1.0.10-beta"

theme = "lightblue"

description = "Description of FL project here"

default_dataset_path = resource_path("path/of/your/full_dataset/here.csv")
default_dataset_info = "Dataset information here"
selected_target = "No target selected"
default_targets = ["alpha", "beta", "gamma"]
MODEL_EXTENSIONS = {"rfc": "Random Forest Classifier", "svc": "Support Vector Classifier"}

DEFAULT_DETECTION_UNITS = "pV"


DEFAULT_FONT = "DejaVu Sans"
MIN_FONTSIZE = 6
MAX_FONTSIZE = 36
DEFAULT_FONTSIZE = 12
DEFAULT_LINEALPHA = 1
DEFAULT_FILLALPHA = 0.5
DEFAULT_FIGUREHEIGHT = 8
DEFAULT_FIGUREWIDTH = 8
DEFAULT_FONTROTATION = 0
DEFAULT_NTICKS = 7
DEFAULT_ROUND = 2
DEFAULT_ALPHA = 1.0

SHOW_LEGEND = 0
LEGEND_ANCHOR = 'best'

DEFAULT_DPI = 100

LEGEND_POS = ['best', 'upper left', 'upper right', 'lower left', 'lower right', 'upper center', 'lower center', 'center left', 'center right', 'center', 'custom']
LEGEND_DRAGGABLE = False
LEGEND_NCOLS = 1
LEGEND_FONTSIZE = 10
LEGEND_ALPHA = 100

font_manager.get_font_names()
FONTS = sorted(font_manager.get_font_names())

DEFAULT_LINESTYLE = 'solid'
DEFAULT_LINEWIDTH = 1
DEFAULT_COLOR = 'green'
DEFAULT_MARKER = 'point'
DEFAULT_MARKERSIZE = 10

MARKERS = {'point': '.', 'pixel': ',', 'circle': 'o', 'triangle down': 'v', 'triangle up': '^', 'triangle left': '<',
           'triangle right': '>', 'tripod down': '1', 'tripod up': '2', 'tripod left': '3', 'tripod right': '4',
           'octagon': '8', 'square': 's', 'pentagon': 'p', 'star': '*', 'hexagon 1': 'h',
           'hexagon 2': 'H', 'plus (filled)': 'P', 'plus': '+', 'cross': 'x', 'cross (filled)': 'X',
           'diamond': 'D', 'diamond (thin)': 'd', 'vertical line': '|', 'horizontal line': '_'}

LINESTYLES_FULL = {"solid": "solid", "dotted": "dotted", "dashed": "dashed", "dashdot": "dashdot",
                   'loosely dotted': (0, (1, 10)), 'densely dotted': (0, (1, 1)), 'long dash with offset': (5, (10, 3)),
                   'loosely dashed': (0, (5, 10)), 'densely dashed': (0, (5, 1)),
                   'loosely dashdotted': (0, (3, 10, 1, 10)),
                   'dashdotted': (0, (3, 5, 1, 5)), 'densely dashdotted': (0, (3, 1, 1, 1)),
                   'loosely dashdotdotted': (0, (3, 10, 1, 10, 1, 10)),
                   'densely dashdotdotted': (0, (3, 1, 1, 1, 1, 1))}

LINESTYLES = {"solid": "solid", "dotted": "dotted", "dashed": "dashed", "dashdot": "dashdot", }

COLORS = ['black', 'dimgray', 'dimgrey', 'gray', 'grey', 'darkgray', 'darkgrey', 'silver', 'lightgray', 'lightgrey',
          'gainsboro',
          'whitesmoke', 'white', 'snow', 'rosybrown', 'lightcoral', 'indianred', 'brown', 'firebrick', 'maroon',
          'darkred',
          'red', 'mistyrose', 'salmon', 'tomato', 'darksalmon', 'coral', 'orangered', 'lightsalmon',
          'sienna', 'seashell', 'chocolate', 'saddlebrown', 'sandybrown', 'peachpuff', 'peru', 'linen',
          'bisque', 'darkorange', 'burlywood', 'antiquewhite', 'tan', 'navajowhite', 'blanchedalmond', 'papayawhip',
          'moccasin', 'orange', 'wheat', 'oldlace', 'floralwhite', 'darkgoldenrod', 'goldenrod', 'cornsilk',
          'gold', 'lemonchiffon', 'khaki', 'palegoldenrod', 'darkkhaki', 'ivory', 'beige', 'lightyellow',
          'lightgoldenrodyellow', 'olive', 'yellow', 'olivedrab', 'yellowgreen', 'darkolivegreen', 'greenyellow',
          'chartreuse', 'lawngreen', 'honeydew', 'darkseagreen', 'palegreen', 'lightgreen', 'forestgreen', 'limegreen',
          'darkgreen', 'green', 'lime', 'seagreen', 'mediumseagreen', 'springgreen', 'mintcream',
          'mediumspringgreen', 'mediumaquamarine', 'aquamarine', 'turquoise', 'lightseagreen', 'mediumturquoise',
          'azure', 'lightcyan',
          'paleturquoise', 'darkslategray', 'darkslategrey', 'teal', 'darkcyan', 'aqua', 'cyan',
          'darkturquoise', 'cadetblue', 'powderblue', 'lightblue', 'deepskyblue', 'skyblue', 'lightskyblue',
          'steelblue',
          'aliceblue', 'dodgerblue', 'lightslategray', 'lightslategrey', 'slategray', 'slategrey', 'lightsteelblue',
          'cornflowerblue',
          'royalblue', 'ghostwhite', 'lavender', 'midnightblue', 'navy', 'darkblue', 'mediumblue',
          'blue', 'slateblue', 'darkslateblue', 'mediumslateblue', 'mediumpurple', 'blueviolet',
          'indigo',
          'darkorchid', 'darkviolet', 'mediumorchid', 'thistle', 'plum', 'violet', 'purple', 'darkmagenta',
          'fuchsia', 'magenta', 'orchid', 'mediumvioletred', 'deeppink', 'hotpink', 'lavenderblush',
          'palevioletred', 'crimson', 'pink', 'lightpink', ]
DEFAULT_COLORMAP = 'Blues'
COLORMAPS = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r',
             'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Greens', 'Greens_r',
             'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired',
             'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn',
             'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r',
             'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r',
             'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r',
             'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r',
             'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis',
             'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'crest', 'crest_r',
             'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'flare', 'flare_r', 'gist_earth', 'gist_earth_r',
             'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r',
             'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gist_yerg',
             'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'grey', 'hot', 'hot_r', 'hsv',
             'hsv_r', 'icefire', 'icefire_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'mako',
             'mako_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r',
             'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 'seismic', 'seismic_r', 'spring',
             'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c',
             'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted',
             'twilight_shifted_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r']

FONT_TITLE1 = (DEFAULT_FONT, 26, 'bold')
FONT_TITLE2 = (DEFAULT_FONT, 23, 'bold')
FONT_TITLE3 = (DEFAULT_FONT, 20, 'bold')
