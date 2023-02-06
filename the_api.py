from fastapi import Depends, FastAPI
from pydantic import BaseModel

import services
import models
from repository import SqlRepository

app = FastAPI()


def get_session():
    raise NotImplementedError


class LineItemRequest(BaseModel):
    order_id: str
    sku: str
    qty: int


@app.post("/allocate", status_code=201)
def allocate_endpoint(line: LineItemRequest, session=Depends(get_session)):
    line_item = models.OrderLine(line.order_id, line.sku, line.qty)
    repo = SqlRepository(session)

    ref = services.allocate(line_item, repo, session)
    return {"batchref": ref}
