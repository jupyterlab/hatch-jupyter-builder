# Copyright (c) me.
# Distributed under the terms of the Modified BSD License.

from ..example import ExampleWidget


def test_example_creation_blank():
    w = ExampleWidget()
    assert w.value == "Hello World"
