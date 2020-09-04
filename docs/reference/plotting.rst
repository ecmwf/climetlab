Plotting
========


legend
------

.. ContinuousLegendMethod 

.. HistogramLegendMethod 

.. LegendVisitor Collection of parameters defining how a legend will be plotted. To plot a legend the parameter 'Legend' needs to set to 'on'.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **legend_label_frequency**
       | Frequency of the labels.
     - | int
     - | 1
   * - | **legend_label_frequency**
       | Frequency of the labels.
     - | int
     - | 1
   * - | **legend_histogram_border**
       | add a border to the the bars
     - | string
     - | on
   * - | **legend_histogram_border_colour**
       | border colour of the bars
     - | string
     - | black
   * - | **legend_histogram_mean_value**
       | show the mean value
     - | string
     - | off
   * - | **legend_histogram_mean_value_marker**
       | show the mean value
     - | int
     - | 15
   * - | **legend_histogram_mean_value_marker_colour**
       | show the mean value
     - | string
     - | black
   * - | **legend_histogram_mean_value_marker_size**
       | show the mean value
     - | float
     - | 0.4
   * - | **legend_histogram_max_value**
       | show the max value
     - | string
     - | on
   * - | **legend_histogram_grid_colour**
       | Colour of the grids
     - | string
     - | black
   * - | **legend_histogram_grid_line_style**
       | Line Style of the grids
     - | string
     - | solid
   * - | **legend_histogram_grid_thickness**
       | thickness of the grids
     - | int
     - | 1
   * - | **legend_text_colour**
       | Legend text colour
     - | string
     - | blue
   * - | **legend_title**
       | plot legend title text
     - | string
     - | off
   * - | **legend_title_text**
       | Text to plot as legend title
     - | string
     - | legend
   * - | **legend_title_orientation**
       | Orientation of legend title, if automatic the title will be horizontal for horizontal legend and vertical for vertical
     - | ['vertical', 'horizontal', 'automatic']
     - | automatic
   * - | **legend_title_font_size**
       | Font size used for the title: The default is the same as text_entry
     - | float
     - | -1
   * - | **legend_title_font_colour**
       | Font Colour used for the title: The defaut is the same as the text_entry
     - | string
     - | automatic
   * - | **legend_title_position**
       | relative title position
     - | ['automatic', 'top', 'bottom', 'left', 'right']
     - | automatic
   * - | **legend_title_position_ratio**
       | percentage of the legend box used for the title
     - | float
     - | 25
   * - | **legend_units_text**
       | Text to plot as units
     - | string
     - | 
   * - | **legend_user_minimum**
       | Use of user tailored text for minimum
     - | string
     - | off
   * - | **legend_user_minimum_text**
       | User tailored text for minimum
     - | string
     - | 
   * - | **legend_user_maximum**
       | Use of user tailored text for maximum
     - | string
     - | off
   * - | **legend_user_maximum_text**
       | User tailored text for maximum
     - | string
     - | 
   * - | **legend_display_type**
       | type of shaded legend required
     - | string
     - | disjoint
   * - | **legend_text_format**
       | Format of automatic text (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **legend_box_mode**
       | Whether legend box is positioned automatically or by the user
     - | ['automatic', 'positional']
     - | automatic
   * - | **legend_automatic_position**
       | Whether legend box is positioned on the top or on the right of the drawing area
     - | ['top', 'right']
     - | top
   * - | **legend_automatic_box_margin**
       | margin in % of the legend box [top/bottom] for vertical layout and [left/right] for horizontal layout
     - | float
     - | 5
   * - | **legend_text_font**
       | Font name - please make sure this font is installed!
     - | string
     - | sansserif
   * - | **legend_text_font_style**
       | Font style. Set this to an empty string in order to remove all styling.
     - | ['normal', 'bold', 'italic', 'bolditalic']
     - | normal
   * - | **legend_text_font_size**
       | Font size, specified in cm or in % ex: 0.5cm or 10%
     - | string
     - | 0.3
   * - | **legend_text_quality**
       | Quality of text in legend : deprecated use legend_text_font and legend_text_font_style
     - | string
     - | medium
   * - | **legend_text_orientation**
       | Orientation of the text : horizontal by default
     - | float
     - | 0
   * - | **legend_user_lines**
       | List of text for legend entries
     - | stringarray
     - | stringarray()
   * - | **legend_column_count**
       | Number of columns in the legend
     - | int
     - | 1
   * - | **legend_entry_plot_direction**
       | Method of filling in legend entries
     - | ['automatic', 'row', 'column']
     - | automatic
   * - | **legend_entry_plot_orientation**
       | going from bootom to top ot top to bottom in column mode!
     - | ['bottom_top', 'top_bottom']
     - | bottom_top
   * - | **legend_text_composition**
       | Determines whether to use automatically-generated or user-generated text (or both) in the legend
     - | ['automatic_text_only', 'user_text_only', 'both']
     - | automatic_text_only
   * - | **legend_values_list**
       | List of values to show in the legend
     - | floatarray
     - | floatarray()
   * - | **legend_user_text**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_1**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_2**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_3**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_4**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_5**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_6**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_7**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_8**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_9**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_user_text_10**
       | User text to be associated with a legend sub-entry from a multiple entry
     - | string
     - | 
   * - | **legend_symbol_height_factor**
       | Factor to apply to the symbol_height in the legend
     - | float
     - | 1
   * - | **legend_box_x_position**
       | X coordinate of lower left corner of legend box (Relative to page_x_position)
     - | float
     - | -1
   * - | **legend_box_y_position**
       | Y coordinate of lower left corner of legend box (Relative to page_y_position)
     - | float
     - | -1
   * - | **legend_box_x_length**
       | Length of legend box in X direction
     - | float
     - | -1
   * - | **legend_box_y_length**
       | Length of legend box in Y direction
     - | float
     - | 0
   * - | **legend_box_blanking**
       | blanking of legend box
     - | string
     - | off
   * - | **legend_border**
       | Plot border around legend box
     - | string
     - | off
   * - | **legend_border_line_style**
       | Line style of border around legend box
     - | string
     - | solid
   * - | **legend_border_colour**
       | Colour of border around text box (Full choice of colours)
     - | string
     - | blue
   * - | **legend_border_thickness**
       | Thickness of legend box border
     - | int
     - | 1
   * - | **legend_wrep**
       | activate wrep mode for legend building
     - | string
     - | off
   * - | **legend_only**
       | generate only the legend ( used for the wrep..
     - | string
     - | off
   * - | **legend_entry_text_width**
       | Width in percent used for the text part of a legend Entry
     - | float
     - | 60
   * - | **legend_entry_border**
       | add a border to the graphical part of each legend entry
     - | string
     - | on
   * - | **legend_entry_border_colour**
       | border colour
     - | string
     - | black


pbinning
--------

.. NoBinningObject 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **binning_x_method**
       | Method to compute binns : count/list/interval
     - | ['count', 'list', 'interval']
     - | count
   * - | **binning_x_min_value**
       | Min value used to compute the binns
     - | float
     - | -1e+21
   * - | **binning_x_max_value**
       | Max value used to compute the binns
     - | float
     - | 1e+21
   * - | **binning_x_count**
       | Aprroximate number on binns when using the count method
     - | int
     - | 10
   * - | **binning_x_list**
       | list of binns when using the list method
     - | floatarray
     - | floatarray()
   * - | **binning_x_interval**
       | list of binns when using the interval method
     - | float
     - | 10
   * - | **binning_x_reference**
       | list of binns when using the interval method
     - | float
     - | 0
   * - | **binning_y_method**
       | Method to compute binns : count/list/interval
     - | ['count', 'list', 'interval']
     - | count
   * - | **binning_y_min_value**
       | Min value used to compute the binns
     - | float
     - | -1e+21
   * - | **binning_y_max_value**
       | Max value used to compute the binns
     - | float
     - | 1e+21
   * - | **binning_y_count**
       | Aprroximate number on binns when using the count method
     - | int
     - | 10
   * - | **binning_y_list**
       | list of binns when using the list method
     - | floatarray
     - | floatarray()
   * - | **binning_y_interval**
       | list of binns when using the interval method
     - | float
     - | 10
   * - | **binning_y_reference**
       | list of binns when using the interval method
     - | float
     - | 0


pcdfgram
--------

.. CdfGraph The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. EfiGraph The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **cdf_graph_type**
       | Colour of the curve
     - | string
     - | medium
   * - | **cdf_lines_colour_array**
       | Colour of the curve
     - | stringarray
     - | stringarray()
   * - | **cdf_lines_style_array**
       | Style of the curve
     - | stringarray
     - | stringarray()
   * - | **cdf_lines_thickness_array**
       | Thickness of the curve
     - | intarray
     - | intarray()
   * - | **cdf_clim_line_colour**
       | Colour of the clim curve
     - | string
     - | black
   * - | **cdf_clim_line_thickness**
       | Thickness of the clim curve
     - | int
     - | 4
   * - | **cdf_clim_line_style**
       | Style of the clim curve
     - | string
     - | solid
   * - | **legend**
       | Style of the clim curve
     - | string
     - | off
   * - | **efi_box_colour_array**
       | Colour of the curve
     - | stringarray
     - | stringarray()
   * - | **efi_box_border_colour**
       | Style of the curve
     - | string
     - | black
   * - | **efi_box_border_thickness**
       | Style of the curve
     - | int
     - | 1
   * - | **efi_box_border_line_style**
       | Style of the curve
     - | string
     - | solid
   * - | **efi_normal_colour**
       | Style of the curve
     - | string
     - | black
   * - | **efi_normal_thickness**
       | Style of the curve
     - | int
     - | 4
   * - | **efi_normal_line_style**
       | Style of the curve
     - | string
     - | solid
   * - | **efi_font**
       | 
     - | string
     - | sansserif
   * - | **efi_font_size**
       | 
     - | float
     - | 0.25
   * - | **efi_font_style**
       | 
     - | string
     - | 
   * - | **efi_font_colour**
       | 
     - | string
     - | black


pcoast
------

.. Boundaries This object sets the properties of the political boundaries.

.. Cities 

.. CoastPlotting 

.. Coastlines The parameters relating to action routine PCOAST (C++ class Coastlines) enable users to control the plotting of coastlines and grid lines.

.. GridPlotting This object will control the settings of the Map Grids.

.. LabelPlotting This object will control the settings of the Map Labels.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **map_boundaries_style**
       | Line style of boundaries
     - | string
     - | solid
   * - | **map_boundaries_colour**
       | Colour of boundaries
     - | string
     - | grey
   * - | **map_boundaries_thickness**
       | Line thickness of boundaries
     - | int
     - | 1
   * - | **map_disputed_boundaries**
       | Display the disputed boundaries (on/off)
     - | string
     - | on
   * - | **map_disputed_boundaries_style**
       | Line style of disputed boundaries
     - | string
     - | dash
   * - | **map_disputed_boundaries_colour**
       | Colour of disputed boundaries
     - | string
     - | automatic
   * - | **map_disputed_boundaries_thickness**
       | Line thickness of disputed boundaries
     - | int
     - | 1
   * - | **map_administrative_boundaries**
       | Display administrative boundaries (on/off)
     - | string
     - | off
   * - | **map_administrative_boundaries_countries_list**
       | List of countries for which to show administrative borders. Convention used is the 3 Letters ISO Codes, e.g FRA for France, DEU for Germany and GBR for the UK
     - | ['']
     - | stringarray()
   * - | **map_administrative_boundaries_style**
       | Line style of administrative boundaries
     - | string
     - | dash
   * - | **map_administrative_boundaries_colour**
       | Colour of administrative boundaries
     - | string
     - | automatic
   * - | **map_administrative_boundaries_thickness**
       | Line thickness of administrative boundaries
     - | int
     - | 1
   * - | **map_cities_unit_system**
       | Unit for city name sizes.
     - | ['percent', 'cm']
     - | percent
   * - | **map_cities_font**
       | Font used to display the city names.
     - | string
     - | sansserif
   * - | **map_cities_font_style**
       | Font style used for city names.
     - | string
     - | normal
   * - | **map_cities_text_blanking**
       | Use Blanking when plotting the cityes names .
     - | string
     - | on
   * - | **map_cities_font_size**
       | Font size of city names.
     - | float
     - | 2.5
   * - | **map_cities_font_colour**
       | Colour used for city names.
     - | string
     - | navy
   * - | **map_cities_name_position**
       | Position where to display the city names.
     - | ['above', 'below', 'left', 'right']
     - | above
   * - | **map_cities_marker**
       | Marker for cities.
     - | ['circle', 'box', 'snowflake', 'plus']
     - | plus
   * - | **map_cities_marker_height**
       | Height of city markers.
     - | float
     - | 0.7
   * - | **map_cities_marker_colour**
       | Colour for city markers.
     - | string
     - | evergreen
   * - | **map_coastline_resolution**
       | Select one of the pre-defined resolutions: automatic, low, medium, and high. When set to AUTOMATIC, a resolution appropriate to the scale of the map is chosen in order to balance quality with speed.
     - | ['automatic', 'low', 'medium', 'high']
     - | automatic
   * - | **map_coastline_land_shade**
       | Sets if land areas are shaded
     - | string
     - | off
   * - | **map_coastline_land_shade_colour**
       | Colour of Shading of land areas
     - | string
     - | green
   * - | **map_coastline_sea_shade**
       | Shade the sea areas
     - | string
     - | off
   * - | **map_coastline_sea_shade_colour**
       | Colour of Shading of sea areas
     - | string
     - | blue
   * - | **map_boundaries**
       | Add the political boundaries
     - | string
     - | off
   * - | **map_cities**
       | Add the cities (capitals)
     - | string
     - | off
   * - | **map_preview**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Add a preview : only for metview')])
     - | string
     - | off
   * - | **map_rivers**
       | Display rivers (on/off)
     - | ['on', 'off']
     - | off
   * - | **map_rivers_style**
       | Line style for rivers
     - | string
     - | solid
   * - | **map_rivers_colour**
       | Colour of the rivers
     - | string
     - | blue
   * - | **map_rivers_thickness**
       | Line thickness of rivers
     - | int
     - | 1
   * - | **map_efas**
       | Display rivers (on/off)
     - | ['on', 'off']
     - | off
   * - | **map_efas_domain**
       | Display EFAS Domain (on/off)
     - | ['current', 'extended']
     - | current
   * - | **map_efas_style**
       | Line style for EFAS
     - | string
     - | solid
   * - | **map_efas_colour**
       | Colour of the EFAS
     - | string
     - | blue
   * - | **map_efas_thickness**
       | Line thickness of EFAS
     - | int
     - | 1
   * - | **map_user_layer**
       | Display user shape file layer
     - | ['on', 'off']
     - | off
   * - | **map_user_layer_name**
       | Path + name of the shape file to use
     - | string
     - | 
   * - | **map_user_layer_projection**
       | Projection used in the shape file
     - | string
     - | 
   * - | **map_user_layer_style**
       | Line style for User Layer
     - | string
     - | solid
   * - | **map_user_layer_colour**
       | Colour of the User Layer
     - | string
     - | blue
   * - | **map_user_layer_thickness**
       | Line thickness of User Layer
     - | int
     - | 1
   * - | **map_coastline_colour**
       | Colour of coastlines
     - | string
     - | black
   * - | **map_coastline_style**
       | Line style of coastlines
     - | string
     - | solid
   * - | **map_coastline_thickness**
       | Line thickness of coastlines
     - | int
     - | 1
   * - | **map_coastline_general_style**
       | Use a predefined style depending on the general theme
     - | string
     - | 
   * - | **map_coastline**
       | Plot coastlines on map (ON/OFF)
     - | string
     - | on
   * - | **map_grid**
       | Plot grid lines on map (On/OFF)
     - | string
     - | on
   * - | **map_label**
       | Plot label on map grid lines (On/OFF)
     - | string
     - | on
   * - | **map_grid_latitude_reference**
       | Reference Latitude from which all latitude lines are drawn
     - | float
     - | 0
   * - | **map_grid_latitude_increment**
       | Interval between latitude grid lines
     - | float
     - | 10
   * - | **map_grid_longitude_reference**
       | Reference Longitude from which all longitude lines are drawn
     - | float
     - | 0
   * - | **map_grid_longitude_increment**
       | Interval between longitude grid lines
     - | float
     - | 20
   * - | **map_grid_line_style**
       | Line style of map grid lines
     - | string
     - | solid
   * - | **map_grid_thickness**
       | Thickness of map grid lines
     - | int
     - | 1
   * - | **map_grid_colour**
       | Colour of map grid lines
     - | string
     - | BLACK
   * - | **map_grid_frame**
       | Add a frame around the projection
     - | string
     - | off
   * - | **map_grid_frame_line_style**
       | Line style of map grid lines
     - | string
     - | solid
   * - | **map_grid_frame_thickness**
       | Thickness of map grid lines
     - | int
     - | 1
   * - | **map_grid_frame_colour**
       | Colour of map grid lines
     - | string
     - | black
   * - | **map_label_font**
       | Font of grid labels
     - | string
     - | sansserif
   * - | **map_label_font_style**
       | Font of grid labels
     - | string
     - | normal
   * - | **map_label_colour**
       | Colour of map labels
     - | string
     - | black
   * - | **map_label_height**
       | Height og grid labels
     - | float
     - | 0.25
   * - | **map_label_blanking**
       | Blanking of the grid labels
     - | string
     - | on
   * - | **map_label_latitude_frequency**
       | Evry Nth latitue grid is labelled
     - | int
     - | 1
   * - | **map_label_longitude_frequency**
       | Evry Nth longitude grid is labelled
     - | int
     - | 1
   * - | **map_label_left**
       | Enable the labels on the left of the map
     - | string
     - | on
   * - | **map_label_right**
       | Enable the labels on the right of the map
     - | string
     - | on
   * - | **map_label_top**
       | Enable the labels on the top of the map
     - | string
     - | on
   * - | **map_label_bottom**
       | Enable the labels on the bottom of the map
     - | string
     - | on


pcont
-----

.. GradientColourTechnique 

.. Akima474Method Generates contour lines from a regular/irregular grid of data points. First a denser regular grid is created based on the original grid and then the isolines are produced by applying a simple linear contouring algorithm. The user may, by calling the parameter setting routines, select the interpolation level which defines the density of the output grid, which then determines the smoothness of the isolines.

.. Akima760Method Generates contour lines from a regular/irregular grid of data points. First a denser regular grid is created based on the original grid and then the isolines are produced by applying a simple linear contouring algorithm. The user may, by calling the parameter setting routines, select the interpolation level which defines the density of the output grid, which then determines the smoothness of the isolines.

.. Akima761Method Generates contour lines from an irregularly-distributed set of points.

.. BothValuePlotMethod This object is reponsible for plotting both values and markers on grid points.

.. CalculateColourTechnique 

.. CellShading 

.. Contour This controls the plotting of isolines, contour bands and grid points.

.. ContourLibrary 

.. CountSelectionType The number of contour levels may be set by the user by setting the parameter CONTOUR_LEVEL_SELECTION_TYPE to 'COUNT' (default) and CONTOUR_LEVEL_COUNT to the number of levels to be plotted. MAGICS will then calculate the contour interval and the user's plot will consist of the number of levels specified with a regular contour interval. This is the default method and the default number of levels is 10. The exact number of contour levels plotted may not be CONTOUR_LEVEL_COUNT as PCONT will always use the value stored in CONTOUR_REFERENCE_LEVEL as a starting point and will pick reasonable values for the contour interval.

.. DotPolyShadingMethod 

.. DumpShading 

.. DumpShadingWrapper 

.. GradientsColourTechnique 

.. GridShading 

.. HatchPolyShadingMethod 

.. HiLoBoth 

.. HiLoMarker The position of a maxima/minima value may be marked by plotting a symbol on the precise location. Users may define their own symbol by setting the parameter CONTOUR_HILO_MARKER_INDEX

.. HiLoNumber This object is reponsible for plotting the HI/Lo as text.

.. HiLoText This object is reponsible for plotting the HI/Lo as text.

.. HighHiLo 

.. ImageListColourTechnique 

.. IntervalSelectionType If the parameter CONTOUR_LEVEL_SELECTION_TYPE is set to 'INTERVAL' , MAGICS will plot contours at regularly spaced intervals using the value of CONTOUR_REFERENCE_LEVEL as a base and the value in CONTOUR_INTERVAL as the interval between levels.

.. IsoHighlight This object is responsible of plotting the hightlight isolines

.. IsoLabel The action routine PCONT will plot labels on contour lines either by default or as directed by the user. Contour labels may be plotted with different attributes from the contour line, e.g. colour and thickness. Contour labels are, by default, plotted on every 2nd contour line, but this may be changed by the user, if desired.

.. IsoShading 

.. LevelListSelectionType Users may supply a list of the contour levels to be plotted by setting the parameter CONTOUR_LEVEL_SELECTION_TYPE to 'LEVEL_LIST' and passing an array of contour level values. This method enables users to plot contours with irregular intervals.

.. ListColourTechnique 

.. LowHiLo 

.. MarkerShadingTechnique 

.. MarkerValuePlotMethod 

.. NoHiLo This object suppresses Hi/Lo information.

.. NoHiLoMarker This object suppresses the plotting of Hi/Lo markers

.. NoIsoPlot 

.. NoValuePlot This object suppresses the plotting of grid values.

.. PaletteColourTechnique 

.. ValuePlot 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **contour_gradients_colour_list**
       | Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
     - | stringarray
     - | stringarray()
   * - | **contour_gradients_value_list**
       | List of stops.
     - | floatarray
     - | floatarray()
   * - | **contour_gradients_technique_list**
       | Technique to apply to compute the gradients linear-clockwise/linear-anticlockwise
     - | stringarray
     - | stringarray()
   * - | **contour_gradients_step_list**
       | Nimber of steps to compute for each interval
     - | intarray
     - | intarray()
   * - | **contour_akima_x_resolution**
       | X Resolution
     - | float
     - | 1.5
   * - | **contour_akima_y_resolution**
       | Y Resolution
     - | float
     - | 1.5
   * - | **contour_akima_x_resolution**
       | X resolution of Akima interpolation
     - | float
     - | 1.5
   * - | **contour_akima_y_resolution**
       | Y resolution of Akima interpolation
     - | float
     - | 1.5
   * - | **contour_akima_x_resolution**
       | X Resolution of the Akima output matrix
     - | float
     - | 1.5
   * - | **contour_akima_y_resolution**
       | Y Resolution of the Akima output matrix
     - | float
     - | 1.5
   * - | **contour_grid_value_min**
       | The minimum value for which grid point values are to be plotted
     - | float
     - | -1e+21
   * - | **contour_grid_value_max**
       | The maximum value for which grid point values are to be plotted
     - | float
     - | 1e+21
   * - | **contour_grid_value_lat_frequency**
       | The grid point values in every Nth latitude row are plotted
     - | int
     - | 1
   * - | **contour_grid_value_lon_frequency**
       | The grid point values in every Nth longitude column are plotted
     - | int
     - | 1
   * - | **contour_grid_value_height**
       | Height of grid point values
     - | float
     - | 0.25
   * - | **contour_grid_value_colour**
       | Colour of grid point values (Full choice of colours)
     - | string
     - | blue
   * - | **contour_grid_value_format**
       | Format of grid point values (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_grid_value_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_grid_value_justification**
       | (LEFT/CENTRE/RIGHT)
     - | string
     - | centre
   * - | **contour_grid_value_vertical_align**
       | (NORMAL/TOP/CAP/HALF/BASE/BOTTOM)
     - | ['normal', 'top', 'cap', 'half', 'base', 'bottom']
     - | base
   * - | **contour_grid_value_marker_height**
       | Height of grid point markers
     - | float
     - | 0.25
   * - | **contour_grid_value_marker_colour**
       | Colour of grid point markers (Full choice of colours)
     - | string
     - | red
   * - | **contour_grid_value_marker_qual**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_grid_value_marker_index**
       | Table number of marker index. See Appendix for Plotting Attributes
     - | int
     - | 3
   * - | **contour_grid_value_position**
       | Position of the value
     - | ['right', 'left', 'bottom', 'top']
     - | top
   * - | **contour_shade_max_level_colour**
       | Highest shading band colour
     - | string
     - | blue
   * - | **contour_shade_min_level_colour**
       | Lowest shading band colour
     - | string
     - | red
   * - | **contour_shade_colour_direction**
       | Direction of colour sequencing for shading (CLOCKWISE/ ANTI_CLOCKWISE)
     - | ['clockwise', 'anti_clockwise']
     - | anti_clockwise
   * - | **contour_shade_cell_resolution**
       | Number of cells per cm for CELL shading
     - | float
     - | 10
   * - | **contour_shade_cell_method**
       | NMethod of determining the colour of a cell (INTERPOLATE/ NEAREST)
     - | ['nearest', 'interpolate']
     - | nearest
   * - | **contour_shade_cell_resolution_method**
       | if adaptive, magics will switch to grid_shading when the data resolution is greater that the requested resolution
     - | ['classic', 'adaptive']
     - | classic
   * - | **legend**
       | Turn legend on or off
     - | string
     - | off
   * - | **contour**
       | Turn contouring on or off
     - | string
     - | on
   * - | **contour_method**
       | Contouring method
     - | string
     - | automatic
   * - | **contour_interpolation_floor**
       | Any value below this floor will be forced to the floor value. avoid the bubbles artificially created by the interpolation method
     - | float
     - | -INT_MAX
   * - | **contour_interpolation_ceiling**
       | any value above this ceiling will be forced to the ceiling value. avoid the bubbles artificially created by the interpolation method
     - | float
     - | INT_MAX
   * - | **contour_automatic_setting**
       | Turn the automatic setting of contouring attributes
     - | ['off', 'style_name', 'ecmwf']
     - | off
   * - | **contour_style_name**
       | Use of a predeined setting
     - | string
     - | 
   * - | **contour_metadata_only**
       | Only get the metadata
     - | string
     - | off
   * - | **contour_automatic_library_path**
       | Users can give their own directory to setup the automatic library of contours
     - | string
     - | 
   * - | **contour_hilo**
       | Plot local maxima/minima
     - | string
     - | off
   * - | **contour_grid_value_plot**
       | Plot Grid point values
     - | string
     - | off
   * - | **contour_predefined_setting**
       | Use of a predeined setting
     - | string
     - | 
   * - | **contour_automatic_library_path**
       | Users can give their own directory to setup the automatic library of contours
     - | string
     - | 
   * - | **contour_max_level**
       | Highest level for contours to be drawn
     - | float
     - | 1e+21
   * - | **contour_min_level**
       | Lowest level for contours to be drawn
     - | float
     - | -1e+21
   * - | **contour_shade_max_level**
       | Highest level for contours to be shaded
     - | float
     - | 1e+21
   * - | **contour_shade_min_level**
       | Lowest level for contours to be shaded
     - | float
     - | -1e+21
   * - | **contour_level_count**
       | Count or number of levels to be plotted. Magics will try to find "nice levels", this means that the number of levels could be slightly different from the asked number of levels
     - | int
     - | 10
   * - | **contour_level_tolerance**
       | Tolerance: Do not use nice levels if the number of levels is really to different [count +/- tolerance]
     - | int
     - | 2
   * - | **contour_reference_level**
       | Contour level from which contour interval is calculated
     - | float
     - | 0.0
   * - | **contour_shade_dot_size**
       | Size of dot in shading pattern
     - | float
     - | 0.02
   * - | **contour_shade_max_level_density**
       | Dots/square centimetre in highest shading band
     - | float
     - | 50.0
   * - | **contour_shade_min_level_density**
       | Dots/square centimetre in lowest shading band
     - | float
     - | 1.0
   * - | **contour_shade_cell_resolution**
       | Number of cells per cm for CELL shading
     - | float
     - | 10
   * - | **contour_shade_cell_method**
       | NMethod of determining the colour of a cell (INTERPOLATE/ NEAREST)
     - | ['nearest', 'interpolate']
     - | nearest
   * - | **contour_gradients_colour_list**
       | Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
     - | stringarray
     - | stringarray()
   * - | **contour_gradients_waypoint_method**
       | waypoints at the left, right, middle of the interval.
     - | ['both', 'ignore', 'left', 'right']
     - | both
   * - | **contour_gradients_technique**
       | Technique to apply to compute the gradients rgb/hcl/hsl
     - | ['rgb', 'hcl', 'hsl']
     - | rgb
   * - | **contour_gradients_technique_direction**
       | Technique to apply to compute the gradients clockwise/anticlockwise
     - | ['clockwise', 'anti_clockwise', 'shortest', 'longest']
     - | clockwise
   * - | **contour_gradients_step_list**
       | Number of steps to compute for each interval
     - | intarray
     - | intarray()
   * - | **contour_shade_method**
       | Method used for shading (DOT/ AREA_FILL/ HATCH)
     - | string
     - | dot
   * - | **contour_grid_shading_position**
       | Middle : the point is in the midlle of the cell, bottom_left : the point is in the bottom left corner
     - | ['middle', 'bottom_left']
     - | middle
   * - | **contour_shade_hatch_index**
       | The hatching pattern(s) to use. 0 Provides an automatic sequence of patterns, other values set a constant pattern across all contour bands.
     - | int
     - | 0
   * - | **contour_shade_hatch_thickness**
       | Thickness of hatch lines
     - | int
     - | 1
   * - | **contour_shade_hatch_density**
       | Number of hatch lines per cm.
     - | float
     - | 18.0
   * - | **contour_hilo_height**
       | Height of local maxima/minima text or numbers
     - | float
     - | 0.4
   * - | **contour_hilo_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_hi_colour**
       | Colour of local maxima text or number
     - | string
     - | blue
   * - | **contour_lo_colour**
       | Colour of local minima text or number
     - | string
     - | blue
   * - | **contour_hilo_format**
       | Format of HILO numbers (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_hilo_marker_height**
       | Height of HILO marker symbol
     - | float
     - | 0.1
   * - | **contour_hilo_marker_index**
       | Table number of marker symbol. See chapter on Plotting Attributes
     - | int
     - | 3
   * - | **contour_hilo_marker_colour**
       | Colour of grid point markers(Full choice of colours)
     - | string
     - | red
   * - | **contour_hilo_height**
       | Height of local maxima/minima text or numbers
     - | float
     - | 0.4
   * - | **contour_hilo_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_hi_colour**
       | Colour of local maxima text or number
     - | string
     - | blue
   * - | **contour_lo_colour**
       | Colour of local minima text or number
     - | string
     - | blue
   * - | **contour_hilo_format**
       | Format of HILO numbers (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_hilo_height**
       | Height of local maxima/minima text or numbers
     - | float
     - | 0.4
   * - | **contour_hilo_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_hi_colour**
       | Colour of local maxima text or number
     - | string
     - | blue
   * - | **contour_lo_colour**
       | Colour of local minima text or number
     - | string
     - | blue
   * - | **contour_hilo_format**
       | Format of HILO numbers (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_hi_text**
       | Text to represent local maxima
     - | string
     - | H
   * - | **contour_lo_text**
       | Text to represent local minima
     - | string
     - | L
   * - | **contour_hilo_blanking**
       | Blank around highs and lows (ON/OFF)
     - | string
     - | off
   * - | **contour_hilo_type**
       | Type of high/low (TEXT/NUMBER/BOTH)
     - | string
     - | text
   * - | **contour_hilo_window_size**
       | Size of the window used to calculate the Hi/Lo
     - | int
     - | 3
   * - | **contour_hilo_reduction_radius**
       | Search radius (in grid points) for reducing the number of minima
     - | float
     - | 0.0
   * - | **contour_hilo_suppress_radius**
       | Radius of HiLo search in grid points (default value is for global cylindrical map)
     - | float
     - | 15.0
   * - | **contour_hilo_max_value**
       | Local HiLo above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_hilo_min_value**
       | Local HiLo below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_hi_max_value**
       | Local HI above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_hi_min_value**
       | Local HI below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_lo_max_value**
       | Local Lo above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_lo_min_value**
       | Local Lo below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_hilo_marker**
       | Plot hilo marker (ON/OFF)
     - | string
     - | off
   * - | **image_colour_table**
       | List of colours to be used in image plotting.
     - | stringarray
     - | stringarray()
   * - | **contour_max_level**
       | Highest level for contours to be drawn
     - | float
     - | 1e+21
   * - | **contour_min_level**
       | Lowest level for contours to be drawn
     - | float
     - | -1e+21
   * - | **contour_shade_max_level**
       | Highest level for contours to be shaded
     - | float
     - | 1e+21
   * - | **contour_shade_min_level**
       | Lowest level for contours to be shaded
     - | float
     - | -1e+21
   * - | **contour_reference_level**
       | Contour level from which contour interval is calculated
     - | float
     - | 0.0
   * - | **contour_interval**
       | Interval in data units between two contour lines
     - | float
     - | 8.0
   * - | **contour_highlight_style**
       | Style of highlighting (SOLID/ DASH/ DOT/ CHAIN_DASH/ CHAIN_DOT)
     - | string
     - | solid
   * - | **contour_reference_level**
       | Contour level reference
     - | float
     - | 0.0
   * - | **contour_highlight_colour**
       | Colour of highlight line
     - | string
     - | blue
   * - | **contour_highlight_thickness**
       | Thickness of highlight line
     - | int
     - | 3
   * - | **contour_highlight_frequency**
       | Frequency of highlight line
     - | int
     - | 4
   * - | **contour_label_type**
       | Type of label (TEXT/NUMBER/BOTH)
     - | string
     - | number
   * - | **contour_label_text**
       | Text for labels
     - | string
     - | 
   * - | **contour_label_height**
       | Height of contour labels
     - | float
     - | 0.3
   * - | **contour_label_format**
       | Format of contour labels (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_label_blanking**
       | Label Blanking
     - | string
     - | on
   * - | **contour_label_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_label_font**
       | Name of the font
     - | string
     - | sansserif
   * - | **contour_label_font_style**
       | Style of the font bold/italic
     - | string
     - | normal
   * - | **contour_label_colour**
       | Colour of contour labels
     - | string
     - | contour_line_colour
   * - | **contour_label_frequency**
       | Every Nth contour line is labelled
     - | int
     - | 2
   * - | **contour_shade_technique**
       | Technique used for shading (POLYGON_SHADING/ CELL_SHADING/ MARKER)
     - | string
     - | polygon_shading
   * - | **contour_shade_max_level**
       | Maximum level for which shading is required
     - | float
     - | 1e+21
   * - | **contour_shade_min_level**
       | Minimum level for which shading is required
     - | float
     - | -1e+21
   * - | **contour_shade_colour_method**
       | Method of generating the colours of the bands in contour shading (list/calculate/advanced)
     - | string
     - | calculate
   * - | **contour_max_level**
       | Highest level for contours to be drawn
     - | float
     - | 1e+21
   * - | **contour_min_level**
       | Lowest level for contours to be drawn
     - | float
     - | -1e+21
   * - | **contour_shade_max_level**
       | Highest level for contours to be shaded
     - | float
     - | 1e+21
   * - | **contour_shade_min_level**
       | Lowest level for contours to be shaded
     - | float
     - | -1e+21
   * - | **contour_level_list**
       | List of contour levels to be plotted
     - | floatarray
     - | floatarray()
   * - | **contour_shade_colour_list**
       | List of colours to be used in contour shading.
     - | stringarray
     - | stringarray()
   * - | **contour_hilo_type**
       | Type of high/low (TEXT/NUMBER/BOTH)
     - | string
     - | text
   * - | **contour_hilo_window_size**
       | Size of the window used to calculate the Hi/Lo
     - | int
     - | 3
   * - | **contour_hilo_reduction_radius**
       | Search radius (in grid points) for reducing the number of minima
     - | float
     - | 0.0
   * - | **contour_hilo_suppress_radius**
       | Radius of HiLo search in grid points (default value is for global cylindrical map)
     - | float
     - | 15.0
   * - | **contour_hilo_max_value**
       | Local HiLo above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_hilo_min_value**
       | Local HiLo below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_hi_max_value**
       | Local HI above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_hi_min_value**
       | Local HI below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_lo_max_value**
       | Local Lo above specified value are not drawn
     - | float
     - | 1e+21
   * - | **contour_lo_min_value**
       | Local Lo below specified value are not drawn
     - | float
     - | -1e+21
   * - | **contour_hilo_marker**
       | Plot hilo marker (ON/OFF)
     - | string
     - | off
   * - | **contour_shade_colour_table**
       | Colour table to be used with MARKER shading technique
     - | stringarray
     - | stringarray()
   * - | **contour_shade_height_table**
       | Height table to be used with MARKER shading technique
     - | floatarray
     - | floatarray()
   * - | **contour_shade_marker_table_type**
       | index: using contour_shade_marker_table and definiing the markers by index, name: using contour_shade_marker_name_table and defining the symbols by their names
     - | ['index', 'marker']
     - | index
   * - | **contour_shade_marker_table**
       | Marker table to be used with MARKER shading technique
     - | intarray
     - | intarray()
   * - | **contour_shade_marker_name_table**
       | Marker name table to be used with MARKER shading technique
     - | stringarray
     - | stringarray()
   * - | **contour_grid_value_min**
       | The minimum value for which grid point values are to be plotted
     - | float
     - | -1e+21
   * - | **contour_grid_value_max**
       | The maximum value for which grid point values are to be plotted
     - | float
     - | 1e+21
   * - | **contour_grid_value_lat_frequency**
       | The grid point values in every Nth latitude row are plotted
     - | int
     - | 1
   * - | **contour_grid_value_lon_frequency**
       | The grid point values in every Nth longitude column are plotted
     - | int
     - | 1
   * - | **contour_grid_value_height**
       | Height of grid point values
     - | float
     - | 0.25
   * - | **contour_grid_value_colour**
       | Colour of grid point values (Full choice of colours)
     - | string
     - | blue
   * - | **contour_grid_value_format**
       | Format of grid point values (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **contour_grid_value_quality**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_grid_value_justification**
       | (LEFT/CENTRE/RIGHT)
     - | string
     - | centre
   * - | **contour_grid_value_vertical_align**
       | (NORMAL/TOP/CAP/HALF/BASE/BOTTOM)
     - | ['normal', 'top', 'cap', 'half', 'base', 'bottom']
     - | base
   * - | **contour_grid_value_marker_height**
       | Height of grid point markers
     - | float
     - | 0.25
   * - | **contour_grid_value_marker_colour**
       | Colour of grid point markers (Full choice of colours)
     - | string
     - | red
   * - | **contour_grid_value_marker_qual**
       | (LOW/MEDIUM/HIGH)
     - | string
     - | low
   * - | **contour_grid_value_marker_index**
       | Table number of marker index. See Appendix for Plotting Attributes
     - | int
     - | 3
   * - | **contour_special_legend**
       | Used in wrep to produce special legend such as spaghetti!
     - | string
     - | 
   * - | **contour_threads**
       | NUmber of threads used to optimise the contouring (possible 1, 4 or 9)
     - | int
     - | 4
   * - | **contour_internal_reduction_factor**
       | Internal factor for contouring
     - | float
     - | 4
   * - | **contour_internal_technique**
       | Internal technique for contouring : interpolate/nearest
     - | string
     - | interpolate
   * - | **contour_legend_text**
       | Text to be used in legend
     - | string
     - |  
   * - | **contour_line_style**
       | Style of contour line
     - | string
     - | solid
   * - | **contour_line_thickness**
       | Thickness of contour line
     - | int
     - | 1
   * - | **contour_line_colour_rainbow**
       | if On, rainbow colouring method will be used.
     - | string
     - | off
   * - | **contour_line_colour**
       | Colour of contour line
     - | string
     - | blue
   * - | **contour_line_colour_rainbow_method**
       | Method of generating the colours for isoline
     - | string
     - | calculate
   * - | **contour_line_colour_rainbow_max_level_colour**
       | Colour to be used for the max level
     - | string
     - | blue
   * - | **contour_line_colour_rainbow_min_level_colour**
       | Colour to be used for the mainlevel
     - | string
     - | red
   * - | **contour_line_colour_rainbow_direction**
       | Direction of colour sequencing for colouring
     - | ['clockwise', 'anti-clockwise']
     - | anti_clockwise
   * - | **contour_line_colour_rainbow_colour_list**
       | List of colours to be used in rainbow isolines
     - | stringarray
     - | stringarray()
   * - | **contour_line_colour_rainbow_colour_list_policy**
       | What to do if the list of colours is smaller that the list of contour: lastone/cycle
     - | string
     - | lastone
   * - | **contour_line_thickness_rainbow_list**
       | List of thickness to used when rainbow method is on
     - | intarray
     - | intarray()
   * - | **contour_line_thickness_rainbow_list_policy**
       | What to do if the list of thickness is smaller that the list of contour: lastone/cycle
     - | string
     - | lastone
   * - | **contour_line_style_rainbow_list**
       | List of line style to used when rainbow method is on
     - | stringarray
     - | stringarray()
   * - | **contour_line_style_rainbow_list_policy**
       | What to do if the list of line styles is smaller that the list of contour: lastone/cycle
     - | string
     - | lastone
   * - | **contour_highlight**
       | Plot contour highlights (ON/OFF)
     - | string
     - | on
   * - | **contour_level_selection_type**
       | count: calculate a reasonable contour interval taking into account the min/max and the requested number of isolines. interval: regularly spaced intervals using the reference_level as base. level_list: uses the given list of levels.
     - | string
     - | count
   * - | **contour_label**
       | Plot labels on contour lines
     - | string
     - | on
   * - | **contour_shade**
       | Turn shading on
     - | string
     - | off
   * - | **contour_legend_only**
       | Inform the contour object do generate only the legend and not the plot!
     - | string
     - | off
   * - | **contour_shade_palette_name**
       | Colour used at the stops : the gradeint will be calculated between 2 consecutive ones.
     - | string
     - | 
   * - | **contour_shade_palette_policy**
       | What to do if the list of colours is smaller that the list of levels: lastone/cycle
     - | string
     - | lastone
   * - | **contour_grid_value_type**
       | For Gaussian fields, plot normal (regular) values or reduced grid values. (NORMAL/REDUCED/akima). If akima, the akima grid values will be plotted
     - | ['normal', 'reduced', 'akima']
     - | normal
   * - | **contour_grid_value_plot_type**
       | (VALUE/MARKER/BOTH)
     - | string
     - | value


pefigram
--------

.. EfigramDecoder The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **efi_root_database**
       | database to access
     - | string
     - | 
   * - | **efi_legend_root_database**
       | legend
     - | string
     - | 
   * - | **efi_clim_root_database**
       | climatalogy database
     - | string
     - | 
   * - | **efi_dates**
       | date to select In date format (YYYYMMDDHHHH)
     - | stringarray
     - | stringarray()
   * - | **efi_clim_parameter**
       | date to select for the clim In date format (YYYYMMDDHHHH)
     - | string
     - | 
   * - | **efi_clim_date**
       | date to select for the clim In date format (YYYYMMDDHHHH)
     - | string
     - | 
   * - | **efi_clim_step**
       | date to select for the clim In date format (YYYYMMDDHHHH)
     - | int
     - | 36
   * - | **efi_steps**
       | steps to extract ( legend will use step+12)
     - | intarray
     - | intarray()
   * - | **efi_parameter**
       | epsgram latitude column name
     - | string
     - | 
   * - | **efi_long_title**
       | efigram long title ( Point Position ... General title!)
     - | string
     - | off
   * - | **efi_title**
       | epsgram title ( parameter name)
     - | string
     - | off
   * - | **efi_latitude**
       | epsgram latitude column name
     - | float
     - | 0
   * - | **efi_longitude**
       | epsgram longitude column name
     - | float
     - | 0
   * - | **efi_legend**
       | legend
     - | string
     - | on
   * - | **efi_legend_colour_list**
       | legend box colour list
     - | stringarray
     - | stringarray()
   * - | **efi_legend_box_type**
       | both/negative/positive
     - | string
     - | both
   * - | **efi_legend_normal_colour**
       | legend colour box
     - | string
     - | black
   * - | **efi_legend_normal_thickness**
       | legend colour box
     - | int
     - | 4


pemagram
--------

.. Emagram 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **x_min**
       | 
     - | float
     - | 0
   * - | **subpage_x_automatic**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | 
     - | string
     - | off
   * - | **x_max**
       | 
     - | float
     - | 100
   * - | **y_min**
       | 
     - | float
     - | 0
   * - | **y_max**
       | 
     - | float
     - | 100
   * - | **thermo_annotation_width**
       | Percentage of the width used to display the annotation on the right side .
     - | float
     - | 25


peps
----

.. CapeBox The Epsgraph is repsonsible for plotting the espgram using box and whisker visualisation

.. EpsCloud The EpsCloud is repsonsible for plotting the espgram using Cloud rose visualisation

.. EpsGraph The Epsgraph is repsonsible for plotting the espgram using box and whisker visualisation

.. EpsWave The Epsgraph is repsonsible for plotting the espgram using wind rose visualisation

.. EpsWind The Epsgraph is repsonsible for plotting the espgram using wind rose visualisation

.. EpsgramDecoder The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **cape_control_colour**
       | 
     - | string
     - | red
   * - | **cape_hres_colour**
       | 
     - | string
     - | blue
   * - | **cape_box_colour**
       | 
     - | string
     - | black
   * - | **cape_box_border_colour**
       | 
     - | string
     - | black
   * - | **cape_box_border_thickness**
       | 
     - | float
     - | 2
   * - | **cape_marker_index**
       | 
     - | int
     - | 15
   * - | **cape_marker_height**
       | 
     - | float
     - | 0.5
   * - | **cape_marker_colour**
       | 
     - | string
     - | black
   * - | **cape_box_line_style**
       | 
     - | string
     - | solid
   * - | **cape_box_thickness**
       | 
     - | float
     - | 1
   * - | **cape_box_width**
       | 
     - | float
     - | 1
   * - | **cape_text_font_size**
       | 
     - | float
     - | 0.5
   * - | **cape_text_font_colour**
       | 
     - | string
     - | black
   * - | **eps_rose_cloud_colour**
       | Rose wind darker colour
     - | string
     - | black
   * - | **eps_rose_cloud_border_colour**
       | Rose wind border colour
     - | string
     - | none
   * - | **eps_font**
       | 
     - | string
     - | sansserif
   * - | **eps_font_size**
       | 
     - | float
     - | 0.25
   * - | **eps_font_style**
       | 
     - | string
     - | 
   * - | **eps_font_colour**
       | 
     - | string
     - | blue
   * - | **eps_box_colour**
       | 
     - | string
     - | cyan
   * - | **eps_box_shift**
       | 
     - | int
     - | 0
   * - | **eps_box_quantiles_colour**
       | if set, the list of colours will be used as follow colour1 between 10-25, colour2 between 25-75, colour3 between 75-90
     - | stringarray
     - | stringarray()
   * - | **eps_right_box_colour**
       | 
     - | string
     - | red
   * - | **eps_left_box_colour**
       | 
     - | string
     - | blue
   * - | **eps_box_border_colour**
       | 
     - | string
     - | black
   * - | **eps_box_border_thickness**
       | 
     - | int
     - | 3
   * - | **eps_box_median_thickness**
       | 
     - | int
     - | 3
   * - | **eps_box_median_colour**
       | 
     - | string
     - | black
   * - | **eps_maximum**
       | 
     - | float
     - | INT_MAX
   * - | **eps_maximum_font**
       | 
     - | string
     - | sansserif
   * - | **eps_maximum_font_style**
       | 
     - | string
     - | normal
   * - | **eps_maximum_font_size**
       | 
     - | float
     - | 0.25
   * - | **eps_maximum_font_colour**
       | 
     - | string
     - | red
   * - | **eps_box_width**
       | 
     - | float
     - | -1
   * - | **eps_whisker**
       | 
     - | string
     - | on
   * - | **eps_legend_resolution**
       | 
     - | string
     - | truncature
   * - | **eps_legend_control_text**
       | 
     - | string
     - | 
   * - | **eps_legend_font_size**
       | 
     - | float
     - | 0.3
   * - | **eps_legend_forecast_text**
       | 
     - | string
     - | 
   * - | **eps_deterministic**
       | plot the deterministic Forecast
     - | string
     - | on
   * - | **eps_deterministic_line_colour**
       | Colour of deterministic Forecast
     - | string
     - | blue
   * - | **eps_deterministic_line_style**
       | line style of deterministic Forecast
     - | string
     - | solid
   * - | **eps_deterministic_line_thickness**
       | line style of deterministic Forecast
     - | int
     - | 2
   * - | **eps_deterministic_legend_text**
       | Text to be used in the legend
     - | string
     - | High Resolution
   * - | **eps_control**
       | plot the deterministic Forecast
     - | string
     - | on
   * - | **eps_control_line_colour**
       | Colour of deterministic Forecast
     - | string
     - | red
   * - | **eps_control_line_style**
       | Control of deterministic Forecast
     - | string
     - | dash
   * - | **eps_control_line_thickness**
       | line style of deterministic Forecast
     - | int
     - | 2
   * - | **eps_control_legend_text**
       | Text to be used in the legend
     - | string
     - | ENS Control
   * - | **legend**
       | 
     - | string
     - | on
   * - | **eps_grey_legend**
       | 
     - | string
     - | on
   * - | **eps_rose_wave_colour**
       | Rose wind darker colour
     - | stringarray
     - | stringarray()
   * - | **eps_rose_wind_colour**
       | Rose wind darker colour
     - | string
     - | grey
   * - | **eps_rose_wind_border_colour**
       | Rose wind border colour
     - | string
     - | grey
   * - | **eps_rose_wind_convention**
       | Define the convention to use to plot the wind direction [ meteorological : Direction the parameter is coming from, oceanographic : Direction the parameter is goint to]
     - | string
     - | meteorological
   * - | **legend**
       | turn the legend (on/off)
     - | string
     - | on
   * - | **eps_title**
       | text block to be plotted
     - | stringarray
     - | stringarray()
   * - | **eps_type**
       | Eps Metgram type : eps10 or eps15
     - | string
     - | eps10
   * - | **eps_database**
       | Epsgram Database Path
     - | string
     - | /vol/epsgram/data/spotbase/epsdb
   * - | **eps_title_text**
       | Epsgram Parameter
     - | string
     - | EPS Meteogram
   * - | **eps_parameter**
       | Epsgram Parameter
     - | string
     - | 
   * - | **eps_parameter_title**
       | epsgram parameter title : used only in case of an unknow parameter
     - | string
     - | 
   * - | **eps_latitude**
       | epsgram latitude column name
     - | float
     - | 0
   * - | **eps_longitude**
       | epsgram longitude column name
     - | float
     - | 0
   * - | **eps_parameter_hour_shift**
       | valid date is shifted ( temporary..)
     - | float
     - | 0
   * - | **eps_parameter_scaling_factor**
       | Scaling factor to apply to the values
     - | float
     - | 1
   * - | **eps_parameter_offset_factor**
       | Scaling factor to apply to the values
     - | float
     - | 0
   * - | **eps_date**
       | epsgram longitude column name
     - | string
     - | -1
   * - | **eps_time**
       | epsgram date
     - | string
     - | 0
   * - | **eps_long_title**
       | epsgram long title
     - | string
     - | off
   * - | **eps_long_title_station**
       | epsgram long title : add the station name
     - | string
     - | on
   * - | **eps_long_title_height**
       | epsgram long title: add the station height
     - | string
     - | on
   * - | **eps_long_title_point**
       | epsgram long title: add the grid point position
     - | string
     - | on
   * - | **eps_station_name**
       | epsgram long title
     - | string
     - | 
   * - | **eps_station_height**
       | epsgram long title
     - | float
     - | INT_MAX
   * - | **eps_temperature_correction**
       | Temperature correction
     - | string
     - | yes
   * - | **eps_y_axis_percentile**
       | Temperature correction
     - | float
     - | 1
   * - | **eps_y_axis_threshold**
       | Temperature correction
     - | float
     - | 50


pgeo
----

.. GeoPointsDecoder 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **geo_input_file_name**
       | The name of the input file containing the GeoPoints code field(s)
     - | string
     - | 
   * - | **geo_missing_value**
       | missing value for geopoints
     - | float
     - | 3e+38


pgeojson
--------

.. GeoJSon 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **geojson_input_type**
       | data are in a file ( file ) or passed as a string (string)
     - | ['string', 'file']
     - | file
   * - | **geojson_input_filename**
       | Path to the file containing the GeoJson data
     - | string
     - | 
   * - | **geojson_input**
       | String containing the GeoJson data
     - | string
     - | {}
   * - | **geojson_binning_grid_resolution**
       | String containing the GeoJson data
     - | float
     - | 1.0


pgrib
-----

.. DateGribLoopStep Sets the parameters related to looping on dates in a GRIB loop.

.. GribDecoder Responsible for reading and interpolating GRIB data.

.. GribLoop The purpose of the GRIB loop is to easily create an animation. This feature is only available in MagML.

.. ParamGribLoopStep None

.. SDWindMode 

.. TileDecoder Responsible for reading and interpolating GRIB data.

.. UVWindMode 

.. VDWindMode 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **grib_loop_step_span**
       | Time interval
     - | float
     - | 3
   * - | **grib_file_address_mode**
       | Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
     - | string
     - | record
   * - | **grib_input_file_name**
       | The name of the input file containing the GRIB code field(s)
     - | string
     - | 
   * - | **grib_id**
       | Id used to identify a grib file in the title production
     - | string
     - | 
   * - | **grib_loop**
       | we can loop
     - | string
     - | off
   * - | **grib_automatic_scaling**
       | Scaling of the decoded field
     - | string
     - | on
   * - | **grib_automatic_derived_scaling**
       | Scaling of the decoded derived field. A field is considered derived if the GRIB_API key generatingProcessIdentifier is 254.
     - | string
     - | off
   * - | **grib_scaling_factor**
       | Apply a scaling factor to the field.
     - | float
     - | 1
   * - | **grib_scaling_offset**
       | Apply a scaling offset to the field.
     - | float
     - | 0
   * - | **grib_interpolation_regular_resolution**
       | Space View : Resolution of the regular Matrix
     - | float
     - | 0.1
   * - | **grib_interpolation_method**
       | Used for reduced gaussian grid: use an linear interpolation to convert from reduced to regular
     - | ['interpolate', 'nearest', 'nearest_valid']
     - | interpolate
   * - | **grib_interpolation_method_missing_fill_count**
       | Number of missing values to fill with the nearest valid value
     - | int
     - | 1
   * - | **grib_text_experiment**
       | Include the name or number of the experiment, used to generate the GRIB code field, in the automatic text (ON/OFF)
     - | string
     - | off
   * - | **grib_text_units**
       | Include the units of the input field in the automatic text
     - | string
     - | off
   * - | **grib_file_address_mode**
       | Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
     - | string
     - | record
   * - | **grib_wind_mode**
       | The incoming wind field may contain data other than wind components, e.g. wave height and direction. grib_wind_mode should be set to indicate how to interpret the incoming wind field, as u/v components, or speed/direction (uv/vd).
     - | string
     - | uv
   * - | **grib_field_position**
       | The position in the input file of a field other than a wind component
     - | int
     - | 1
   * - | **grib_wind_position_1**
       | The position in the input file of a wind component field
     - | int
     - | 1
   * - | **grib_wind_position_2**
       | The position in the input file of a wind component field
     - | int
     - | 2
   * - | **grib_wind_position_colour**
       | The position in the input file of a wind component field used to colour the flag
     - | int
     - | 3
   * - | **grib_missing_value_indicator**
       | When MAGICS is decoding GRIB code, this is the value to be assigned to field values where data is missing, as indicated by the bit map in the GRIB file.
     - | float
     - | -1.5e+21
   * - | **grib_file_address_mode**
       | Normally GRIB fields are stored as records on a file. If the BYTE offset method is being used, the parameter GRIB_FILE_ADDRESS_MODE should be set to 'BYTE_OFFSET'.(RECORD_NUMBER/BYTE_OFFSET)
     - | string
     - | record
   * - | **grib_dimension**
       | Metview:dimension of the input : 1 for field, 2 for wind
     - | intarray
     - | intarray()
   * - | **grib_position_1**
       | Metview:position of the fields for x component in the fieldset
     - | longintarray
     - | longintarray()
   * - | **grib_position_2**
       | Metview:position of the fields for y component in the fieldset
     - | longintarray
     - | longintarray()
   * - | **grib_position_colour**
       | Metview:position of the fields for colour component in the fieldset
     - | longintarray
     - | longintarray()
   * - | **grib_position**
       | Metview:position of the fields to plot in the fieldset
     - | longintarray
     - | longintarray()
   * - | **grib_loop_path**
       | Path of the grib to animate
     - | string
     - | 
   * - | **grib_loop_step**
       | Method to create the steps names for each plot of the animation
     - | string
     - | loopondate
   * - | **grib_automatic_scaling**
       | Scaling of the decoded field (ON/OFF)
     - | string
     - | on
   * - | **grib_automatic_derived_scaling**
       | Scaling of the decoded derived field (ON/OFF). A field is considered derived if the GRIB_API key generatingProcessIdentifier is 254.
     - | string
     - | off
   * - | **grib_scaling_factor**
       | Apply a scaling factor to the field.
     - | float
     - | 1
   * - | **grib_scaling_offset**
       | Apply a scaling offset to the field.
     - | float
     - | 0
   * - | **grib_interpolation_regular_resolution**
       | Space View : Resolution of the regular Matrix
     - | float
     - | 0.1
   * - | **grib_interpolation_method**
       | Used for reduced gaussian grid: use an linear interpolation to convert from reduced to regular
     - | ['interpolate', 'nearest', 'nearest_valid']
     - | interpolate
   * - | **grib_interpolation_method_missing_fill_count**
       | Number of missing values to fill with the nearest valid value
     - | int
     - | 1
   * - | **grib_wind_mode**
       | The incoming wind field may contain data other than wind components, e.g. wave height and direction. grib_wind_mode should be set to indicate how to interpret the incoming wind field, as u/v components, or speed/direction (uv/vd).
     - | string
     - | uv
   * - | **grib_input_file_name**
       | The name of the input file containing the GRIB code field(s)
     - | string
     - | 
   * - | **grib_tile_projection**
       | 
     - | string
     - | cylindrical
   * - | **grib_loop**
       | 
     - | string
     - | off
   * - | **grib_tile_z**
       | 
     - | int
     - | 1
   * - | **grib_tile_x**
       | 
     - | int
     - | 0
   * - | **grib_tile_y**
       | 
     - | int
     - | 0
   * - | **grib_automatic_scaling**
       | Scaling of the decoded field
     - | string
     - | on
   * - | **grib_scaling_factor**
       | Apply a scaling factor to the field.
     - | float
     - | 1
   * - | **grib_scaling_offset**
       | Apply a scaling offset to the field.
     - | float
     - | 0


pimage
------

.. ImageCalculateColourTechnique 

.. ImagePlotting Here comes the documentation of the ImagePlotting object

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **image_max_level_colour**
       | Highest image band colour
     - | string
     - | blue
   * - | **image_min_level_colour**
       | Lowest image band colour
     - | string
     - | red
   * - | **image_colour_direction**
       | Direction of colour sequencing for image (CLOCKWISE / ANTI_CLOCKWISE)
     - | string
     - | anti_clockwise
   * - | **image_colour_table_creation_mode**
       | Method for computing the output image according to the Colour table.
     - | string
     - | equidistant
   * - | **image_colour_table_type**
       | Method for setting Colour table for imaging.
     - | string
     - | computed
   * - | **image_level_count**
       | Number of levels
     - | int
     - | 127
   * - | **image_pixel_selection_frequency**
       | Number of pixels/centimetre to be plotted
     - | int
     - | 10


pimport
-------

.. ImportAction Import facilities allow users to import external graphics files (jpeg/gif/eps)

.. ImportObjectHandler 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **import_file_name**
       | File to import
     - | string
     - | 
   * - | **import_valid_time**
       | Valid Time
     - | string
     - | 
   * - | **service**
       | Metview info : which service created this image
     - | string
     - | 
   * - | **url**
       | Metview info : which url created this image : add it in the titles
     - | string
     - | 
   * - | **layers**
       | Metview info :Short name to be put in the layers!
     - | string
     - | 
   * - | **import_file_name**
       | File to import
     - | string
     - | 
   * - | **import_format**
       | Specify the format of the imported file
     - | ['png', 'jpeg', 'gif']
     - | png
   * - | **import_overlay**
       | if on, the import object will always be displayed last
     - | string
     - | on
   * - | **import_x_position**
       | X position of the imported image
     - | float
     - | 0
   * - | **import_y_position**
       | Y position of the imported image
     - | float
     - | 0
   * - | **import_width**
       | Width of the imported image (-1 means use the dimension of the image)
     - | float
     - | -1
   * - | **import_height**
       | Height of the imported image (-1 means use the dimension of the image)
     - | float
     - | -1


pline
-----

.. SimplePolyline 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **polyline_input_latitudes**
       | Array containing the latitudes of the polylines. Each polyline is separated by the break value
     - | floatarray
     - | floatarray()
   * - | **polyline_input_longitudes**
       | Array containing the longitudes of the polylines. Each polyline is separated by the break value
     - | floatarray
     - | floatarray()
   * - | **polyline_input_values**
       | Array containing the values for each polyline
     - | floatarray
     - | floatarray()
   * - | **polyline_input_break_indicator**
       | Value used as either a latitude or longitude to denote a separation between polylines
     - | float
     - | -999
   * - | **polyline_input_positions_filename**
       | Path to a file containing the coordinates for all polylines' points.
     - | string
     - | 
   * - | **polyline_input_values_filename**
       | Path to a file containing the values for each polyline.
     - | string
     - | 
   * - | **legend**
       | Turn the legend on
     - | string
     - | off
   * - | **polyline_line_colour**
       | Colour of the polylines
     - | string
     - | blue
   * - | **polyline_line_style**
       | Style of the polylines (SOLID/ DASH/ DOT/ CHAIN_DASH/ CHAIN_DOT)
     - | string
     - | solid
   * - | **polyline_line_thickness**
       | Thickness of the polylines
     - | int
     - | 1
   * - | **polyline_effect_method**
       | Method applied to draw the line
     - | ['classic', 'trajectory']
     - | classic
   * - | **polyline_trajectory_pivot_index**
       | Method applied to draw the line
     - | int
     - | -1
   * - | **polyline_trajectory_factor**
       | Method applied to draw the line
     - | int
     - | -1
   * - | **polyline_level_count**
       | Count or number of levels to be plotted. Magics will try to find "nice levels", this means that the number of levels could be slightly different from the requested number of levels
     - | int
     - | 10
   * - | **polyline_level_tolerance**
       | Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
     - | int
     - | 2
   * - | **polyline_reference_level**
       | Level from which the level interval is calculated
     - | float
     - | 0.0
   * - | **polyline_interval**
       | Interval in data units between different bands of shading
     - | float
     - | 8.0
   * - | **polyline_level_list**
       | List of shading band levels to be plotted
     - | floatarray
     - | floatarray()
   * - | **polyline_shade**
       | Whether to shade polygons or not (ON/OFF)
     - | string
     - | none
   * - | **polyline_shade_max_level**
       | Maximum level for which shading is required
     - | float
     - | 1e+21
   * - | **polyline_shade_min_level**
       | Minimum level for which shading is required
     - | float
     - | -1e+21
   * - | **polyline_shade_level_selection_type**
       | Can be set to one of: (COUNT/ INTERVAL/ LEVEL_LIST)
     - | string
     - | count
   * - | **polyline_shade_colour_method**
       | Method of generating the colours of the bands in polygon shading (LIST/CALCULATE)
     - | string
     - | calculate
   * - | **polyline_shade_max_level_colour**
       | Highest shading band colour
     - | string
     - | blue
   * - | **polyline_shade_min_level_colour**
       | Lowest shading band colour
     - | string
     - | red
   * - | **polyline_shade_colour_direction**
       | Direction of colour sequencing for shading (CLOCKWISE/ ANTI_CLOCKWISE)
     - | string
     - | anti_clockwise
   * - | **polyline_shade_colour_list**
       | List of colours to be used in polygon shading.
     - | stringarray
     - | stringarray()
   * - | **polyline_priority_variable_name**
       | Variable used for setting the priority of the segments
     - | string
     - | 
   * - | **polyline_colour_variable_name**
       | Data Variable used for setting the colour of the segments
     - | string
     - | 
   * - | **polyline_colour_list**
       | list of colours to use
     - | stringarray
     - | stringarray()
   * - | **polyline_colour_level_list**
       | level list to use for setting the colours
     - | floatarray
     - | floatarray()
   * - | **polyline_colour_list_policy**
       | What to do if the list of colours is smaller that the list of levels: lastone/cycle
     - | string
     - | lastone
   * - | **polyline_line_style_variable_name**
       | Data Variable used for setting the line style of the segments
     - | string
     - | 
   * - | **polyline_line_style_list**
       | list of line styles to use
     - | stringarray
     - | stringarray()
   * - | **polyline_line_style_level_list**
       | level list to use for setting the colours
     - | floatarray
     - | floatarray()
   * - | **polyline_line_style_list_policy**
       | What to do if the list of line styles is smaller that the list of levels: lastone/cycle
     - | string
     - | lastone
   * - | **polyline_thickness_variable_name**
       | Data Variable used for setting the thickness of the segments
     - | string
     - | 
   * - | **polyline_thickness_list**
       | list of thicknesses to use
     - | floatarray
     - | floatarray()
   * - | **polyline_thickness_level_list**
       | level list to use for setting the Thickness
     - | floatarray
     - | floatarray()
   * - | **polyline_thickness_list_policy**
       | What to do if the list of line styles is smaller that the list of levels: lastone/cycle
     - | string
     - | lastone
   * - | **polyline_transparency_variable_name**
       | Data Variable used for setting the transparency of the segments
     - | string
     - | 
   * - | **polyline_transparency_pivot_variable_name**
       | Data Variable used for setting the pivot used to compute the transparency of the segments
     - | string
     - | 
   * - | **polyline_pivot_marker**
       | Add a marker to the the last trajectory plotted to materialse the pivot
     - | ['all', 'none', 'lastone']
     - | none
   * - | **polyline_pivot_marker_name**
       | name of the marker to use
     - | string
     - | cyclone
   * - | **polyline_pivot_marker_height**
       | height of the marker to use
     - | float
     - | 0.4
   * - | **polyline_pivot_marker_colour**
       | Colour of the marker to use
     - | string
     - | black
   * - | **polyline_transparency_level_list**
       | level list to use for setting the Transparency
     - | floatarray
     - | floatarray()
   * - | **polyline_legend_only**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Wrep only : to build only the legend...')])
     - | string
     - | off


pmapgen
-------

.. MapGenDecoder 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **mapgen_input_file_name**
       | The name of the input file containing the MapGen data
     - | string
     - | 
   * - | **mapgen_record**
       | The name of the input file containing the MapGen data to plot
     - | int
     - | -1


pmetgram
--------

.. ClassicMtgDecoder The Classic Metgram is responsible for accessing the classic metgram database and prepare the data to plotting.

.. EfiJSon 

.. EpsBufr 

.. EpsDirection The EpsPlumeis responsible for plotting epsplume graph

.. EpsPlume The EpsPlumeis responsible for plotting epsplume graph

.. EpsShade The EpsSahde is responsible for plotting climate information as Shaded area.

.. EpsXmlInput 

.. MetgramBar The metgram curve will plot the metgram a s a curve!

.. MetgramCurve The metgram curve will plot the metgram a s a curve!

.. MetgramFlags The metgram curve will plot the metgram a s a curve!

.. MetgramGraph The Epsgram is responsible for accessing the espgram database its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **metgram_database**
       | Classic Metgram Database Path
     - | string
     - | /vol/epsgram/data/spotbase/epsdb
   * - | **metgram_parameter**
       | Classic Metgram Parameter
     - | string
     - | 
   * - | **metgram_latitude**
       | Classic Metgram latitude
     - | float
     - | 0
   * - | **metgram_parameter_scaling_factor**
       | metgram scaling factor : used only in case of an unknow parameter
     - | float
     - | 1
   * - | **metgram_parameter_offset**
       | metgram offset : used only in case of an unknow parameter
     - | float
     - | 0
   * - | **metgram_parameter_title**
       | metgram parameter title : used only in case of an unknow parameter
     - | string
     - | 
   * - | **metgram_longitude**
       | Classic Metgram longitude
     - | float
     - | 0
   * - | **metgram_date**
       | Classic Metgram date
     - | string
     - | -1
   * - | **metgram_time**
       | Classic Metgram time
     - | string
     - | 0
   * - | **metgram_long_title**
       | epsgram long title
     - | string
     - | off
   * - | **metgram_station_name**
       | epsgram long title
     - | string
     - | 
   * - | **metgram_station_height**
       | epsgram long title
     - | float
     - | -1.0
   * - | **metgram_temperature_correction**
       | Temperature correction
     - | string
     - | yes
   * - | **efijson_input_filename**
       | Path to the file containing the Efi data (JSon format)
     - | string
     - | 
   * - | **efi_long_title**
       | efigram long title ( Point Position ... General title!)
     - | string
     - | off
   * - | **efi_title**
       | epsgram title ( parameter name)
     - | string
     - | off
   * - | **efi_legend**
       | legend
     - | string
     - | on
   * - | **efi_legend_colour_list**
       | legend box colour list
     - | stringarray
     - | stringarray()
   * - | **efi_legend_box_type**
       | both/negative/positive
     - | string
     - | both
   * - | **efi_legend_normal_colour**
       | legend colour box
     - | string
     - | black
   * - | **efi_legend_normal_thickness**
       | legend colour box
     - | int
     - | 4
   * - | **epsbufr_input_filename**
       | Path to the file containing the Bufr data
     - | string
     - | 
   * - | **epsbufr_title**
       | text block to be plotted
     - | string
     - | 
   * - | **epsbufr_parameter_title**
       | Title to use to describe the parameter
     - | string
     - | 
   * - | **epsbufr_information**
       | Plot or not information about station/forecast in a long title
     - | string
     - | on
   * - | **epsbufr_short_title**
       | Plot or not information about station/forecast in a long title
     - | string
     - | on
   * - | **epsbufr_parameter_descriptor**
       | Descriptor to use
     - | int
     - | 0
   * - | **epsbufr_parameter_2_descriptor**
       | Descriptor to use
     - | int
     - | 0
   * - | **epsbufr_accumulated_parameter**
       | Descriptor to use
     - | string
     - | off
   * - | **epsbufr_station_name**
       | Name of the station to use in the title
     - | string
     - | 
   * - | **epsbufr_station_latitude**
       | Latitude of the point to extract
     - | float
     - | 0
   * - | **epsbufr_station_longitude**
       | Longitude of the point to extract
     - | float
     - | 0
   * - | **epsbufr_parameter_scaling_factor**
       | Scaling factor to apply to the values
     - | float
     - | 1
   * - | **epsbufr_parameter_offset_factor**
       | Scaling factor to apply to the values
     - | float
     - | 0
   * - | **epsbufr_y_axis_percentile**
       | Temperature correction
     - | float
     - | 1
   * - | **epsbufr_y_axis_threshold**
       | Temperature correction
     - | float
     - | 50
   * - | **eps_direction_keyword**
       | keyword to plot : forecast/control!
     - | string
     - | forecast
   * - | **eps_direction_line_colour**
       | Colour of lines ...
     - | string
     - | red
   * - | **eps_direction_line_style**
       | Line Style
     - | string
     - | solid
   * - | **eps_direction_line_thickness**
       | Thickness of the line ...
     - | int
     - | 1
   * - | **eps_plume_method**
       | Type of visualisation required : time_serie or vertical_profile
     - | ['time_serie', 'vertical_profile']
     - | time_serie
   * - | **eps_plume_legend**
       | ignore legend
     - | string
     - | on
   * - | **eps_plume_members**
       | show the eps members
     - | string
     - | on
   * - | **eps_plume_line_colour**
       | Line colour of the eps members
     - | string
     - | magenta
   * - | **eps_plume_line_style**
       | Line style of the eps members
     - | string
     - | solid
   * - | **eps_plume_line_thickness**
       | Line thickness of the eps members
     - | int
     - | 1
   * - | **eps_plume_forecast**
       | show the forecast
     - | string
     - | on
   * - | **eps_plume_forecast_line_colour**
       | Line colour of the deterministic forecast
     - | string
     - | cyan
   * - | **eps_plume_forecast_line_style**
       | Line Style of the deterministic forecast
     - | string
     - | dash
   * - | **eps_plume_forecast_line_thickness**
       | Line thickness of the deterministic forecast
     - | int
     - | 5
   * - | **eps_plume_control**
       | show the forecast
     - | string
     - | on
   * - | **eps_plume_control_line_colour**
       | Line colour of the control forecast
     - | string
     - | cyan
   * - | **eps_plume_control_line_style**
       | Line Style of the control forecast
     - | string
     - | solid
   * - | **eps_plume_control_line_thickness**
       | Line thickness of the deterministic forecast
     - | int
     - | 5
   * - | **eps_plume_median**
       | show the forecast
     - | string
     - | off
   * - | **eps_plume_median_line_colour**
       | Line colour of the control forecast
     - | string
     - | cyan
   * - | **eps_plume_median_line_style**
       | Line Style of the control forecast
     - | string
     - | solid
   * - | **eps_plume_median_line_thickness**
       | Line thickness of the deterministic forecast
     - | int
     - | 5
   * - | **eps_plume_shading**
       | Turn on/off the plume shading
     - | string
     - | off
   * - | **eps_plume_shading_level_list**
       | levels used for plumes shading
     - | floatarray
     - | floatarray()
   * - | **eps_plume_shading_colour_list**
       | colours used for plumes shading
     - | stringarray
     - | stringarray()
   * - | **eps_shade_colour**
       | Colour of the darkest shade area ...
     - | string
     - | red
   * - | **eps_shade_line_colour**
       | Colour of the darkest shade area ...
     - | string
     - | red
   * - | **eps_shade_line_style**
       | Colour of the darkest shade area ...
     - | string
     - | solid
   * - | **eps_shade_line_thickness**
       | Colour of the darkest shade area ...
     - | int
     - | 1
   * - | **epsxml_input_filename**
       | Path to the file containing the Xml Description
     - | string
     - | 
   * - | **epsxml_parameter**
       | Parameter to extract
     - | string
     - | 
   * - | **epsxml_long_title**
       | epsgram long title
     - | string
     - | off
   * - | **epsxml_title**
       | epsgram long title
     - | string
     - | on
   * - | **metgram_bar_keyword**
       | keyword used for define the bars
     - | string
     - | curve1
   * - | **metgram_bar_colour**
       | Colour of the curve
     - | string
     - | blue
   * - | **metgram_curve_line_style**
       | LineStyle of the curve
     - | string
     - | solid
   * - | **metgram_curve2_line_style**
       | LineStyle of the second curve
     - | string
     - | solid
   * - | **metgram_curve_keyword**
       | keyword used for fefine the first curve
     - | string
     - | curve1
   * - | **metgram_curve_keyword2**
       | keyword used for fefine the second curve
     - | string
     - | curve2
   * - | **metgram_curve_colour**
       | Colour of the curve
     - | string
     - | red
   * - | **metgram_curve2_colour**
       | Colour of the second curve
     - | string
     - | blue
   * - | **metgram_curve_thickness**
       | Thickness of the curve
     - | int
     - | 2
   * - | **metgram_curve2_thickness**
       | Thickness of the second curve
     - | int
     - | 2
   * - | **metgram_flag_colour**
       | Colour of Flag
     - | string
     - | red
   * - | **metgram_flag_frequency**
       | Frequency to plot the flags
     - | int
     - | 1
   * - | **metgram_flag_method**
       | SD : speed/direction is given UV : U/V components
     - | string
     - | SD
   * - | **metgram_flag_component1**
       | Keyword used for the First component
     - | string
     - | curve1
   * - | **metgram_flag_component2**
       | Keyword used for the second component
     - | string
     - | curve2
   * - | **metgram_flag_length**
       | length of the flag
     - | float
     - | 0.5
   * - | **metgram_plot_style**
       | Type of plot
     - | string
     - | curve


pnetcdf
-------

.. NetcdfDecoder This handles the decoding of NetCDF Files.

.. NetcdfGeoMatrixInterpretor 

.. NetcdfGeoPolarMatrixInterpretor 

.. NetcdfGeoVectorInterpretor 

.. NetcdfGeopointsInterpretor 

.. NetcdfGuessInterpretor 

.. NetcdfMatrixInterpretor 

.. NetcdfOrcaInterpretor 

.. NetcdfVectorInterpretor 

.. NetcdfXYpointsInterpretor 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **netcdf_type**
       | Type of data arrangement in the file (possible values: matrix)
     - | string
     - | guess
   * - | **netcdf_metadata**
       | Json string containing metadata information: useful to choose a style
     - | string
     - | {}
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude
   * - | **netcdf_filename**
       | Path of the file to be read
     - | string
     - | 
   * - | **netcdf_dimension_setting**
       | Extract only of a subset of variables [ex: level:100:500]
     - | stringarray
     - | stringarray()
   * - | **netcdf_time_variable**
       | Name of the time variable
     - | string
     - | time
   * - | **netcdf_level_variable**
       | Name of the level variable
     - | string
     - | level
   * - | **netcdf_number_variable**
       | Name of the number variable
     - | string
     - | number
   * - | **netcdf_time_dimension_setting**
       | Extract only the specified times : date specified in Human readable format YYYY-MM-DD HH:MM:00
     - | string
     - | 
   * - | **netcdf_level_dimension_setting**
       | Extract only the specified level
     - | string
     - | 
   * - | **netcdf_number_dimension_setting**
       | Extract only the specified number
     - | string
     - | 
   * - | **netcdf_dimension_setting_method**
       | Method used to specify how to interpret the extraction of a subset, the range can by specified by value or by index
     - | ['index', 'value']
     - | value
   * - | **netcdf_latitude_variable**
       | Variable name representing the latitude dimension
     - | string
     - | latitude
   * - | **netcdf_longitude_variable**
       | Variable name representing the longitude dimension
     - | string
     - | longitude
   * - | **netcdf_speed_component_variable**
       | Variable name representing the speed component of the vector
     - | string
     - | 
   * - | **netcdf_direction_component_variable**
       | Variable name representing the direction component of the vector
     - | string
     - | 
   * - | **netcdf_value_variable**
       | Variable to plot
     - | string
     - | 
   * - | **netcdf_x_component_variable**
       | x_component for vector plotting
     - | string
     - | 
   * - | **netcdf_y_component_variable**
       | y_component for vector plotting
     - | string
     - | 
   * - | **netcdf_colour_component_variable**
       | Variable name representing the colour component of the vector ( in case of coloured wind)
     - | string
     - | 
   * - | **netcdf_field_automatic_scaling**
       | Apply an automatic scaling, if needed
     - | string
     - | on
   * - | **netcdf_field_scaling_factor**
       | Scaling factor to multiply the field value by
     - | float
     - | 1
   * - | **netcdf_field_add_offset**
       | Offset added to the field values
     - | float
     - | 0
   * - | **netcdf_missing_attribute**
       | Attribute indicating the value used to indicate a missing value in the data
     - | string
     - | _FillValue
   * - | **netcdf_reference_date**
       | attribute indicating the reference date
     - | string
     - | 0
   * - | **netcdf_field_suppress_below**
       | Values in the input field(s) below this value are to be suppressed, i.e. not to be taken into consideration for plotting purposes
     - | float
     - | -1e+21
   * - | **netcdf_field_suppress_above**
       | Values in the input field(s) above this value are to be suppressed, i.e not to be taken into consideration for plotting purposes
     - | float
     - | 1e+21
   * - | **netcdf_x_variable**
       | Variable name for the x values
     - | string
     - | x
   * - | **netcdf_x2_variable**
       | Variable name for the auxiliary x values (used in CurveArea)
     - | string
     - | x2
   * - | **netcdf_y_variable**
       | Variable name for the y values
     - | string
     - | y
   * - | **netcdf_y2_variable**
       | Variable name for the auxiliary y values (used in CurveArea)
     - | string
     - | y2
   * - | **netcdf_x_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_x_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_geoline_convention**
       | Geoline Convention used lonlat or latlon
     - | string
     - | lonlat
   * - | **netcdf_y_auxiliary_variable**
       | variable can used to define geoline definition.
     - | string
     - | 
   * - | **netcdf_matrix_primary_index**
       | Primary index latitude/longitude
     - | string
     - | longitude


pnew
----

.. CartesianTransformation 

.. FortranRootSceneNode 

.. FortranSceneNode 

.. FortranViewNode 

.. MagicsGlobal 

.. MvRootSceneNode 

.. XDateCoordinate 

.. XHyperCoordinate 

.. XLogarithmicCoordinate 

.. XRegularCoordinate 

.. YDateCoordinate 

.. YHyperCoordinate 

.. YLogarithmicCoordinate 

.. YRegularCoordinate 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **subpage_x_axis_type**
       | 
     - | string
     - | regular
   * - | **subpage_y_axis_type**
       | 
     - | string
     - | regular
   * - | **super_page_x_length**
       | Horizontal length of super page
     - | float
     - | 29.7
   * - | **super_page_y_length**
       | Vertical length of super page
     - | float
     - | 21.0
   * - | **super_page_frame**
       | Plot frame around super page (ON/OFF)
     - | string
     - | off
   * - | **super_page_frame_colour**
       | Colour of super page frame
     - | string
     - | blue
   * - | **super_page_theme**
       | Theme to apply to the content of the document : the default magics will ensure that no theme is applied and ensure fully backwards compatibility
     - | string
     - | cream
   * - | **super_page_frame_line_style**
       | Style of super page frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
     - | string
     - | solid
   * - | **super_page_frame_thickness**
       | Thickness of super page frame
     - | int
     - | 1
   * - | **layout**
       | Type of page layout (POSITIONAL/AUTOMATIC)
     - | string
     - | automatic
   * - | **plot_start**
       | Position of first page plotted (BOTTOM/TOP)
     - | string
     - | bottom
   * - | **plot_direction**
       | Direction of plotting (HORIZONTAL/VERTICAL)
     - | string
     - | vertical
   * - | **legend**
       | Turn on/off legend
     - | string
     - | off
   * - | **magics_silent**
       | Turn on/off legend
     - | string
     - | off
   * - | **page_x_position**
       | X-Coordinate of lower left hand corner of page.Default
     - | float
     - | 0
   * - | **page_y_position**
       | Y-Coordinate of lower left hand corner of page.Default
     - | float
     - | 0
   * - | **page_x_length**
       | Length of page in horizontal direction
     - | float
     - | 29.7
   * - | **page_y_length**
       | Length of page in vertical direction
     - | float
     - | 21
   * - | **page_frame**
       | Plot frame around page (ON/OFF)
     - | string
     - | off
   * - | **page_frame_colour**
       | Colour of page frame (Full choice of colours)
     - | string
     - | charcoal
   * - | **page_frame_line_style**
       | Style of page frame(SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
     - | string
     - | solid
   * - | **page_frame_thickness**
       | Thickness of page frame
     - | int
     - | 2
   * - | **page_id_line**
       | Plot identification line and ECMWF logo (ON/OFF)
     - | string
     - | on
   * - | **page_x_gap**
       | Gap between pages in X direction
     - | float
     - | 0.0
   * - | **page_y_gap**
       | Gap between pages in Y direction
     - | float
     - | 0.0
   * - | **layout**
       | Type of page layout (POSITIONAL/AUTOMATIC)
     - | string
     - | automatic
   * - | **plot_start**
       | Position of first page plotted (BOTTOM/TOP)
     - | string
     - | bottom
   * - | **plot_direction**
       | Direction of plotting (HORIZONTAL/VERTICAL)
     - | string
     - | vertical
   * - | **page_theme**
       | Theme to apply to the content of the page : the default is the super_page_theme
     - | string
     - | super_page_theme
   * - | **skinny_mode**
       | Turn special features skinny
     - | string
     - | off
   * - | **subpage_x_position**
       | Y-Coordinate of lower left hand corner of subpage in cm. -1 is the default: 7.5% of the parent page
     - | float
     - | -1
   * - | **subpage_y_position**
       | X-Coordinate of lower left hand corner of subpage in cm. -1 is the default: 5% of the parent page
     - | float
     - | -1
   * - | **subpage_x_length**
       | Length of subpage in horizontal direction in cm. -1 is the default: 85% of the parent page
     - | float
     - | -1
   * - | **subpage_y_length**
       | Length of subpage in vertical direction in cm. -1 is the default: 85% of the parent page
     - | float
     - | -1
   * - | **subpage_map_library_area**
       | if On, pickup a predefined geographical area
     - | string
     - | off
   * - | **subpage_map_area_name**
       | Name of the predefined area
     - | string
     - | off
   * - | **subpage_map_projection**
       | Projection to set in the drawing area
     - | string
     - | cylindrical
   * - | **subpage_y_position_internal**
       | X-Coordinate of lower left hand corner of subpage
     - | float
     - | -1
   * - | **subpage_x_position_internal**
       | Y-Coordinate of lower left hand corner of subpage
     - | float
     - | -1
   * - | **subpage_right_position**
       | X-Coordinate of lower right hand corner of subpage
     - | float
     - | -1
   * - | **subpage_y_length_internal**
       | Length of subpage in vertical direction.Default
     - | float
     - | -1
   * - | **subpage_x_length_internal**
       | Length of subpage in horizontal direction.Default
     - | float
     - | -1
   * - | **subpage_top_position**
       | Y-Coordinate of upper left hand corner of subpage
     - | float
     - | -1
   * - | **subpage_clipping**
       | Apply a clipping to the subpage to avoid any symbol, flag or arrow to go outside of the plotting area
     - | string
     - | off
   * - | **subpage_background_colour**
       | Colour of the subpage background
     - | string
     - | none
   * - | **subpage_frame**
       | Plot frame around subpage (ON/OFF)
     - | string
     - | on
   * - | **subpage_frame_colour**
       | Colour of subpage frame (Full choice of colours)
     - | string
     - | charcoal
   * - | **subpage_frame_line_style**
       | Style of subpage frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
     - | string
     - | solid
   * - | **subpage_frame_thickness**
       | Thickness of subpage frame
     - | int
     - | 2
   * - | **subpage_vertical_axis_width**
       | width of the vertical axis in cm
     - | float
     - | 1
   * - | **subpage_horizontal_axis_height**
       | height of the horizontal axis in cm
     - | float
     - | 0.5
   * - | **subpage_map_overlay_control**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Metview Only: overlay method. always: plot the fields as they come; never: never overlay; by_date/by_level: only overlay data with the same valid date/level')])
     - | string
     - | basic
   * - | **subpage_align_horizontal**
       | Used in automatic layout to setup the horizontal alignment of the drawing area in the subpage
     - | ['left', 'right']
     - | left
   * - | **subpage_align_vertical**
       | Used in automatic layout to setup the vertical alignment of the drawing area in the subpage
     - | ['bottom', 'top']
     - | bottom
   * - | **subpage_map_json_definition**
       | Metview only : store internal information about zooned area
     - | string
     - | 
   * - | **automatic_title**
       | Plot the title (ON/OFF)
     - | string
     - | off
   * - | **subpage_map_preview**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Mv4: turn on/off the generation of the infomation for the preview box')])
     - | string
     - | off
   * - | **subpage_map_magnifier**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Mv4: turn on/off the generation of the infomation for the magnifier tool')])
     - | string
     - | off
   * - | **magics_silent**
       | Turn on/off
     - | string
     - | off
   * - | **magics_backward_compatibility**
       | Turn on/off
     - | string
     - | true
   * - | **super_page_x_length**
       | Horizontal length of super page
     - | float
     - | 29.7
   * - | **super_page_y_length**
       | Vertical length of super page
     - | float
     - | 21.0
   * - | **super_page_frame**
       | Plot frame around super page (ON/OFF)
     - | string
     - | off
   * - | **super_page_frame_colour**
       | Colour of super page frame
     - | string
     - | blue
   * - | **super_page_frame_line_style**
       | Style of super page frame (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
     - | string
     - | solid
   * - | **super_page_frame_thickness**
       | Thickness of super page frame
     - | int
     - | 1
   * - | **layout**
       | Type of page layout (POSITIONAL/AUTOMATIC)
     - | string
     - | automatic
   * - | **plot_start**
       | Position of first page plotted (BOTTOM/TOP)
     - | string
     - | bottom
   * - | **plot_direction**
       | Direction of plotting (HORIZONTAL/VERTICAL)
     - | string
     - | vertical
   * - | **legend**
       | Turn on/off legend
     - | string
     - | off
   * - | **subpage_x_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_x_date_min**
       | 
     - | string
     - | 
   * - | **subpage_x_date_max**
       | 
     - | string
     - | 
   * - | **subpage_x_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_x_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_x_min_latitude**
       | 
     - | float
     - | -90
   * - | **subpage_x_max_latitude**
       | 
     - | float
     - | 90
   * - | **subpage_x_min_longitude**
       | 
     - | float
     - | -180
   * - | **subpage_x_max_longitude**
       | 
     - | float
     - | 180
   * - | **subpage_x_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_x_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_x_min**
       | 
     - | float
     - | 0
   * - | **subpage_x_max**
       | 
     - | float
     - | 100
   * - | **subpage_x_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_x_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_x_min**
       | 
     - | float
     - | 0
   * - | **subpage_x_max**
       | 
     - | float
     - | 100
   * - | **subpage_x_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_y_date_min**
       | 
     - | string
     - | 
   * - | **subpage_y_date_max**
       | 
     - | string
     - | 
   * - | **subpage_y_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_y_min_latitude**
       | 
     - | float
     - | -90
   * - | **subpage_y_max_latitude**
       | 
     - | float
     - | 90
   * - | **subpage_y_min_longitude**
       | Set Y min value
     - | float
     - | -180
   * - | **subpage_y_max_longitude**
       | Set max Lon value
     - | float
     - | 180
   * - | **subpage_y_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_y_min**
       | 
     - | float
     - | 0
   * - | **subpage_y_max**
       | 
     - | float
     - | 100
   * - | **subpage_y_automatic_reverse**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | The Min and Max are calculated from the data
     - | ['on', 'off', 'min_only', 'max_only']
     - | off
   * - | **subpage_y_min**
       | 
     - | float
     - | 0
   * - | **subpage_y_max**
       | 
     - | float
     - | 100
   * - | **subpage_y_automatic_reverse**
       | 
     - | string
     - | off


pobsjson
--------

.. ObsJSon 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **obsjson_input_filename**
       | Path to the file containing the Observation data
     - | string
     - | 
   * - | **obsjson_info_list**
       | list of values described using json format
     - | stringarray
     - | stringarray()


pobsstat
--------

.. ObsStatDecoder The Obstat decoder is responsible for decoding Obstat Ascii file.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **obsstat_filename**
       | Epsgram Database Path
     - | string
     - | 


podb
----

.. OdaGeoDecoder New odb Access (Prototype Status)

.. OdaXYDecoder New odb Access (Prototype Status)

.. OdbDecoder This is responsible for accessing the ODB and passing its data to MAGICS.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **odb_filename**
       | odb Database Path
     - | string
     - | 
   * - | **odb_latitude_variable**
       | odb Column name for the latitudes
     - | string
     - | lat
   * - | **odb_longitude_variable**
       | odb Column name for the longitudes
     - | string
     - | lon
   * - | **odb_value_variable**
       | odb Column name for the values
     - | string
     - | 
   * - | **odb_y_component_variable**
       | odb Column name for the y component of a vector
     - | string
     - | 
   * - | **odb_x_component_variable**
       | odb Column name for the x component of a vector
     - | string
     - | 
   * - | **odb_nb_rows**
       | umber of rows to be retrieved
     - | int
     - | -1
   * - | **odb_user_title**
       | User defined title for automatic title
     - | string
     - | 
   * - | **odb_coordinates_unit**
       | Coordinates unit used to define the location of the points (degrees/radians)
     - | string
     - | degrees
   * - | **odb_binning**
       | Information for the binning (degrees/radians)
     - | string
     - | off
   * - | **odb_filename**
       | odb Database Path
     - | string
     - | 
   * - | **odb_x_variable**
       | odb Column name for the x coordinates
     - | string
     - | lat
   * - | **odb_y_variable**
       | odb Column name for the y coordinates
     - | string
     - | lon
   * - | **odb_value_variable**
       | odb Column name for the values
     - | string
     - | 
   * - | **odb_y_component_variable**
       | odb Column name for the y component of a vector
     - | string
     - | 
   * - | **odb_x_component_variable**
       | odb Column name for the x component of a vector
     - | string
     - | 
   * - | **odb_nb_rows**
       | umber of rows to be retrieved
     - | int
     - | -1
   * - | **odb_user_title**
       | User defined title for automatic title
     - | string
     - | 
   * - | **odb_binning**
       | Information for the binning (degrees/radians)
     - | string
     - | off
   * - | **odb_database**
       | Odb Database Path
     - | string
     - | 
   * - | **odb_database_option**
       | Odb Database option : clean
     - | string
     - | 
   * - | **odb_query**
       | Odb Query
     - | string
     - | 
   * - | **odb_latitude**
       | Odb latitude column name
     - | string
     - | latitude
   * - | **odb_longitude**
       | Odb longitude column name
     - | string
     - | longitude
   * - | **odb_observation**
       | Odb observation column name
     - | string
     - | obsvalue
   * - | **odb_observation_2**
       | Odb observation#2 column name (for vectors)
     - | string
     - | obsvalue
   * - | **odb_level**
       | Odb level column name
     - | string
     - | press
   * - | **odb_date**
       | Odb date column name name used to save in to geopoint format
     - | string
     - | 
   * - | **odb_time**
       | Odb time column name used to save in to geopoint format
     - | string
     - | 
   * - | **odb_x**
       | Odb column name used as X input for curve plotting
     - | string
     - | press
   * - | **odb_y**
       | Odb column name used as Y input for curve plotting
     - | string
     - | press
   * - | **odb_parameters**
       | enable to bind a float value to a odb parameter ($?)
     - | floatarray
     - | floatarray()
   * - | **odb_starting_row**
       | info sent to the odb server to set the starting row
     - | int
     - | 1
   * - | **odb_nb_rows**
       | info sent to the odb server to set the number of rows to be retrieved from the starting row
     - | int
     - | 1000


popen
-----

.. OutputHandler 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **output_format**
       | Defines the device to be used (ps/png/pdf/svg/kml).
     - | string
     - | ps
   * - | **output_formats**
       | Defines the list of devices to be used (ps/png/pdf/svg/kml).
     - | stringarray
     - | stringarray()


popen/pnew
----------

.. AutomaticPlotManager Object used to handle the call to the Pseudo action routine PNEW

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **plot_start**
       | Position of first page plotted (BOTTOM/TOP)
     - | string
     - | bottom
   * - | **plot_direction**
       | Direction of plotting (HORIZONTAL/VERTICAL)
     - | string
     - | vertical
   * - | **page_x_gap**
       | Gap between pages in X direction
     - | float
     - | 0.0cm
   * - | **page_y_gap**
       | Gap between pages in Y direction
     - | float
     - | 0.0cm


pplot
-----

.. ImportPlot 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **import_format**
       | Specify the format of the imported file
     - | string
     - | PNG
   * - | **import_system_coordinates**
       | Specify the format of the imported file
     - | string
     - | user
   * - | **import_x_position**
       | X position of the imported image
     - | float
     - | 0
   * - | **import_y_position**
       | Y position of the imported image
     - | float
     - | 0
   * - | **import_width**
       | Width of the imported image (-1 means use the dimension of the image)
     - | float
     - | -1
   * - | **crs**
       | Metview info :Crs used for the import
     - | string
     - | 
   * - | **crs_minx**
       | Metview info :Crs used for the import
     - | float
     - | -180.0
   * - | **crs_maxx**
       | Metview info :Crs used for the import
     - | float
     - | 180.0
   * - | **crs_miny**
       | Metview info :Crs used for the import
     - | float
     - | -90.0
   * - | **crs_maxy**
       | Metview info :Crs used for the import
     - | float
     - | -90.0
   * - | **import_height**
       | Height of the imported image (-1 means use the dimension of the image)
     - | float
     - | -1


projection
----------

.. MercatorProjection 

.. PolarStereographicProjection These are the attributes of the PolarStereographic projection.

.. Proj4Automatic 

.. Proj4Bonne 

.. Proj4Collignon 

.. Proj4EPSG32661 

.. Proj4EPSG32761 

.. Proj4EPSG3857 

.. Proj4EPSG4326 

.. Proj4EPSG900913 

.. Proj4Efas 

.. Proj4Geos 

.. Proj4Geose 

.. Proj4Geosw 

.. Proj4Goode 

.. Proj4Google 

.. Proj4Lambert 

.. Proj4LambertNorthAtlantic 

.. Proj4Mercator 

.. Proj4Meteosat0 

.. Proj4Meteosat145 

.. Proj4Meteosat57 

.. Proj4Mollweide 

.. Proj4PolarNorth 

.. Proj4PolarSouth 

.. Proj4Robinson 

.. Proj4TPers 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map
     - | float
     - | 180.0
   * - | **subpage_minimal_area**
       | Dimension in degrees of the minimal area to display
     - | float
     - | 0.1
   * - | **subpage_map_area_coordinate_system**
       | If set to projection, the coordinates of the bounding box are described in projection coordinates instead of the more natural lat/lon system ( this is useful in the WMS context)
     - | string
     - | users
   * - | **subpage_map_area_definition_polar**
       | Method of defining a polar stereographic map
     - | ['full', 'corners', 'centre']
     - | corners
   * - | **subpage_map_hemisphere**
       | Hemisphere required for polar stereographic map(NORTH/SOUTH)
     - | string
     - | north
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map, if map is CYLINDRICAL, MERCATOR or defined by 'CORNERS' in POLAR STEREOGRAPHIC
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Vertical longitude of polar stereographic or Aitoff map
     - | float
     - | 0.0
   * - | **subpage_map_centre_latitude**
       | Latitude of centre of polar stereographic map defined by 'CENTRE' or centre latitude of Lambert/satellite subarea projections
     - | float
     - | 90.0
   * - | **subpage_map_centre_longitude**
       | Longitude of centre of polar stereographic map defined by 'CENTRE' or centre longitude of Lambert/satellite subarea projections
     - | float
     - | 0.0
   * - | **subpage_map_scale**
       | Scale of polar stereographic or Aitoff map
     - | float
     - | 50000000.0
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon
   * - | **subpage_map_area_definition**
       | method used to define the geographical area.
     - | ['corners', 'full']
     - | full
   * - | **subpage_lower_left_latitude**
       | Latitude of lower left corner of map.
     - | float
     - | -90.0
   * - | **subpage_lower_left_longitude**
       | Longitude of lower left corner of map.
     - | float
     - | -180.0
   * - | **subpage_upper_right_latitude**
       | Latitude of upper right corner of map.
     - | float
     - | 90.0
   * - | **subpage_upper_right_longitude**
       | Longitude of upper right corner of map.
     - | float
     - | 180.0
   * - | **subpage_map_vertical_longitude**
       | Developement in progress
     - | float
     - | 0
   * - | **subpage_map_true_scale_north**
       | Developement in progress
     - | float
     - | 6
   * - | **subpage_map_true_scale_south**
       | Developement in progress
     - | float
     - | -60
   * - | **subpage_map_projection_height**
       | height (in meters) above the surface
     - | float
     - | 42164000
   * - | **subpage_map_projection_tilt**
       | angle (in degrees) away from nadir
     - | float
     - | 0
   * - | **subpage_map_projection_azimuth**
       | bearing (in degrees) from due north
     - | float
     - | 20
   * - | **subpage_map_projection_view_latitude**
       | latitude (in degrees) of the view position
     - | float
     - | 20
   * - | **subpage_map_projection_view_longitude**
       | longitude (in degrees) of the view position
     - | float
     - | -60
   * - | **subpage_map_geos_sweep**
       | the sweep angle axis of the viewing instrument
     - | float
     - | 0
   * - | **subpage_map_proj4_definition**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | 
   * - | **subpage_coordinates_system**
       | Proj4 defintion string : to be used very carefully --> possible side effect
     - | string
     - | latlon


pshape
------

.. ShapeDecoder 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **shape_input_file_name**
       | The name of the input file containing the shape data ( geography only)
     - | string
     - | 


pskewt
------

.. Skewt 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **x_min**
       | 
     - | float
     - | 0
   * - | **subpage_x_automatic**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | 
     - | string
     - | off
   * - | **x_max**
       | 
     - | float
     - | 100
   * - | **y_min**
       | 
     - | float
     - | 0
   * - | **y_max**
       | 
     - | float
     - | 100
   * - | **thermo_annotation_width**
       | Percentage of the width used to display the annotation on the right side .
     - | float
     - | 25


psymb
-----

.. SymbolPlotting This action routine (and C++object) controls the plotting of meteorological and marker symbols.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **legend**
       | Turn legend on or off (ON/OFF) : New Parameter!
     - | string
     - | off
   * - | **symbol_scaling_method**
       | Turn legend on or off (ON/OFF) : New Parameter!
     - | string
     - | off
   * - | **symbol_scaling_level_0_height**
       | Turn legend on or off (ON/OFF) : New Parameter!
     - | float
     - | 0.1
   * - | **symbol_scaling_factor**
       | Turn legend on or off (ON/OFF) : New Parameter!
     - | float
     - | 4.0
   * - | **symbol_type**
       | Defines the type of symbol plotting required
     - | ['number', 'text', 'marker', 'wind']
     - | number
   * - | **symbol_table_mode**
       | Specifies if plotting is to be in advanced, table (on) or individual mode (off). Note: The simple table mode is not recommended anymore, try to use the advanced mode instead, this should give you easier control of the plot.
     - | string
     - | OFF
   * - | **symbol_marker_mode**
       | Method to select a marker : by name, by index, by image : in that case, Magics will use an external image as marker.
     - | ['index', 'name', 'image']
     - | index
   * - | **symbol_format**
       | Format used to plot values (MAGICS Format/(AUTOMATIC))
     - | string
     - | (automatic)
   * - | **symbol_text_blanking**
       | blanking of the text
     - | string
     - | off
   * - | **symbol_outline**
       | Add an outline to each symbol
     - | string
     - | off
   * - | **symbol_outline_colour**
       | Colour of the outline
     - | string
     - | black
   * - | **symbol_outline_thickness**
       | thickness of the outline
     - | int
     - | 1
   * - | **symbol_outline_style**
       | Line Style of outline
     - | string
     - | solid
   * - | **symbol_connect_line**
       | Connect all the symbols with a line
     - | string
     - | off
   * - | **symbol_connect_automatic_line_colour**
       | if on, will use the colour of the symbol
     - | string
     - | on
   * - | **symbol_connect_line_colour**
       | Colour of the connecting line
     - | string
     - | black
   * - | **symbol_connect_line_thickness**
       | thickness of the connecting line
     - | int
     - | 1
   * - | **symbol_connect_line_style**
       | Line Style of connecting line
     - | string
     - | solid
   * - | **symbol_legend_only**
       | Inform the contour object do generate only the legend and not the plot .. [Web sdpecific]
     - | string
     - | off


ptaylor
-------

.. TaylorGrid description of the grid

.. TaylorProjection None

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **taylor_label**
       | Label of the grid
     - | string
     - | Correlation
   * - | **taylor_label_colour**
       | Colour of the label
     - | string
     - | navy
   * - | **taylor_label_height**
       | Hieght of the label
     - | float
     - | 0.35
   * - | **taylor_primary_grid_increment**
       | Reference used of the Standard deviation plotting.
     - | float
     - | 0.5
   * - | **taylor_primary_grid_line_colour**
       | Colour used to plot the primary grid
     - | string
     - | navy
   * - | **taylor_primary_grid_line_thickness**
       | Thickness used to plot the primary grid
     - | int
     - | 1
   * - | **taylor_primary_grid_line_style**
       | Line Style used to plot the primary grid
     - | string
     - | solid
   * - | **taylor_primary_grid_reference**
       | Reference used of the Standard deviation plotting.
     - | float
     - | 0.5
   * - | **taylor_reference_line_colour**
       | Colour used to plot the primary grid
     - | string
     - | navy
   * - | **taylor_reference_line_thickness**
       | Thickness used to plot the primary grid
     - | int
     - | 2
   * - | **taylor_reference_line_style**
       | Line Style used to plot the primary grid
     - | string
     - | solid
   * - | **taylor_primary_label**
       | Turn the labels (on/off) of the primary grid
     - | string
     - | on
   * - | **taylor_primary_label_colour**
       | Colour of the labels of the primary grid
     - | string
     - | navy
   * - | **taylor_primary_label_height**
       | Height of the labels of the primary grid
     - | float
     - | 0.35
   * - | **taylor_secondary_grid**
       | turn on/off the secondaries lines for the grid.
     - | string
     - | off
   * - | **taylor_secondary_grid_reference**
       | Reference used of the Standard deviation plotting.
     - | float
     - | 0.5
   * - | **taylor_secondary_grid_increment**
       | Reference used of the Standard deviation plotting.
     - | float
     - | 0.5
   * - | **taylor_secondary_grid_line_colour**
       | Colour used to plot the primary grid
     - | string
     - | navy
   * - | **taylor_secondary_grid_line_thickness**
       | Thickness used to plot the primary grid
     - | int
     - | 1
   * - | **taylor_secondary_grid_line_style**
       | Line Style used to plot the primary grid
     - | string
     - | solid
   * - | **taylor_secondary_label**
       | Turn the labels (on/off) of the secondary grid
     - | string
     - | on
   * - | **taylor_secondary_label_colour**
       | Colour of the labels of the secondary grid
     - | string
     - | navy
   * - | **taylor_secondary_label_height**
       | Height of the labels of the secondary grid
     - | float
     - | 0.35
   * - | **taylor_standard_deviation_min**
       | Min of the Standard deviation axis.
     - | float
     - | 0
   * - | **taylor_standard_deviation_max**
       | Max of the Standard deviation axis.
     - | float
     - | 1


ptephi
------

.. EmagramGrid 

.. SkewtGrid 

.. TephiInfo 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **thermo_annotation_width**
       | Percentage of the width used to display the annotation on the right side .
     - | float
     - | 25
   * - | **thermo_isotherm_grid**
       | Plot the isotherms
     - | ['on', 'off']
     - | on
   * - | **thermo_isotherm_colour**
       | Colou of the isotherms
     - | string
     - | charcoal
   * - | **thermo_isotherm_thickness**
       | Thickness of the isotherms
     - | int
     - | 1
   * - | **thermo_isotherm_style**
       | Line Style of the isotherms
     - | string
     - | solid
   * - | **thermo_isotherm_interval**
       | interval for isotherms grid
     - | float
     - | 10
   * - | **thermo_isotherm_reference**
       | Reference of the isotherms
     - | float
     - | 0
   * - | **thermo_isotherm_reference_colour**
       | Reference of the isotherms
     - | string
     - | red
   * - | **thermo_isotherm_reference_style**
       | Reference of the isotherms
     - | string
     - | solid
   * - | **thermo_isotherm_reference_thickness**
       | Reference of the isotherms
     - | int
     - | 2
   * - | **thermo_isotherm_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_isotherm_label_font**
       | Font name used for the isotherms labels
     - | string
     - | helvetica
   * - | **thermo_isotherm_label_font_style**
       | Font Style used for the isotherms labels
     - | string
     - | normal
   * - | **thermo_isotherm_label_font_size**
       | Font Size used for the isotherms labels
     - | float
     - | 0.3
   * - | **thermo_isotherm_label_frequency**
       | Isotherm frequency for labelling
     - | int
     - | 1
   * - | **thermo_isobar_grid**
       | Plot the isobars
     - | string
     - | on
   * - | **thermo_isobar_colour**
       | Colou of the isobars
     - | string
     - | evergreen
   * - | **thermo_isobar_thickness**
       | Thickness of the isobars
     - | int
     - | 2
   * - | **thermo_isobar_style**
       | Line Style of the isobars
     - | string
     - | solid
   * - | **thermo_isobar_interval**
       | Interval between isobars
     - | float
     - | 100
   * - | **thermo_isobar_reference**
       | Line Style of the isobars
     - | float
     - | 1000
   * - | **thermo_isobar_label_colour**
       | Label Colour for the isotherms
     - | string
     - | evergreen
   * - | **thermo_isobar_label_font**
       | Font name used for the isobars labels
     - | string
     - | helvetica
   * - | **thermo_isobar_label_font_style**
       | Font Style used for the isobars labels
     - | string
     - | normal
   * - | **thermo_isobar_label_font_size**
       | Font Size used for the isobars labels
     - | float
     - | 0.3
   * - | **thermo_isobar_label_frequency**
       | isobar frequency for labelling
     - | int
     - | 1
   * - | **thermo_dry_adiabatic_grid**
       | Plot the dry_adiabatics
     - | string
     - | on
   * - | **thermo_dry_adiabatic_colour**
       | Colou of the dry_adiabatics
     - | string
     - | charcoal
   * - | **thermo_dry_adiabatic_thickness**
       | Thickness of the dry_adiabatics
     - | int
     - | 1
   * - | **thermo_dry_adiabatic_style**
       | Line Style of the dry_adiabatics
     - | string
     - | solid
   * - | **thermo_dry_adiabatic_interval**
       | Interval between 2 dry_adiabatics.
     - | float
     - | 10
   * - | **thermo_dry_adiabatic_reference**
       | Reference of the dry_adiabatics
     - | float
     - | 0
   * - | **thermo_dry_adiabatic_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_dry_adiabatic_label_font**
       | Font name used for the dry_adiabatics labels
     - | string
     - | helvetica
   * - | **thermo_dry_adiabatic_label_font_style**
       | Font Style used for the dry_adiabatics labels
     - | string
     - | normal
   * - | **thermo_dry_adiabatic_label_font_size**
       | Font Size used for the dry_adiabatics labels
     - | float
     - | 0.3
   * - | **thermo_dry_adiabatic_label_frequency**
       | frequency for dry_adiabatic labelling
     - | int
     - | 1
   * - | **thermo_saturated_adiabatic_grid**
       | Plot the saturated_adiabatics
     - | string
     - | on
   * - | **thermo_saturated_adiabatic_colour**
       | Colou of the saturated_adiabatics
     - | string
     - | charcoal
   * - | **thermo_saturated_adiabatic_thickness**
       | Thickness of the dry_adiabatics
     - | int
     - | 2
   * - | **thermo_saturated_adiabatic_style**
       | Line Style of the saturated_adiabatics
     - | string
     - | solid
   * - | **thermo_saturated_adiabatic_interval**
       | interval for saturated_adiabatics grid
     - | float
     - | 5
   * - | **thermo_saturated_adiabatic_reference**
       | Reference of the saturated_adiabatics
     - | float
     - | 0
   * - | **thermo_saturated_adiabatic_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_saturated_adiabatic_label_font**
       | Font name used for the saturated_adiabatics labels
     - | string
     - | helvetica
   * - | **thermo_saturated_adiabatic_label_font_style**
       | Font Style used for the saturated_adiabatics labels
     - | string
     - | normal
   * - | **thermo_saturated_adiabatic_label_font_size**
       | Font Size used for the saturated_adiabatics labels
     - | float
     - | 0.3
   * - | **thermo_saturated_adiabatic_label_frequency**
       | saturated_adiabatic frequency for labelling
     - | int
     - | 1
   * - | **thermo_mixing_ratio_grid**
       | Plot the mixing_ratios
     - | string
     - | on
   * - | **thermo_mixing_ratio_colour**
       | Colou of the mixing_ratios
     - | string
     - | purple
   * - | **thermo_mixing_ratio_thickness**
       | Thickness of the mixing_ratios
     - | int
     - | 1
   * - | **thermo_mixing_ratio_style**
       | Line Style of the mixing_ratios
     - | string
     - | dash
   * - | **thermo_mixing_ratio_frequency**
       | mixing_ratio frequency for grid
     - | int
     - | 1
   * - | **thermo_mixing_ratio_label_colour**
       | Label Colour for the isotherms
     - | string
     - | purple
   * - | **thermo_mixing_ratio_label_font**
       | Font name used for the mixing_ratios labels
     - | string
     - | helvetica
   * - | **thermo_mixing_ratio_label_font_style**
       | Font Style used for the mixing_ratios labels
     - | string
     - | normal
   * - | **thermo_mixing_ratio_label_font_size**
       | Font Size used for the mixing_ratios labels
     - | float
     - | 0.3
   * - | **thermo_mixing_ratio_label_frequency**
       | mixing_ratio frequency for labelling
     - | int
     - | 1
   * - | **thermo_annotation_width**
       | Percentage of the width used to display the annotation on the right side .
     - | float
     - | 25
   * - | **thermo_isotherm_grid**
       | Plot the isotherms
     - | ['on', 'off']
     - | on
   * - | **thermo_isotherm_colour**
       | Colou of the isotherms
     - | string
     - | charcoal
   * - | **thermo_isotherm_thickness**
       | Thickness of the isotherms
     - | int
     - | 1
   * - | **thermo_isotherm_style**
       | Line Style of the isotherms
     - | string
     - | solid
   * - | **thermo_isotherm_interval**
       | interval for isotherms grid
     - | float
     - | 10
   * - | **thermo_isotherm_reference**
       | Reference of the isotherms
     - | float
     - | 0
   * - | **thermo_isotherm_reference_colour**
       | Reference of the isotherms
     - | string
     - | red
   * - | **thermo_isotherm_reference_style**
       | Reference of the isotherms
     - | string
     - | solid
   * - | **thermo_isotherm_reference_thickness**
       | Reference of the isotherms
     - | int
     - | 2
   * - | **thermo_isotherm_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_isotherm_label_font**
       | Font name used for the isotherms labels
     - | string
     - | helvetica
   * - | **thermo_isotherm_label_font_style**
       | Font Style used for the isotherms labels
     - | string
     - | normal
   * - | **thermo_isotherm_label_font_size**
       | Font Size used for the isotherms labels
     - | float
     - | 0.3
   * - | **thermo_isotherm_label_frequency**
       | Isotherm frequency for labelling
     - | int
     - | 1
   * - | **thermo_isobar_grid**
       | Plot the isobars
     - | string
     - | on
   * - | **thermo_isobar_colour**
       | Colou of the isobars
     - | string
     - | evergreen
   * - | **thermo_isobar_thickness**
       | Thickness of the isobars
     - | int
     - | 2
   * - | **thermo_isobar_style**
       | Line Style of the isobars
     - | string
     - | solid
   * - | **thermo_isobar_interval**
       | Interval between isobars
     - | float
     - | 100
   * - | **thermo_isobar_reference**
       | Line Style of the isobars
     - | float
     - | 1000
   * - | **thermo_isobar_label_colour**
       | Label Colour for the isotherms
     - | string
     - | evergreen
   * - | **thermo_isobar_label_font**
       | Font name used for the isobars labels
     - | string
     - | helvetica
   * - | **thermo_isobar_label_font_style**
       | Font Style used for the isobars labels
     - | string
     - | normal
   * - | **thermo_isobar_label_font_size**
       | Font Size used for the isobars labels
     - | float
     - | 0.3
   * - | **thermo_isobar_label_frequency**
       | isobar frequency for labelling
     - | int
     - | 1
   * - | **thermo_dry_adiabatic_grid**
       | Plot the dry_adiabatics
     - | string
     - | on
   * - | **thermo_dry_adiabatic_colour**
       | Colou of the dry_adiabatics
     - | string
     - | charcoal
   * - | **thermo_dry_adiabatic_thickness**
       | Thickness of the dry_adiabatics
     - | int
     - | 1
   * - | **thermo_dry_adiabatic_style**
       | Line Style of the dry_adiabatics
     - | string
     - | solid
   * - | **thermo_dry_adiabatic_interval**
       | Interval between 2 dry_adiabatics.
     - | float
     - | 10
   * - | **thermo_dry_adiabatic_reference**
       | Reference of the dry_adiabatics
     - | float
     - | 0
   * - | **thermo_dry_adiabatic_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_dry_adiabatic_label_font**
       | Font name used for the dry_adiabatics labels
     - | string
     - | helvetica
   * - | **thermo_dry_adiabatic_label_font_style**
       | Font Style used for the dry_adiabatics labels
     - | string
     - | normal
   * - | **thermo_dry_adiabatic_label_font_size**
       | Font Size used for the dry_adiabatics labels
     - | float
     - | 0.3
   * - | **thermo_dry_adiabatic_label_frequency**
       | frequency for dry_adiabatic labelling
     - | int
     - | 1
   * - | **thermo_saturated_adiabatic_grid**
       | Plot the saturated_adiabatics
     - | string
     - | on
   * - | **thermo_saturated_adiabatic_colour**
       | Colou of the saturated_adiabatics
     - | string
     - | charcoal
   * - | **thermo_saturated_adiabatic_thickness**
       | Thickness of the dry_adiabatics
     - | int
     - | 2
   * - | **thermo_saturated_adiabatic_style**
       | Line Style of the saturated_adiabatics
     - | string
     - | solid
   * - | **thermo_saturated_adiabatic_interval**
       | interval for saturated_adiabatics grid
     - | float
     - | 5
   * - | **thermo_saturated_adiabatic_reference**
       | Reference of the saturated_adiabatics
     - | float
     - | 0
   * - | **thermo_saturated_adiabatic_label_colour**
       | Label Colour for the isotherms
     - | string
     - | charcoal
   * - | **thermo_saturated_adiabatic_label_font**
       | Font name used for the saturated_adiabatics labels
     - | string
     - | helvetica
   * - | **thermo_saturated_adiabatic_label_font_style**
       | Font Style used for the saturated_adiabatics labels
     - | string
     - | normal
   * - | **thermo_saturated_adiabatic_label_font_size**
       | Font Size used for the saturated_adiabatics labels
     - | float
     - | 0.3
   * - | **thermo_saturated_adiabatic_label_frequency**
       | saturated_adiabatic frequency for labelling
     - | int
     - | 1
   * - | **thermo_mixing_ratio_grid**
       | Plot the mixing_ratios
     - | string
     - | on
   * - | **thermo_mixing_ratio_colour**
       | Colou of the mixing_ratios
     - | string
     - | purple
   * - | **thermo_mixing_ratio_thickness**
       | Thickness of the mixing_ratios
     - | int
     - | 1
   * - | **thermo_mixing_ratio_style**
       | Line Style of the mixing_ratios
     - | string
     - | dash
   * - | **thermo_mixing_ratio_frequency**
       | mixing_ratio frequency for grid
     - | int
     - | 1
   * - | **thermo_mixing_ratio_label_colour**
       | Label Colour for the isotherms
     - | string
     - | purple
   * - | **thermo_mixing_ratio_label_font**
       | Font name used for the mixing_ratios labels
     - | string
     - | helvetica
   * - | **thermo_mixing_ratio_label_font_style**
       | Font Style used for the mixing_ratios labels
     - | string
     - | normal
   * - | **thermo_mixing_ratio_label_font_size**
       | Font Size used for the mixing_ratios labels
     - | float
     - | 0.3
   * - | **thermo_mixing_ratio_label_frequency**
       | mixing_ratio frequency for labelling
     - | int
     - | 1
   * - | **x_min**
       | 
     - | float
     - | 0
   * - | **subpage_x_automatic**
       | 
     - | string
     - | off
   * - | **subpage_y_automatic**
       | 
     - | string
     - | off
   * - | **x_max**
       | 
     - | float
     - | 100
   * - | **y_min**
       | 
     - | float
     - | 0
   * - | **y_max**
       | 
     - | float
     - | 100
   * - | **thermo_annotation_width**
       | Percentage of the width used to display the annotation on the right side .
     - | float
     - | 25


ptext
-----

.. TextVisitor None

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **text_html**
       | enable use of HTML convention
     - | string
     - | on
   * - | **text_line_count**
       | The number of lines of text to be plotted
     - | int
     - | 1
   * - | **text_line_1**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | <magics_title/>
   * - | **text_line_2**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_3**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_4**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_5**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_6**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_7**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_8**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_9**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_line_10**
       | Character string for holding lines of text (n=1,10)
     - | string
     - | 
   * - | **text_first_line**
       | The first line in the text block to be plotted
     - | int
     - | 1
   * - | **text_colour**
       | Colour of text in text block (Full choice of colours)
     - | string
     - | navy
   * - | **text_font**
       | Font name - please make sure this font is installed!
     - | string
     - | helvetica
   * - | **text_font_style**
       | Font style. Set this to an empty string in order to remove all styling.
     - | string
     - | normal
   * - | **text_font_size**
       | Font size, specified in cm.
     - | string
     - | 0.5
   * - | **text_justification**
       | How text is to be positioned in each line (LEFT/CENTRE/RIGHT)
     - | string
     - | centre
   * - | **text_orientation**
       | Orientation of the text
     - | ['horizontal', 'top_bottom', 'bottom_top']
     - | horizontal
   * - | **text_automatic**
       | How text is to be positioned in each line (LEFT/CENTRE/RIGHT)
     - | string
     - | on
   * - | **text_lines**
       | text block to be plotted
     - | stringarray
     - | stringarray()
   * - | **text_mode**
       | Whether text is to be a title or user positioned (TITLE/POSITIONAL)
     - | ['title', 'positional']
     - | title
   * - | **text_box_x_position**
       | X coordinate of lower left corner of text box (Relative to PAGE_X_POSITION)
     - | float
     - | -1
   * - | **text_box_y_position**
       | Y coordinate of lower left corner of text box (Relative to PAGE_Y_POSITION)
     - | float
     - | -1
   * - | **text_box_x_length**
       | Length of text box in X direction
     - | float
     - | -1
   * - | **text_box_y_length**
       | 
     - | float
     - | -1
   * - | **text_box_blanking**
       | All plotting in the text box previous to PTEXT call will be blanked out. Plotting after PTEXT call will not be affected. (ON/OFF)
     - | string
     - | off
   * - | **text_border**
       | Plot border around text box (ON/OFF)
     - | string
     - | off
   * - | **text_border_line_style**
       | Line style of border around text box (SOLID/DASH/DOT/CHAIN_DASH/CHAIN_DOT)
     - | string
     - | solid
   * - | **text_border_colour**
       | Colour of border around text box (Full choice of colours)
     - | string
     - | blue
   * - | **text_border_thickness**
       | Thickness of text box border
     - | int
     - | 1
   * - | **text_character_1**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_2**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_3**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_4**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_5**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_6**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_7**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_8**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_9**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_character_10**
       | 10 Magics parameters enabling users to store CHARACTER info for plotting in text lines (n=1,10)
     - | string
     - | 
   * - | **text_integer_1**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_2**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_3**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_4**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_5**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_6**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_7**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_8**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_9**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_integer_10**
       | 10 Magics parameters enabling users to store INTEGER info for plotting in text lines (n=1,10)
     - | int
     - | 0
   * - | **text_real_1**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_2**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_3**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_4**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_5**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_6**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_7**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_8**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_9**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_real_10**
       | 10 Magics parameters enabling users to store REAL information for plotting in text lines (n=1,10)
     - | float
     - | 0
   * - | **text_line_height_ratio_1**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_2**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_3**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_4**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_5**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_6**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_7**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_8**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_9**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_line_height_ratio_10**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | float
     - | 1
   * - | **text_instruction_shift_character**
       | Symbol or character for indicating that an Instruction String follows
     - | string
     - | \
   * - | **text_escape_character**
       | Symbol or character followed by 3 octal numbers
     - | string
     - | #
   * - | **text_parameter_escape_character**
       | Symbol or character for indicating that a Magics parameter follows. The Magics parameter is also terminated by the same symbol or character.
     - | string
     - | 
   * - | **text_line_height_ratios**
       | Ratio of height of text lines to text reference character height (n=1,10). See main text
     - | floatarray
     - | floatarray()
   * - | **text_line_space_ratio**
       | Ratio of space above and below each line to text reference character height. See main text
     - | float
     - | 1.5


pwind
-----

.. ArrowPlotting None

.. FlagPlotting WMO standard wind flags; represented by barbs and solid pennants

.. Streamlines Magics parameters exist to control the calculation and plotting of streamlines.

.. Wind Wind plotting facilities allow users to plot wind fields as either arrows or flags.

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **legend**
       | Add a wind legend information in the legend
     - | string
     - | off
   * - | **wind_legend_only**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Wrep only : to build only the legned...')])
     - | string
     - | off
   * - | **wind_legend_text**
       | Use your own text in the legend
     - | string
     - | vector
   * - | **wind_advanced_method**
       | Enable advanced plotting of wind (default is off for backward compatibility). The coour is selected according to the intensity of the wind (vector)
     - | ['on', 'off']
     - | off
   * - | **wind_advanced_colour_parameter**
       | if speed, the wind is coloured using the norm of the vector, If parameter, a third parameter is used.
     - | ['speed', 'parameter']
     - | speed
   * - | **wind_advanced_colour_selection_type**
       | Set selection method
     - | string
     - | count
   * - | **wind_advanced_colour_max_value**
       | Max value to plot
     - | float
     - | 1e+21
   * - | **wind_advanced_colour_min_value**
       | Min value to plot
     - | float
     - | -1e+21
   * - | **wind_advanced_colour_level_count**
       | Number of levels to be plotted. Magics will try to find "nice levels", this means that the number of levels could be slightly different
     - | int
     - | 10
   * - | **wind_advanced_colour_level_tolerance**
       | Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
     - | int
     - | 2
   * - | **wind_advanced_colour_reference_level**
       | Level from which the level interval is calculated
     - | float
     - | 0.0
   * - | **wind_advanced_colour_level_interval**
       | Interval in data units between different bands of colours
     - | float
     - | 8.0
   * - | **wind_advanced_colour_level_list**
       | List of levels to be used
     - | floatarray
     - | floatarray()
   * - | **wind_advanced_colour_table_colour_method**
       | Method of generating the colours
     - | string
     - | calculate
   * - | **wind_advanced_colour_max_level_colour**
       | Highest shading band colour
     - | string
     - | blue
   * - | **wind_advanced_colour_min_level_colour**
       | Lowest shading band colour
     - | string
     - | red
   * - | **wind_advanced_colour_direction**
       | Direction of colour sequencing for plotting
     - | ['clockwise', 'anti_clockwise']
     - | anti_clockwise
   * - | **wind_advanced_colour_list**
       | List of colours to be used in wind plotting
     - | stringarray
     - | stringarray()
   * - | **wind_advanced_colour_list_policy**
       | What to do if, the list of colours is smaller that the list of intervals: lastone/cycle
     - | string
     - | lastone
   * - | **wind_arrow_calm_indicator**
       | Plot calm indicator circle if wind speed is less than or equal to the value in WIND_ARROW_CALM_BELOW (ON / OFF)
     - | ['on', 'off']
     - | off
   * - | **wind_arrow_calm_indicator_size**
       | The radius of the circle which indicates calm
     - | float
     - | 0.3
   * - | **wind_arrow_calm_below**
       | Winds less than or equal to this value will be drawn as calm.
     - | float
     - | 0.5
   * - | **wind_arrow_colour**
       | Colour of wind arrow
     - | string
     - | blue
   * - | **wind_arrow_cross_boundary**
       | If set to 'ON', wind arrows are truncated if they cross the subpage border (ON / OFF).
     - | string
     - | on
   * - | **wind_arrow_head_shape**
       | Table number, XY, indicating shape of arrowhead X
     - | int
     - | 0
   * - | **wind_arrow_head_ratio**
       | Table number, XY, indicating style and shape of arrowhead X
     - | float
     - | 0.3
   * - | **wind_arrow_max_speed**
       | Highest value of wind speed to be plotted
     - | float
     - | 1e+21
   * - | **wind_arrow_min_speed**
       | Lowest value of wind speed to be plotted
     - | float
     - | -1e+21
   * - | **wind_arrow_origin_position**
       | The position of the wind arrow relative to the wind origin
     - | ['centre', 'tail']
     - | tail
   * - | **wind_arrow_thickness**
       | Thickness of wind arrow shaft
     - | int
     - | 1
   * - | **wind_arrow_style**
       | Controls the line style of the arrow flag shaft.
     - | string
     - | solid
   * - | **wind_arrow_unit_system**
       | Coordinates sysem used to sacle the arrow : paper -->1cm, user-->1 user unit
     - | ['paper', 'user']
     - | paper
   * - | **wind_arrow_unit_velocity**
       | Wind speed in m/s represented by a unit vector (1.0 cm or 1.0 user unit depending on the value of wind_arrow_unit_system ).
     - | float
     - | 25.0
   * - | **wind_arrow_legend_text**
       | Text to be used as units in the legend text
     - | string
     - | m/s
   * - | **wind_arrow_fixed_velocity**
       | Fixed velocity arrows (m/s).
     - | float
     - | 0.0
   * - | **legend**
       | Add a wind legend information in the legend
     - | string
     - | off
   * - | **wind_legend_only**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Wrep only : to build only the legned...')])
     - | string
     - | off
   * - | **wind_legend_text**
       | Use your own text in the legend
     - | string
     - | vector
   * - | **wind_advanced_method**
       | Enable advanced plotting of wind (default is off for backward compatibility). The coour is selected according to the intensity of the wind (vector)
     - | ['on', 'off']
     - | off
   * - | **wind_advanced_colour_parameter**
       | if speed, the wind is coloured using the norm of the vector, If parameter, a third parameter is used.
     - | ['speed', 'parameter']
     - | speed
   * - | **wind_advanced_colour_selection_type**
       | Set selection method
     - | string
     - | count
   * - | **wind_advanced_colour_max_value**
       | Max value to plot
     - | float
     - | 1e+21
   * - | **wind_advanced_colour_min_value**
       | Min value to plot
     - | float
     - | -1e+21
   * - | **wind_advanced_colour_level_count**
       | Number of levels to be plotted. Magics will try to find "nice levels", this means that the number of levels could be slightly different
     - | int
     - | 10
   * - | **wind_advanced_colour_level_tolerance**
       | Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
     - | int
     - | 2
   * - | **wind_advanced_colour_reference_level**
       | Level from which the level interval is calculated
     - | float
     - | 0.0
   * - | **wind_advanced_colour_level_interval**
       | Interval in data units between different bands of colours
     - | float
     - | 8.0
   * - | **wind_advanced_colour_level_list**
       | List of levels to be used
     - | floatarray
     - | floatarray()
   * - | **wind_advanced_colour_table_colour_method**
       | Method of generating the colours
     - | string
     - | calculate
   * - | **wind_advanced_colour_max_level_colour**
       | Highest shading band colour
     - | string
     - | blue
   * - | **wind_advanced_colour_min_level_colour**
       | Lowest shading band colour
     - | string
     - | red
   * - | **wind_advanced_colour_direction**
       | Direction of colour sequencing for plotting
     - | ['clockwise', 'anti_clockwise']
     - | anti_clockwise
   * - | **wind_advanced_colour_list**
       | List of colours to be used in wind plotting
     - | stringarray
     - | stringarray()
   * - | **wind_advanced_colour_list_policy**
       | What to do if, the list of colours is smaller that the list of intervals: lastone/cycle
     - | string
     - | lastone
   * - | **wind_flag_calm_indicator**
       | Plot calm indicator circle, if wind speed is less than 0.5 m/s (ON / OFF)
     - | ['on', 'off']
     - | on
   * - | **wind_flag_calm_indicator_size**
       | The radius of the circle which indicates calm in centimeter
     - | float
     - | 0.3
   * - | **wind_flag_calm_below**
       | Winds less than or equal to this value will be drawn as calm.
     - | float
     - | 0.5
   * - | **wind_flag_colour**
       | Colour of wind flag shaft, barbs and pennants
     - | string
     - | blue
   * - | **wind_flag_cross_boundary**
       | If set to 'ON', wind flags are truncated if they cross the subpage border (ON / OFF)
     - | string
     - | on
   * - | **wind_flag_length**
       | Physical length of wind flag shaft
     - | float
     - | 1.0
   * - | **wind_flag_max_speed**
       | Highest value of wind speed to be plotted
     - | float
     - | 1e+21
   * - | **wind_flag_min_speed**
       | Lowest value of wind speed to be plotted
     - | float
     - | -1e+21
   * - | **wind_flag_mode**
       | Controls the line style of the wind flag shaft.(NORMAL / OFF_LEVEL / OFF_TIME)
     - | string
     - | normal
   * - | **wind_flag_style**
       | Controls the line style of the wind flag shaft.
     - | string
     - | solid
   * - | **wind_flag_origin_marker**
       | Symbol for marking the exact location of the current grid point.
     - | ['circle', 'dot', 'off']
     - | circle
   * - | **wind_flag_origin_marker_size**
       | 
     - | float
     - | 0.3
   * - | **wind_flag_thickness**
       | Thickness of wind flag shaft
     - | int
     - | 1
   * - | **legend**
       | Add a wind legend information in the legend
     - | string
     - | off
   * - | **wind_legend_only**
       | OrderedDict([('for_docs', 'no'), ('#text', 'Wrep only : to build only the legned...')])
     - | string
     - | off
   * - | **wind_legend_text**
       | Use your own text in the legend
     - | string
     - | vector
   * - | **wind_advanced_method**
       | Enable advanced plotting of wind (default is off for backward compatibility). The coour is selected according to the intensity of the wind (vector)
     - | ['on', 'off']
     - | off
   * - | **wind_advanced_colour_parameter**
       | if speed, the wind is coloured using the norm of the vector, If parameter, a third parameter is used.
     - | ['speed', 'parameter']
     - | speed
   * - | **wind_advanced_colour_selection_type**
       | Set selection method
     - | string
     - | count
   * - | **wind_advanced_colour_max_value**
       | Max value to plot
     - | float
     - | 1e+21
   * - | **wind_advanced_colour_min_value**
       | Min value to plot
     - | float
     - | -1e+21
   * - | **wind_advanced_colour_level_count**
       | Number of levels to be plotted. Magics will try to find "nice levels", this means that the number of levels could be slightly different
     - | int
     - | 10
   * - | **wind_advanced_colour_level_tolerance**
       | Tolerance: Do not use "nice levels" if the number of levels is really to different [count +/- tolerance]
     - | int
     - | 2
   * - | **wind_advanced_colour_reference_level**
       | Level from which the level interval is calculated
     - | float
     - | 0.0
   * - | **wind_advanced_colour_level_interval**
       | Interval in data units between different bands of colours
     - | float
     - | 8.0
   * - | **wind_advanced_colour_level_list**
       | List of levels to be used
     - | floatarray
     - | floatarray()
   * - | **wind_advanced_colour_table_colour_method**
       | Method of generating the colours
     - | string
     - | calculate
   * - | **wind_advanced_colour_max_level_colour**
       | Highest shading band colour
     - | string
     - | blue
   * - | **wind_advanced_colour_min_level_colour**
       | Lowest shading band colour
     - | string
     - | red
   * - | **wind_advanced_colour_direction**
       | Direction of colour sequencing for plotting
     - | ['clockwise', 'anti_clockwise']
     - | anti_clockwise
   * - | **wind_advanced_colour_list**
       | List of colours to be used in wind plotting
     - | stringarray
     - | stringarray()
   * - | **wind_advanced_colour_list_policy**
       | What to do if, the list of colours is smaller that the list of intervals: lastone/cycle
     - | string
     - | lastone
   * - | **wind_streamline_min_density**
       | The minimum number of streamlines to be plotted in one square cm of the user's subpage
     - | float
     - | 1
   * - | **wind_streamline_min_speed**
       | Wind speed below which streamline plotting will be stopped
     - | float
     - | 1
   * - | **wind_streamline_thickness**
       | Thickness of streamlines
     - | int
     - | 2
   * - | **wind_streamline_colour**
       | Colour of streamlines
     - | string
     - | blue
   * - | **wind_streamline_style**
       | Line style of streamlines
     - | string
     - | solid
   * - | **wind_streamline_head_shape**
       | Table number, XY, indicating shape of arrowhead X
     - | int
     - | 1
   * - | **wind_streamline_head_ratio**
       | Table number, XY, indicating style and shape of arrowhead X
     - | float
     - | 0.2
   * - | **wind_field_type**
       | Method of wind field plotting
     - | string
     - | arrows
   * - | **wind_thinning_method**
       | Method to control the thinning: data : wind_thinning_factor will determine the frequency as before user : wind_thining_factor will determine the minimal distance in user coordinates betvween 2 winds. the default is "data" for backward compatibility.
     - | ['data', 'user']
     - | data
   * - | **wind_thinning_factor**
       | Controls the actual number of wind arrows or flags plotted. See main text for explanation. Needs to 1.0 or larger.
     - | float
     - | 2.0
   * - | **wind_thinning_debug**
       | Add Position requiered for thiniing [ Debug mode only]
     - | string
     - | off


pwrepjson
---------

.. WrepJSon 

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **wrepjson_input_filename**
       | Path to the file containing the Bufr data
     - | string
     - | 
   * - | **wrepjson_parameter_information**
       | Product information for key=parameter_info
     - | string
     - | 
   * - | **wrepjson_title**
       | Do not create automatic title
     - | string
     - | on
   * - | **wrepjson_position_information**
       | Switch on/off the position information in the title.
     - | string
     - | on
   * - | **wrepjson_product_information**
       | Product information for key=product_info
     - | string
     - | 
   * - | **wrepjson_family**
       | How to interpret the json file
     - | string
     - | eps
   * - | **wrepjson_key**
       | Forecast information to plot!
     - | string
     - | 
   * - | **wrepjson_plumes_interval**
       | plumes interval
     - | float
     - | 1
   * - | **wrepjson_information**
       | Plot or not information about station/forecast in a long title
     - | string
     - | on
   * - | **wrepjson_keyword**
       | if several eps data are put in the same json object, give the keyowrd to find them
     - | string
     - | 
   * - | **wrepjson_station_name**
       | Name of the station to use in the title
     - | string
     - | 
   * - | **wrepjson_parameter**
       | Scaling factor to apply to the values
     - | string
     - | 1
   * - | **wrepjson_parameter_scaling_factor**
       | Scaling factor to apply to the values
     - | float
     - | 1
   * - | **wrepjson_parameter_offset_factor**
       | Scaling factor to apply to the values
     - | float
     - | 0
   * - | **wrepjson_clim_parameter**
       | date to select for the clim In date format (YYYYMMDDHHHH)
     - | string
     - | 
   * - | **wrepjson_clim_step**
       | date to select for the clim In date format (YYYYMMDDHHHH)
     - | int
     - | 36
   * - | **wrepjson_steps**
       | steps to extract ( legend will use step+12)
     - | intarray
     - | intarray()
   * - | **wrepjson_y_axis_percentile**
       | use of threshold
     - | float
     - | 1
   * - | **wrepjson_y_axis_threshold**
       | use of threshold to get rid of the unlikely values
     - | float
     - | 50
   * - | **wrepjson_y_max_threshold**
       | If all the values are below the threshold, use the threshold as max value when automatic setting of y axis
     - | float
     - | INT_MAX
   * - | **wrepjson_y_percentage**
       | percentage of the range to add to compute automatic minmax of axis.
     - | float
     - | 0.01
   * - | **wrepjson_temperature_correction**
       | Temperature correction
     - | string
     - | off
   * - | **wrepjson_missing_value**
       | Missing value
     - | float
     - | -9999
   * - | **wrepjson_ignore_keys**
       | List of keys to ignore when reading onput data
     - | stringarray
     - | stringarray()
   * - | **wrepjson_profile_quantile**
       | List of keys to ignore when reading onput data
     - | string
     - | 
   * - | **wrepjson_hodograph_grid**
       | add the Grid for the hodograph!
     - | string
     - | off
   * - | **wrepjson_hodograph_tephi**
       | add the Grid for the hodograph!
     - | string
     - | off
   * - | **wrepjson_hodograph_member**
       | slecet only one member
     - | int
     - | -1


xml
---

.. EfiDataDecoder The Efi decoder is responsible for decoding EFi Ascii file.(Metops)

.. list-table::
   :header-rows: 1
   :widths: 70 20 10

   * - | Name
     - | Type
     - | Default
   * - | **efi_filename**
       | Efi file name Path
     - | string
     - | 
   * - | **efi_record**
       | Efi record ( starting at 0)
     - | int
     - | 0

