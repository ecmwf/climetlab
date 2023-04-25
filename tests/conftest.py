import pytest

SKIP = {
    "short": ["documentation", "download", "external_download", "ftp", "long_test"],
    "long": ["documentation", "ftp"],
    "release": [],
    "documentation": None,
    # pytest.mark.short_download not used
}


def pytest_addoption(parser):
    help_str = "NAME: short, long, release. Runs a subset of tests.\n"
    for k, v in SKIP.items():
        if v:
            help_str += f"'{k}': skip tests marked as {','.join(v)}.\n"
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
    flag = item.config.getoption("-E")
    marks_to_skip = SKIP[flag]

    marks_in_items = list([m.name for m in item.iter_markers()])

    if marks_to_skip is None:
        if flag not in marks_in_items:
            pytest.skip(f"test is skipped because custom pytest option : -E {flag}")
        return

    for m in marks_in_items:
        if m in marks_to_skip:
            pytest.skip(f"test is skipped because custom pytest option: -E {flag}")
