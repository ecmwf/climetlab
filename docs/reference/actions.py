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
    # [Coastlines] This action controls the plotting of coastlines, rivers, cities and country boundaries, as well as the latitude/longitude grid lines.
    map_coastline_general_style: str = "",
    map_coastline: bool = True,
    map_grid: bool = True,
    map_label: bool = True,
    # [CoastPlotting]
    map_coastline_resolution: str = "automatic",
    map_coastline_land_shade: bool = False,
    map_coastline_land_shade_colour: str = "green",
    map_coastline_sea_shade: bool = False,
    map_coastline_sea_shade_colour: str = "blue",
    map_boundaries: bool = False,
    map_cities: bool = False,
    map_rivers: bool = False,
    map_rivers_style: str = "solid",
    map_rivers_colour: str = "blue",
    map_rivers_thickness: int = 1,
    map_user_layer: bool = False,
    map_user_layer_name: str = "",
    map_user_layer_projection: str = "",
    map_user_layer_style: str = "solid",
    map_user_layer_colour: str = "blue",
    map_user_layer_thickness: int = 1,
    map_coastline_colour: str = "black",
    map_coastline_style: str = "solid",
    map_coastline_thickness: int = 1,
    # [GridPlotting]
    map_grid_latitude_reference: float = 0.0,
    map_grid_latitude_increment: float = 10.0,
    map_grid_longitude_reference: float = 0.0,
    map_grid_longitude_increment: float = 20.0,
    map_grid_line_style: str = "solid",
    map_grid_thickness: int = 1,
    map_grid_colour: str = "black",
    map_grid_frame: bool = False,
    map_grid_frame_line_style: str = "solid",
    map_grid_frame_thickness: int = 1,
    map_grid_frame_colour: str = "black",
    # [LabelPlotting]
    map_label_font: str = "sansserif",
    map_label_font_style: str = "normal",
    map_label_colour: str = "black",
    map_label_height: float = 0.25,
    map_label_blanking: bool = True,
    map_label_latitude_frequency: float = 1.0,
    map_label_longitude_frequency: float = 1.0,
    map_label_left: bool = True,
    map_label_right: bool = True,
    map_label_top: bool = True,
    map_label_bottom: bool = True,
):
    return macro.mcoast(**_given_args(inspect.currentframe()))


