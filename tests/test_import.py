"""Basic smoke test: project package imports."""

def test_import_src_package():
    import importlib
    importlib.import_module('src')
    assert True
