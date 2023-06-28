from matplotlib import font_manager

version = "0.0.7"
default_dataset_path = "path/of/your/dataset/here.csv"
default_dataset_info = "Dataset information here"
selected_target = "No target selected"
default_targets = ["alpha", "beta", "gamma"]
MODEL_EXTENSIONS = {"rfc": "Random Forest Classifier"}

DEFAULT_FONT = "DejaVu Sans"
font_manager.get_font_names()
FONTS = sorted(font_manager.get_font_names())

LINESTYLES = {"solid": "solid", "dotted": "dotted", "dashed": "dashed", "dashdot": "dashdot",
              'loosely dotted': (0, (1, 10)), 'densely dotted': (0, (1, 1)), 'long dash with offset': (5, (10, 3)),
              'loosely dashed': (0, (5, 10)), 'densely dashed': (0, (5, 1)), 'loosely dashdotted': (0, (3, 10, 1, 10)),
              'dashdotted': (0, (3, 5, 1, 5)), 'densely dashdotted': (0, (3, 1, 1, 1)),
              'loosely dashdotdotted': (0, (3, 10, 1, 10, 1, 10)), 'densely dashdotdotted': (0, (3, 1, 1, 1, 1, 1))}

COLORS = ['black', 'dimgray', 'dimgrey', 'gray', 'grey', 'darkgray', 'darkgrey', 'silver', 'lightgray', 'lightgrey', 'gainsboro',
          'whitesmoke', 'white', 'snow', 'rosybrown', 'lightcoral', 'indianred', 'brown', 'firebrick', 'maroon', 'darkred',
          'red', 'mistyrose', 'salmon', 'tomato', 'darksalmon', 'coral', 'orangered', 'lightsalmon',
          'sienna', 'seashell', 'chocolate', 'saddlebrown', 'sandybrown', 'peachpuff', 'peru', 'linen',
          'bisque', 'darkorange', 'burlywood', 'antiquewhite', 'tan', 'navajowhite', 'blanchedalmond', 'papayawhip',
          'moccasin', 'orange', 'wheat', 'oldlace', 'floralwhite', 'darkgoldenrod', 'goldenrod', 'cornsilk',
          'gold', 'lemonchiffon', 'khaki', 'palegoldenrod', 'darkkhaki', 'ivory', 'beige', 'lightyellow',
          'lightgoldenrodyellow', 'olive','yellow', 'olivedrab', 'yellowgreen', 'darkolivegreen', 'greenyellow',
          'chartreuse', 'lawngreen', 'honeydew', 'darkseagreen', 'palegreen', 'lightgreen', 'forestgreen', 'limegreen',
          'darkgreen', 'green', 'lime', 'seagreen', 'mediumseagreen', 'springgreen', 'mintcream',
          'mediumspringgreen', 'mediumaquamarine', 'aquamarine', 'turquoise', 'lightseagreen', 'mediumturquoise', 'azure', 'lightcyan',
          'paleturquoise', 'darkslategray', 'darkslategrey', 'teal', 'darkcyan', 'aqua', 'cyan',
          'darkturquoise', 'cadetblue', 'powderblue', 'lightblue', 'deepskyblue', 'skyblue', 'lightskyblue', 'steelblue',
          'aliceblue', 'dodgerblue', 'lightslategray', 'lightslategrey', 'slategray', 'slategrey', 'lightsteelblue', 'cornflowerblue',
          'royalblue', 'ghostwhite', 'lavender', 'midnightblue', 'navy', 'darkblue', 'mediumblue',
          'blue', 'slateblue', 'darkslateblue', 'mediumslateblue', 'mediumpurple', 'rebeccapurple', 'blueviolet', 'indigo',
          'darkorchid', 'darkviolet', 'mediumorchid', 'thistle', 'plum', 'violet', 'purple', 'darkmagenta',
          'fuchsia', 'magenta', 'orchid', 'mediumvioletred', 'deeppink', 'hotpink', 'lavenderblush',
          'palevioletred', 'crimson', 'pink', 'lightpink',]
