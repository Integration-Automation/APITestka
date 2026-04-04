collect_ignore_glob = ["je_api_testka/*"]


def pytest_collection_modifyitems(config, items):
    """Filter out source functions that pytest mistakenly collects via imports."""
    filtered = []
    for item in items:
        # Skip items whose definition lives outside the test directory
        if "je_api_testka" in str(item.fspath):
            continue
        filtered.append(item)
    items[:] = filtered
