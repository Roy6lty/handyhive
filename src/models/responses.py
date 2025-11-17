from src.root.abstract_base import AbstractBaseModel


class SuccessfulResponse(AbstractBaseModel):
    message: str = "successful"
