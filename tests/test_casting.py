from __future__ import division, absolute_import, print_function

from pymushra import casting


def test_casting():
    val = {"test": "Test1", "participants": [{"age": "30", "name": "Nils"},
           {"age": "30", "name": "Nils", "as": None, "yo": ""}], "yoo": "True", "foo": 100}
    expected = {"test": "Test1", "participants": [{"age": 30, "name": "Nils"},
                {"age": 30, "name": "Nils", "as": None, "yo": ""}], "yoo": True, "foo": 100}

    assert expected == casting.cast_recursively(val)
