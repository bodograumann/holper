from datetime import datetime
from typing import Annotated

from pydantic_xml import attr, element
from typing_extensions import Doc

from .common import BaseMessageElement, Class, ControlCard, IOFBaseModel, Organisation, Person, Score


class Competitor(IOFBaseModel):
    """Represents information about a person in a competition context, i.e. including organisation and control card."""

    person: Annotated[Person, element(tag="Person")]
    organisations: Annotated[
        list[Organisation],
        element(tag="Organisation"),
        Doc("The organisations that the person is member of."),
    ] = []
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc("The default control cards of the competitor."),
    ] = []
    classes: Annotated[list[Class], element(tag="Class"), Doc("The default classes of the competitor.")] = []
    scores: Annotated[list[Score], element(tag="Score"), Doc("Any scores, e.g. ranking scores, for the person.")] = []
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class CompetitorList(BaseMessageElement):
    """A list of competitors. This is used to exchange a "brutto" list of possible competitors. This should not be used to exchange entries; use EntryList instead."""

    competitors: Annotated[list[Competitor], element(tag="Competitor")] = []
