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


def mcoast(
    *,
    # [CoastPlotting] 
    map_coastline_resolution: str = "automatic",
    map_coastline_land_shade: bool = False,
    map_coastline_land_shade_colour: str = "green",
    map_coastline_sea_shade: bool = False,
    map_coastline_sea_shade_colour: str = "blue",
    map_boundaries: bool = False,
    map_cities: bool = False,
    map_preview: bool = False,
    map_rivers: str = False,
    map_rivers_style: str = "solid",
    map_rivers_colour: str = "blue",
    map_rivers_thickness: int = 1,
    map_user_layer: str = False,
    map_user_layer_name: str = "",
    map_user_layer_projection: str = "",
    map_user_layer_style: str = "solid",
    map_user_layer_colour: str = "blue",
    map_user_layer_thickness: int = 1,
    map_coastline_colour: str = "black",
    map_coastline_style: str = "solid",
    map_coastline_thickness: int = 1,
    # [Coastlines] The parameters relating to action routine PCOAST (C++ class Coastlines) enable users to control the plotting of coastlines and grid lines.
    map_coastline_general_style: str = "",
    map_coastline: bool = True,
    map_grid: bool = True,
    map_label: bool = True,
    # [GridPlotting] This object will control the settings of the Map Grids.
    map_grid_latitude_reference: float = 0,
    map_grid_latitude_increment: float = 10.0,
    map_grid_longitude_reference: float = 0,
    map_grid_longitude_increment: float = 20.0,
    map_grid_line_style: str = "solid",
    map_grid_thickness: int = 1,
    map_grid_colour: str = "black",
    map_grid_frame: bool = False,
    map_grid_frame_line_style: str = "solid",
    map_grid_frame_thickness: int = 1,
    map_grid_frame_colour: str = "black",
    # [LabelPlotting] This object will control the settings of the Map Labels.
    map_label_font: str = "sansserif",
    map_label_font_style: str = "normal",
    map_label_colour: str = "black",
    map_label_height: float = 0.25,
    map_label_blanking: bool = True,
    map_label_latitude_frequency: int = 1,
    map_label_longitude_frequency: int = 1,
    map_label_left: bool = True,
    map_label_right: bool = True,
    map_label_top: bool = True,
    map_label_bottom: bool = True,
):
    return macro.mcoast(**_given_args(inspect.currentframe()))


