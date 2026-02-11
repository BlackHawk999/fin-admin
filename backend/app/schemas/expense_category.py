from pydantic import BaseModel, Field


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ExpenseCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True
