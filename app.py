from fastapi import FastAPI, Request
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

app = FastAPI()

# Metrics
REQUEST_COUNT = Counter(
    "request_count",
    "Total number of requests"
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Time spent processing request"
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    latency = time.time() - start_time
    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(latency)

    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health")
def health():
    return {"status": "ok"}


# Prometheus metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)