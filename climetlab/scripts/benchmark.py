# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from .benchmarks.indexed_url import benchmark as benchmark_indexed_url
from .tools import experimental, parse_args


class BenchmarkCmd:
    @parse_args(
        indexedurl=dict(
            action="store_true",
            help="Benchmark on using indexed URL (byte-range) and various servers.",
        ),
        all=dict(action="store_true", help="Run all benchmarks."),
    )
    @experimental
    def do_benchmark(self, args):
        """Run predefined benchmarks, for CliMetLab development purposes."""
        if args.all or args.indexedurl:
            print("Starting benchmark.")
            benchmark_indexed_url()
