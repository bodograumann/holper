from typing import Annotated

from pydantic_xml import element

from .common import BaseMessageElement, Class


class ClassList(BaseMessageElement):
    """A list of classes."""

    classes: Annotated[list[Class], element(tag="Class")] = []
