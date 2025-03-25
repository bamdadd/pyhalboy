from collections.abc import Mapping
from typing import Sequence

type JsonObject = Mapping[str, JsonValue]
type JsonArray = Sequence[JsonValue]
type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonObject | JsonArray | JsonPrimitive

JsonValueType = JsonValue.__value__


PropertyName = str
PropertyValue = JsonValue
Properties = JsonObject
ResourceRel = str
LinkRel = str
Href = str

StatusCode = int
