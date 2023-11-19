"""Representation of the IOF Data Standard, version 3.0 as pydantic-xml models.

We cannot parse Extensions, because they might contain arbitrary data.

pydantic-xml does not support forward refs with `from __future__ import annotations`, so we define all models in roughly inverted order from the xml schema.

Cf. https://github.com/international-orienteering-federation/datastandard-v3/blob/master/IOF.xsd
"""

from .class_list import ClassList
from .competitor_list import CompetitorList
from .control_card_list import ControlCardList
from .course_data import CourseData
from .entry_list import EntryList
from .event_list import EventList
from .organisation_list import OrganisationList
from .result_list import ResultList
from .service_request_list import ServiceRequestList
from .start_list import StartList

__all__ = [
    "ClassList",
    "CompetitorList",
    "ControlCardList",
    "CourseData",
    "EntryList",
    "EventList",
    "OrganisationList",
    "ResultList",
    "ServiceRequestList",
    "StartList",
]
