import inspect
from typing import List
from Magics import macro


def _given_args(frame):
    func = frame.f_globals[frame.f_code.co_name]
    user_args = inspect.getargvalues(frame)
    code_args = inspect.getfullargspec(func)
    given = {}

    if code_args.kwonlydefaults:
        pairs = list(code_args.kwonlydefaults.items())
    else:
        pairs = list(zip(code_args.args, code_args.defaults))

    for name, value in pairs:
        if user_args.locals[name] is not value:
            given[name] = user_args.locals[name]
    return given


def mIcont(
    *,
    # [NoIsoPlot] 
    contour_line_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    contour_line_thickness: str = 1,
    contour_line_colour_rainbow: str = False,
    contour_line_colour: str = "blue",
    contour_line_colour_rainbow_method: str = "calculate",
    contour_line_colour_rainbow_max_level_colour: str = "blue",
    contour_line_colour_rainbow_min_level_colour: str = "red",
    contour_line_colour_rainbow_direction: str = "anti_clockwise",
    contour_line_colour_rainbow_colour_list: str = [],
    contour_line_colour_rainbow_colour_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    contour_line_thickness_rainbow_list: str = [],
    contour_line_thickness_rainbow_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    contour_line_style_rainbow_list: str = [],
    contour_line_style_rainbow_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    contour_highlight: bool = True,
    contour_level_selection_type: str = "count",
    contour_label: bool = True,
    contour_shade: bool = False,
    contour_legend_only: str = False,
):
    return macro.mIcont(**_given_args(inspect.currentframe()))


def mcoast(
    *,
    # [Coastlines] This action controls the plotting of coastlines, rivers, cities and country boundaries, as well as the latitude/longitude grid lines.
    map_coastline_general_style: str = "",
    map_coastline: bool = True,
    map_grid: bool = True,
    map_label: bool = True,
    # [CoastPlotting] 
    map_coastline_resolution: str = "automatic",
    map_coastline_land_shade: str = False,
    map_coastline_land_shade_colour: str = "green",
    map_coastline_sea_shade: str = False,
    map_coastline_sea_shade_colour: str = "blue",
    map_boundaries: bool = False,
    map_cities: bool = False,
    map_preview: str = False,
    map_rivers: str = False,
    map_rivers_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    map_rivers_colour: str = "blue",
    map_rivers_thickness: str = 1,
    map_user_layer: str = False,
    map_user_layer_name: str = "",
    map_user_layer_projection: str = "",
    map_user_layer_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    map_user_layer_colour: str = "blue",
    map_user_layer_thickness: str = 1,
    map_coastline_colour: str = "black",
    map_coastline_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    map_coastline_thickness: str = 1,
    # [GridPlotting] 
    map_grid_latitude_reference: str = 0,
    map_grid_latitude_increment: str = 10,
    map_grid_longitude_reference: str = 0,
    map_grid_longitude_increment: str = 20,
    map_grid_line_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    map_grid_thickness: str = 1,
    map_grid_colour: str = "black",
    map_grid_frame: str = False,
    map_grid_frame_line_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    map_grid_frame_thickness: str = 1,
    map_grid_frame_colour: str = "black",
    # [LabelPlotting] 
    map_label_font: str = "sansserif",
    map_label_font_style: str = "normal",
    map_label_colour: str = "black",
    map_label_height: str = 0.25,
    map_label_blanking: str = True,
    map_label_latitude_frequency: str = 1,
    map_label_longitude_frequency: str = 1,
    map_label_left: str = True,
    map_label_right: str = True,
    map_label_top: str = True,
    map_label_bottom: str = True,
):
    return macro.mcoast(**_given_args(inspect.currentframe()))


