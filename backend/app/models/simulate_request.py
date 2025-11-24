from pydantic import BaseModel


class SimulateRequest(BaseModel):
    genres: list
    user_name: str = None
