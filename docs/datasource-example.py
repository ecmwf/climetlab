import climetlab as cml

data = cml.load_source(
    "url",
    (
        "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs"
        "/v04r00/access/csv/ibtracs.SP.list.v04r00.csv"
    ),
)

pd = data.to_pandas()
uma = pd[pd.NAME == "UMA:VELI"]
cml.plot_map(uma, style="cyclone-track")
