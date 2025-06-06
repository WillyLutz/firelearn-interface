import logging
import traceback

import numpy as np
import pandas as pd
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QMessageBox

from QtScripts.MODEL.DatasetModel import DatasetModel
from QtScripts.VIEW.DatasetView import DatasetView

logger = logging.getLogger("__RFC__")

class DatasetController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = DatasetModel(self)  # set model
        self.view = DatasetView(self.app, parent=self.parent_controller.view.dataset_tab, controller=self)
        
    def load_dataset(self):
        dialog = (self.parent_controller.parent_controller.
         load_path_and_update_edit(self.view.widgets["specific_load_edit"], mode='getOpenFileName',
                                   filter_="Dataset (*.csv)"))
        
        if dialog:
            try:
                df = pd.read_csv(dialog)
            except Exception as e:
                QMessageBox.warning(self.view, "Error", f"Error while loading file. {traceback.format_exc()}")
                return
            
            self.model.dataset = df
            self.view.widgets["specific_dataset_tableplot"].clear()
            combo = self.view.widgets["specific_target_col_cbbox"]
            combo.currentIndexChanged.disconnect()
            combo.clear()
            combo.currentIndexChanged.connect(lambda: self.update_combotable_items("specific_dataset_tableplot"))
            combo.addItems(self.model.dataset.columns)
        
    def update_combotable_items(self, combotable_name: str):
        if combotable_name in self.view.widgets.keys():
            combotable = self.view.widgets[combotable_name]
            target_col = self.view.widgets["specific_target_col_cbbox"].currentText()
            items = list(set(self.model.dataset[target_col]))
            
            if len(items) > 200:
                reply = QMessageBox.question(self.view, "Warning",
                                             "The number of unique elements in the column exceeds 200. Proceed ?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return
            
            combotable.update_combo_items(items)
            
            
    def draw(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        if self.check_params():
            self.view.ax.clear()
            df = pd.read_csv(self.model.widgets_values["specific_load_edit"], index_col=False)
            targets_column = self.model.widgets_values["specific_target_col_cbbox"]
            n_val = 0
            ymin = 0
            ymax = 0
            
            for row in range(self.view.widgets["specific_dataset_tableplot"].table.rowCount()):
                target = self.model.widgets_values[f"dataplot_target_cbbox_{row}"]
    
                color_btn = self.view.widgets[f"dataplot_color_btn_{row}"]
                palette = color_btn.palette()
                bg_color = palette.color(QPalette.ColorRole.Button)
                color = bg_color.name()
                
                df[targets_column] = df[targets_column].astype(str)
                sub = df[df[targets_column] == target]
                sub = sub.reset_index(drop=True)
                sub = sub.loc[:, ~df.columns.isin([targets_column,])]
                
                stds = sub.std(axis=0)
                means = sub.mean(axis=0)
                target_max = max([means[x] + stds[x] for x in means.index])
                target_min = min([means[x] - stds[x] for x in means.index])
                ymax = max(target_max, ymax)
                ymin = min(target_min, ymin)
                
                self.view.ax.plot(means, color=color,
                        label=target,
                        linewidth=self.model.widgets_values[f"dataplot_linewidth_edit_{row}"],
                        linestyle=self.model.widgets_values[f"dataplot_linestyle_cbbox_{row}"])
                
                if self.model.widgets_values[f"dataplot_std_ckbox_{row}"]:
                    self.view.ax.fill_between([x for x in range(len(means))],
                                    [means[x] - stds[x] for x in means.index],
                                    [means[x] + stds[x] for x in means.index],
                                    color=color,
                                    alpha=self.model.widgets_values[f"dataplot_std_alpha_slider_{row}"]/100)
                n_val = len(means)
            self.set_ticks(self.view.ax, n_val, ymin, ymax)
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
                          framealpha=self.model.widgets_values["plot_alpha_slider"]/100,
                          )
            else:
                ax.legend(loc=self.model.widgets_values["plot_anchor_cbbox"],
                          draggable=self.model.widgets_values["plot_draggable_ckbox"],
                          ncols=self.model.widgets_values["plot_legend_col_edit"],
                          fontsize=self.model.widgets_values["plot_legend_size_slider"],
                          framealpha=self.model.widgets_values["plot_alpha_slider"]/100,
                          )
            
            for t, lh in zip(ax.get_legend().texts, ax.get_legend().legend_handles):
                t.set_alpha(self.model.widgets_values["plot_alpha_slider"]/100)
                lh.set_alpha(self.model.widgets_values["plot_alpha_slider"]/100)
        
        elif ax.get_legend():
            ax.get_legend().remove()

    def check_params(self):
        errors = []
        n_artists = self.view.widgets["specific_dataset_tableplot"].table.rowCount()
        if not n_artists:
            errors.append("You need to add Artists to plot.")
            
        for artist in range(n_artists):
            dataplot_keys = [key for key in self.model.widgets_values.keys() if key.startswith('dataplot_') and key.endswith(f'_{artist}')]
            linewidths = [key for key in dataplot_keys if 'linewidth_edit' in key]
            for l in linewidths:
                if not self.model.widgets_values[l]:
                    errors.append(f"Linewidth {n_artists} is not defined.")
        
        if errors:
            QMessageBox.warning(self.view, "Warning", "\n".join(errors))
            return False
        else:
            return True