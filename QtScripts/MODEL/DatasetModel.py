from QtScripts import params


class DatasetModel:
    def __init__(self, controller):
        self.controller = controller
        self.version = params.version
        self.widgets_values = {}
        self.dataset = None
        self.plot_default_params = {'x_label': '', 'y_label': '', 'x_label_size': params.DEFAULT_FONTSIZE,
                          'y_label_size': params.DEFAULT_FONTSIZE, 'x_n_tick': params.DEFAULT_NTICKS,
                          'y_n_tick': params.DEFAULT_NTICKS, 'x_tick_rotation': params.DEFAULT_FONTROTATION,
                          'y_tick_rotation': params.DEFAULT_FONTROTATION, 'x_tick_size': params.DEFAULT_FONTSIZE,
                          'y_tick_size': params.DEFAULT_FONTSIZE, 'x_round': params.DEFAULT_ROUND,
                          'y_round': params.DEFAULT_ROUND, 'axes_font': params.DEFAULT_FONT,
                            'title': '', 'title_font': params.DEFAULT_FONT, 'title_size': params.DEFAULT_FONTSIZE, 'dpi': params.DEFAULT_DPI,
                            'show_legend': params.SHOW_LEGEND, 'legend_anchor': params.LEGEND_ANCHOR,
                            'legend_alpha': params.LEGEND_ALPHA, 'legend_x_pos': 0.0, 'legend_y_pos': 0.0,
                            'legend_draggable': params.LEGEND_DRAGGABLE, 'legend_ncols': params.LEGEND_NCOLS,
                            'legend_fontsize': params.LEGEND_FONTSIZE,
                            }
        
        