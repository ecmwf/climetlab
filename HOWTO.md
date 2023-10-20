# Instructions for developers

(This is a place holder for developer's documentation).

## Generate documentation

TODO: Add documentation

## Upload sample data

To push sample data to ECMWF's object storage (authorised persons only):

First install `s3cmd` if needed:
```bash
% pip install s3cmd
```

Then set `~/.s3cfg` to:
```
host_base = object-store.os-api.cci1.ecmwf.int
host_bucket =
access_key = xxxxxxxxxxxx
secret_key = yyyyyyyyyyyy
use_https = True
```

First time (already done):
```bash
% s3cmd mb --no-preserve s3://climetlab
```

```bash
% s3cmd put --acl-public --no-preserve example.file s3://climetlab/directory/example.file
```

The file is then available at: https://object-store.os-api.cci1.ecmwf.int/climetlab/samples/example.file.

Please note that only `https` is supported, even if `s3cmd` reports a url starting with `http`.


If you use several S3 account, use:
```bash
% s3cmd -c ~/.s3cfg.climetlab ...
```

Make sure that you can re-create, re-upload all data.
