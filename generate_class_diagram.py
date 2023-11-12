#!/usr/bin/env python3

"""Generate a Mermaid class diagram from the SQLAlchemy model classes"""

import inspect
from collections.abc import Generator
from pathlib import Path

from sqlalchemy.orm import Mapper, RelationshipProperty, class_mapper

from holper import model

INDENT = 4 * " "


def card(prop: RelationshipProperty):
    """Generate cardinality indicator for a relationship property"""

    if prop.uselist:
        return "*"
    try:
        columns = prop.local_side
    except AttributeError:
        columns = prop.local_columns
    if any(column.nullable for column in columns):
        return "0..1"
    return ""


visited_as_reverse = set()


def yield_mapper_mermaid(mapper: Mapper) -> Generator[str, None, None]:
    name = mapper.class_.__name__
    yield f"{INDENT}class {name} {{"

    for column in mapper.columns:
        yield f"{2 * INDENT}+{column.type.__class__.__name__} {column.key}"

    yield f"{INDENT}}}"

    if mapper.inherits:
        yield f"{INDENT}{name} <|-- {mapper.inherits.class_.__name__}"

    for prop in mapper.relationships:
        if prop in visited_as_reverse:
            continue
        if prop.back_populates:
            reverse = prop.mapper.get_property(prop.back_populates)
            visited_as_reverse.add(reverse)
            yield (
                f'{INDENT}{name} "{card(reverse)}" -- '
                f'"{card(prop)}" {prop.mapper.class_.__name__} : {prop.key} / {reverse.key}'
            )
        else:
            yield f'{INDENT}{name} --> "{card(prop)}" {prop.mapper.class_.__name__} : {prop.key}'


classes = [
    cls
    for (cls_name, cls) in inspect.getmembers(
        model,
        lambda value: inspect.isclass(value)
        and not value.__name__.startswith("_")
        and issubclass(value, model.Base)
        and value is not model.Base,
    )
]

with Path("docs/class_diagram.mmd").open("w") as output:
    output.write("%%{init: { class: { useMaxWidth: false }}}%%\n")
    output.write("classDiagram\n")
    output.write(f"{INDENT}direction LR\n")
    for cls in classes:
        output.write("\n")
        for line in yield_mapper_mermaid(class_mapper(cls)):
            output.write(line + "\n")
