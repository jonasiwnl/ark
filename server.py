from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opensearchpy import OpenSearch

from apple_notes import index_apple_notes, query_apple_notes, read_apple_notes
from imessage import index_imessages, query_imessages, read_new_imessages

app = FastAPI(title="Ark")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
def search(query: str):
    os_client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}], use_ssl=False)
    imessage_results = query_imessages(os_client, query)
    apple_note_results = query_apple_notes(os_client, query)
    return {"results": imessage_results + apple_note_results}


@app.post("/reindex")
def reindex():
    os_client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}], use_ssl=False)
    apple_notes = read_apple_notes()
    apple_note_indexed_count, apple_note_indexing_errors = index_apple_notes(os_client, apple_notes)
    imessages = read_new_imessages()
    imessage_indexed_count, imessage_indexing_errors = index_imessages(os_client, imessages)
    return {
        "count": apple_note_indexed_count + imessage_indexed_count,
        "errors": apple_note_indexing_errors + imessage_indexing_errors,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
