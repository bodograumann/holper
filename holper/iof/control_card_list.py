from typing import Annotated

from pydantic_xml import element
from typing_extensions import Doc

from .common import BaseMessageElement, ControlCard


class ControlCardList(BaseMessageElement):
    """Defines control card ownership, e.g. for rental control card handling purposes."""

    owner: Annotated[str | None, element(tag="Owner"), Doc("The owner of the control cards.")] = None
    control_cards: Annotated[list[ControlCard], element(tag="ControlCard"), Doc("The control cards.")]
