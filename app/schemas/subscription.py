from pydantic import BaseModel, Field
from typing import List


class SubscriptionCreate(BaseModel):
    openid: str = Field(..., description="微信用户OpenID")
    lake_ids: List[int] = Field(default_factory=list, description="订阅的盐湖ID列表")
    threshold: int = Field(default=90, description="推送阈值")