def mcont(
    *,
    # [Contour] This action controls the plotting of isolines, contour bands and grid points. It is used to plot gridded data, such as fields.
    legend: bool = False,
    contour: bool = True,
    contour_method: str = "automatic",
    contour_interpolation_floor: float = -2147483647.0,
    contour_interpolation_ceiling: float = 2147483647.0,
    contour_automatic_setting: str = False,
    contour_style_name: str = "",
    contour_metadata_only: bool = False,
    contour_hilo: str = False,
    contour_grid_value_plot: bool = False,
    # [Akima474Method]
    contour_akima_x_resolution: float = 1.5,
    contour_akima_y_resolution: float = 1.5,
    # [Akima760Method]
    # contour_akima_x_resolution: float = 1.5,
    # contour_akima_y_resolution: float = 1.5,
    # [AutomaticContourMethod]
    # [BothValuePlotMethod]
    contour_grid_value_min: float = -1e21,
    contour_grid_value_max: float = 1e21,
    contour_grid_value_lat_frequency: int = 1,
    contour_grid_value_lon_frequency: int = 1,
    contour_grid_value_height: float = 0.25,
    contour_grid_value_colour: str = "blue",
    contour_grid_value_format: str = "(automatic)",
    contour_grid_value_marker_height: float = 0.25,
    contour_grid_value_marker_colour: str = "red",
    contour_grid_value_marker_qual: str = "low",
    contour_grid_value_marker_index: int = 3,
    contour_grid_value_position: str = "top",
    # [CalculateColourTechnique]
    contour_shade_max_level_colour: str = "blue",
    contour_shade_min_level_colour: str = "red",
    contour_shade_colour_direction: str = "anti_clockwise",
    # [CellShading]
    contour_shade_cell_resolution: float = 10.0,
    contour_shade_cell_method: str = "nearest",
    contour_shade_cell_resolution_method: str = "classic",
    # [CountSelectionType]
    contour_max_level: float = 1e21,
    contour_min_level: float = -1e21,
    contour_shade_max_level: float = 1e21,
    contour_shade_min_level: float = -1e21,
    contour_level_count: int = 10,
    contour_level_tolerance: int = 2,
    contour_reference_level: float = 0.0,
    # [DotPolyShadingMethod]
    contour_shade_dot_size: float = 0.02,
    contour_shade_max_level_density: float = 50.0,
    contour_shade_min_level_density: float = 1.0,
    # [DumpShading]
    # [GradientsColourTechnique]
    contour_gradients_colour_list: List[str] = [],
    contour_gradients_waypoint_method: str = "both",
    contour_gradients_technique: str = "rgb",
    contour_gradients_technique_direction: str = "clockwise",
    contour_gradients_step_list: List[int] = [],
    # [GridShading]
    contour_shade_method: str = "dot",
    contour_grid_shading_position: str = "middle",
    # [HatchPolyShadingMethod]
    contour_shade_hatch_index: int = 0,
    contour_shade_hatch_thickness: int = 1,
    contour_shade_hatch_density: float = 18.0,
    # [HiLoBoth]
    contour_hilo_height: float = 0.4,
    contour_hi_colour: str = "blue",
    contour_lo_colour: str = "blue",
    contour_hilo_format: str = "(automatic)",
    # [HiLoMarker]
    contour_hilo_marker_height: float = 0.1,
    contour_hilo_marker_index: int = 3,
    contour_hilo_marker_colour: str = "red",
    # [HiLoNumber]
    # contour_hilo_height: float = 0.4,
    # contour_hi_colour: str = "blue",
    # contour_lo_colour: str = "blue",
    # contour_hilo_format: str = "(automatic)",
    # [HiLoText]
    # contour_hilo_height: float = 0.4,
    # contour_hi_colour: str = "blue",
    # contour_lo_colour: str = "blue",
    # contour_hilo_format: str = "(automatic)",
    contour_hi_text: str = "H",
    contour_lo_text: str = "L",
    contour_hilo_blanking: bool = False,
    # [HighHiLo]
    contour_hilo_type: str = "text",
    contour_hilo_window_size: int = 3,
    contour_hilo_max_value: float = 1e21,
    contour_hilo_min_value: float = -1e21,
    contour_hi_max_value: float = 1e21,
    contour_hi_min_value: float = -1e21,
    contour_lo_max_value: float = 1e21,
    contour_lo_min_value: float = -1e21,
    contour_hilo_marker: bool = False,
    # [IntervalSelectionType]
    # contour_max_level: float = 1e+21,
    # contour_min_level: float = -1e+21,
    # contour_shade_max_level: float = 1e+21,
    # contour_shade_min_level: float = -1e+21,
    # contour_reference_level: float = 0.0,
    contour_interval: float = 8.0,
    # [IsoHighlight]
    contour_highlight_style: str = "solid",
    # contour_reference_level: float = 0.0,
    contour_highlight_colour: str = "blue",
    contour_highlight_thickness: int = 3,
    contour_highlight_frequency: int = 4,
    # [IsoLabel]
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
    # contour_shade_max_level: float = 1e+21,
    # contour_shade_min_level: float = -1e+21,
    contour_shade_colour_method: str = "calculate",
    # [LevelListSelectionType]
    # contour_max_level: float = 1e+21,
    # contour_min_level: float = -1e+21,
    # contour_shade_max_level: float = 1e+21,
    # contour_shade_min_level: float = -1e+21,
    contour_level_list: List[float] = [],
    # [ListColourTechnique]
    contour_shade_colour_list: List[str] = [],
    # [LowHiLo]
    # contour_hilo_type: str = "text",
    # contour_hilo_window_size: int = 3,
    # contour_hilo_max_value: float = 1e+21,
    # contour_hilo_min_value: float = -1e+21,
    # contour_hi_max_value: float = 1e+21,
    # contour_hi_min_value: float = -1e+21,
    # contour_lo_max_value: float = 1e+21,
    # contour_lo_min_value: float = -1e+21,
    # contour_hilo_marker: bool = False,
    # [MarkerShadingTechnique]
    contour_shade_colour_table: List[str] = [],
    contour_shade_height_table: List[float] = [],
    contour_shade_marker_table_type: str = "index",
    contour_shade_marker_table: List[int] = [],
    contour_shade_marker_name_table: List[str] = [],
    # [MarkerValuePlotMethod]
    # contour_grid_value_min: float = -1e+21,
    # contour_grid_value_max: float = 1e+21,
    # contour_grid_value_lat_frequency: int = 1,
    # contour_grid_value_lon_frequency: int = 1,
    # contour_grid_value_height: float = 0.25,
    # contour_grid_value_colour: str = "blue",
    # contour_grid_value_format: str = "(automatic)",
    # contour_grid_value_marker_height: float = 0.25,
    # contour_grid_value_marker_colour: str = "red",
    # contour_grid_value_marker_qual: str = "low",
    # contour_grid_value_marker_index: int = 3,
    # [NoHiLo]
    # [NoHiLoMarker]
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
    # [NoValuePlot]
    # [PaletteColourTechnique]
    contour_shade_palette_name: str = "",
    contour_shade_palette_policy: str = "lastone",
    # [ValuePlot]
    contour_grid_value_type: str = "normal",
    contour_grid_value_plot_type: str = "value",
):
    return macro.mcont(**_given_args(inspect.currentframe()))


