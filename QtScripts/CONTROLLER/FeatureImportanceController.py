import logging
import pickle

import numpy as np
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QMessageBox

from QtScripts.MODEL.FeatureImportanceModel import FeatureImportanceModel
from QtScripts.VIEW.FeatureImportanceView import FeatureImportanceView

logger = logging.getLogger("__FI__")

class FeatureImportanceController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = FeatureImportanceModel(self)  # set model
        self.view = FeatureImportanceView(self.app, parent=self.parent_controller.view.feature_importances_tab, controller=self)
        
    def draw(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        if self.check_params():
            self.view.ax.clear()
            
            y_data = np.mean([tree.feature_importances_ for tree in self.model.classifier.estimators_], axis=0)
            x_data = [i for i in range(len(y_data))]
            
            color_btn = self.view.widgets[f"specific_color_btn"]
            palette = color_btn.palette()
            bg_color = palette.color(QPalette.ColorRole.Button)
            color = bg_color.name()
            
            self.view.ax.plot(x_data, y_data,
                    linewidth=self.model.widgets_values["specific_linewidth_edit"],
                    linestyle=self.model.widgets_values["specific_linestyle_cbbox"],
                    color=color,
                    alpha=self.model.widgets_values["specific_alpha_slider"]/100,
                    label="Feature importance"
                    )
            
            
            if self.model.widgets_values["specific_fill_ckbox"]:
                ylim = self.view.figure.gca().get_ylim()
                self.view.ax.fill_between(x_data, y_data, max(min(y_data), ylim[0]),
                                color=color,
                                alpha=self.model.widgets_values["specific_fill_alpha_slider"]/100
                                )
        
            self.set_ticks(self.view.ax, len(y_data), min(y_data), max(y_data))
            self.set_labels(self.view.ax)
            self.set_legend(self.view.ax)
            self.view.figure.tight_layout()
        
        self.view.canvas.draw()
    
    def set_ticks(self, ax, n_val, ymin, ymax):
        x_data = [i for i in range(n_val)]
        xmin = min(x_data)
        xmax = max(x_data)
        xstep = (xmax - xmin) / (int(self.model.widgets_values["plot_x_n_tick_edit"]) - 1)
        xtick = xmin
        xticks = []
        for i in range(int(self.model.widgets_values["plot_x_n_tick_edit"]) - 1):
            xticks.append(xtick)
            xtick += xstep
        xticks.append(xmax)
        xticks_labels = np.array(xticks)
        xticks_labels = [np.around(x, int(self.model.widgets_values["plot_x_round_edit"])) for x in xticks_labels]
        
        if int(self.model.widgets_values["plot_x_round_edit"]) == 0:
            xticks_labels = [int(x) for x in xticks_labels]
        
        xticks_labels = [str(x) for x in xticks_labels]
        
        rounded_xticks = list(np.around(np.array(xticks), int(self.model.widgets_values["plot_x_round_edit"])))
        ax.set_xticks(rounded_xticks, xticks_labels)
        ax.tick_params(axis='x',
                       labelsize=int(self.model.widgets_values["plot_x_tick_size_slider"]),
                       labelrotation=int(self.model.widgets_values["plot_x_tick_rotation_slider"]))
        
        ystep = (ymax - ymin) / (int(self.model.widgets_values["plot_y_n_tick_edit"]) - 1)
        ytick = ymin
        yticks = []
        for i in range(int(self.model.widgets_values["plot_y_n_tick_edit"]) - 1):
            yticks.append(ytick)
            ytick += ystep
        yticks.append(ymax)
        yticks_labels = np.array(yticks)
        # yticks_labels = [np.around(y, int(self.model.widgets_values["plot_y_round_edit"])) for y in yticks_labels]
        # rounded_yticks = list(np.around(np.array(yticks), int(self.model.widgets_values["plot_y_round_edit"])))
        # ax.set_yticks(rounded_yticks, yticks_labels)
        ax.tick_params(axis='y',
                       labelsize=int(self.model.widgets_values["plot_y_tick_size_slider"]),
                       labelrotation=int(self.model.widgets_values["plot_y_tick_rotation_slider"]))
    
    def set_labels(self, ax):
        ax.set_xlabel(self.model.widgets_values["plot_x_label_edit"],
                      fontdict={"font": self.model.widgets_values["plot_axes_font_cbbox"],
                                "fontsize": self.model.widgets_values["plot_x_label_size_slider"]})
        
        ax.set_ylabel(self.model.widgets_values["plot_y_label_edit"],
                      fontdict={"font": self.model.widgets_values["plot_axes_font_cbbox"],
                                "fontsize": self.model.widgets_values["plot_y_label_size_slider"]})
        ax.set_title(self.model.widgets_values["plot_title_edit"],
                     fontdict={"font": self.model.widgets_values["plot_title_font_cbbox"],
                               "fontsize": self.model.widgets_values["plot_title_size_slider"], })
    
    def set_legend(self, ax):
        if self.model.widgets_values["plot_legend_ckbox"]:
            if self.model.widgets_values["plot_anchor_cbbox"] == 'custom':
                ax.legend(loc='upper left',
                          bbox_to_anchor=(self.model.widgets_values["plot_legend_x_pos_slider"],
                                          self.model.widgets_values["plot_legend_y_pos_slider"]),
                          draggable=self.model.widgets_values["plot_draggable_ckbox"],
                          ncols=self.model.widgets_values["plot_legend_col_edit"],
                          fontsize=self.model.widgets_values["plot_legend_size_slider"],
                          framealpha=self.model.widgets_values["plot_alpha_slider"] / 100,
                          )
            else:
                ax.legend(loc=self.model.widgets_values["plot_anchor_cbbox"],
                          draggable=self.model.widgets_values["plot_draggable_ckbox"],
                          ncols=self.model.widgets_values["plot_legend_col_edit"],
                          fontsize=self.model.widgets_values["plot_legend_size_slider"],
                          framealpha=self.model.widgets_values["plot_alpha_slider"] / 100,
                          )
            
            for t, lh in zip(ax.get_legend().texts, ax.get_legend().legend_handles):
                t.set_alpha(self.model.widgets_values["plot_alpha_slider"] / 100)
                lh.set_alpha(self.model.widgets_values["plot_alpha_slider"] / 100)
        
        elif ax.get_legend():
            ax.get_legend().remove()
    
    def check_params(self):
        errors = []
        
        if not self.model.widgets_values["specific_load_edit"]:
            errors.append('RFC Classifier not loaded')
            
        if not self.model.widgets_values["specific_linewidth_edit"]:
            errors.append(f"Linewidth is not defined.")
        
        if errors:
            QMessageBox.warning(self.view, "Warning", "\n".join(errors))
            return False
        else:
            return True
    
    def load_clf(self, ):
        dialog = self.parent_controller.parent_controller.load_path_and_update_edit(self.view.widgets["specific_load_edit"], filter_="RFC (*.rfc)",
                                                                                    mode='getOpenFileName')
        if dialog:
            clf = pickle.load(open(dialog, "rb"))
            self.model.classifier = clf
            