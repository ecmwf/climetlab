import pytest

SKIP = {
    "short": ["notebook", "long_test", "external_download", "ftp"],
    "long": ["external_download", "ftp"],
    "release": [],
}


def pytest_addoption(parser):
    help_str = "NAME: short, long, release. Runs a subset of tests.\n"
    for k, v in SKIP.items():
        if v:
            help_str += f"'{k}': skip test marked as {','.join(v)}.\n"
        else:
            help_str += f"'{k}': do not skip tests.\n"

    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        default="short",
        help=help_str,
    )


def pytest_runtest_setup(item):
    subset = item.config.getoption("-E")
    mark_to_skip = SKIP[subset]

    for m in item.iter_markers():
        if m.name in mark_to_skip:
            pytest.skip(f"test is skipped because custom pytest option: -E {subset}")