def mmap(
    *,
    # [CartesianTransformation]
    subpage_x_axis_type: str = "regular",
    subpage_y_axis_type: str = "regular",
    # [Emagram]
    x_min: float = 0.0,
    subpage_x_automatic: bool = False,
    subpage_y_automatic: bool = False,
    x_max: float = 100.0,
    y_min: float = 0.0,
    y_max: float = 100.0,
    thermo_annotation_width: float = 25.0,
    # [FortranViewNode]
    subpage_x_position: float = -1.0,
    subpage_y_position: float = -1.0,
    subpage_x_length: float = -1.0,
    subpage_y_length: float = -1.0,
    subpage_map_library_area: bool = False,
    subpage_map_area_name: str = False,
    subpage_map_projection: str = "cylindrical",
    subpage_clipping: bool = False,
    subpage_background_colour: str = "none",
    subpage_frame: bool = True,
    subpage_frame_colour: str = "charcoal",
    subpage_frame_line_style: str = "solid",
    subpage_frame_thickness: int = 2,
    subpage_vertical_axis_width: float = 1.0,
    subpage_horizontal_axis_height: float = 0.5,
    subpage_align_horizontal: str = "left",
    subpage_align_vertical: str = "bottom",
    # [MercatorProjection]
    subpage_lower_left_latitude: float = -90.0,
    subpage_lower_left_longitude: float = -180.0,
    subpage_upper_right_latitude: float = 90.0,
    subpage_upper_right_longitude: float = 180.0,
    # [PolarStereographicProjection]
    subpage_map_area_definition_polar: str = "corners",
    subpage_map_hemisphere: str = "north",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    subpage_map_vertical_longitude: float = 0.0,
    subpage_map_centre_latitude: float = 90.0,
    subpage_map_centre_longitude: float = 0.0,
    subpage_map_scale: float = 50000000.0,
    # [Proj4Automatic]
    subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    subpage_map_true_scale_north: float = 6.0,
    subpage_map_true_scale_south: float = -60.0,
    subpage_map_projection_height: float = 42164000.0,
    subpage_map_projection_tilt: float = 0.0,
    subpage_map_projection_azimuth: float = 20.0,
    subpage_map_projection_view_latitude: float = 20.0,
    subpage_map_projection_view_longitude: float = -60.0,
    subpage_map_geos_sweep: float = 0.0,
    # [Proj4Bonne]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Collignon]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4EPSG32661]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4EPSG32761]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4EPSG3857]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4EPSG4326]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4EPSG900913]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Efas]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Geos]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Geose]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Geosw]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Goode]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Google]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Lambert]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4LambertNorthAtlantic]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Mercator]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Meteosat0]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Meteosat145]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Meteosat57]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Mollweide]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4PolarNorth]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4PolarSouth]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4Robinson]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Proj4TPers]
    # subpage_map_area_definition: str = "full",
    # subpage_lower_left_latitude: float = -90.0,
    # subpage_lower_left_longitude: float = -180.0,
    # subpage_upper_right_latitude: float = 90.0,
    # subpage_upper_right_longitude: float = 180.0,
    # subpage_map_vertical_longitude: float = 0.0,
    # subpage_map_true_scale_north: float = 6.0,
    # subpage_map_true_scale_south: float = -60.0,
    # subpage_map_projection_height: float = 42164000.0,
    # subpage_map_projection_tilt: float = 0.0,
    # subpage_map_projection_azimuth: float = 20.0,
    # subpage_map_projection_view_latitude: float = 20.0,
    # subpage_map_projection_view_longitude: float = -60.0,
    # subpage_map_geos_sweep: float = 0.0,
    # [Skewt]
    # x_min: float = 0.0,
    # subpage_x_automatic: bool = False,
    # subpage_y_automatic: bool = False,
    # x_max: float = 100.0,
    # y_min: float = 0.0,
    # y_max: float = 100.0,
    # thermo_annotation_width: float = 25.0,
    # [TaylorProjection]
    taylor_standard_deviation_min: float = 0.0,
    taylor_standard_deviation_max: float = 1.0,
    # [Tephigram]
    # x_min: float = 0.0,
    # subpage_x_automatic: bool = False,
    # subpage_y_automatic: bool = False,
    # x_max: float = 100.0,
    # y_min: float = 0.0,
    # y_max: float = 100.0,
    # thermo_annotation_width: float = 25.0,
):
    return macro.mmap(**_given_args(inspect.currentframe()))


