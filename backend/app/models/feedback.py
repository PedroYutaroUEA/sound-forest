from pydantic import BaseModel


class Feedback(BaseModel):
    user_id: int
    item_id: int
    rating: int
