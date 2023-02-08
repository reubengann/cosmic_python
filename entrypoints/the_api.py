from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

import domain.models as models
import service_layer.services as services
from adapters.repository import SqlRepository

app = FastAPI()


def get_session():
    raise NotImplementedError


class LineItemRequest(BaseModel):
    order_id: str
    sku: str
    qty: int


class BatchRequest(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[date]


@app.post("/allocate", status_code=201)
def allocate_endpoint(line: LineItemRequest, session=Depends(get_session)):
    repo = SqlRepository(session)
    try:
        ref = services.allocate(line.order_id, line.sku, line.qty, repo, session)
    except (services.InvalidSku, models.OutOfStock) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"batchref": ref}


@app.post("/batch", status_code=201)
def batch_endpoint(batch: BatchRequest, session=Depends(get_session)):
    repo = SqlRepository(session)
    services.add_batch(batch.ref, batch.sku, batch.qty, batch.eta, repo, session)
    return {"message": "ok"}