def msymb(
    *,
    # [SymbolAdvancedTableMode]
    symbol_advanced_table_selection_type: str = "count",
    symbol_advanced_table_min_value: float = -1e21,
    symbol_advanced_table_max_value: float = 1e21,
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
    symbol_advanced_table_outlayer_method: str = "none",
    # [SymbolIndividualMode]
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
    # [SymbolPlotting] This action controls the plotting of meteorological and marker symbols. It is used to plot point data, such as observations.
    legend: bool = False,
    symbol_scaling_method: bool = False,
    symbol_scaling_level_0_height: float = 0.1,
    symbol_scaling_factor: float = 4.0,
    symbol_type: str = "number",
    symbol_table_mode: str = "OFF",
    # symbol_marker_mode: str = "index",
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
    # [SymbolTableMode]
    symbol_min_table: List[float] = [],
    symbol_max_table: List[float] = [],
    symbol_marker_table: List[int] = [],
    symbol_name_table: List[str] = [],
    symbol_colour_table: List[str] = [],
    symbol_height_table: List[float] = [],
):
    return macro.msymb(**_given_args(inspect.currentframe()))


def mtable(
    *,
    # [TableDecoder]
    table_filename: str = "",
    table_delimiter: str = ",",
    table_combine_delimiters: bool = False,
    table_header_row: int = 1,
    table_data_row_offset: int = 1,
    table_meta_data_rows: List[int] = [],
    table_x_type: str = "number",
    table_y_type: str = "number",
    table_variable_identifier_type: str = "index",
    table_x_variable: str = 1,
    table_y_variable: str = 2,
    table_value_variable: str = -1,
    table_latitude_variable: float = 2.0,
    table_longitude_variable: float = 1.0,
    table_x_component_variable: str = -1,
    table_y_component_variable: str = -1,
    table_x_missing_value: float = -21000000.0,
    table_y_missing_value: float = -21000000.0,
    table_binning: bool = True,
):
    return macro.mtable(**_given_args(inspect.currentframe()))