def mcont(
    *,
    # [Contour] This action controls the plotting of isolines, contour bands and grid points. It is used to plot gridded data, such as fields.
    legend: str = False,
    contour: str = True,
    contour_method: str = "automatic",
    contour_interpolation_floor: str = "-INT_MAX",
    contour_interpolation_ceiling: str = "INT_MAX",
    contour_automatic_setting: str = False,
    contour_style_name: str = "",
    contour_metadata_only: str = False,
    contour_hilo: str = False,
    contour_grid_value_plot: str = False,
    # [Akima474Method] 
    contour_akima_x_resolution: str = 1.5,
    contour_akima_y_resolution: str = 1.5,
    # [Akima760Method] 
    #contour_akima_x_resolution: str = 1.5,
    #contour_akima_y_resolution: str = 1.5,
    # [AutomaticContourMethod] 
    # [BothValuePlotMethod] 
    contour_grid_value_min: str = -1e+21,
    contour_grid_value_max: str = 1e+21,
    contour_grid_value_lat_frequency: str = 1,
    contour_grid_value_lon_frequency: str = 1,
    contour_grid_value_height: str = 0.25,
    contour_grid_value_colour: str = "blue",
    contour_grid_value_format: str = "(automatic)",
    contour_grid_value_marker_height: str = 0.25,
    contour_grid_value_marker_colour: str = "red",
    contour_grid_value_marker_qual: str = "low",
    contour_grid_value_marker_index: str = 3,
    contour_grid_value_position: str = "top",
    # [CalculateColourTechnique] 
    contour_shade_max_level_colour: str = "blue",
    contour_shade_min_level_colour: str = "red",
    contour_shade_colour_direction: str = "anti_clockwise",
    # [CellShading] 
    contour_shade_cell_resolution: str = 10,
    contour_shade_cell_method: str = "nearest",
    contour_shade_cell_resolution_method: str = "classic",
    # [CountSelectionType] 
    contour_max_level: str = 1e+21,
    contour_min_level: str = -1e+21,
    contour_shade_max_level: str = 1e+21,
    contour_shade_min_level: str = -1e+21,
    contour_level_count: str = 10,
    contour_level_tolerance: str = 2,
    contour_reference_level: str = 0.0,
    # [DotPolyShadingMethod] 
    contour_shade_dot_size: str = 0.02,
    contour_shade_max_level_density: str = 50.0,
    contour_shade_min_level_density: str = 1.0,
    # [DumpShading] 
    # [GradientsColourTechnique] 
    contour_gradients_colour_list: str = [],
    contour_gradients_waypoint_method: str = "both",
    contour_gradients_technique: str = "rgb",
    contour_gradients_technique_direction: str = "clockwise",
    contour_gradients_step_list: str = [],
    # [GridShading] 
    contour_shade_method: str = "dot",
    contour_grid_shading_position: str = "middle",
    # [HatchPolyShadingMethod] 
    contour_shade_hatch_index: str = 0,
    contour_shade_hatch_thickness: str = 1,
    contour_shade_hatch_density: str = 18.0,
    # [HiLoBoth] 
    contour_hilo_height: str = 0.4,
    contour_hi_colour: str = "blue",
    contour_lo_colour: str = "blue",
    contour_hilo_format: str = "(automatic)",
    # [HiLoMarker] 
    contour_hilo_marker_height: str = 0.1,
    contour_hilo_marker_index: str = 3,
    contour_hilo_marker_colour: str = "red",
    # [HiLoNumber] 
    #contour_hilo_height: str = 0.4,
    #contour_hi_colour: str = "blue",
    #contour_lo_colour: str = "blue",
    #contour_hilo_format: str = "(automatic)",
    # [HiLoText] 
    #contour_hilo_height: str = 0.4,
    #contour_hi_colour: str = "blue",
    #contour_lo_colour: str = "blue",
    #contour_hilo_format: str = "(automatic)",
    contour_hi_text: str = "H",
    contour_lo_text: str = "L",
    contour_hilo_blanking: str = False,
    # [HighHiLo] 
    contour_hilo_type: str = "text",
    contour_hilo_window_size: str = 3,
    contour_hilo_max_value: str = 1e+21,
    contour_hilo_min_value: str = -1e+21,
    contour_hi_max_value: str = 1e+21,
    contour_hi_min_value: str = -1e+21,
    contour_lo_max_value: str = 1e+21,
    contour_lo_min_value: str = -1e+21,
    contour_hilo_marker: str = False,
    # [IntervalSelectionType] 
    #contour_max_level: str = 1e+21,
    #contour_min_level: str = -1e+21,
    #contour_shade_max_level: str = 1e+21,
    #contour_shade_min_level: str = -1e+21,
    #contour_reference_level: str = 0.0,
    contour_interval: str = 8.0,
    # [IsoLabel] 
    contour_label_type: str = "number",
    contour_label_text: str = "",
    contour_label_height: str = 0.3,
    contour_label_format: str = "(automatic)",
    contour_label_blanking: str = True,
    contour_label_font: str = "sansserif",
    contour_label_font_style: str = "normal",
    contour_label_colour: str = "contour_line_colour",
    contour_label_frequency: str = 2,
    # [IsoShading] 
    contour_shade_technique: str = "polygon_shading",
    #contour_shade_max_level: str = 1e+21,
    #contour_shade_min_level: str = -1e+21,
    contour_shade_colour_method: str = "calculate",
    # [LevelListSelectionType] 
    #contour_max_level: str = 1e+21,
    #contour_min_level: str = -1e+21,
    #contour_shade_max_level: str = 1e+21,
    #contour_shade_min_level: str = -1e+21,
    contour_level_list: str = [],
    # [ListColourTechnique] 
    contour_shade_colour_list: str = [],
    # [LowHiLo] 
    #contour_hilo_type: str = "text",
    #contour_hilo_window_size: str = 3,
    #contour_hilo_max_value: str = 1e+21,
    #contour_hilo_min_value: str = -1e+21,
    #contour_hi_max_value: str = 1e+21,
    #contour_hi_min_value: str = -1e+21,
    #contour_lo_max_value: str = 1e+21,
    #contour_lo_min_value: str = -1e+21,
    #contour_hilo_marker: str = False,
    # [MarkerShadingTechnique] 
    contour_shade_colour_table: str = [],
    contour_shade_height_table: str = [],
    contour_shade_marker_table_type: str = "index",
    contour_shade_marker_table: str = [],
    contour_shade_marker_name_table: str = [],
    # [MarkerValuePlotMethod] 
    #contour_grid_value_min: str = -1e+21,
    #contour_grid_value_max: str = 1e+21,
    #contour_grid_value_lat_frequency: str = 1,
    #contour_grid_value_lon_frequency: str = 1,
    #contour_grid_value_height: str = 0.25,
    #contour_grid_value_colour: str = "blue",
    #contour_grid_value_format: str = "(automatic)",
    #contour_grid_value_marker_height: str = 0.25,
    #contour_grid_value_marker_colour: str = "red",
    #contour_grid_value_marker_qual: str = "low",
    #contour_grid_value_marker_index: str = 3,
    # [NoHiLo] 
    # [NoValuePlot] 
    # [PaletteColourTechnique] 
    contour_shade_palette_name: str = "",
    contour_shade_palette_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    # [ValuePlot] 
    contour_grid_value_type: str = "normal",
    contour_grid_value_plot_type: str = "value",
):
    return macro.mcont(**_given_args(inspect.currentframe()))


