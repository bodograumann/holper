"""Representation of the IOF Data Standard, version 3.0 as pydantic-xml models.

We cannot parse Extensions, because they might contain arbitrary data.

pydantic-xml does not support forward refs with `from __future__ import annotations`, so we define all models in roughly inverted order from the xml schema.

Cf. https://github.com/international-orienteering-federation/datastandard-v3/blob/master/IOF.xsd
"""
