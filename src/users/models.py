from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class User(BaseModel):
    id_name: str
    description: str
    official: bool = False
    name: str
    icon: str
