import ast
import logging
import os
import traceback

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMessageBox
from matplotlib.backend_bases import MouseButton
from matplotlib.colors import ListedColormap, BoundaryNorm

from QtScripts.MODEL.SpikeAnalysisModel import SpikeAnalysisModel
from QtScripts.VIEW.SpikeAnalysisView import SpikeAnalysisView

logger = logging.getLogger("__Pca__")


class SpikeAnalysisController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = SpikeAnalysisModel(self)  # set model
        self.view = SpikeAnalysisView(self.app, parent=self.parent_controller.view.spike_detection_tab, controller=self)
        self.selected_spike_coordinates = ()
        self.selected_spike_key = ""
        self.selected_spike_artist = None
        self.selected_spike_row = None
        
        self.spike_keys_to_plot = []
        
        self.raster_binding_id = plt.connect('motion_notify_event', self.raster_plot_on_move)
        self.view.raster_figure.canvas.mpl_connect('button_press_event', self.raster_plot_on_click)
        
        self.raster_drawn = False
        
    
    def load_dataset(self):
        dialog = (self.parent_controller.parent_controller.
                  load_path_and_update_edit(self.view.widgets["specific_load_edit"], mode='getOpenFileName',
                                            ))
        
        if dialog:
            try:
                df = pd.read_csv(dialog)
                df_columns = df.columns
                format_error = False
                for col in df_columns:
                    if '[' in col:
                        col = col.split('[')[0].strip()
                    if col not in self.model.dataset_base_columns:
                        format_error = True
                if len(df_columns) != len(self.model.dataset_base_columns):
                    format_error = True
                if format_error:
                    QMessageBox.critical(self.view, "", "Loaded dataset is not correctly formatted for spike analysis."
                                                        " Please use the dataset obtained through the Spike detection"
                                                        " processing feature in the software.")
                    self.view.widgets["specific_load_edit"].clear()
                    return
                self.model.dataset = df
                self.view.widgets["specific_subsample_table"].clear()
            except Exception as e:
                QMessageBox.warning(self.view, "Error", f"Error while loading file. {traceback.format_exc()}")
                return
    
    def filter_column_changed(self):
        if self.model.dataset is not None:
            filter_column = self.view.widgets["specific_subsample_cbbox"].currentText()
            if filter_column == "None":
                self.view.widgets["specific_subsample_table"].clear()
                
            if filter_column == "File" or filter_column == "Target":
                unique_values = self.model.dataset[filter_column].unique()
                table = self.view.widgets["specific_subsample_table"]
                table.clear()
                table.update_items(unique_values)
                

    def draw_raster(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        if self.check_parameters():
            self.view.raster_figure.clf()
            self.view.raster_ax.clear()
            self.view.raster_ax = self.view.raster_figure.add_subplot(111)
            subsample_cbbox = self.model.widgets_values["specific_subsample_cbbox"]
            if subsample_cbbox == "File" or subsample_cbbox == "Target":
                subsample_values = [item for item, checked in self.view.widgets["specific_subsample_table"].get_current_values().items() if checked == True]
                dataset = self.model.dataset.loc[self.model.dataset[subsample_cbbox].isin(subsample_values)]
            else:
                dataset = self.model.dataset
            
            show_as_colormap = self.model.widgets_values["raster_as_colormap_cbbox"]
            if show_as_colormap == "Filtered values":
                colored_column_name = self.model.widgets_values["specific_subsample_cbbox"]
            elif show_as_colormap != "None":
                colored_column_name = [col for col in self.model.dataset.columns if show_as_colormap in col][0]
            else:
                colored_column_name = ""
                
            columns_indices = {}
            for i, unique_col in enumerate(sorted(self.model.dataset["Column ID"].unique())):
                columns_indices[unique_col] = i
                
            # Create a colormap (e.g., 'viridis', 'plasma', 'coolwarm', etc.)
            cmap = matplotlib.pyplot.colormaps[self.model.widgets_values["raster_colormap_cbbox"]]
            
            print(colored_column_name)
            if colored_column_name:
                if "Target" in colored_column_name or 'File' in colored_column_name: # Do not use cmap but individual colors instead
                    unique_labels = sorted(dataset[colored_column_name].unique())
                    n_labels = len(unique_labels)
                    
                    colors = cmap(np.linspace(0, 1, n_labels))
                    cmap = ListedColormap(colors)
                    # Create boundaries: 0, 1, 2, ..., n_labels
                    bounds = np.arange(n_labels + 1) - 0.5
                    norm = BoundaryNorm(bounds, n_labels)
                    
                    plotted_labels = set()
                    labels_colors = {}
                    for i, unique_label in enumerate(unique_labels):
                        labels_colors[unique_label] = (i, colors[i])
                    
                    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
                    sm.set_array([])  # Needed for older versions of matplotlib
                    cbar = self.view.raster_figure.colorbar(sm, ax=self.view.raster_ax, label=colored_column_name,
                                                            ticks=np.arange(n_labels))
                    if 'File' in colored_column_name:
                        unique_labels = [os.path.basename(l)[-30:] for l in unique_labels if len(l) > 30 ]
                    cbar.ax.set_yticklabels(unique_labels)  # Write labels beside ticks (Y-axis for vertical bar)
                    
                    for row_index, row in dataset.iterrows():
                        label = row[colored_column_name] if colored_column_name else ""
                        
                        if label and label in labels_colors:
                            label_index, label_color = labels_colors[label]
                            color = label_color
                        else:
                            color = 'k'  # fallback for safety
                        
                        label = row[colored_column_name] if colored_column_name else ""
                        y = columns_indices[row["Column ID"]]
                        # Only show label once for legend
                        if label not in plotted_labels and label:
                            self.view.raster_ax.vlines(
                                x=row['Peak index'],
                                ymin=y - 0.4, ymax=y + 0.4,
                                color=color,
                                label=label,
                                linewidth=1
                            )
                            plotted_labels.add(label)
                        else:
                            self.view.raster_ax.vlines(
                                x=row['Peak index'],
                                ymin=y - 0.4, ymax=y + 0.4,
                                color=color,
                                linewidth=1
                            )
                        
                else:
                    if "Slope" in colored_column_name:
                        # Convert column to numeric, ignoring errors (non-convertible become NaN)
                        numeric_values = pd.to_numeric(dataset[colored_column_name], errors='coerce')
                        max_val = numeric_values.max()
                        replacement_val = 1.10 * max_val
                        dataset[colored_column_name] = dataset[colored_column_name].replace("Uncomputable", replacement_val)
                        dataset[colored_column_name] = dataset[colored_column_name].astype(float)
                        
                    vmin = np.min(dataset[colored_column_name].values)  # min value
                    vmax = np.max(dataset[colored_column_name].values)  # max value
                    
                    # Create a normalization object
                    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
                    
                    # Create a ScalarMappable and add the colorbar
                    
                    plotted_labels = set()
                    for row_index, row in dataset.iterrows():
                        label = row[colored_column_name] if colored_column_name else ""
                        y = columns_indices[row["Column ID"]]
                        color = cmap(norm(row[colored_column_name]))
                        if label not in plotted_labels and label:
                            self.view.raster_ax.vlines(
                                x=row['Peak index'],
                                ymin=y - 0.4, ymax=y + 0.4,  # These will be scaled later (see note below)
                                color=color,
                                label=label,
                                linewidth=1
                            )
                            plotted_labels.add(label)
                        else:
                            self.view.raster_ax.vlines(
                                x=row['Peak index'],
                                ymin=y - 0.4, ymax=y + 0.4,  # These will be scaled later (see note below)
                                linewidth=1,
                                color=color,
                            )
                    
                    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
                    sm.set_array([])  # Needed for older versions of matplotlib
                    self.view.raster_figure.colorbar(sm, ax=self.view.raster_ax, label=colored_column_name)
            else:
                plotted_labels = set()
                
                cmap = matplotlib.cm.get_cmap(self.model.widgets_values["raster_colormap_cbbox"])
                for row_index, row in dataset.iterrows():
                    label = row[colored_column_name] if colored_column_name else ""
                    y = columns_indices[row["Column ID"]]
                    color = cmap(1.0)
                    if label not in plotted_labels and label:
                        self.view.raster_ax.vlines(
                            x=row['Peak index'],
                            ymin=y - 0.4, ymax=y + 0.4,  # These will be scaled later (see note below)
                            color=color,
                            label=label,
                            linewidth=1
                        )
                        plotted_labels.add(label)
                    else:
                        self.view.raster_ax.vlines(
                            x=row['Peak index'],
                            ymin=y - 0.4, ymax=y + 0.4,  # These will be scaled later (see note below)
                            linewidth=1,
                            color=color,
                        )
            self.view.raster_ax.set_ylim(-0.5, len(self.model.dataset["Column ID"].unique())+1)
            self.view.raster_ax.set_xlim(0, dataset["Number of values"].max())
            plt.legend()
            
            self.view.raster_figure.tight_layout()
            self.view.raster_canvas.draw()
            self.raster_drawn = True
    
    def check_parameters(self):
        errors = []
        print(self.view.widgets["specific_subsample_table"].get_current_values())
        if self.model.dataset is None:
            errors.append("No dataset loaded.")
            
        if self.model.widgets_values["raster_as_colormap_cbbox"] == "Filtered values" and self.model.widgets_values["specific_subsample_cbbox"] == "None":
            errors.append("You can not specify 'Filtered values' as colormap if you've not filtered any values.")
        if errors:
            QMessageBox.warning(self.view, "Warning", "\n".join(errors))
            return False
        else: return True
    
    
    def raster_plot_on_move(self, event):
        pass
    
    
    
    def raster_plot_on_click(self, event):
        if self.raster_drawn:
            if event.button is MouseButton.LEFT:
                if event.inaxes:
                    x, y = int(event.xdata), int(event.ydata)
                    x, spike_key = self.find_closest_spike_x_given_y(x, y)
                    if x:
                        self.selected_spike_coordinates = x, y
                        self.selected_spike_key = spike_key
                        self.view.widgets["raster_selected_spike_label"].setText(f"Selected spike: "
                                                                                 f"(x={x},"
                                                                                 f" y={y}), key: {self.selected_spike_key}")
                    
                        # Remove old point if it exists
                        if self.selected_spike_artist is not None:
                            self.selected_spike_artist.remove()
                            self.selected_spike_artist = None
                        
                        # Plot a new point
                        self.selected_spike_artist = self.view.raster_ax.vlines(x=x,
                                                               ymin=y-0.4,
                                                               ymax=y+0.4,
                                                               color='red', linewidth=3, zorder=5)
                        
                        # Redraw the canvas
                        self.view.raster_canvas.draw()
                    
    def select_next_previous_spike(self, axis, increment):
        if self.raster_drawn:

            x, y = self.selected_spike_coordinates if self.selected_spike_coordinates is not None else (0, 0)
            
            x, spike_key = self.get_next_previous_x(x, y, increment)
            y = y+1 if axis=='y' and increment==1 else y
            y = y-1 if axis=='y' and increment==-1 else y
            self.selected_spike_coordinates = x, y
            self.selected_spike_key = spike_key
            
            if self.selected_spike_artist is not None:
                self.selected_spike_artist.remove()
                self.selected_spike_artist = None
            
            self.selected_spike_artist = self.view.raster_ax.vlines(x=x,
                                                   ymin=y - 0.4,
                                                   ymax=y + 0.4,
                                                   color='red', linewidth=3, zorder=5)
            
            self.view.raster_canvas.draw()
            self.view.widgets["raster_selected_spike_label"].setText(f"Selected spike: "
                                                                     f"(x={x},"
                                                                     f" y={y}), key: {self.selected_spike_key}")
            
    def find_closest_spike_x_given_y(self, x, y):
        subsample_cbbox = self.model.widgets_values["specific_subsample_cbbox"]
        if subsample_cbbox == "File" or subsample_cbbox == "Target":
            subsample_values = [item for item, checked in
                                self.view.widgets["specific_subsample_table"].get_current_values().items() if
                                checked == True]
            dataset = self.model.dataset.loc[self.model.dataset[subsample_cbbox].isin(subsample_values)]
        else:
            dataset = self.model.dataset
            
        selected_column = ""
        for i, unique_col in enumerate(sorted(dataset["Column ID"].unique())):
            if i == y:
                selected_column = unique_col
                print(selected_column, x)
        
        dataset = dataset.loc[dataset["Column ID"]==selected_column]
        all_x = dataset["Peak index"].to_numpy()
        all_keys = dataset["Key"].to_numpy()
        if len(all_x) > 0:
            # Compute squared distances (avoid sqrt for performance if you just want the minimum)
            dist_sq = (all_x - x) ** 2
            
            # Index of closest point
            closest_idx = np.argmin(dist_sq)
            
            # Closest point (as Series)
            closest_spike = dataset.iloc[closest_idx]
            return closest_spike["Peak index"], closest_spike["Key"]
        else:
            return None, None
    
    def get_next_previous_x(self, x, y, increment):
        subsample_cbbox = self.model.widgets_values["specific_subsample_cbbox"]
        if subsample_cbbox == "File" or subsample_cbbox == "Target":
            subsample_values = [item for item, checked in
                                self.view.widgets["specific_subsample_table"].get_current_values().items() if
                                checked == True]
            dataset = self.model.dataset.loc[self.model.dataset[subsample_cbbox].isin(subsample_values)]
        else:
            dataset = self.model.dataset
        
        selected_column = ""
        for i, unique_col in enumerate(sorted(dataset["Column ID"].unique())):
            if i == y:
                selected_column = unique_col
                print(selected_column, x)
        
        dataset = dataset.loc[dataset["Column ID"] == selected_column]
        sorted_dataset = dataset.sort_values(by="Peak index",)
        sorted_dataset = sorted_dataset.reset_index(drop=True)
        x_index = 0
        for index in sorted_dataset.index:
            if x == sorted_dataset["Peak index"].iloc[index]:
                x_index = index
        x_index = x_index + increment if 0 < x_index + increment < len(sorted_dataset["Peak index"]) else len(sorted_dataset["Peak index"])
        x_index = len(sorted_dataset["Peak index"])-1 if x_index >= len(sorted_dataset["Peak index"]) else x_index
        x_index = 0 if x_index <= 0 else x_index

        return sorted_dataset["Peak index"][x_index], sorted_dataset["Key"][x_index]
        
    def add_selected_spike(self):
        if self.selected_spike_coordinates and self.raster_drawn:
            tableeditor = self.view.widgets["spike_plot_table"]
            tableeditor.add_row()
            tableeditor.set_spike_coord(self.selected_spike_coordinates[0], self.selected_spike_coordinates[1])
            tableeditor.set_spike_key(self.selected_spike_key)
            tableeditor.set_spike_target(self.model.dataset.loc[self.model.dataset["Key"] == self.selected_spike_key]["Target"].values[0])
            self.spike_keys_to_plot.append(self.selected_spike_key)
    
    def draw_spikes(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        if self.check_parameters():
            self.view.spike_ax.clear()
            if self.spike_keys_to_plot:
                tableeditor = self.view.widgets["spike_plot_table"]
                extracted_col = [col for col in self.model.dataset.columns if "Extracted data" in col][0]
                row_count = tableeditor.table.rowCount()
                for r in range(row_count):
                    spike_key = self.model.widgets_values[f"spikeplot_key_label_{r}"]
                    row = self.model.dataset.loc[self.model.dataset["Key"] == spike_key]
                    target = row["Target"]
                    linestyle = self.model.widgets_values[f"spikeplot_linestyle_cbbox_{r}"]
                    alpha = self.model.widgets_values[f"spikeplot_alpha_slider_{r}"] / 100
                    linewidth = self.model.widgets_values[f"spikeplot_linewidth_edit_{r}"]
                    color_btn = self.view.widgets[f"spikeplot_color_btn_{r}"]
                    color = self.parent_controller.extract_button_color(btn=color_btn)
                    data = ast.literal_eval(row[extracted_col].iloc[0])
                    self.view.spike_ax.plot(data, color=color, alpha=alpha, linestyle=linestyle, linewidth=linewidth,
                                            label=spike_key)
                    
                    
                self.view.spike_figure.legend()
                self.view.spike_figure.tight_layout()
                self.view.spike_canvas.draw()
            
    