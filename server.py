from fastapi import FastAPI

app = FastAPI(title="Ark")


@app.get("/search")
def search(query: str):
    return {"results": []}


@app.post("/reindex")
def reindex():
    return {"errors": []}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
