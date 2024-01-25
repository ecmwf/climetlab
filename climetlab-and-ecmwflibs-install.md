# How to run climetlab without ecmwflibs (using conda)

This workaround should address some of the issues related to ecmwflibs version not found or not installing correctly occuring during the installation of the climetlab package. 
This is how to install eccodes manually and use an environment variable to avoid installing ecmwflibs.

``` 
# install eccodes manually
conda install -c conda-forge eccodes
pip install eccodes

# install climetlab without ecmwflibs
CLIMETLAB_DO_NOT_INSTALL_ECMWFLIBS=1 pip install climetlab
```

# Limitations

Obviously installing climetlab without one of its dependencies has some impact on its features.
And installing eccodes is not enough to provide them all : more packages are bundled in ecmwflibs (other than eccodes). 
Depending on the required functinalities, there may be other missing packages to install manually.

|    Feature    | default (ecmwflibs) | With workaround above |
|:-------------:|:-------------------:|:---------------------:|
|   Read GRIB   |         ✅          |          ✅           |
|   Write GRIB  |         ✅          |          ✅           |
|   Plot GRIB   |         ✅          |          ❌           |

All CliMetLab features related to **reading (or writing) GRIB** data be supported with this workaround.  The CliMetLab features related to ploting GRIB data which are relying on the other package Magics will not be avaible. The same logic may be applied to install Magics in the environment, but this has not been tested.

# Debugging

## Check eccodes installation
``` 
import eccodes
print(eccodes.__file__)
```

## Check that climetlab can read GRIB

``` python
import climetlab as cml
url = "https://github.com/ecmwf/climetlab/raw/develop/docs/examples/test.grib"
ds=cml.load_source("url", url)
print(ds[0])
```


# Support

Issues related to this workaround should be raised at https://github.com/ecmwf/ecmwflibs/issues.
