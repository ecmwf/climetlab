def zarr_not_installed():
    try:
        import zarr
        import s3fs

        return False
    except ImportError:
        return True
