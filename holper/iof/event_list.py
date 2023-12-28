from typing import Annotated

from pydantic_xml import element

from .common import BaseMessageElement, Event


class EventList(BaseMessageElement):
    """A list of events. This can be used to exchange fixtures."""

    events: Annotated[list[Event], element(tag="Event")] = []
