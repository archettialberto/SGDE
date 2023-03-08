from pydantic import BaseModel


class SGDEBaseModel(BaseModel):
    class Config:
        orm_mode = True
