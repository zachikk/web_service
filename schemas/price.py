from pydantic import BaseModel
from .mover_amount import MoverAmountGet


class MoverPriceBase(BaseModel):
    price: int

    class Config:
        orm_mode = True


class MoverPriceCreate(MoverPriceBase):
    mover_amount_id: int
    price_tag_id: int


class MoverPriceGet(MoverPriceBase):
    id: int
    company_id: int
    mover_amount: MoverAmountGet