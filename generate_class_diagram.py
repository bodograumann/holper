"""Generate a Mermaid class diagram from the SQLAlchemy model classes"""
import inspect
from sqlalchemy.orm import class_mapper, RelationshipProperty, Mapper
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


def print_mapper_mermaid(mapper: Mapper):
    name = mapper.class_.__name__
    print(f"{INDENT}class {name} {{")

    for column in mapper.columns:
        print(f"{2 * INDENT}+{column.type.__class__.__name__} {column.key}")

    print(f"{INDENT}}}")

    if mapper.inherits:
        print(f"{INDENT}{name} <|-- {mapper.inherits.class_.__name__}")

    for prop in mapper.relationships:
        if prop in visited_as_reverse:
            continue
        if prop.back_populates:
            reverse = prop.mapper.get_property(prop.back_populates)
            visited_as_reverse.add(reverse)
            print(
                f'{INDENT}{name} "{card(reverse)}" -- '
                f'"{card(prop)}" {prop.mapper.class_.__name__} : {prop.key} / {reverse.key}'
            )
        else:
            print(
                f'{INDENT}{name} --> "{card(prop)}" {prop.mapper.class_.__name__} : {prop.key}'
            )


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

print("%%{init: { class: { useMaxWidth: false }}}%%")
print("classDiagram")
print(f"{INDENT}direction LR")
for cls in classes:
    print_mapper_mermaid(class_mapper(cls))
