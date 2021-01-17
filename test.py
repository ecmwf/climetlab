from climetlab import dataset

P = (
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
    # "constants",
    # "geopotential" ,
    "geopotential_500",
    "potential_vorticity",
    "relative_humidity",
    "specific_humidity",
    "temperature",
    "temperature_850",
    "toa_incident_solar_radiation",
    "total_cloud_cover",
    "total_precipitation",
    "u_component_of_wind",
    "v_component_of_wind",
    "vorticity",
)

R = (1.40625, 2.8125, 5.625)
R = (5.625,)


# for p in P:
#     for r in R:
#         print(p, r)
#         ds = load_dataset("weather-bench", p, r)


print(dataset.sample_bufr_data)
print(help(dataset("weather-bench")))
