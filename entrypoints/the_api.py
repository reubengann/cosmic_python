from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

import service_layer.services as services
import domain.models as models
from adapters.repository import SqlRepository

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
    try:
        ref = services.allocate(line_item, repo, session)
    except (services.InvalidSku, models.OutOfStock) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"batchref": ref}
