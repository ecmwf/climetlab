


def pytest_configure(config):
    import climetlab
    climetlab._running_pytest_ = True
