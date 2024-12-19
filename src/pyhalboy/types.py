from collections.abc import Mapping, Sequence

JSONNode = (
    str
    | int
    | float
    | bool
    | None
    | Mapping[str, "JSONNode"]
    | Sequence["JSONNode"]
)

PropertyName = str
PropertyValue = JSONNode
ResourceRel = str
LinkRel = str
Href = str

StatusCode = int
