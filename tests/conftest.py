import pytest

SKIP = {
    "short": ["notebook", "long_test", "external_download"],
    "long": ["external_download"],
    "release": [],
}


def pytest_addoption(parser):
    help_str = ""
    for k, v in help_str:
        if v:
            help_str += f"'{k}': skip test marked as {','.join(v)}."
        else:
            help_str += f"'{k}': do skip tests."

    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        default="short",
        help="NAME: short, long, release. Runs a subset of tests." "Short",
    )


# def pytest_collection_modifyitems(config, items):
#    if config.getoption("--run-long"):
#        # --runslow given in cli: do not skip slow tests
#        return
#    skip_slow = pytest.mark.skip(reason="Need --run-long option to run")
#    for item in items:
#        if "long_test" in item.keywords:
#            item.add_marker(skip_slow)


def pytest_runtest_setup(item):
    subset = item.config.getoption("-E")
    mark_to_skip = SKIP[subset]

    for m in item.iter_markers():
        if m in mark_to_skip:
            pytest.skip(f"test is skipped because -E {subset}")