def mcont(
    *,
    # [Akima474Method] Generates contour lines from a regular/irregular grid of data points. First a denser regular grid is created based on the original grid and then the isolines are produced by applying a simple linear contouring algorithm. The user may, by calling the parameter setting routines, select the interpolation level which defines the density of the output grid, which then determines the smoothness of the isolines.
    contour_akima_x_resolution: float = 1.5,
    contour_akima_y_resolution: float = 1.5,
    # [Akima760Method] Generates contour lines from a regular/irregular grid of data points. First a denser regular grid is created based on the original grid and then the isolines are produced by applying a simple linear contouring algorithm. The user may, by calling the parameter setting routines, select the interpolation level which defines the density of the output grid, which then determines the smoothness of the isolines.
    #contour_akima_x_resolution: float = 1.5,
    #contour_akima_y_resolution: float = 1.5,
    # [AutomaticContourMethod] 
    # [Contour] This controls the plotting of isolines, contour bands and grid points.
    legend: bool = False,
    contour: str = True,
    contour_method: str = "automatic",
    contour_interpolation_floor: float = -2147483647,
    contour_interpolation_ceiling: float = 2147483647,
    contour_automatic_setting: str = False,
    contour_style_name: str = "",
    contour_metadata_only: bool = False,
    contour_hilo: str = False,
    contour_grid_value_plot: str = False,
    # [CountSelectionType] The number of contour levels may be set by the user by setting the parameter CONTOUR_LEVEL_SELECTION_TYPE to 'COUNT' (default) and CONTOUR_LEVEL_COUNT to the number of levels to be plotted. MAGICS will then calculate the contour interval and the user's plot will consist of the number of levels specified with a regular contour interval. This is the default method and the default number of levels is 10. The exact number of contour levels plotted may not be CONTOUR_LEVEL_COUNT as PCONT will always use the value stored in CONTOUR_REFERENCE_LEVEL as a starting point and will pick reasonable values for the contour interval.
    contour_max_level: float = 1e+21,
    contour_min_level: float = -1e+21,
    contour_shade_max_level: float = 1e+21,
    contour_shade_min_level: float = -1e+21,
    contour_level_count: int = 10,
    contour_level_tolerance: int = 2,
    contour_reference_level: float = 0.0,
    # [HighHiLo] 
    contour_hilo_type: str = "text",
    contour_hilo_window_size: int = 3,
    contour_hilo_max_value: float = 1e+21,
    contour_hilo_min_value: float = -1e+21,
    contour_hi_max_value: float = 1e+21,
    contour_hi_min_value: float = -1e+21,
    contour_lo_max_value: float = 1e+21,
    contour_lo_min_value: float = -1e+21,
    contour_hilo_marker: str = False,
    # [IntervalSelectionType] If the parameter CONTOUR_LEVEL_SELECTION_TYPE is set to 'INTERVAL' , MAGICS will plot contours at regularly spaced intervals using the value of CONTOUR_REFERENCE_LEVEL as a base and the value in CONTOUR_INTERVAL as the interval between levels.
    #contour_max_level: float = 1e+21,
    #contour_min_level: float = -1e+21,
    #contour_shade_max_level: float = 1e+21,
    #contour_shade_min_level: float = -1e+21,
    #contour_reference_level: float = 0.0,
    contour_interval: float = 8.0,
    # [IsoLabel] The action routine PCONT will plot labels on contour lines either by default or as directed by the user. Contour labels may be plotted with different attributes from the contour line, e.g. colour and thickness. Contour labels are, by default, plotted on every 2nd contour line, but this may be changed by the user, if desired.
    contour_label_type: str = "number",
    contour_label_text: str = "",
    contour_label_height: float = 0.3,
    contour_label_format: str = "(automatic)",
    contour_label_blanking: bool = True,
    contour_label_font: str = "sansserif",
    contour_label_font_style: str = "normal",
    contour_label_colour: str = "contour_line_colour",
    contour_label_frequency: int = 2,
    # [IsoShading] 
    contour_shade_technique: str = "polygon_shading",
    #contour_shade_max_level: float = 1e+21,
    #contour_shade_min_level: float = -1e+21,
    contour_shade_colour_method: str = "calculate",
    # [LevelListSelectionType] Users may supply a list of the contour levels to be plotted by setting the parameter CONTOUR_LEVEL_SELECTION_TYPE to 'LEVEL_LIST' and passing an array of contour level values. This method enables users to plot contours with irregular intervals.
    #contour_max_level: float = 1e+21,
    #contour_min_level: float = -1e+21,
    #contour_shade_max_level: float = 1e+21,
    #contour_shade_min_level: float = -1e+21,
    contour_level_list: List[float] = [],
    # [LowHiLo] 
    #contour_hilo_type: str = "text",
    #contour_hilo_window_size: int = 3,
    #contour_hilo_max_value: float = 1e+21,
    #contour_hilo_min_value: float = -1e+21,
    #contour_hi_max_value: float = 1e+21,
    #contour_hi_min_value: float = -1e+21,
    #contour_lo_max_value: float = 1e+21,
    #contour_lo_min_value: float = -1e+21,
    #contour_hilo_marker: str = False,
    # [NoIsoPlot] 
    contour_line_style: str = "solid",
    contour_line_thickness: int = 1,
    contour_line_colour_rainbow: bool = False,
    contour_line_colour: str = "blue",
    contour_line_colour_rainbow_method: str = "calculate",
    contour_line_colour_rainbow_max_level_colour: str = "blue",
    contour_line_colour_rainbow_min_level_colour: str = "red",
    contour_line_colour_rainbow_direction: str = "anti_clockwise",
    contour_line_colour_rainbow_colour_list: List[str] = [],
    contour_line_colour_rainbow_colour_list_policy: str = "lastone",
    contour_line_thickness_rainbow_list: List[int] = [],
    contour_line_thickness_rainbow_list_policy: str = "lastone",
    contour_line_style_rainbow_list: List[str] = [],
    contour_line_style_rainbow_list_policy: str = "lastone",
    contour_highlight: bool = True,
    contour_level_selection_type: str = "count",
    contour_label: bool = True,
    contour_shade: bool = False,
    contour_legend_only: bool = False,
    # [ValuePlot] 
    contour_grid_value_type: str = "normal",
    contour_grid_value_plot_type: str = "value",
):
    return macro.mcont(**_given_args(inspect.currentframe()))


