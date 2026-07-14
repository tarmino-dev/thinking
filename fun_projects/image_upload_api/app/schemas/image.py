from pydantic import BaseModel, ConfigDict


class ImageOut(BaseModel):
    id: int
    filename: str
    path: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)
