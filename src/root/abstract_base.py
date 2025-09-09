from pydantic import BaseModel, ConfigDict


class AbstractBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        str_min_length=1,
        str_max_length=1000,
        use_enum_values=True,
    )