def mcoont(
    *,
    # [NoHiLoMarker] 
):
    return macro.mcoont(**_given_args(inspect.currentframe()))


def msymb(
    *,
    # [SymbolAdvancedTableMode] 
    symbol_advanced_table_selection_type: str = "count",
    symbol_advanced_table_min_value: str = -1e+21,
    symbol_advanced_table_max_value: str = 1e+21,
    symbol_advanced_table_level_count: str = 10,
    symbol_advanced_table_level_tolerance: str = 2,
    symbol_advanced_table_interval: str = 8.0,
    symbol_advanced_table_reference_level: str = 0.0,
    symbol_advanced_table_level_list: str = [],
    symbol_advanced_table_colour_method: str = "calculate",
    symbol_advanced_table_max_level_colour: str = "blue",
    symbol_advanced_table_min_level_colour: str = "red",
    symbol_advanced_table_colour_direction: str = "anti_clockwise",
    symbol_advanced_table_colour_list: str = [],
    symbol_advanced_table_colour_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    symbol_advanced_table_marker_list: str = [],
    symbol_advanced_table_marker_name_list: str = [],
    symbol_advanced_table_marker_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    symbol_advanced_table_height_method: str = "list",
    symbol_advanced_table_height_max_value: str = 0.2,
    symbol_advanced_table_height_min_value: str = 0.1,
    symbol_advanced_table_height_list: str = [],
    symbol_advanced_table_height_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "lastone",
    symbol_advanced_table_text_list: str = [],
    symbol_advanced_table_text_list_policy: {'documentation': 'hello', 'values': {'lastone': 'la doc', 'cycle': 'la doc'}} = "cycle",
    symbol_advanced_table_text_font: str = "sansserif",
    symbol_advanced_table_text_font_size: str = 0.25,
    symbol_advanced_table_text_font_style: str = "normal",
    symbol_advanced_table_text_font_colour: str = "automatic",
    symbol_advanced_table_text_display_type: str = "none",
    symbol_advanced_table_outlayer_method: bool = "none",
    symbol_advanced_table_outlayer_min_value: str = -1e+21,
    symbol_advanced_table_outlayer_max_value: str = 1e+21,
    # [SymbolIndividualMode] 
    legend_user_text: str = "",
    symbol_colour: str = "blue",
    symbol_height: str = 0.2,
    symbol_marker_mode: str = "index",
    symbol_marker_index: str = 1,
    symbol_marker_name: str = "dot",
    symbol_image_path: str = "",
    symbol_image_format: str = "automatic",
    symbol_image_width: str = -1,
    symbol_image_height: str = -1,
    symbol_text_list: str = [],
    symbol_text_position: str = "right",
    symbol_text_font: str = "sansserif",
    symbol_text_font_size: str = 0.25,
    symbol_text_font_style: str = "normal",
    symbol_text_font_colour: str = "automatic",
    symbol_legend_height: str = -1,
    # [SymbolPlotting] This action controls the plotting of meteorological and marker symbols. It is used to plot point data, such as observations.
    legend: str = False,
    symbol_scaling_method: str = False,
    symbol_scaling_level_0_height: str = 0.1,
    symbol_scaling_factor: str = 4.0,
    symbol_type: str = "number",
    symbol_table_mode: str = "OFF",
    #symbol_marker_mode: str = "index",
    symbol_format: str = "(automatic)",
    symbol_text_blanking: str = False,
    symbol_outline: str = False,
    symbol_outline_colour: str = "black",
    symbol_outline_thickness: str = 1,
    symbol_outline_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    symbol_connect_line: str = False,
    symbol_connect_automatic_line_colour: str = True,
    symbol_connect_line_colour: str = "black",
    symbol_connect_line_thickness: str = 1,
    symbol_connect_line_style: {'documentation': 'hello', 'values': {'solid': 'la doc', 'dash': 'la doc', 'dot': 'la doc', 'chain_dash': 'la doc', 'chain_dot': 'la doc'}} = "solid",
    symbol_legend_only: str = False,
    # [SymbolTableMode] 
    symbol_min_table: str = [],
    symbol_max_table: str = [],
    symbol_marker_table: str = [],
    symbol_name_table: str = [],
    symbol_colour_table: str = [],
    symbol_height_table: str = [],
):
    return macro.msymb(**_given_args(inspect.currentframe()))
