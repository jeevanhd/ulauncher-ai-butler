from fastapi import FastAPI
from pydantic import BaseModel

from daemon.model import query_needle, load_model
from dispatcher.dispatcher import dispatch

app = FastAPI()


class QueryRequest(BaseModel):
    text: str


@app.on_event("startup")
def startup():
    # warm load at boot, not on first request
    load_model()


@app.post("/query")
def handle_query(req: QueryRequest):
    tool_calls = query_needle(req.text)
    if not tool_calls:
        return {"summary": "Didn't understand that", "detail": ""}

    result = dispatch(tool_calls[0])
    return result
