# Changelog

All notable changes to CliMetLab will be documented in this file.

Notice that CliMetLab is still alpha. Things will break, public API will change.

## [0.14.30]

## [0.11.1] - 2022-04-11

- Added support to python 3.10.
- Dropped support for python 3.6 (not supported by numpy anymore).

## [0.10.1] - 2022-02-17

### Changed
- When using GRIB files. ``to_xarray()`` does not remove empty coordinates anymore.
  Use ``to_xarray(xarray_open_dataset_kwargs=dict(squeeze=True))`` to revert to
  previous behaviour.

### Removed
- ``DateListNormaliser`` has been removed. The same functionality is provided
  by the decorator ``cml.decorator.normalize``.



## [0.0.0] - YYYY-MM-DD

*Added* for new features.
*Changed* for changes in existing functionality.
*Deprecated* for once-stable features removed in upcoming releases.
*Removed* for deprecated features removed in this release.
*Fixed* for any bug fixes.
*Security* to invite users to upgrade in case of vulnerabilities.
