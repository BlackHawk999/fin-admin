from pydantic import BaseModel


class OwnerCreate(BaseModel):
    name: str
    color_hex: str = "#808080"


class OwnerUpdate(BaseModel):
    name: str | None = None
    color_hex: str | None = None


class OwnerResponse(BaseModel):
    id: int
    name: str
    color_hex: str

    class Config:
        from_attributes = True
