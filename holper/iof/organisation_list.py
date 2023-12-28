from typing import Annotated

from pydantic_xml import element

from .common import BaseMessageElement, Organisation


class OrganisationList(BaseMessageElement):
    """A list of organisations, including address and contact information."""

    organisations: Annotated[list[Organisation], element(tag="Organisation")] = []
