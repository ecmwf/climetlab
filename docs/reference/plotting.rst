Plotting
========


legend
------

Collection of parameters defining how a legend will be plotted. To plot a legend the parameter 'Legend'   needs to set to 'on'.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - legend_automatic_box_margin
     - float
     - 5.0
     - margin in % of the legend box [top/bottom] for vertical layout and [left/right] for horizontal layout
   * - legend_automatic_position
     - string
     - top
     - Whether legend box is positioned on the top or on the right of the drawing area
   * - legend_border
     - bool(string)
     - False
     - Plot border around legend box
   * - legend_border_colour
     - Colour(string)
     - blue
     - Colour of border around text box (Full choice of colours)
   * - legend_border_line_style
     - LineStyle(string)
     - solid
     - Line style of border around legend box
   * - legend_border_thickness
     - int
     - 1.0
     - Thickness of legend box border
   * - legend_box_blanking
     - bool(string)
     - False
     - blanking of legend box
   * - legend_box_mode
     - string
     - automatic
     - Whether legend box is positioned automatically or by the user
   * - legend_box_x_length
     - float
     - -1.0
     - Length of legend box in X direction
   * - legend_box_x_position
     - float
     - -1.0
     - X coordinate of lower left corner of legend box (Relative to page_x_position)
   * - legend_box_y_length
     - float
     - 0.0
     - Length of legend box in Y direction
   * - legend_box_y_position
     - float
     - -1.0
     - Y coordinate of lower left corner of legend box (Relative to page_y_position)
   * - legend_column_count
     - int
     - 1.0
     - Number of columns in the legend
   * - legend_display_type
     - LegendMethod(string)
     - disjoint
     - type of shaded legend required
   * - legend_entry_border
     - bool(string)
     - True
     - add a border to the graphical part of each legend entry
   * - legend_entry_border_colour
     - Colour(string)
     - black
     - border colour
   * - legend_entry_plot_direction
     - string
     - automatic
     - Method of filling in legend entries
   * - legend_entry_plot_orientation
     - string
     - bottom_top
     - going from bootom to top ot top to bottom in column mode!
   * - legend_entry_text_width
     - float
     - 60.0
     - Width in percent used for the text part of a legend Entry
   * - legend_histogram_border
     - bool(string)
     - True
     - add a border to the the bars
   * - legend_histogram_border_colour
     - Colour(string)
     - black
     - border colour of the bars
   * - legend_histogram_grid_colour
     - Colour(string)
     - black
     - Colour of the grids
   * - legend_histogram_grid_line_style
     - LineStyle(string)
     - solid
     - Line Style of the grids
   * - legend_histogram_grid_thickness
     - int
     - 1.0
     - thickness of the grids
   * - legend_histogram_max_value
     - bool(string)
     - True
     - show the max value
   * - legend_histogram_mean_value
     - bool(string)
     - False
     - show the mean value
   * - legend_histogram_mean_value_marker
     - int
     - 15.0
     - show the mean value
   * - legend_histogram_mean_value_marker_colour
     - Colour(string)
     - black
     - show the mean value
   * - legend_histogram_mean_value_marker_size
     - float
     - 0.4
     - show the mean value
   * - legend_label_frequency
     - int
     - 1.0
     - Frequency of the labels.
   * - legend_label_frequency
     - int
     - 1.0
     - Frequency of the labels.
   * - legend_only
     - bool(string)
     - False
     - generate only the legend ( used for the wrep..
   * - legend_symbol_height_factor
     - float
     - 1.0
     - Factor to apply to the symbol_height in the legend
   * - legend_text_colour
     - Colour(string)
     - blue
     - Legend text colour
   * - legend_text_composition
     - string
     - automatic_text_only
     - Determines whether to use automatically-generated or user-generated text (or both) in the legend
   * - legend_text_font
     - string
     - sansserif
     - Font name - please make sure this font is installed!
   * - legend_text_font_size
     - string
     - 0.3
     - Font size, specified in cm or in % ex: 0.5cm or 10%
   * - legend_text_font_style
     - string
     - normal
     - Font style. Set this to an empty string in order to remove all styling.
   * - legend_text_format
     - string
     - (automatic)
     - Format of automatic text (MAGICS Format/(AUTOMATIC))
   * - legend_text_orientation
     - float
     - 0.0
     - Orientation of the text : horizontal by default
   * - legend_text_quality
     - string
     - medium
     - Quality of text in legend :  deprecated use legend_text_font and legend_text_font_style
   * - legend_title
     - bool(string)
     - False
     - plot legend title text
   * - legend_title_font_colour
     - Colour(string)
     - automatic
     - Font Colour used for the title: The defaut is the same as the text_entry
   * - legend_title_font_size
     - float
     - -1.0
     - Font size used for the title: The default is the same as text_entry
   * - legend_title_orientation
     - string
     - automatic
     - Orientation of legend title, if automatic the title will be    horizontal for horizontal legend and vertical for vertical
   * - legend_title_position
     - Position(string)
     - automatic
     - relative title position
   * - legend_title_position_ratio
     - float
     - 25.0
     - percentage of the legend box used for the title
   * - legend_title_text
     - string
     - legend
     - Text to plot as legend title
   * - legend_units_text
     - string
     - 
     - Text to plot as units
   * - legend_user_lines
     - stringarray
     - []
     - List of text for legend entries
   * - legend_user_maximum
     - bool(string)
     - False
     - Use of user tailored text for maximum
   * - legend_user_maximum_text
     - string
     - 
     - User tailored text for maximum
   * - legend_user_minimum
     - bool(string)
     - False
     - Use of user tailored text for minimum
   * - legend_user_minimum_text
     - string
     - 
     - User tailored text for minimum
   * - legend_user_text
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_1
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_10
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_2
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_3
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_4
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_5
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_6
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_7
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_8
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_user_text_9
     - string
     - 
     - User text to be associated with a legend sub-entry from a multiple entry
   * - legend_values_list
     - floatarray
     - []
     - List of values to show in the legend
   * - legend_wrep
     - bool(string)
     - False
     - activate wrep mode for legend building

pbinning
--------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - binning_x_count
     - int
     - 10.0
     - Aprroximate number on binns when using the count method
   * - binning_x_interval
     - float
     - 10.0
     - list of binns when using the interval method
   * - binning_x_list
     - floatarray
     - []
     - list of binns when using the list method
   * - binning_x_max_value
     - float
     - 1e+21
     - Max value used to compute the binns
   * - binning_x_method
     - string
     - count
     - Method to compute binns : count/list/interval
   * - binning_x_min_value
     - float
     - -1e+21
     - Min value used to compute the binns
   * - binning_x_reference
     - float
     - 0.0
     - list of binns when using the interval method
   * - binning_y_count
     - int
     - 10.0
     - Aprroximate number on binns when using the count method
   * - binning_y_interval
     - float
     - 10.0
     - list of binns when using the interval method
   * - binning_y_list
     - floatarray
     - []
     - list of binns when using the list method
   * - binning_y_max_value
     - float
     - 1e+21
     - Max value used to compute the binns
   * - binning_y_method
     - string
     - count
     - Method to compute binns : count/list/interval
   * - binning_y_min_value
     - float
     - -1e+21
     - Min value used to compute the binns
   * - binning_y_reference
     - float
     - 0.0
     - list of binns when using the interval method

pcdfgram
--------

The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - cdf_clim_line_colour
     - Colour(string)
     - black
     - Colour of the clim curve
   * - cdf_clim_line_style
     - LineStyle(string)
     - solid
     - Style of the clim curve
   * - cdf_clim_line_thickness
     - int
     - 4.0
     - Thickness of the clim curve
   * - cdf_graph_type
     - string
     - medium
     - Colour of the curve
   * - cdf_lines_colour_array
     - stringarray
     - []
     - Colour of the curve
   * - cdf_lines_style_array
     - stringarray
     - []
     - Style of the curve
   * - cdf_lines_thickness_array
     - intarray
     - []
     - Thickness of the curve
   * - efi_box_border_colour
     - Colour(string)
     - black
     - Style of the curve
   * - efi_box_border_line_style
     - LineStyle(string)
     - solid
     - Style of the curve
   * - efi_box_border_thickness
     - int
     - 1.0
     - Style of the curve
   * - efi_box_colour_array
     - stringarray
     - []
     - Colour of the curve
   * - efi_font
     - string
     - sansserif
     - 
   * - efi_font_colour
     - Colour(string)
     - black
     - 
   * - efi_font_size
     - float
     - 0.25
     - 
   * - efi_font_style
     - string
     - 
     - 
   * - efi_normal_colour
     - Colour(string)
     - black
     - Style of the curve
   * - efi_normal_line_style
     - LineStyle(string)
     - solid
     - Style of the curve
   * - efi_normal_thickness
     - int
     - 4.0
     - Style of the curve
   * - legend
     - bool(string)
     - False
     - Style of the clim curve

pcoast
------

This object suppresses the plotting of the map grid labels

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - map_administrative_boundaries
     - bool(string)
     - False
     - Display administrative boundaries (on/off)
   * - map_administrative_boundaries_colour
     - Colour(string)
     - automatic
     - Colour of administrative boundaries
   * - map_administrative_boundaries_countries_list
     - stringarray
     - []
     - List of countries for which to show administrative borders. Convention used is the 3 Letters ISO Codes, e.g FRA for France, DEU for Germany and GBR for the UK
   * - map_administrative_boundaries_style
     - LineStyle(string)
     - dash
     - Line style of administrative boundaries
   * - map_administrative_boundaries_thickness
     - int
     - 1.0
     - Line thickness of administrative boundaries
   * - map_boundaries
     - NoBoundaries(string)
     - False
     - Add the political boundaries
   * - map_boundaries_colour
     - Colour(string)
     - grey
     - Colour of boundaries
   * - map_boundaries_style
     - LineStyle(string)
     - solid
     - Line style of boundaries
   * - map_boundaries_thickness
     - int
     - 1.0
     - Line thickness of boundaries
   * - map_cities
     - NoCities(string)
     - False
     - Add the cities (capitals)
   * - map_cities_font
     - string
     - sansserif
     - Font used to display the city names.
   * - map_cities_font_colour
     - Colour(string)
     - navy
     - Colour used for city names.
   * - map_cities_font_size
     - float
     - 2.5
     - Font size of city names.
   * - map_cities_font_style
     - string
     - normal
     - Font style used for city names.
   * - map_cities_marker
     - string
     - plus
     - Marker for cities.
   * - map_cities_marker_colour
     - Colour(string)
     - evergreen
     - Colour for city markers.
   * - map_cities_marker_height
     - float
     - 0.7
     - Height of city markers.
   * - map_cities_name_position
     - string
     - above
     - Position where to display the city names.
   * - map_cities_text_blanking
     - bool(string)
     - True
     - Use Blanking when plotting the cityes names .
   * - map_cities_unit_system
     - string
     - percent
     - Unit for city name sizes.
   * - map_coastline
     - NoCoastPlotting(string)
     - True
     - Plot coastlines on map (ON/OFF)
   * - map_coastline_colour
     - Colour(string)
     - black
     - Colour of coastlines
   * - map_coastline_general_style
     - string
     - 
     - Use a predefined style depending on the general theme
   * - map_coastline_land_shade
     - bool(string)
     - False
     - Sets if land areas are shaded
   * - map_coastline_land_shade_colour
     - Colour(string)
     - green
     - Colour of Shading of land areas
   * - map_coastline_resolution
     - string
     - automatic
     - Select one of the pre-defined resolutions: automatic, low, medium, and high.  When set to AUTOMATIC, a resolution appropriate to the scale of the map is chosen in order to balance quality with speed.
   * - map_coastline_sea_shade
     - bool(string)
     - False
     - Shade the sea areas
   * - map_coastline_sea_shade_colour
     - Colour(string)
     - blue
     - Colour of Shading of sea areas
   * - map_coastline_style
     - LineStyle(string)
     - solid
     - Line style of coastlines
   * - map_coastline_thickness
     - int
     - 1.0
     - Line thickness of coastlines
   * - map_disputed_boundaries
     - bool(string)
     - True
     - Display the disputed boundaries (on/off)
   * - map_disputed_boundaries_colour
     - Colour(string)
     - automatic
     - Colour of disputed boundaries
   * - map_disputed_boundaries_style
     - LineStyle(string)
     - dash
     - Line style of disputed boundaries
   * - map_disputed_boundaries_thickness
     - int
     - 1.0
     - Line thickness of disputed boundaries
   * - map_efas
     - string
     - False
     - Display rivers (on/off)
   * - map_efas_colour
     - Colour(string)
     - blue
     - Colour of the EFAS
   * - map_efas_domain
     - string
     - current
     - Display EFAS Domain (on/off)
   * - map_efas_style
     - LineStyle(string)
     - solid
     - Line style for EFAS
   * - map_efas_thickness
     - int
     - 1.0
     - Line thickness of EFAS
   * - map_grid
     - NoGridPlotting(string)
     - True
     - Plot grid lines on map (On/OFF)
   * - map_grid_colour
     - Colour(string)
     - BLACK
     - Colour of map grid lines
   * - map_grid_frame
     - bool(string)
     - False
     - Add a frame around the projection
   * - map_grid_frame_colour
     - Colour(string)
     - black
     - Colour of map grid lines
   * - map_grid_frame_line_style
     - LineStyle(string)
     - solid
     - Line style of map grid lines
   * - map_grid_frame_thickness
     - int
     - 1.0
     - Thickness of map grid lines
   * - map_grid_latitude_increment
     - float
     - 10.0
     - Interval between latitude grid lines
   * - map_grid_latitude_reference
     - float
     - 0.0
     - Reference Latitude from which all latitude lines are drawn
   * - map_grid_line_style
     - LineStyle(string)
     - solid
     - Line style of map grid lines
   * - map_grid_longitude_increment
     - float
     - 20.0
     - Interval between longitude grid lines
   * - map_grid_longitude_reference
     - float
     - 0.0
     - Reference Longitude from which all longitude lines are drawn
   * - map_grid_thickness
     - int
     - 1.0
     - Thickness of map grid lines
   * - map_label
     - NoLabelPlotting(string)
     - True
     - Plot label on map grid lines (On/OFF)
   * - map_label_blanking
     - bool(string)
     - True
     - Blanking of the grid labels
   * - map_label_bottom
     - bool(string)
     - True
     - Enable the labels on the bottom of the map
   * - map_label_colour
     - Colour(string)
     - black
     - Colour of map labels
   * - map_label_font
     - string
     - sansserif
     - Font of grid labels
   * - map_label_font_style
     - string
     - normal
     - Font of grid labels
   * - map_label_height
     - float
     - 0.25
     - Height og grid labels
   * - map_label_latitude_frequency
     - int
     - 1.0
     - Evry Nth latitue grid is labelled
   * - map_label_left
     - bool(string)
     - True
     - Enable the labels on the left of the map
   * - map_label_longitude_frequency
     - int
     - 1.0
     - Evry Nth longitude grid is labelled
   * - map_label_right
     - bool(string)
     - True
     - Enable the labels on the right of the map
   * - map_label_top
     - bool(string)
     - True
     - Enable the labels on the top of the map
   * - map_preview
     - bool(string)
     - False
     - {'for_docs': False, '#text': 'Add a preview : only for metview'}
   * - map_rivers
     - string
     - False
     - Display rivers (on/off)
   * - map_rivers_colour
     - Colour(string)
     - blue
     - Colour of the rivers
   * - map_rivers_style
     - LineStyle(string)
     - solid
     - Line style for rivers
   * - map_rivers_thickness
     - int
     - 1.0
     - Line thickness of rivers
   * - map_user_layer
     - string
     - False
     - Display user shape file layer
   * - map_user_layer_colour
     - Colour(string)
     - blue
     - Colour of the User Layer
   * - map_user_layer_name
     - string
     - 
     - Path + name of the shape file to use
   * - map_user_layer_projection
     - string
     - 
     - Projection used in the shape file
   * - map_user_layer_style
     - LineStyle(string)
     - solid
     - Line style for User Layer
   * - map_user_layer_thickness
     - int
     - 1.0
     - Line thickness of User Layer

pcont
-----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - contour
     - IsoPlot(string)
     - True
     - Turn contouring on or off
   * - contour_akima_x_resolution
     - float
     - 1.5
     - X Resolution
   * - contour_akima_x_resolution
     - float
     - 1.5
     - X resolution of Akima interpolation
   * - contour_akima_x_resolution
     - float
     - 1.5
     - X Resolution of the Akima output matrix
   * - contour_akima_y_resolution
     - float
     - 1.5
     - Y Resolution
   * - contour_akima_y_resolution
     - float
     - 1.5
     - Y resolution of Akima interpolation
   * - contour_akima_y_resolution
     - float
     - 1.5
     - Y Resolution of the Akima output matrix
   * - contour_automatic_library_path
     - string
     - 
     - Users can give their own directory to setup the automatic library of contours
   * - contour_automatic_library_path
     - string
     - 
     - Users can give their own directory to setup the automatic library of contours
   * - contour_automatic_setting
     - string
     - False
     - Turn the automatic setting of contouring attributes
   * - contour_gradients_colour_list
     - stringarray
     - []
     - Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
   * - contour_gradients_colour_list
     - stringarray
     - []
     - Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
   * - contour_gradients_step_list
     - intarray
     - []
     - Nimber of steps to compute for each interval
   * - contour_gradients_step_list
     - intarray
     - []
     - Number of steps to compute for each interval
   * - contour_gradients_technique
     - string
     - rgb
     - Technique to apply to compute the gradients rgb/hcl/hsl
   * - contour_gradients_technique_direction
     - string
     - clockwise
     - Technique to apply to compute the gradients clockwise/anticlockwise
   * - contour_gradients_technique_list
     - stringarray
     - []
     - Technique to apply to compute the gradients linear-clockwise/linear-anticlockwise
   * - contour_gradients_value_list
     - floatarray
     - []
     - List of stops.
   * - contour_gradients_waypoint_method
     - string
     - both
     - waypoints at the left, right, middle of the interval.
   * - contour_grid_shading_position
     - string
     - middle
     - Middle : the point is in the midlle of the cell, bottom_left : the point is in the bottom left corner
   * - contour_grid_value_colour
     - Colour(string)
     - blue
     - Colour of grid point values (Full choice of colours)
   * - contour_grid_value_format
     - string
     - (automatic)
     - Format of grid point values (MAGICS Format/(AUTOMATIC))
   * - contour_grid_value_height
     - float
     - 0.25
     - Height of grid point values
   * - contour_grid_value_justification
     - Justification(string)
     - centre
     - (LEFT/CENTRE/RIGHT)
   * - contour_grid_value_lat_frequency
     - int
     - 1.0
     - The grid point values in every Nth latitude row are plotted
   * - contour_grid_value_lon_frequency
     - int
     - 1.0
     - The grid point values in every Nth longitude column are plotted
   * - contour_grid_value_marker_colour
     - Colour(string)
     - red
     - Colour of grid point markers (Full choice of colours)
   * - contour_grid_value_marker_colour
     - Colour(string)
     - red
     - Colour of grid point markers (Full choice of colours)
   * - contour_grid_value_marker_height
     - float
     - 0.25
     - Height of grid point markers
   * - contour_grid_value_marker_height
     - float
     - 0.25
     - Height of grid point markers
   * - contour_grid_value_marker_index
     - int
     - 3.0
     - Table number of marker index. See Appendix for Plotting Attributes
   * - contour_grid_value_marker_index
     - int
     - 3.0
     - Table number of marker index. See Appendix for Plotting Attributes
   * - contour_grid_value_marker_qual
     - string
     - low
     - (LOW/MEDIUM/HIGH)
   * - contour_grid_value_marker_qual
     - string
     - low
     - (LOW/MEDIUM/HIGH)
   * - contour_grid_value_max
     - float
     - 1e+21
     - The maximum value for which grid point values are to be plotted
   * - contour_grid_value_min
     - float
     - -1e+21
     - The minimum value for which grid point values are to be plotted
   * - contour_grid_value_plot
     - ValuePlotBase(string)
     - False
     - Plot Grid point values
   * - contour_grid_value_plot_type
     - ValuePlotMethod(string)
     - value
     - (VALUE/MARKER/BOTH)
   * - contour_grid_value_position
     - string
     - top
     - Position of the value
   * - contour_grid_value_quality
     - string
     - low
     - (LOW/MEDIUM/HIGH)
   * - contour_grid_value_type
     - string
     - normal
     - For Gaussian fields, plot normal (regular) values or reduced grid values. (NORMAL/REDUCED/akima). If akima, the akima grid values will be plotted
   * - contour_grid_value_vertical_align
     - string
     - base
     - (NORMAL/TOP/CAP/HALF/BASE/BOTTOM)
   * - contour_hi_colour
     - Colour(string)
     - blue
     - Colour of local maxima text or number
   * - contour_hi_max_value
     - float
     - 1e+21
     - Local HI above specified value are not drawn
   * - contour_hi_min_value
     - float
     - -1e+21
     - Local HI below specified value are not drawn
   * - contour_hi_text
     - string
     - H
     - Text to represent local maxima
   * - contour_highlight
     - NoIsoHighlight(string)
     - True
     - Plot contour highlights (ON/OFF)
   * - contour_highlight_colour
     - Colour(string)
     - blue
     - Colour of highlight line
   * - contour_highlight_frequency
     - int
     - 4.0
     - Frequency of highlight line
   * - contour_highlight_style
     - LineStyle(string)
     - solid
     - Style of highlighting (SOLID/ DASH/ DOT/ CHAIN_DASH/ CHAIN_DOT)
   * - contour_highlight_thickness
     - int
     - 3.0
     - Thickness of highlight line
   * - contour_hilo
     - HiLoBase(string)
     - False
     - Plot local maxima/minima
   * - contour_hilo_blanking
     - bool(string)
     - False
     - Blank around highs and lows (ON/OFF)
   * - contour_hilo_format
     - string
     - (automatic)
     - Format of HILO numbers (MAGICS Format/(AUTOMATIC))
   * - contour_hilo_height
     - float
     - 0.4
     - Height of local maxima/minima text or numbers
   * - contour_hilo_marker
     - HiLoMarkerBase(string)
     - False
     - Plot hilo marker (ON/OFF)
   * - contour_hilo_marker_colour
     - Colour(string)
     - red
     - Colour of grid point markers(Full choice of colours)
   * - contour_hilo_marker_height
     - float
     - 0.1
     - Height of HILO marker symbol
   * - contour_hilo_marker_index
     - int
     - 3.0
     - Table number of marker symbol. See chapter on Plotting Attributes
   * - contour_hilo_max_value
     - float
     - 1e+21
     - Local HiLo above specified value are not drawn
   * - contour_hilo_min_value
     - float
     - -1e+21
     - Local HiLo below specified value are not drawn
   * - contour_hilo_quality
     - string
     - low
     - (LOW/MEDIUM/HIGH)
   * - contour_hilo_reduction_radius
     - float
     - 0.0
     - Search radius (in grid points) for reducing the number of minima
   * - contour_hilo_suppress_radius
     - float
     - 15.0
     - Radius of HiLo search in grid points (default value is for global cylindrical map)
   * - contour_hilo_type
     - HiLoTechnique(string)
     - text
     - Type of high/low (TEXT/NUMBER/BOTH)
   * - contour_hilo_window_size
     - int
     - 3.0
     - Size of the window used to calculate the Hi/Lo
   * - contour_internal_reduction_factor
     - float
     - 4.0
     - Internal factor for contouring
   * - contour_internal_technique
     - string
     - interpolate
     - Internal technique for contouring : interpolate/nearest
   * - contour_interpolation_ceiling
     - float
     - INT_MAX
     - any value above this ceiling will be forced to the ceiling value.  avoid the bubbles artificially created by the interpolation method
   * - contour_interpolation_floor
     - float
     - -INT_MAX
     - Any value below this floor will be forced to the floor value.  avoid the bubbles artificially created by the interpolation method
   * - contour_interval
     - float
     - 8.0
     - Interval in data units between two contour lines
   * - contour_label
     - NoIsoLabel(string)
     - True
     - Plot labels on contour lines
   * - contour_label_blanking
     - bool(string)
     - True
     - Label Blanking
   * - contour_label_colour
     - string
     - contour_line_colour
     - Colour of contour labels
   * - contour_label_font
     - string
     - sansserif
     - Name of the font
   * - contour_label_font_style
     - string
     - normal
     - Style of the font bold/italic
   * - contour_label_format
     - string
     - (automatic)
     - Format of contour labels (MAGICS Format/(AUTOMATIC))
   * - contour_label_frequency
     - int
     - 2.0
     - Every Nth contour line is labelled
   * - contour_label_height
     - float
     - 0.3
     - Height of contour labels
   * - contour_label_quality
     - string
     - low
     - (LOW/MEDIUM/HIGH)
   * - contour_label_text
     - string
     - 
     - Text for labels
   * - contour_label_type
     - string
     - number
     - Type of label (TEXT/NUMBER/BOTH)
   * - contour_legend_only
     - bool(string)
     - False
     - Inform the contour object do generate only the legend and not the plot!
   * - contour_legend_text
     - string
     - 
     - Text to be used in legend
   * - contour_level_count
     - int
     - 10.0
     - Count or number of levels to be plotted. Magics will try to find "nice levels",      this means that the number of levels could be slightly different from the asked number of levels
   * - contour_level_list
     - floatarray
     - []
     - List of contour levels to be plotted
   * - contour_level_selection_type
     - LevelSelection(string)
     - count
     - count: calculate a reasonable contour interval taking into account the min/max and the requested number of isolines.     interval: regularly spaced intervals using the reference_level as base.     level_list: uses the given list of levels.
   * - contour_level_tolerance
     - int
     - 2.0
     - Tolerance: Do not use nice levels if the number of levels is really to different [count +/- tolerance]
   * - contour_line_colour
     - Colour(string)
     - blue
     - Colour of contour line
   * - contour_line_colour_rainbow
     - bool(string)
     - False
     - if On, rainbow colouring method will be used.
   * - contour_line_colour_rainbow_colour_list
     - stringarray
     - []
     - List of colours to be used in rainbow isolines
   * - contour_line_colour_rainbow_colour_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of colours is smaller that the list of contour: lastone/cycle
   * - contour_line_colour_rainbow_direction
     - string
     - anti_clockwise
     - Direction of colour sequencing for colouring
   * - contour_line_colour_rainbow_max_level_colour
     - Colour(string)
     - blue
     - Colour to be used for the max level
   * - contour_line_colour_rainbow_method
     - ColourTechnique(string)
     - calculate
     - Method of generating the colours for isoline
   * - contour_line_colour_rainbow_min_level_colour
     - Colour(string)
     - red
     - Colour to be used for the mainlevel
   * - contour_line_style
     - LineStyle(string)
     - solid
     - Style of contour line
   * - contour_line_style_rainbow_list
     - stringarray
     - []
     - List of line style to used when rainbow method is on
   * - contour_line_style_rainbow_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of line styles is smaller that the list of contour: lastone/cycle
   * - contour_line_thickness
     - int
     - 1.0
     - Thickness of contour line
   * - contour_line_thickness_rainbow_list
     - intarray
     - []
     - List of thickness to used when rainbow method is on
   * - contour_line_thickness_rainbow_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of thickness is smaller that the list of contour: lastone/cycle
   * - contour_lo_colour
     - Colour(string)
     - blue
     - Colour of local minima text or number
   * - contour_lo_max_value
     - float
     - 1e+21
     - Local Lo above specified value are not drawn
   * - contour_lo_min_value
     - float
     - -1e+21
     - Local Lo below specified value are not drawn
   * - contour_lo_text
     - string
     - L
     - Text to represent local minima
   * - contour_max_level
     - float
     - 1e+21
     - Highest level for contours to be drawn
   * - contour_metadata_only
     - bool(string)
     - False
     - Only get the metadata
   * - contour_method
     - ContourMethod(string)
     - automatic
     - Contouring method
   * - contour_min_level
     - float
     - -1e+21
     - Lowest level for contours to be drawn
   * - contour_predefined_setting
     - string
     - 
     - Use of a predeined setting
   * - contour_reference_level
     - float
     - 0.0
     - Contour level from which contour interval is calculated
   * - contour_reference_level
     - float
     - 0.0
     - Contour level from which contour interval is calculated
   * - contour_reference_level
     - float
     - 0.0
     - Contour level reference
   * - contour_shade
     - NoIsoShading(string)
     - False
     - Turn shading on
   * - contour_shade_cell_method
     - string
     - nearest
     - NMethod of determining the colour of a cell (INTERPOLATE/ NEAREST)
   * - contour_shade_cell_method
     - string
     - nearest
     - NMethod of determining the colour of a cell (INTERPOLATE/ NEAREST)
   * - contour_shade_cell_resolution
     - float
     - 10.0
     - Number of cells per cm for CELL shading
   * - contour_shade_cell_resolution
     - float
     - 10.0
     - Number of cells per cm for CELL shading
   * - contour_shade_cell_resolution_method
     - string
     - classic
     - if adaptive, magics will switch to grid_shading when the data resolution is greater that the requested resolution
   * - contour_shade_colour_direction
     - string
     - anti_clockwise
     - Direction of colour sequencing for shading (CLOCKWISE/ ANTI_CLOCKWISE)
   * - contour_shade_colour_list
     - stringarray
     - []
     - List of colours to be used in contour shading.
   * - contour_shade_colour_method
     - ColourTechnique(string)
     - calculate
     - Method of generating the colours of the bands in contour shading (list/calculate/advanced)
   * - contour_shade_colour_table
     - stringarray
     - []
     - Colour table to be used with MARKER shading technique
   * - contour_shade_dot_size
     - float
     - 0.02
     - Size of dot in shading pattern
   * - contour_shade_hatch_density
     - float
     - 18.0
     - Number of hatch lines per cm.
   * - contour_shade_hatch_index
     - int
     - 0.0
     - The hatching pattern(s) to use. 0 Provides an automatic sequence of patterns, other values set a constant pattern across all contour bands.
   * - contour_shade_hatch_thickness
     - int
     - 1.0
     - Thickness of hatch lines
   * - contour_shade_height_table
     - floatarray
     - []
     - Height table to be used with MARKER shading technique
   * - contour_shade_marker_name_table
     - stringarray
     - []
     - Marker name table to be used with MARKER shading technique
   * - contour_shade_marker_table
     - intarray
     - []
     - Marker table to be used with MARKER shading technique
   * - contour_shade_marker_table_type
     - string
     - index
     - index: using contour_shade_marker_table and definiing the markers by index, name: using contour_shade_marker_name_table and defining the symbols by their names
   * - contour_shade_max_level
     - float
     - 1e+21
     - Maximum level for which shading is required
   * - contour_shade_max_level
     - float
     - 1e+21
     - Highest level for contours to be shaded
   * - contour_shade_max_level_colour
     - Colour(string)
     - blue
     - Highest shading band colour
   * - contour_shade_max_level_density
     - float
     - 50.0
     - Dots/square centimetre in highest shading band
   * - contour_shade_method
     - PolyShadingMethod(string)
     - dot
     - Method used for shading (DOT/ AREA_FILL/ HATCH)
   * - contour_shade_min_level
     - float
     - -1e+21
     - Minimum level for which shading is required
   * - contour_shade_min_level
     - float
     - -1e+21
     - Lowest level for contours to be shaded
   * - contour_shade_min_level_colour
     - Colour(string)
     - red
     - Lowest shading band colour
   * - contour_shade_min_level_density
     - float
     - 1.0
     - Dots/square centimetre in lowest shading band
   * - contour_shade_palette_name
     - string
     - 
     - Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
   * - contour_shade_palette_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of colours is smaller that the list of levels: lastone/cycle
   * - contour_shade_technique
     - ShadingTechnique(string)
     - polygon_shading
     - Technique used for shading (POLYGON_SHADING/ CELL_SHADING/ MARKER)
   * - contour_special_legend
     - string
     - 
     - Used in wrep to produce special legend such as spaghetti!
   * - contour_style_name
     - string
     - 
     - Use of a predeined setting
   * - contour_threads
     - int
     - 4.0
     - NUmber of threads used to optimise the contouring (possible 1, 4 or 9)
   * - image_colour_table
     - stringarray
     - []
     - List of colours to be used in image plotting.
   * - legend
     - bool(string)
     - False
     - Turn legend on or off

pefigram
--------

The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - efi_clim_date
     - string
     - 
     - date to select for the clim In date format (YYYYMMDDHHHH)
   * - efi_clim_parameter
     - string
     - 
     - date to select for the clim In date format (YYYYMMDDHHHH)
   * - efi_clim_root_database
     - string
     - 
     - climatalogy database
   * - efi_clim_step
     - int
     - 36.0
     - date to select for the clim In date format (YYYYMMDDHHHH)
   * - efi_dates
     - stringarray
     - []
     - date to select In date format (YYYYMMDDHHHH)
   * - efi_latitude
     - float
     - 0.0
     - epsgram latitude column name
   * - efi_legend
     - bool(string)
     - True
     - legend
   * - efi_legend_box_type
     - string
     - both
     - both/negative/positive
   * - efi_legend_colour_list
     - stringarray
     - []
     - legend box colour list
   * - efi_legend_normal_colour
     - Colour(string)
     - black
     - legend colour box
   * - efi_legend_normal_thickness
     - int
     - 4.0
     - legend colour box
   * - efi_legend_root_database
     - string
     - 
     - legend
   * - efi_long_title
     - bool(string)
     - False
     - efigram long title ( Point Position ... General title!)
   * - efi_longitude
     - float
     - 0.0
     - epsgram longitude column name
   * - efi_parameter
     - string
     - 
     - epsgram latitude column name
   * - efi_root_database
     - string
     - 
     - database to access
   * - efi_steps
     - intarray
     - []
     - steps to extract ( legend will use step+12)
   * - efi_title
     - bool(string)
     - False
     - epsgram title ( parameter name)

pemagram
--------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - subpage_x_automatic
     - bool(string)
     - False
     - 
   * - subpage_y_automatic
     - bool(string)
     - False
     - 
   * - thermo_annotation_width
     - float
     - 25.0
     - Percentage of the width used to display the annotation on the right side .
   * - x_max
     - float
     - 100.0
     - 
   * - x_min
     - float
     - 0.0
     - 
   * - y_max
     - float
     - 100.0
     - 
   * - y_min
     - float
     - 0.0
     - 

peps
----

The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - cape_box_border_colour
     - Colour(string)
     - black
     - 
   * - cape_box_border_thickness
     - float
     - 2.0
     - 
   * - cape_box_colour
     - Colour(string)
     - black
     - 
   * - cape_box_line_style
     - LineStyle(string)
     - solid
     - 
   * - cape_box_thickness
     - float
     - 1.0
     - 
   * - cape_box_width
     - float
     - 1.0
     - 
   * - cape_control_colour
     - Colour(string)
     - red
     - 
   * - cape_hres_colour
     - Colour(string)
     - blue
     - 
   * - cape_marker_colour
     - Colour(string)
     - black
     - 
   * - cape_marker_height
     - float
     - 0.5
     - 
   * - cape_marker_index
     - int
     - 15.0
     - 
   * - cape_text_font_colour
     - Colour(string)
     - black
     - 
   * - cape_text_font_size
     - float
     - 0.5
     - 
   * - eps_box_border_colour
     - Colour(string)
     - black
     - 
   * - eps_box_border_thickness
     - int
     - 3.0
     - 
   * - eps_box_colour
     - Colour(string)
     - cyan
     - 
   * - eps_box_median_colour
     - Colour(string)
     - black
     - 
   * - eps_box_median_thickness
     - int
     - 3.0
     - 
   * - eps_box_quantiles_colour
     - stringarray
     - []
     - if set, the list of colours will be used as follow colour1 between 10-25, colour2 between 25-75, colour3 between 75-90
   * - eps_box_shift
     - int
     - 0.0
     - 
   * - eps_box_width
     - float
     - -1.0
     - 
   * - eps_control
     - bool(string)
     - True
     - plot the deterministic Forecast
   * - eps_control_legend_text
     - string
     - ENS Control
     - Text to be used in the legend
   * - eps_control_line_colour
     - Colour(string)
     - red
     - Colour of deterministic Forecast
   * - eps_control_line_style
     - LineStyle(string)
     - dash
     - Control of deterministic Forecast
   * - eps_control_line_thickness
     - int
     - 2.0
     - line style of deterministic Forecast
   * - eps_database
     - string
     - /vol/epsgram/data/spotbase/epsdb
     - Epsgram Database Path
   * - eps_date
     - string
     - -1.0
     - epsgram longitude column name
   * - eps_deterministic
     - bool(string)
     - True
     - plot the deterministic Forecast
   * - eps_deterministic_legend_text
     - string
     - High Resolution
     - Text to be used in the legend
   * - eps_deterministic_line_colour
     - Colour(string)
     - blue
     - Colour of deterministic Forecast
   * - eps_deterministic_line_style
     - LineStyle(string)
     - solid
     - line style of deterministic Forecast
   * - eps_deterministic_line_thickness
     - int
     - 2.0
     - line style of deterministic Forecast
   * - eps_font
     - string
     - sansserif
     - 
   * - eps_font_colour
     - Colour(string)
     - blue
     - 
   * - eps_font_size
     - float
     - 0.25
     - 
   * - eps_font_style
     - string
     - 
     - 
   * - eps_grey_legend
     - bool(string)
     - True
     - 
   * - eps_latitude
     - float
     - 0.0
     - epsgram latitude column name
   * - eps_left_box_colour
     - Colour(string)
     - blue
     - 
   * - eps_legend_control_text
     - string
     - 
     - 
   * - eps_legend_font_size
     - float
     - 0.3
     - 
   * - eps_legend_forecast_text
     - string
     - 
     - 
   * - eps_legend_resolution
     - string
     - truncature
     - 
   * - eps_long_title
     - bool(string)
     - False
     - epsgram long title
   * - eps_long_title_height
     - bool(string)
     - True
     - epsgram long title: add the station height
   * - eps_long_title_point
     - bool(string)
     - True
     - epsgram long title: add the grid point position
   * - eps_long_title_station
     - bool(string)
     - True
     - epsgram long title : add the station name
   * - eps_longitude
     - float
     - 0.0
     - epsgram longitude column name
   * - eps_maximum
     - float
     - INT_MAX
     - 
   * - eps_maximum_font
     - string
     - sansserif
     - 
   * - eps_maximum_font_colour
     - Colour(string)
     - red
     - 
   * - eps_maximum_font_size
     - float
     - 0.25
     - 
   * - eps_maximum_font_style
     - string
     - normal
     - 
   * - eps_parameter
     - string
     - 
     - Epsgram Parameter
   * - eps_parameter_hour_shift
     - float
     - 0.0
     - valid date is shifted ( temporary..)
   * - eps_parameter_offset_factor
     - float
     - 0.0
     - Scaling factor to apply to the values
   * - eps_parameter_scaling_factor
     - float
     - 1.0
     - Scaling factor to apply to the values
   * - eps_parameter_title
     - string
     - 
     - epsgram parameter title : used only in case of an unknow parameter
   * - eps_right_box_colour
     - Colour(string)
     - red
     - 
   * - eps_rose_cloud_border_colour
     - Colour(string)
     - none
     - Rose wind border colour
   * - eps_rose_cloud_colour
     - Colour(string)
     - black
     - Rose wind darker colour
   * - eps_rose_wave_colour
     - stringarray
     - []
     - Rose wind darker colour
   * - eps_rose_wind_border_colour
     - Colour(string)
     - grey
     - Rose wind border colour
   * - eps_rose_wind_colour
     - Colour(string)
     - grey
     - Rose wind darker colour
   * - eps_rose_wind_convention
     - string
     - meteorological
     - Define the convention to use to plot the wind direction    [ meteorological : Direction the parameter is coming from,     oceanographic : Direction the parameter is goint to]
   * - eps_station_height
     - float
     - INT_MAX
     - epsgram long title
   * - eps_station_name
     - string
     - 
     - epsgram long title
   * - eps_temperature_correction
     - bool(string)
     - yes
     - Temperature correction
   * - eps_time
     - string
     - 0.0
     - epsgram date
   * - eps_title
     - stringarray
     - []
     - text block to be plotted
   * - eps_title_text
     - string
     - EPS Meteogram
     - Epsgram Parameter
   * - eps_type
     - string
     - eps10
     - Eps Metgram type : eps10 or eps15
   * - eps_whisker
     - bool(string)
     - True
     - 
   * - eps_y_axis_percentile
     - float
     - 1.0
     - Temperature correction
   * - eps_y_axis_threshold
     - float
     - 50.0
     - Temperature correction
   * - legend
     - bool(string)
     - True
     - 
   * - legend
     - bool(string)
     - True
     - turn the legend (on/off)

pgeo
----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - geo_input_file_name
     - string
     - 
     - The name of the input file containing the GeoPoints code field(s)
   * - geo_missing_value
     - float
     - 3e+38
     - missing value for geopoints

pgeojson
--------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - geojson_binning_grid_resolution
     - float
     - 1.0
     - String containing the GeoJson data
   * - geojson_input
     - string
     - {}
     - String containing the GeoJson data
   * - geojson_input_filename
     - string
     - 
     - Path to the file containing the GeoJson data
   * - geojson_input_type
     - string
     - file
     - data are in a file ( file ) or passed as a string (string)

pgrib
-----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - grib_automatic_derived_scaling
     - bool(string)
     - False
     - Scaling of the decoded derived field. A field is considered derived if the GRIB_API key generatingProcessIdentifier is 254.
   * - grib_automatic_derived_scaling
     - bool(string)
     - False
     - Scaling of the decoded derived field (ON/OFF). A field is considered derived if the GRIB_API key generatingProcessIdentifier is 254.
   * - grib_automatic_scaling
     - bool(string)
     - True
     - Scaling of the decoded field
   * - grib_automatic_scaling
     - bool(string)
     - True
     - Scaling of the decoded field (ON/OFF)
   * - grib_automatic_scaling
     - bool(string)
     - True
     - Scaling of the decoded field
   * - grib_dimension
     - intarray
     - []
     - Metview:dimension of the input : 1 for field, 2 for wind
   * - grib_field_position
     - int
     - 1.0
     - The position in the input file of a field other than a wind component
   * - grib_file_address_mode
     - GribAddressMode(string)
     - record
     - Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
   * - grib_file_address_mode
     - GribAddressMode(string)
     - record
     - Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
   * - grib_file_address_mode
     - GribAddressMode(string)
     - record
     - Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
   * - grib_id
     - string
     - 
     - Id used to identify a grib file in the title production
   * - grib_input_file_name
     - string
     - 
     - The name of the input file containing the GRIB code field(s)
   * - grib_input_file_name
     - string
     - 
     - The name of the input file containing the GRIB code field(s)
   * - grib_interpolation_method
     - string
     - interpolate
     - Used for reduced gaussian grid: use an linear interpolation to convert from reduced to regular
   * - grib_interpolation_method
     - string
     - interpolate
     - Used for reduced gaussian grid: use an linear interpolation to convert from reduced to regular
   * - grib_interpolation_method_missing_fill_count
     - int
     - 1.0
     - Number of missing values to fill with the nearest valid value
   * - grib_interpolation_method_missing_fill_count
     - int
     - 1.0
     - Number of missing values to fill with the nearest valid value
   * - grib_interpolation_regular_resolution
     - float
     - 0.1
     - Space View : Resolution of the regular Matrix
   * - grib_interpolation_regular_resolution
     - float
     - 0.1
     - Space View : Resolution of the regular Matrix
   * - grib_loop
     - bool(string)
     - False
     - we can loop
   * - grib_loop
     - bool(string)
     - False
     - 
   * - grib_loop_path
     - string
     - 
     - Path of the grib to animate
   * - grib_loop_step
     - GribLoopStep(string)
     - loopondate
     - Method to create the steps names for each plot of the animation
   * - grib_loop_step_span
     - float
     - 3.0
     - Time interval
   * - grib_missing_value_indicator
     - float
     - -1.5e+21
     - When MAGICS is decoding GRIB code, this is the value to be assigned to field values where data is missing, as indicated by the bit map in the GRIB file.
   * - grib_position
     - longintarray
     - longintarray()
     - Metview:position of the fields to plot in the fieldset
   * - grib_position_1
     - longintarray
     - longintarray()
     - Metview:position of the fields for x component in the fieldset
   * - grib_position_2
     - longintarray
     - longintarray()
     - Metview:position of the fields for y component in the fieldset
   * - grib_position_colour
     - longintarray
     - longintarray()
     - Metview:position of the fields for colour component in the fieldset
   * - grib_scaling_factor
     - float
     - 1.0
     - Apply a scaling factor to the field.
   * - grib_scaling_factor
     - float
     - 1.0
     - Apply a scaling factor to the field.
   * - grib_scaling_factor
     - float
     - 1.0
     - Apply a scaling factor to the field.
   * - grib_scaling_offset
     - float
     - 0.0
     - Apply a scaling offset to the field.
   * - grib_scaling_offset
     - float
     - 0.0
     - Apply a scaling offset to the field.
   * - grib_scaling_offset
     - float
     - 0.0
     - Apply a scaling offset to the field.
   * - grib_text_experiment
     - bool(string)
     - False
     - Include the name or number of the experiment, used to generate the GRIB code field, in the automatic text (ON/OFF)
   * - grib_text_units
     - bool(string)
     - False
     - Include the units of the input field in the automatic text
   * - grib_tile_projection
     - string
     - cylindrical
     - 
   * - grib_tile_x
     - int
     - 0.0
     - 
   * - grib_tile_y
     - int
     - 0.0
     - 
   * - grib_tile_z
     - int
     - 1.0
     - 
   * - grib_wind_mode
     - WindMode(string)
     - uv
     - The incoming wind field may contain data other than wind components, e.g. wave height and direction.          grib_wind_mode should be set to indicate how to interpret the incoming wind field,          as u/v components, or speed/direction (uv/vd).
   * - grib_wind_mode
     - WindMode(string)
     - uv
     - The incoming wind field may contain data other than wind components, e.g. wave height and direction.          grib_wind_mode should be set to indicate how to interpret the incoming wind field,          as u/v components, or speed/direction (uv/vd).
   * - grib_wind_position_1
     - int
     - 1.0
     - The position in the input file of a wind component field
   * - grib_wind_position_2
     - int
     - 2.0
     - The position in the input file of a wind component field
   * - grib_wind_position_colour
     - int
     - 3.0
     - The position in the input file of a wind component field used to colour the flag

pimage
------

Here comes the documentation of the ImagePlotting object

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - image_colour_direction
     - string
     - anti_clockwise
     - Direction of colour sequencing for image (CLOCKWISE / ANTI_CLOCKWISE)
   * - image_colour_table_creation_mode
     - LookupTableMode(string)
     - equidistant
     - Method for computing the output image according to the Colour table.
   * - image_colour_table_type
     - ColourTableDefinition(string)
     - computed
     - Method for setting Colour table for imaging.
   * - image_level_count
     - int
     - 127.0
     - Number of levels
   * - image_max_level_colour
     - Colour(string)
     - blue
     - Highest image band colour
   * - image_min_level_colour
     - Colour(string)
     - red
     - Lowest image band colour
   * - image_pixel_selection_frequency
     - int
     - 10.0
     - Number of pixels/centimetre to be plotted

pimport
-------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - import_file_name
     - string
     - 
     - File to import
   * - import_file_name
     - string
     - 
     - File to import
   * - import_format
     - string
     - png
     - Specify the format of the imported file
   * - import_height
     - float
     - -1.0
     - Height of the imported image (-1 means use the dimension of the image)
   * - import_overlay
     - bool(string)
     - True
     - if on, the import object will always be displayed last
   * - import_valid_time
     - string
     - 
     - Valid Time
   * - import_width
     - float
     - -1.0
     - Width of the imported image (-1 means use the dimension of the image)
   * - import_x_position
     - float
     - 0.0
     - X position of the imported image
   * - import_y_position
     - float
     - 0.0
     - Y position of the imported image
   * - layers
     - string
     - 
     - Metview info :Short name to be put in the layers!
   * - service
     - string
     - 
     - Metview info : which service created this image
   * - url
     - string
     - 
     - Metview info : which url created this image : add it in the titles

pline
-----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - legend
     - bool(string)
     - False
     - Turn the legend on
   * - polyline_colour_level_list
     - floatarray
     - []
     - level list to use for setting the colours
   * - polyline_colour_list
     - stringarray
     - []
     - list of colours to use
   * - polyline_colour_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of colours is smaller that the list of levels: lastone/cycle
   * - polyline_colour_variable_name
     - string
     - 
     - Data Variable used for setting the colour of the segments
   * - polyline_effect_method
     - string
     - classic
     - Method applied to draw the line
   * - polyline_input_break_indicator
     - float
     - -999.0
     - Value used as either a latitude or longitude to denote a separation between polylines
   * - polyline_input_latitudes
     - floatarray
     - []
     - Array containing the latitudes of the polylines. Each polyline is separated by the break value
   * - polyline_input_longitudes
     - floatarray
     - []
     - Array containing the longitudes of the polylines. Each polyline is separated by the break value
   * - polyline_input_positions_filename
     - string
     - 
     - Path to a file containing the coordinates for all polylines' points.
   * - polyline_input_values
     - floatarray
     - []
     - Array containing the values for each polyline
   * - polyline_input_values_filename
     - string
     - 
     - Path to a file containing the values for each polyline.
   * - polyline_interval
     - float
     - 8.0
     - Interval in data units between different bands of shading
   * - polyline_legend_only
     - bool(string)
     - False
     - {'for_docs': False, '#text': 'Wrep only : to build only the legend...'}
   * - polyline_level_count
     - int
     - 10.0
     - Count or number of levels to be plotted. Magics will try to find "nice levels",      this means that the number of levels could be slightly different from the requested number of levels
   * - polyline_level_list
     - floatarray
     - []
     - List of shading band levels to be plotted
   * - polyline_level_tolerance
     - int
     - 2.0
     - Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
   * - polyline_line_colour
     - Colour(string)
     - blue
     - Colour of the polylines
   * - polyline_line_style
     - LineStyle(string)
     - solid
     - Style of the polylines (SOLID/ DASH/ DOT/ CHAIN_DASH/ CHAIN_DOT)
   * - polyline_line_style_level_list
     - floatarray
     - []
     - level list to use for setting the colours
   * - polyline_line_style_list
     - stringarray
     - []
     - list of line styles to use
   * - polyline_line_style_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of line styles is smaller that the list of levels: lastone/cycle
   * - polyline_line_style_variable_name
     - string
     - 
     - Data Variable used for setting the line style of the segments
   * - polyline_line_thickness
     - int
     - 1.0
     - Thickness of the polylines
   * - polyline_pivot_marker
     - string
     - none
     - Add a marker to the the last trajectory plotted to materialse the pivot
   * - polyline_pivot_marker_colour
     - Colour(string)
     - black
     - Colour of the marker to use
   * - polyline_pivot_marker_height
     - float
     - 0.4
     - height of the marker to use
   * - polyline_pivot_marker_name
     - string
     - cyclone
     - name of the marker to use
   * - polyline_priority_variable_name
     - string
     - 
     - Variable used for setting the priority of the segments
   * - polyline_reference_level
     - float
     - 0.0
     - Level from which the level interval is calculated
   * - polyline_shade
     - bool(string)
     - none
     - Whether to shade polygons or not (ON/OFF)
   * - polyline_shade_colour_direction
     - string
     - anti_clockwise
     - Direction of colour sequencing for shading (CLOCKWISE/ ANTI_CLOCKWISE)
   * - polyline_shade_colour_list
     - stringarray
     - []
     - List of colours to be used in polygon shading.
   * - polyline_shade_colour_method
     - ColourTechnique(string)
     - calculate
     - Method of generating the colours of the bands in polygon shading (LIST/CALCULATE)
   * - polyline_shade_level_selection_type
     - LevelSelection(string)
     - count
     - Can be set to one of: (COUNT/ INTERVAL/ LEVEL_LIST)
   * - polyline_shade_max_level
     - float
     - 1e+21
     - Maximum level for which shading is required
   * - polyline_shade_max_level_colour
     - Colour(string)
     - blue
     - Highest shading band colour
   * - polyline_shade_min_level
     - float
     - -1e+21
     - Minimum level for which shading is required
   * - polyline_shade_min_level_colour
     - Colour(string)
     - red
     - Lowest shading band colour
   * - polyline_thickness_level_list
     - floatarray
     - []
     - level list to use for setting the Thickness
   * - polyline_thickness_list
     - floatarray
     - []
     - list of thicknesses to use
   * - polyline_thickness_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if the list of line styles is smaller that the list of levels: lastone/cycle
   * - polyline_thickness_variable_name
     - string
     - 
     - Data Variable used for setting the thickness of the segments
   * - polyline_trajectory_factor
     - int
     - -1.0
     - Method applied to draw the line
   * - polyline_trajectory_pivot_index
     - int
     - -1.0
     - Method applied to draw the line
   * - polyline_transparency_level_list
     - floatarray
     - []
     - level list to use for setting the Transparency
   * - polyline_transparency_pivot_variable_name
     - string
     - 
     - Data Variable used for setting the pivot used to compute the transparency of the segments
   * - polyline_transparency_variable_name
     - string
     - 
     - Data Variable used for setting the transparency of the segments

pmapgen
-------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - mapgen_input_file_name
     - string
     - 
     - The name of the input file containing the MapGen data
   * - mapgen_record
     - int
     - -1.0
     - The name of the input file containing the MapGen data to plot

pmetgram
--------

The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - efi_legend
     - bool(string)
     - True
     - legend
   * - efi_legend_box_type
     - string
     - both
     - both/negative/positive
   * - efi_legend_colour_list
     - stringarray
     - []
     - legend box colour list
   * - efi_legend_normal_colour
     - Colour(string)
     - black
     - legend colour box
   * - efi_legend_normal_thickness
     - int
     - 4.0
     - legend colour box
   * - efi_long_title
     - bool(string)
     - False
     - efigram long title ( Point Position ... General title!)
   * - efi_title
     - bool(string)
     - False
     - epsgram title ( parameter name)
   * - efijson_input_filename
     - string
     - 
     - Path to the file containing the Efi data (JSon format)
   * - eps_direction_keyword
     - string
     - forecast
     - keyword to plot : forecast/control!
   * - eps_direction_line_colour
     - Colour(string)
     - red
     - Colour of lines ...
   * - eps_direction_line_style
     - LineStyle(string)
     - solid
     - Line Style
   * - eps_direction_line_thickness
     - int
     - 1.0
     - Thickness of the line ...
   * - eps_plume_control
     - bool(string)
     - True
     - show the forecast
   * - eps_plume_control_line_colour
     - Colour(string)
     - cyan
     - Line colour of the control forecast
   * - eps_plume_control_line_style
     - LineStyle(string)
     - solid
     - Line Style of the control forecast
   * - eps_plume_control_line_thickness
     - int
     - 5.0
     - Line thickness of the deterministic forecast
   * - eps_plume_forecast
     - bool(string)
     - True
     - show the forecast
   * - eps_plume_forecast_line_colour
     - Colour(string)
     - cyan
     - Line colour of the deterministic forecast
   * - eps_plume_forecast_line_style
     - LineStyle(string)
     - dash
     - Line Style of the deterministic forecast
   * - eps_plume_forecast_line_thickness
     - int
     - 5.0
     - Line thickness of the deterministic forecast
   * - eps_plume_legend
     - bool(string)
     - True
     - ignore legend
   * - eps_plume_line_colour
     - Colour(string)
     - magenta
     - Line colour of the eps members
   * - eps_plume_line_style
     - LineStyle(string)
     - solid
     - Line style of the eps members
   * - eps_plume_line_thickness
     - int
     - 1.0
     - Line thickness of the eps members
   * - eps_plume_median
     - bool(string)
     - False
     - show the forecast
   * - eps_plume_median_line_colour
     - Colour(string)
     - cyan
     - Line colour of the control forecast
   * - eps_plume_median_line_style
     - LineStyle(string)
     - solid
     - Line Style of the control forecast
   * - eps_plume_median_line_thickness
     - int
     - 5.0
     - Line thickness of the deterministic forecast
   * - eps_plume_members
     - bool(string)
     - True
     - show the eps members
   * - eps_plume_method
     - string
     - time_serie
     - Type of visualisation required : time_serie or vertical_profile
   * - eps_plume_shading
     - bool(string)
     - False
     - Turn on/off the plume shading
   * - eps_plume_shading_colour_list
     - stringarray
     - []
     - colours used for plumes shading
   * - eps_plume_shading_level_list
     - floatarray
     - []
     - levels used for plumes shading
   * - eps_shade_colour
     - Colour(string)
     - red
     - Colour of the darkest shade area ...
   * - eps_shade_line_colour
     - Colour(string)
     - red
     - Colour of the darkest shade area ...
   * - eps_shade_line_style
     - LineStyle(string)
     - solid
     - Colour of the darkest shade area ...
   * - eps_shade_line_thickness
     - int
     - 1.0
     - Colour of the darkest shade area ...
   * - epsbufr_accumulated_parameter
     - bool(string)
     - False
     - Descriptor to use
   * - epsbufr_information
     - bool(string)
     - True
     - Plot or not information about station/forecast in a long title
   * - epsbufr_input_filename
     - string
     - 
     - Path to the file containing the Bufr data
   * - epsbufr_parameter_2_descriptor
     - int
     - 0.0
     - Descriptor to use
   * - epsbufr_parameter_descriptor
     - int
     - 0.0
     - Descriptor to use
   * - epsbufr_parameter_offset_factor
     - float
     - 0.0
     - Scaling factor to apply to the values
   * - epsbufr_parameter_scaling_factor
     - float
     - 1.0
     - Scaling factor to apply to the values
   * - epsbufr_parameter_title
     - string
     - 
     - Title to use to describe the parameter
   * - epsbufr_short_title
     - bool(string)
     - True
     - Plot or not information about station/forecast in a long title
   * - epsbufr_station_latitude
     - float
     - 0.0
     - Latitude of the point to extract
   * - epsbufr_station_longitude
     - float
     - 0.0
     - Longitude of the point to extract
   * - epsbufr_station_name
     - string
     - 
     - Name of the station to use in the title
   * - epsbufr_title
     - string
     - 
     - text block to be plotted
   * - epsbufr_y_axis_percentile
     - float
     - 1.0
     - Temperature correction
   * - epsbufr_y_axis_threshold
     - float
     - 50.0
     - Temperature correction
   * - epsxml_input_filename
     - string
     - 
     - Path to the file containing the Xml Description
   * - epsxml_long_title
     - bool(string)
     - False
     - epsgram long title
   * - epsxml_parameter
     - string
     - 
     - Parameter to extract
   * - epsxml_title
     - bool(string)
     - True
     - epsgram long title
   * - metgram_bar_colour
     - Colour(string)
     - blue
     - Colour of the curve
   * - metgram_bar_keyword
     - string
     - curve1
     - keyword used for define the bars
   * - metgram_curve2_colour
     - Colour(string)
     - blue
     - Colour of the second curve
   * - metgram_curve2_line_style
     - LineStyle(string)
     - solid
     - LineStyle of the second curve
   * - metgram_curve2_thickness
     - int
     - 2.0
     - Thickness of the second curve
   * - metgram_curve_colour
     - Colour(string)
     - red
     - Colour of the curve
   * - metgram_curve_keyword
     - string
     - curve1
     - keyword used for fefine the first curve
   * - metgram_curve_keyword2
     - string
     - curve2
     - keyword used for fefine the second curve
   * - metgram_curve_line_style
     - LineStyle(string)
     - solid
     - LineStyle of the curve
   * - metgram_curve_thickness
     - int
     - 2.0
     - Thickness of the curve
   * - metgram_database
     - string
     - /vol/epsgram/data/spotbase/epsdb
     - Classic Metgram Database Path
   * - metgram_date
     - string
     - -1.0
     - Classic Metgram date
   * - metgram_flag_colour
     - Colour(string)
     - red
     - Colour of Flag
   * - metgram_flag_component1
     - string
     - curve1
     - Keyword used for the First component
   * - metgram_flag_component2
     - string
     - curve2
     - Keyword used for the second component
   * - metgram_flag_frequency
     - int
     - 1.0
     - Frequency to plot the flags
   * - metgram_flag_length
     - float
     - 0.5
     - length of the flag
   * - metgram_flag_method
     - string
     - SD
     - SD : speed/direction is given UV : U/V components
   * - metgram_latitude
     - float
     - 0.0
     - Classic Metgram latitude
   * - metgram_long_title
     - bool(string)
     - False
     - epsgram long title
   * - metgram_longitude
     - float
     - 0.0
     - Classic Metgram longitude
   * - metgram_parameter
     - string
     - 
     - Classic Metgram Parameter
   * - metgram_parameter_offset
     - float
     - 0.0
     - metgram offset : used only in case of an unknow parameter
   * - metgram_parameter_scaling_factor
     - float
     - 1.0
     - metgram scaling factor : used only in case of an unknow parameter
   * - metgram_parameter_title
     - string
     - 
     - metgram parameter title : used only in case of an unknow parameter
   * - metgram_plot_style
     - MetgramStyle(string)
     - curve
     - Type of plot
   * - metgram_station_height
     - float
     - -1.0
     - epsgram long title
   * - metgram_station_name
     - string
     - 
     - epsgram long title
   * - metgram_temperature_correction
     - bool(string)
     - yes
     - Temperature correction
   * - metgram_time
     - string
     - 0.0
     - Classic Metgram time

pnetcdf
-------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - netcdf_colour_component_variable
     - string
     - 
     - Variable name representing the colour component of the vector ( in case of coloured wind)
   * - netcdf_dimension_setting
     - stringarray
     - []
     - Extract only of a subset of variables [ex: level:100:500]
   * - netcdf_dimension_setting_method
     - string
     - value
     - Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
   * - netcdf_direction_component_variable
     - string
     - 
     - Variable name representing the direction component of the vector
   * - netcdf_field_add_offset
     - float
     - 0.0
     - Offset added to the field values
   * - netcdf_field_automatic_scaling
     - bool(string)
     - True
     - Apply an automatic scaling, if needed
   * - netcdf_field_scaling_factor
     - float
     - 1.0
     - Scaling factor to multiply the field value by
   * - netcdf_field_suppress_above
     - float
     - 1e+21
     - Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
   * - netcdf_field_suppress_below
     - float
     - -1e+21
     - Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
   * - netcdf_filename
     - string
     - 
     - Path of the file to be read
   * - netcdf_latitude_variable
     - string
     - latitude
     - Variable name representing the latitude dimension
   * - netcdf_level_dimension_setting
     - string
     - 
     - Extract only the specified level
   * - netcdf_level_variable
     - string
     - level
     - Name of the level variable
   * - netcdf_longitude_variable
     - string
     - longitude
     - Variable name representing the longitude dimension
   * - netcdf_matrix_primary_index
     - string
     - longitude
     - Primary index latitude/longitude
   * - netcdf_metadata
     - string
     - {}
     - Json string containing metadata information: useful to choose a style
   * - netcdf_missing_attribute
     - string
     - _FillValue
     - Attribute indicating the value used to indicate a missing value in the data
   * - netcdf_number_dimension_setting
     - string
     - 
     - Extract only the specified number
   * - netcdf_number_variable
     - string
     - number
     - Name of the number variable
   * - netcdf_reference_date
     - string
     - 0.0
     - attribute indicating the reference date
   * - netcdf_speed_component_variable
     - string
     - 
     - Variable name representing the speed component of the vector
   * - netcdf_time_dimension_setting
     - string
     - 
     - Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
   * - netcdf_time_variable
     - string
     - time
     - Name of the time variable
   * - netcdf_type
     - NetcdfInterpretor(string)
     - guess
     - Type of data arrangement in the file (possible values: matrix)
   * - netcdf_value_variable
     - string
     - 
     - Variable to plot
   * - netcdf_x2_variable
     - string
     - x2
     - Variable name for the auxiliary x values (used in CurveArea)
   * - netcdf_x_auxiliary_variable
     - string
     - 
     - variable can used to define geoline definition.
   * - netcdf_x_component_variable
     - string
     - 
     - x_component for vector plotting
   * - netcdf_x_geoline_convention
     - string
     - lonlat
     - Geoline Convention used lonlat or latlon
   * - netcdf_x_variable
     - string
     - x
     - Variable name for the x values
   * - netcdf_y2_variable
     - string
     - y2
     - Variable name for the auxiliary y values (used in CurveArea)
   * - netcdf_y_auxiliary_variable
     - string
     - 
     - variable can used to define geoline definition.
   * - netcdf_y_component_variable
     - string
     - 
     - y_component for vector plotting
   * - netcdf_y_geoline_convention
     - string
     - lonlat
     - Geoline Convention used lonlat or latlon
   * - netcdf_y_variable
     - string
     - y
     - Variable name for the y values

pnew
----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - automatic_title
     - bool(string)
     - False
     - Plot the title (ON/OFF)
   * - layout
     - string
     - automatic
     - Type of page layout (POSITIONAL/AUTOMATIC)
   * - layout
     - string
     - automatic
     - Type of page layout (POSITIONAL/AUTOMATIC)
   * - layout
     - string
     - automatic
     - Type of page layout (POSITIONAL/AUTOMATIC)
   * - legend
     - bool(string)
     - False
     - Turn on/off legend
   * - legend
     - bool(string)
     - False
     - Turn on/off legend
   * - magics_backward_compatibility
     - bool(string)
     - true
     - Turn on/off
   * - magics_silent
     - bool(string)
     - False
     - Turn on/off legend
   * - magics_silent
     - bool(string)
     - False
     - Turn on/off
   * - page_frame
     - bool(string)
     - False
     - Plot frame around page (ON/OFF)
   * - page_frame_colour
     - Colour(string)
     - charcoal
     - Colour of page frame (Full choice of colours)
   * - page_frame_line_style
     - LineStyle(string)
     - solid
     - Style of page frame(SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
   * - page_frame_thickness
     - int
     - 2.0
     - Thickness of page frame
   * - page_id_line
     - NoPageID(string)
     - True
     - Plot identification line and ECMWF logo (ON/OFF)
   * - page_theme
     - string
     - super_page_theme
     - Theme to apply to the content of the page : the default is the super_page_theme
   * - page_x_gap
     - float
     - 0.0
     - Gap between pages in X direction
   * - page_x_length
     - float
     - 29.7
     - Length of page in horizontal direction
   * - page_x_position
     - float
     - 0.0
     - X-Coordinate of lower left hand corner of page.Default
   * - page_y_gap
     - float
     - 0.0
     - Gap between pages in Y direction
   * - page_y_length
     - float
     - 21.0
     - Length of page in vertical direction
   * - page_y_position
     - float
     - 0.0
     - Y-Coordinate of lower left hand corner of page.Default
   * - plot_direction
     - string
     - vertical
     - Direction of plotting (HORIZONTAL/VERTICAL)
   * - plot_direction
     - string
     - vertical
     - Direction of plotting (HORIZONTAL/VERTICAL)
   * - plot_direction
     - string
     - vertical
     - Direction of plotting (HORIZONTAL/VERTICAL)
   * - plot_start
     - string
     - bottom
     - Position of first page plotted (BOTTOM/TOP)
   * - plot_start
     - string
     - bottom
     - Position of first page plotted (BOTTOM/TOP)
   * - plot_start
     - string
     - bottom
     - Position of first page plotted (BOTTOM/TOP)
   * - skinny_mode
     - bool(string)
     - False
     - Turn special features skinny
   * - subpage_align_horizontal
     - string
     - left
     - Used in automatic layout to setup the horizontal alignment of the drawing area in the subpage
   * - subpage_align_vertical
     - string
     - bottom
     - Used in automatic layout to setup the vertical alignment of the drawing area in the subpage
   * - subpage_background_colour
     - Colour(string)
     - none
     - Colour of the subpage background
   * - subpage_clipping
     - bool(string)
     - False
     - Apply a clipping to the subpage to avoid any symbol, flag or arrow to go outside of the plotting area
   * - subpage_frame
     - bool(string)
     - True
     - Plot frame around subpage (ON/OFF)
   * - subpage_frame_colour
     - Colour(string)
     - charcoal
     - Colour of subpage frame (Full choice of colours)
   * - subpage_frame_line_style
     - LineStyle(string)
     - solid
     - Style of subpage frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
   * - subpage_frame_thickness
     - int
     - 2.0
     - Thickness of subpage frame
   * - subpage_horizontal_axis_height
     - float
     - 0.5
     - height of the horizontal axis in cm
   * - subpage_map_area_name
     - string
     - False
     - Name of the predefined area
   * - subpage_map_json_definition
     - string
     - 
     - Metview only : store internal information about zooned area
   * - subpage_map_library_area
     - bool(string)
     - False
     - if On, pickup a predefined geographical area
   * - subpage_map_magnifier
     - NoMagnifierVisitor(string)
     - False
     - {'for_docs': False, '#text': 'Mv4: turn on/off the generation of the infomation for the magnifier tool'}
   * - subpage_map_overlay_control
     - string
     - basic
     - {'for_docs': False, '#text': 'Metview Only: overlay method. always: plot the fields as they come; never: never overlay; by_date/by_level: only overlay data with the same valid date/level'}
   * - subpage_map_preview
     - NoPreviewVisitor(string)
     - False
     - {'for_docs': False, '#text': 'Mv4: turn on/off the generation of the infomation for the preview box'}
   * - subpage_map_projection
     - Transformation(string)
     - cylindrical
     - Projection to set in the drawing area
   * - subpage_right_position
     - float
     - -1.0
     - X-Coordinate of lower right hand corner of subpage
   * - subpage_top_position
     - float
     - -1.0
     - Y-Coordinate of upper left hand corner of subpage
   * - subpage_vertical_axis_width
     - float
     - 1.0
     - width of the vertical axis in cm
   * - subpage_x_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_x_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_x_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_x_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_x_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_x_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_x_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_x_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_x_axis_type
     - XCoordinate(string)
     - regular
     - 
   * - subpage_x_date_max
     - string
     - 
     - 
   * - subpage_x_date_min
     - string
     - 
     - 
   * - subpage_x_length
     - float
     - -1.0
     - Length of subpage in horizontal direction in cm.       -1 is the default: 85% of the parent page
   * - subpage_x_length_internal
     - float
     - -1.0
     - Length of subpage in horizontal direction.Default
   * - subpage_x_max
     - float
     - 100.0
     - 
   * - subpage_x_max
     - float
     - 100.0
     - 
   * - subpage_x_max_latitude
     - float
     - 90.0
     - 
   * - subpage_x_max_longitude
     - float
     - 180.0
     - 
   * - subpage_x_min
     - float
     - 0.0
     - 
   * - subpage_x_min
     - float
     - 0.0
     - 
   * - subpage_x_min_latitude
     - float
     - -90.0
     - 
   * - subpage_x_min_longitude
     - float
     - -180.0
     - 
   * - subpage_x_position
     - float
     - -1.0
     - Y-Coordinate of lower left hand corner of subpage in cm.      -1 is the default: 7.5% of the parent page
   * - subpage_x_position_internal
     - float
     - -1.0
     - Y-Coordinate of lower left hand corner of subpage
   * - subpage_y_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_y_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_y_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_y_automatic
     - AxisAutomaticSetting(string)
     - False
     - The Min and Max are calculated from the data
   * - subpage_y_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_y_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_y_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_y_automatic_reverse
     - bool(string)
     - False
     - 
   * - subpage_y_axis_type
     - YCoordinate(string)
     - regular
     - 
   * - subpage_y_date_max
     - string
     - 
     - 
   * - subpage_y_date_min
     - string
     - 
     - 
   * - subpage_y_length
     - float
     - -1.0
     - Length of subpage in vertical direction in cm.     -1 is the default: 85% of the parent page
   * - subpage_y_length_internal
     - float
     - -1.0
     - Length of subpage in vertical direction.Default
   * - subpage_y_max
     - float
     - 100.0
     - 
   * - subpage_y_max
     - float
     - 100.0
     - 
   * - subpage_y_max_latitude
     - float
     - 90.0
     - 
   * - subpage_y_max_longitude
     - float
     - 180.0
     - Set max Lon value
   * - subpage_y_min
     - float
     - 0.0
     - 
   * - subpage_y_min
     - float
     - 0.0
     - 
   * - subpage_y_min_latitude
     - float
     - -90.0
     - 
   * - subpage_y_min_longitude
     - float
     - -180.0
     - Set Y min value
   * - subpage_y_position
     - float
     - -1.0
     - X-Coordinate of lower left hand corner of subpage in cm.      -1 is the default: 5% of the parent page
   * - subpage_y_position_internal
     - float
     - -1.0
     - X-Coordinate of lower left hand corner of subpage
   * - super_page_frame
     - bool(string)
     - False
     - Plot frame around super page (ON/OFF)
   * - super_page_frame
     - bool(string)
     - False
     - Plot frame around super page (ON/OFF)
   * - super_page_frame_colour
     - Colour(string)
     - blue
     - Colour of super page frame
   * - super_page_frame_colour
     - Colour(string)
     - blue
     - Colour of super page frame
   * - super_page_frame_line_style
     - LineStyle(string)
     - solid
     - Style of super page frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
   * - super_page_frame_line_style
     - LineStyle(string)
     - solid
     - Style of super page frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
   * - super_page_frame_thickness
     - int
     - 1.0
     - Thickness of super page frame
   * - super_page_frame_thickness
     - int
     - 1.0
     - Thickness of super page frame
   * - super_page_theme
     - string
     - cream
     - Theme to apply to the content of the document : the default magics will ensure that no theme is applied and ensure fully backwards compatibility
   * - super_page_x_length
     - float
     - 29.7
     - Horizontal length of super page
   * - super_page_x_length
     - float
     - 29.7
     - Horizontal length of super page
   * - super_page_y_length
     - float
     - 21.0
     - Vertical length of super page
   * - super_page_y_length
     - float
     - 21.0
     - Vertical length of super page

pobsjson
--------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - obsjson_info_list
     - stringarray
     - []
     - list of values described using json format
   * - obsjson_input_filename
     - string
     - 
     - Path to the file containing the Observation data

pobsstat
--------

The Obstat decoder is responsible for decoding Obstat Ascii file.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - obsstat_filename
     - string
     - 
     - Epsgram Database Path

podb
----

This is responsible for accessing the ODB and passing  its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - odb_binning
     - BinningObject(string)
     - False
     - Information for the binning (degrees/radians)
   * - odb_binning
     - BinningObject(string)
     - False
     - Information for the binning (degrees/radians)
   * - odb_coordinates_unit
     - string
     - degrees
     - Coordinates unit used to define the location of the points (degrees/radians)
   * - odb_database
     - string
     - 
     - Odb Database Path
   * - odb_database_option
     - string
     - 
     - Odb Database option : clean
   * - odb_date
     - string
     - 
     - Odb date column name name used to save in to geopoint format
   * - odb_filename
     - string
     - 
     - odb Database Path
   * - odb_filename
     - string
     - 
     - odb Database Path
   * - odb_latitude
     - string
     - latitude
     - Odb latitude column name
   * - odb_latitude_variable
     - string
     - lat
     - odb Column name for the latitudes
   * - odb_level
     - string
     - press
     - Odb level column name
   * - odb_longitude
     - string
     - longitude
     - Odb longitude column name
   * - odb_longitude_variable
     - string
     - lon
     - odb Column name for the longitudes
   * - odb_nb_rows
     - int
     - -1.0
     - umber of rows to be retrieved
   * - odb_nb_rows
     - int
     - -1.0
     - umber of rows to be retrieved
   * - odb_nb_rows
     - int
     - 1000.0
     - info sent to the odb server to set the number of rows to be retrieved from the starting row
   * - odb_observation
     - string
     - obsvalue
     - Odb observation column name
   * - odb_observation_2
     - string
     - obsvalue
     - Odb observation#2 column name (for vectors)
   * - odb_parameters
     - floatarray
     - []
     - enable to bind a float value to a odb parameter ($?)
   * - odb_query
     - string
     - 
     - Odb Query
   * - odb_starting_row
     - int
     - 1.0
     - info sent to the odb server to set the starting row
   * - odb_time
     - string
     - 
     - Odb time column name used to save in to geopoint format
   * - odb_user_title
     - string
     - 
     - User defined title for automatic title
   * - odb_user_title
     - string
     - 
     - User defined title for automatic title
   * - odb_value_variable
     - string
     - 
     - odb Column name for the values
   * - odb_value_variable
     - string
     - 
     - odb Column name for the values
   * - odb_x
     - string
     - press
     - Odb column name used as X input for curve plotting
   * - odb_x_component_variable
     - string
     - 
     - odb Column name for the x component of a vector
   * - odb_x_component_variable
     - string
     - 
     - odb Column name for the x component of a vector
   * - odb_x_variable
     - string
     - lat
     - odb Column name for the x coordinates
   * - odb_y
     - string
     - press
     - Odb column name used as Y input for curve plotting
   * - odb_y_component_variable
     - string
     - 
     - odb Column name for the y component of a vector
   * - odb_y_component_variable
     - string
     - 
     - odb Column name for the y component of a vector
   * - odb_y_variable
     - string
     - lon
     - odb Column name for the y coordinates

popen
-----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - output_format
     - string
     - ps
     - Defines the device to be used (ps/png/pdf/svg/kml).
   * - output_formats
     - stringarray
     - []
     - Defines the list of devices to be used (ps/png/pdf/svg/kml).

popen/pnew
----------

Object used to handle the call to the Pseudo action routine PNEW

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - page_x_gap
     - float
     - 0.0cm
     - Gap between pages in X direction
   * - page_y_gap
     - float
     - 0.0cm
     - Gap between pages in Y direction
   * - plot_direction
     - string
     - vertical
     - Direction of plotting (HORIZONTAL/VERTICAL)
   * - plot_start
     - string
     - bottom
     - Position of first page plotted (BOTTOM/TOP)

pplot
-----



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - crs
     - string
     - 
     - Metview info :Crs used for the import
   * - crs_maxx
     - float
     - 180.0
     - Metview info :Crs used for the import
   * - crs_maxy
     - float
     - -90.0
     - Metview info :Crs used for the import
   * - crs_minx
     - float
     - -180.0
     - Metview info :Crs used for the import
   * - crs_miny
     - float
     - -90.0
     - Metview info :Crs used for the import
   * - import_format
     - string
     - PNG
     - Specify the format of the imported file
   * - import_height
     - float
     - -1.0
     - Height of the imported image (-1 means use the dimension of the image)
   * - import_system_coordinates
     - string
     - user
     - Specify the format of the imported file
   * - import_width
     - float
     - -1.0
     - Width of the imported image (-1 means use the dimension of the image)
   * - import_x_position
     - float
     - 0.0
     - X position of the imported image
   * - import_y_position
     - float
     - 0.0
     - Y position of the imported image

projection
----------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - subpage_coordinates_system
     - string
     - latlon
     - Proj4 defintion string : to be used very carefully --> possible side effect
   * - subpage_lower_left_latitude
     - float
     - -90.0
     - Latitude of lower left corner of map.
   * - subpage_lower_left_latitude
     - float
     - -90.0
     - Latitude of lower left corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
   * - subpage_lower_left_latitude
     - float
     - -90.0
     - Latitude of lower left corner of map.
   * - subpage_lower_left_longitude
     - float
     - -180.0
     - Longitude of lower left corner of map
   * - subpage_lower_left_longitude
     - float
     - -180.0
     - Longitude of lower left corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
   * - subpage_lower_left_longitude
     - float
     - -180.0
     - Longitude of lower left corner of map.
   * - subpage_map_area_coordinate_system
     - string
     - users
     - If set to projection, the coordinates of the bounding box are described in projection coordinates      instead of the more natural lat/lon system ( this is useful in the WMS context)
   * - subpage_map_area_definition
     - string
     - full
     - method used to define the geographical area.
   * - subpage_map_area_definition_polar
     - string
     - corners
     - Method of defining a polar stereographic map
   * - subpage_map_centre_latitude
     - float
     - 90.0
     - Latitude of centre of polar stereographic map defined by 'CENTRE' or centre latitude of Lambert/satellite subarea projections
   * - subpage_map_centre_longitude
     - float
     - 0.0
     - Longitude of centre of polar stereographic map defined by 'CENTRE' or centre longitude of Lambert/satellite subarea projections
   * - subpage_map_geos_sweep
     - float
     - 0.0
     - the sweep angle axis of the viewing instrument
   * - subpage_map_hemisphere
     - Hemisphere(string)
     - north
     - Hemisphere required for polar stereographic map(NORTH/SOUTH)
   * - subpage_map_proj4_definition
     - string
     - 
     - Proj4 defintion string : to be used very carefully --> possible side effect
   * - subpage_map_projection_azimuth
     - float
     - 20.0
     - bearing (in degrees) from due north
   * - subpage_map_projection_height
     - float
     - 42164000.0
     - height (in meters) above the surface
   * - subpage_map_projection_tilt
     - float
     - 0.0
     - angle (in degrees) away from nadir
   * - subpage_map_projection_view_latitude
     - float
     - 20.0
     - latitude (in degrees) of the view position
   * - subpage_map_projection_view_longitude
     - float
     - -60.0
     - longitude (in degrees) of the view position
   * - subpage_map_scale
     - float
     - 50000000.0
     - Scale of polar stereographic or Aitoff map
   * - subpage_map_true_scale_north
     - float
     - 6.0
     - Developement in progress
   * - subpage_map_true_scale_south
     - float
     - -60.0
     - Developement in progress
   * - subpage_map_vertical_longitude
     - float
     - 0.0
     - Vertical longitude of polar stereographic or Aitoff map
   * - subpage_map_vertical_longitude
     - float
     - 0.0
     - Developement in progress
   * - subpage_minimal_area
     - float
     - 0.1
     - Dimension in degrees of the minimal area to display
   * - subpage_upper_right_latitude
     - float
     - 90.0
     - Latitude of upper right corner of map
   * - subpage_upper_right_latitude
     - float
     - 90.0
     - Latitude of upper right corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
   * - subpage_upper_right_latitude
     - float
     - 90.0
     - Latitude of upper right corner of map.
   * - subpage_upper_right_longitude
     - float
     - 180.0
     - Longitude of upper right corner of map
   * - subpage_upper_right_longitude
     - float
     - 180.0
     - Longitude of upper right corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
   * - subpage_upper_right_longitude
     - float
     - 180.0
     - Longitude of upper right corner of map.

pshape
------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - shape_input_file_name
     - string
     - 
     - The name of the input file containing the shape data ( geography only)

pskewt
------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - subpage_x_automatic
     - bool(string)
     - False
     - 
   * - subpage_y_automatic
     - bool(string)
     - False
     - 
   * - thermo_annotation_width
     - float
     - 25.0
     - Percentage of the width used to display the annotation on the right side .
   * - x_max
     - float
     - 100.0
     - 
   * - x_min
     - float
     - 0.0
     - 
   * - y_max
     - float
     - 100.0
     - 
   * - y_min
     - float
     - 0.0
     - 

psymb
-----

This action routine (and C++object) controls the plotting of meteorological and marker symbols.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - legend
     - bool(string)
     - False
     - Turn legend on or off (ON/OFF) : New Parameter!
   * - symbol_connect_automatic_line_colour
     - bool(string)
     - True
     - if on, will use the colour of the symbol
   * - symbol_connect_line
     - bool(string)
     - False
     - Connect all the symbols with a line
   * - symbol_connect_line_colour
     - Colour(string)
     - black
     - Colour of the connecting line
   * - symbol_connect_line_style
     - LineStyle(string)
     - solid
     - Line Style of connecting line
   * - symbol_connect_line_thickness
     - int
     - 1.0
     - thickness of the connecting line
   * - symbol_format
     - string
     - (automatic)
     - Format used to plot values (MAGICS Format/(AUTOMATIC))
   * - symbol_legend_only
     - bool(string)
     - False
     - Inform the contour object do generate only the legend and not the plot .. [Web sdpecific]
   * - symbol_marker_mode
     - string
     - index
     - Method to select a marker : by name, by index, by image : in that case, Magics will use an external image as marker.
   * - symbol_outline
     - bool(string)
     - False
     - Add an outline to each symbol
   * - symbol_outline_colour
     - Colour(string)
     - black
     - Colour of the outline
   * - symbol_outline_style
     - LineStyle(string)
     - solid
     - Line Style of outline
   * - symbol_outline_thickness
     - int
     - 1.0
     - thickness of the outline
   * - symbol_scaling_factor
     - float
     - 4.0
     - Turn legend on or off (ON/OFF) : New Parameter!
   * - symbol_scaling_level_0_height
     - float
     - 0.1
     - Turn legend on or off (ON/OFF) : New Parameter!
   * - symbol_scaling_method
     - bool(string)
     - False
     - Turn legend on or off (ON/OFF) : New Parameter!
   * - symbol_table_mode
     - SymbolMode(string)
     - OFF
     - Specifies if plotting is to be in advanced, table (on) or individual mode (off).           Note: The simple table mode is not recommended anymore, try to use the advanced mode instead,          this should give you easier control of the plot.
   * - symbol_text_blanking
     - bool(string)
     - False
     - blanking of the text
   * - symbol_type
     - string
     - number
     - Defines the type of symbol plotting required

ptaylor
-------

None

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - taylor_label
     - string
     - Correlation
     - Label of the grid
   * - taylor_label_colour
     - Colour(string)
     - navy
     - Colour of the label
   * - taylor_label_height
     - float
     - 0.35
     - Hieght of the label
   * - taylor_primary_grid_increment
     - float
     - 0.5
     - Reference used of the Standard deviation plotting.
   * - taylor_primary_grid_line_colour
     - Colour(string)
     - navy
     - Colour used to plot the primary grid
   * - taylor_primary_grid_line_style
     - LineStyle(string)
     - solid
     - Line Style used to plot the primary grid
   * - taylor_primary_grid_line_thickness
     - int
     - 1.0
     - Thickness used to plot the primary grid
   * - taylor_primary_grid_reference
     - float
     - 0.5
     - Reference used of the Standard deviation plotting.
   * - taylor_primary_label
     - bool(string)
     - True
     - Turn the labels (on/off) of the primary grid
   * - taylor_primary_label_colour
     - Colour(string)
     - navy
     - Colour of the labels of the primary grid
   * - taylor_primary_label_height
     - float
     - 0.35
     - Height of the labels of the primary grid
   * - taylor_reference_line_colour
     - Colour(string)
     - navy
     - Colour used to plot the primary grid
   * - taylor_reference_line_style
     - LineStyle(string)
     - solid
     - Line Style used to plot the primary grid
   * - taylor_reference_line_thickness
     - int
     - 2.0
     - Thickness used to plot the primary grid
   * - taylor_secondary_grid
     - bool(string)
     - False
     - turn on/off the secondaries lines for the grid.
   * - taylor_secondary_grid_increment
     - float
     - 0.5
     - Reference used of the Standard deviation plotting.
   * - taylor_secondary_grid_line_colour
     - Colour(string)
     - navy
     - Colour used to plot the primary grid
   * - taylor_secondary_grid_line_style
     - LineStyle(string)
     - solid
     - Line Style used to plot the primary grid
   * - taylor_secondary_grid_line_thickness
     - int
     - 1.0
     - Thickness used to plot the primary grid
   * - taylor_secondary_grid_reference
     - float
     - 0.5
     - Reference used of the Standard deviation plotting.
   * - taylor_secondary_label
     - bool(string)
     - True
     - Turn the labels (on/off) of the secondary grid
   * - taylor_secondary_label_colour
     - Colour(string)
     - navy
     - Colour of the labels of the secondary grid
   * - taylor_secondary_label_height
     - float
     - 0.35
     - Height of the labels of the secondary grid
   * - taylor_standard_deviation_max
     - float
     - 1.0
     - Max of the Standard deviation axis.
   * - taylor_standard_deviation_min
     - float
     - 0.0
     - Min of the Standard deviation axis.

ptephi
------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - subpage_x_automatic
     - bool(string)
     - False
     - 
   * - subpage_y_automatic
     - bool(string)
     - False
     - 
   * - thermo_annotation_width
     - float
     - 25.0
     - Percentage of the width used to display the annotation on the right side .
   * - thermo_annotation_width
     - float
     - 25.0
     - Percentage of the width used to display the annotation on the right side .
   * - thermo_dry_adiabatic_colour
     - Colour(string)
     - charcoal
     - Colou of the dry_adiabatics
   * - thermo_dry_adiabatic_grid
     - bool(string)
     - True
     - Plot the dry_adiabatics
   * - thermo_dry_adiabatic_interval
     - float
     - 10.0
     - Interval between 2 dry_adiabatics.
   * - thermo_dry_adiabatic_label_colour
     - Colour(string)
     - charcoal
     - Label Colour for the isotherms
   * - thermo_dry_adiabatic_label_font
     - string
     - helvetica
     - Font name used for the dry_adiabatics labels
   * - thermo_dry_adiabatic_label_font_size
     - float
     - 0.3
     - Font Size used for the dry_adiabatics labels
   * - thermo_dry_adiabatic_label_font_style
     - string
     - normal
     - Font Style used for the dry_adiabatics labels
   * - thermo_dry_adiabatic_label_frequency
     - int
     - 1.0
     - frequency for dry_adiabatic labelling
   * - thermo_dry_adiabatic_reference
     - float
     - 0.0
     - Reference  of the dry_adiabatics
   * - thermo_dry_adiabatic_style
     - LineStyle(string)
     - solid
     - Line Style of the dry_adiabatics
   * - thermo_dry_adiabatic_thickness
     - int
     - 1.0
     - Thickness of the dry_adiabatics
   * - thermo_isobar_colour
     - Colour(string)
     - evergreen
     - Colou of the isobars
   * - thermo_isobar_grid
     - bool(string)
     - True
     - Plot the isobars
   * - thermo_isobar_interval
     - float
     - 100.0
     - Interval between isobars
   * - thermo_isobar_label_colour
     - Colour(string)
     - evergreen
     - Label Colour for the isotherms
   * - thermo_isobar_label_font
     - string
     - helvetica
     - Font name used for the isobars labels
   * - thermo_isobar_label_font_size
     - float
     - 0.3
     - Font Size used for the isobars labels
   * - thermo_isobar_label_font_style
     - string
     - normal
     - Font Style used for the isobars labels
   * - thermo_isobar_label_frequency
     - int
     - 1.0
     - isobar frequency for labelling
   * - thermo_isobar_reference
     - float
     - 1000.0
     - Line Style of the isobars
   * - thermo_isobar_style
     - LineStyle(string)
     - solid
     - Line Style of the isobars
   * - thermo_isobar_thickness
     - int
     - 2.0
     - Thickness of the isobars
   * - thermo_isotherm_colour
     - Colour(string)
     - charcoal
     - Colou of the isotherms
   * - thermo_isotherm_grid
     - bool(string)
     - True
     - Plot the isotherms
   * - thermo_isotherm_interval
     - float
     - 10.0
     - interval for isotherms grid
   * - thermo_isotherm_label_colour
     - Colour(string)
     - charcoal
     - Label Colour for the isotherms
   * - thermo_isotherm_label_font
     - string
     - helvetica
     - Font name used for the isotherms labels
   * - thermo_isotherm_label_font_size
     - float
     - 0.3
     - Font Size used for the isotherms labels
   * - thermo_isotherm_label_font_style
     - string
     - normal
     - Font Style used for the isotherms labels
   * - thermo_isotherm_label_frequency
     - int
     - 1.0
     - Isotherm frequency for labelling
   * - thermo_isotherm_reference
     - float
     - 0.0
     - Reference  of the isotherms
   * - thermo_isotherm_reference_colour
     - Colour(string)
     - red
     - Reference  of the isotherms
   * - thermo_isotherm_reference_style
     - LineStyle(string)
     - solid
     - Reference  of the isotherms
   * - thermo_isotherm_reference_thickness
     - int
     - 2.0
     - Reference  of the isotherms
   * - thermo_isotherm_style
     - LineStyle(string)
     - solid
     - Line Style of the isotherms
   * - thermo_isotherm_thickness
     - int
     - 1.0
     - Thickness of the isotherms
   * - thermo_mixing_ratio_colour
     - Colour(string)
     - purple
     - Colou of the mixing_ratios
   * - thermo_mixing_ratio_frequency
     - int
     - 1.0
     - mixing_ratio frequency for grid
   * - thermo_mixing_ratio_grid
     - bool(string)
     - True
     - Plot the mixing_ratios
   * - thermo_mixing_ratio_label_colour
     - Colour(string)
     - purple
     - Label Colour for the isotherms
   * - thermo_mixing_ratio_label_font
     - string
     - helvetica
     - Font name used for the mixing_ratios labels
   * - thermo_mixing_ratio_label_font_size
     - float
     - 0.3
     - Font Size used for the mixing_ratios labels
   * - thermo_mixing_ratio_label_font_style
     - string
     - normal
     - Font Style used for the mixing_ratios labels
   * - thermo_mixing_ratio_label_frequency
     - int
     - 1.0
     - mixing_ratio frequency for labelling
   * - thermo_mixing_ratio_style
     - LineStyle(string)
     - dash
     - Line Style of the mixing_ratios
   * - thermo_mixing_ratio_thickness
     - int
     - 1.0
     - Thickness of the mixing_ratios
   * - thermo_saturated_adiabatic_colour
     - Colour(string)
     - charcoal
     - Colou of the saturated_adiabatics
   * - thermo_saturated_adiabatic_grid
     - bool(string)
     - True
     - Plot the saturated_adiabatics
   * - thermo_saturated_adiabatic_interval
     - float
     - 5.0
     - interval for saturated_adiabatics grid
   * - thermo_saturated_adiabatic_label_colour
     - Colour(string)
     - charcoal
     - Label Colour for the isotherms
   * - thermo_saturated_adiabatic_label_font
     - string
     - helvetica
     - Font name used for the saturated_adiabatics labels
   * - thermo_saturated_adiabatic_label_font_size
     - float
     - 0.3
     - Font Size used for the saturated_adiabatics labels
   * - thermo_saturated_adiabatic_label_font_style
     - string
     - normal
     - Font Style used for the saturated_adiabatics labels
   * - thermo_saturated_adiabatic_label_frequency
     - int
     - 1.0
     - saturated_adiabatic frequency for labelling
   * - thermo_saturated_adiabatic_reference
     - float
     - 0.0
     - Reference  of the saturated_adiabatics
   * - thermo_saturated_adiabatic_style
     - LineStyle(string)
     - solid
     - Line Style of the saturated_adiabatics
   * - thermo_saturated_adiabatic_thickness
     - int
     - 2.0
     - Thickness of the dry_adiabatics
   * - x_max
     - float
     - 100.0
     - 
   * - x_min
     - float
     - 0.0
     - 
   * - y_max
     - float
     - 100.0
     - 
   * - y_min
     - float
     - 0.0
     - 

ptext
-----

None

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - text_automatic
     - bool(string)
     - True
     - How text is to be positioned in each line (LEFT/CENTRE/RIGHT)
   * - text_border
     - bool(string)
     - False
     - Plot border around text box (ON/OFF)
   * - text_border_colour
     - Colour(string)
     - blue
     - Colour of border around text box (Full choice of colours)
   * - text_border_line_style
     - LineStyle(string)
     - solid
     - Line style of border around text box (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
   * - text_border_thickness
     - int
     - 1.0
     - Thickness of text box border
   * - text_box_blanking
     - bool(string)
     - False
     - All plotting in the text box previous to PTEXT call will be blanked out. Plotting after PTEXT call will not be affected. (ON/OFF)
   * - text_box_x_length
     - float
     - -1.0
     - Length of text box in X direction
   * - text_box_x_position
     - float
     - -1.0
     - X coordinate of lower left corner of text box (Relative to PAGE_X_POSITION)
   * - text_box_y_length
     - float
     - -1.0
     - 
   * - text_box_y_position
     - float
     - -1.0
     - Y coordinate of lower left corner of text box (Relative to PAGE_Y_POSITION)
   * - text_character_1
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_10
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_2
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_3
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_4
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_5
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_6
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_7
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_8
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_character_9
     - string
     - 
     - 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
   * - text_colour
     - Colour(string)
     - navy
     - Colour of text in text block (Full choice of colours)
   * - text_escape_character
     - string
     - #
     - Symbol or character followed by 3 octal numbers
   * - text_first_line
     - int
     - 1.0
     - The first line in the text block to be plotted
   * - text_font
     - string
     - helvetica
     - Font name - please make sure this font is installed!
   * - text_font_size
     - string
     - 0.5
     - Font size, specified in cm.
   * - text_font_style
     - string
     - normal
     - Font style. Set this to an empty string in order to remove all styling.
   * - text_html
     - bool(string)
     - True
     - enable use of HTML convention
   * - text_instruction_shift_character
     - string
     - \
     - Symbol or character for indicating that an Instruction String follows
   * - text_integer_1
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_10
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_2
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_3
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_4
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_5
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_6
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_7
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_8
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_integer_9
     - int
     - 0.0
     - 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
   * - text_justification
     - Justification(string)
     - centre
     - How text is to be positioned in each line (LEFT/CENTRE/RIGHT)
   * - text_line_1
     - string
     - <magics_title/>
     - Character string for holding lines of text (n=1,10)
   * - text_line_10
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_2
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_3
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_4
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_5
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_6
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_7
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_8
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_9
     - string
     - 
     - Character string for holding lines of text (n=1,10)
   * - text_line_count
     - int
     - 1.0
     - The number of lines of text to be plotted
   * - text_line_height_ratio_1
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_10
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_2
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_3
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_4
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_5
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_6
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_7
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_8
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratio_9
     - float
     - 1.0
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_height_ratios
     - floatarray
     - []
     - Ratio of height of text lines to text reference character height (n=1,10). See main text
   * - text_line_space_ratio
     - float
     - 1.5
     - Ratio of space above and below each line to text reference character height. See main text
   * - text_lines
     - stringarray
     - []
     - text block to be plotted
   * - text_mode
     - string
     - title
     - Whether text is to be a title or user positioned (TITLE/POSITIONAL)
   * - text_orientation
     - string
     - horizontal
     - Orientation of the text
   * - text_parameter_escape_character
     - string
     - 
     - Symbol or character for indicating that a Magics parameter follows. The Magics parameter is also terminated by the same symbol or character.
   * - text_real_1
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_10
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_2
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_3
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_4
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_5
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_6
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_7
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_8
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
   * - text_real_9
     - float
     - 0.0
     - 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)

pwind
-----

Parameters common to the flags and arrows.

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - legend
     - bool(string)
     - False
     - Add a wind legend information in the legend
   * - wind_advanced_colour_direction
     - string
     - anti_clockwise
     - Direction of colour sequencing for plotting
   * - wind_advanced_colour_level_count
     - int
     - 10.0
     - Number of levels to be plotted. Magics will try to find "nice levels",      this means that the number of levels could be slightly different
   * - wind_advanced_colour_level_interval
     - float
     - 8.0
     - Interval in data units between different bands of colours
   * - wind_advanced_colour_level_list
     - floatarray
     - []
     - List of levels to be used
   * - wind_advanced_colour_level_tolerance
     - int
     - 2.0
     - Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
   * - wind_advanced_colour_list
     - stringarray
     - []
     - List of colours to be used in wind plotting
   * - wind_advanced_colour_list_policy
     - ListPolicy(string)
     - lastone
     - What to do if, the list of colours is smaller that the list of intervals: lastone/cycle
   * - wind_advanced_colour_max_level_colour
     - Colour(string)
     - blue
     - Highest shading band colour
   * - wind_advanced_colour_max_value
     - float
     - 1e+21
     - Max value to plot
   * - wind_advanced_colour_min_level_colour
     - Colour(string)
     - red
     - Lowest shading band colour
   * - wind_advanced_colour_min_value
     - float
     - -1e+21
     - Min value to plot
   * - wind_advanced_colour_parameter
     - string
     - speed
     - if speed, the wind is coloured using the norm of the vector, If parameter, a third parameter is used.
   * - wind_advanced_colour_reference_level
     - float
     - 0.0
     - Level from which the level interval is calculated
   * - wind_advanced_colour_selection_type
     - LevelSelection(string)
     - count
     - Set selection method
   * - wind_advanced_colour_table_colour_method
     - ColourTechnique(string)
     - calculate
     - Method of generating the colours
   * - wind_advanced_method
     - string
     - False
     - Enable advanced plotting of wind (default is off for backward compatibility).      The coour is selected according to the intensity of the wind (vector)
   * - wind_arrow_calm_below
     - float
     - 0.5
     - Winds less than or equal to this value will be drawn as calm.
   * - wind_arrow_calm_indicator
     - CalmIndicator(string)
     - False
     - Plot calm indicator circle if wind speed is less than or equal to the value in WIND_ARROW_CALM_BELOW (ON / OFF)
   * - wind_arrow_calm_indicator_size
     - float
     - 0.3
     - The radius of the circle which indicates calm
   * - wind_arrow_colour
     - Colour(string)
     - blue
     - Colour of wind arrow
   * - wind_arrow_cross_boundary
     - bool(string)
     - True
     - If set to 'ON', wind arrows are truncated if they cross the subpage border (ON / OFF).
   * - wind_arrow_fixed_velocity
     - float
     - 0.0
     - Fixed velocity arrows (m/s).
   * - wind_arrow_head_ratio
     - float
     - 0.3
     - Table number, XY, indicating style and shape of arrowhead X
   * - wind_arrow_head_shape
     - int
     - 0.0
     - Table number, XY, indicating shape of arrowhead X
   * - wind_arrow_legend_text
     - string
     - m/s
     - Text to be used as units in the legend text
   * - wind_arrow_max_speed
     - float
     - 1e+21
     - Highest value of wind speed to be plotted
   * - wind_arrow_min_speed
     - float
     - -1e+21
     - Lowest value of wind speed to be plotted
   * - wind_arrow_origin_position
     - ArrowPosition(string)
     - tail
     - The position of the wind arrow relative to the wind origin
   * - wind_arrow_style
     - LineStyle(string)
     - solid
     - Controls the line style of the arrow flag shaft.
   * - wind_arrow_thickness
     - int
     - 1.0
     - Thickness of wind arrow shaft
   * - wind_arrow_unit_system
     - string
     - paper
     - Coordinates sysem used to sacle the arrow : paper -->1cm, user-->1 user unit
   * - wind_arrow_unit_velocity
     - float
     - 25.0
     - Wind speed in m/s represented by a unit vector (1.0 cm or 1.0 user unit depending on the value of wind_arrow_unit_system ).
   * - wind_field_type
     - WindPlotting(string)
     - arrows
     - Method of wind field plotting
   * - wind_flag_calm_below
     - float
     - 0.5
     - Winds less than or equal to this value will be drawn as calm.
   * - wind_flag_calm_indicator
     - CalmIndicator(string)
     - True
     - Plot calm indicator circle, if wind speed is less than 0.5 m/s (ON / OFF)
   * - wind_flag_calm_indicator_size
     - float
     - 0.3
     - The radius of the circle which indicates calm in centimeter
   * - wind_flag_colour
     - Colour(string)
     - blue
     - Colour of wind flag shaft, barbs and pennants
   * - wind_flag_cross_boundary
     - bool(string)
     - True
     - If set to 'ON', wind flags are truncated if they cross the subpage border (ON / OFF)
   * - wind_flag_length
     - float
     - 1.0
     - Physical length of wind flag shaft
   * - wind_flag_max_speed
     - float
     - 1e+21
     - Highest value of wind speed to be plotted
   * - wind_flag_min_speed
     - float
     - -1e+21
     - Lowest value of wind speed to be plotted
   * - wind_flag_mode
     - string
     - normal
     - Controls the line style of the wind flag shaft.(NORMAL / OFF_LEVEL / OFF_TIME)
   * - wind_flag_origin_marker
     - OriginMarker(string)
     - circle
     - Symbol for marking the exact location of the current grid point.
   * - wind_flag_origin_marker_size
     - float
     - 0.3
     - 
   * - wind_flag_style
     - LineStyle(string)
     - solid
     - Controls the line style of the wind flag shaft.
   * - wind_flag_thickness
     - int
     - 1.0
     - Thickness of wind flag shaft
   * - wind_legend_only
     - bool(string)
     - False
     - {'for_docs': False, '#text': 'Wrep only : to build only the legned...'}
   * - wind_legend_text
     - string
     - vector
     - Use your own text in the legend
   * - wind_streamline_colour
     - Colour(string)
     - blue
     - Colour of streamlines
   * - wind_streamline_head_ratio
     - float
     - 0.2
     - Table number, XY, indicating style and shape of arrowhead X
   * - wind_streamline_head_shape
     - int
     - 1.0
     - Table number, XY, indicating shape of arrowhead X
   * - wind_streamline_min_density
     - float
     - 1.0
     - The minimum number of streamlines to be plotted in one square cm of the user's subpage
   * - wind_streamline_min_speed
     - float
     - 1.0
     - Wind speed below which streamline plotting will be stopped
   * - wind_streamline_style
     - LineStyle(string)
     - solid
     - Line style of streamlines
   * - wind_streamline_thickness
     - int
     - 2.0
     - Thickness of streamlines
   * - wind_thinning_debug
     - bool(string)
     - False
     - Add Position requiered for thiniing [ Debug mode only]
   * - wind_thinning_factor
     - float
     - 2.0
     - Controls the actual number of wind arrows or flags plotted. See main text for explanation. Needs to 1.0 or larger.
   * - wind_thinning_method
     - string
     - data
     - Method to control the thinning:      data : wind_thinning_factor will determine the frequency as before      user : wind_thining_factor will determine the minimal distance in user coordinates betvween 2 winds.      the default is "data" for backward compatibility.

pwrepjson
---------



.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - wrepjson_clim_parameter
     - string
     - 
     - date to select for the clim In date format (YYYYMMDDHHHH)
   * - wrepjson_clim_step
     - int
     - 36.0
     - date to select for the clim In date format (YYYYMMDDHHHH)
   * - wrepjson_family
     - string
     - eps
     - How to interpret the json file
   * - wrepjson_hodograph_grid
     - bool(string)
     - False
     - add the Grid for the hodograph!
   * - wrepjson_hodograph_member
     - int
     - -1.0
     - slecet only one member
   * - wrepjson_hodograph_tephi
     - bool(string)
     - False
     - add the Grid for the hodograph!
   * - wrepjson_ignore_keys
     - stringarray
     - []
     - List of keys to ignore when reading onput data
   * - wrepjson_information
     - bool(string)
     - True
     - Plot or not information about station/forecast in a long title
   * - wrepjson_input_filename
     - string
     - 
     - Path to the file containing the Bufr data
   * - wrepjson_key
     - string
     - 
     - Forecast information to plot!
   * - wrepjson_keyword
     - string
     - 
     - if several eps data are put in the same json object, give the keyowrd to find them
   * - wrepjson_missing_value
     - float
     - -9999.0
     - Missing value
   * - wrepjson_parameter
     - string
     - 1.0
     - Scaling factor to apply to the values
   * - wrepjson_parameter_information
     - string
     - 
     - Product information for key=parameter_info
   * - wrepjson_parameter_offset_factor
     - float
     - 0.0
     - Scaling factor to apply to the values
   * - wrepjson_parameter_scaling_factor
     - float
     - 1.0
     - Scaling factor to apply to the values
   * - wrepjson_plumes_interval
     - float
     - 1.0
     - plumes interval
   * - wrepjson_position_information
     - bool(string)
     - True
     - Switch on/off the position information in the title.
   * - wrepjson_product_information
     - string
     - 
     - Product information for key=product_info
   * - wrepjson_profile_quantile
     - string
     - 
     - List of keys to ignore when reading onput data
   * - wrepjson_station_name
     - string
     - 
     - Name of the station to use in the title
   * - wrepjson_steps
     - intarray
     - []
     - steps to extract ( legend will use step+12)
   * - wrepjson_temperature_correction
     - bool(string)
     - False
     - Temperature correction
   * - wrepjson_title
     - bool(string)
     - True
     - Do not create automatic title
   * - wrepjson_y_axis_percentile
     - float
     - 1.0
     - use of threshold
   * - wrepjson_y_axis_threshold
     - float
     - 50.0
     - use of threshold  to get rid of the unlikely values
   * - wrepjson_y_max_threshold
     - float
     - INT_MAX
     - If all the values are below the threshold, use the threshold as max value when automatic setting of y axis
   * - wrepjson_y_percentage
     - float
     - 0.01
     - percentage of the range to add to compute automatic minmax of axis.

xml
---

The Efi decoder is responsible for decoding EFi Ascii file.(Metops)

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 60

   * - Name
     - Type
     - Default
     - Description
   * - efi_filename
     - string
     - 
     - Efi file name Path
   * - efi_record
     - int
     - 0.0
     - Efi record ( starting at 0)