def msymb(
    *,
    # [SymbolAdvancedTableMode] Here comes the description of the SymbolTableMode object
    symbol_advanced_table_selection_type: str = "count",
    symbol_advanced_table_min_value: float = -1e+21,
    symbol_advanced_table_max_value: float = 1e+21,
    symbol_advanced_table_level_count: int = 10,
    symbol_advanced_table_level_tolerance: int = 2,
    symbol_advanced_table_interval: float = 8.0,
    symbol_advanced_table_reference_level: float = 0.0,
    symbol_advanced_table_level_list: List[float] = [],
    symbol_advanced_table_colour_method: str = "calculate",
    symbol_advanced_table_max_level_colour: str = "blue",
    symbol_advanced_table_min_level_colour: str = "red",
    symbol_advanced_table_colour_direction: str = "anti_clockwise",
    symbol_advanced_table_colour_list: List[str] = [],
    symbol_advanced_table_colour_list_policy: str = "lastone",
    symbol_advanced_table_marker_list: List[int] = [],
    symbol_advanced_table_marker_name_list: List[str] = [],
    symbol_advanced_table_marker_list_policy: str = "lastone",
    symbol_advanced_table_height_method: str = "list",
    symbol_advanced_table_height_max_value: float = 0.2,
    symbol_advanced_table_height_min_value: float = 0.1,
    symbol_advanced_table_height_list: List[float] = [],
    symbol_advanced_table_height_list_policy: str = "lastone",
    symbol_advanced_table_text_list: List[str] = [],
    symbol_advanced_table_text_list_policy: str = "cycle",
    symbol_advanced_table_text_font: str = "sansserif",
    symbol_advanced_table_text_font_size: float = 0.25,
    symbol_advanced_table_text_font_style: str = "normal",
    symbol_advanced_table_text_font_colour: str = "automatic",
    symbol_advanced_table_text_display_type: str = "none",
    symbol_advanced_table_outlayer_method: bool = "none",
    symbol_advanced_table_outlayer_min_value: float = -1e+21,
    symbol_advanced_table_outlayer_max_value: float = 1e+21,
    # [SymbolIndividualMode] Here comes the description of the SymbolIndividualMode object
    legend_user_text: str = "",
    symbol_colour: str = "blue",
    symbol_height: float = 0.2,
    symbol_marker_mode: str = "index",
    symbol_marker_index: int = 1,
    symbol_marker_name: str = "dot",
    symbol_image_path: str = "",
    symbol_image_format: str = "automatic",
    symbol_image_width: float = -1.0,
    symbol_image_height: float = -1.0,
    symbol_text_list: List[str] = [],
    symbol_text_position: str = "right",
    symbol_text_font: str = "sansserif",
    symbol_text_font_size: float = 0.25,
    symbol_text_font_style: str = "normal",
    symbol_text_font_colour: str = "automatic",
    symbol_legend_height: float = -1.0,
    # [SymbolPlotting] This action routine (and C++object) controls the plotting of meteorological and marker symbols.
    legend: bool = False,
    symbol_scaling_method: bool = False,
    symbol_scaling_level_0_height: float = 0.1,
    symbol_scaling_factor: float = 4.0,
    symbol_type: str = "number",
    symbol_table_mode: str = "OFF",
    #symbol_marker_mode: str = "index",
    symbol_format: str = "(automatic)",
    symbol_text_blanking: bool = False,
    symbol_outline: bool = False,
    symbol_outline_colour: str = "black",
    symbol_outline_thickness: int = 1,
    symbol_outline_style: str = "solid",
    symbol_connect_line: bool = False,
    symbol_connect_automatic_line_colour: bool = True,
    symbol_connect_line_colour: str = "black",
    symbol_connect_line_thickness: int = 1,
    symbol_connect_line_style: str = "solid",
    symbol_legend_only: bool = False,
    # [SymbolTableMode] Here comes the description of the SymbolTableMode object
    symbol_min_table: List[float] = [],
    symbol_max_table: List[float] = [],
    symbol_marker_table: List[int] = [],
    symbol_name_table: List[str] = [],
    symbol_colour_table: List[str] = [],
    symbol_height_table: List[float] = [],
):
    return macro.msymb(**_given_args(inspect.currentframe()))
