import json
import subprocess
from html.parser import HTMLParser

from opensearchpy import OpenSearch, helpers
from typing_extensions import TypedDict

APPLE_NOTES_OPENSEARCH_INDEX = "apple_notes"
# JXA
READ_APPLE_NOTES_QUERY = """
JSON.stringify(Application("Notes").notes().map(n => ({
    id: n.id(),
    name: n.name(),
    body: n.body()
})));
"""


class RawAppleNote(TypedDict):
    """Raw Apple Note data from JXA query."""

    id: str
    name: str
    body: str


class IndexedAppleNote(TypedDict):
    """Apple Note data as stored in OpenSearch."""

    name: str
    body: str


class AppleNoteSearchHit(TypedDict):
    """OpenSearch search hit for an Apple Note."""

    _index: str
    _id: str
    _score: float | None
    _source: IndexedAppleNote


# Removes HTML tags from the body of the note
def parse_apple_note(parser: HTMLParser, apple_note: RawAppleNote) -> RawAppleNote:
    text_parts: list[str] = []
    parser.handle_data = lambda data: text_parts.append(data)
    parser.feed(apple_note["body"])
    apple_note["body"] = "".join(text_parts)
    return apple_note


def read_apple_notes() -> list[RawAppleNote]:
    osascript_result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", READ_APPLE_NOTES_QUERY], capture_output=True, text=True
    )
    raw_apple_notes = json.loads(osascript_result.stdout)
    parser = HTMLParser()
    return [parse_apple_note(parser, raw_apple_note) for raw_apple_note in raw_apple_notes]


def index_apple_notes(os_client: OpenSearch, apple_notes: list[RawAppleNote]) -> tuple[int, list[dict]]:
    # To avoid having to deal with indexing incremental updates, we nuke and re-index every time.
    # Ignores 404 errors (the index doesn't exist).
    os_client.indices.delete(index=APPLE_NOTES_OPENSEARCH_INDEX, ignore=[404])

    index_operations = (
        {
            "_index": APPLE_NOTES_OPENSEARCH_INDEX,
            "_id": apple_note["id"],
            "_source": {
                "name": apple_note["name"],
                "body": apple_note["body"],
            },
        }
        for apple_note in apple_notes
    )

    indexed_count, errors = helpers.bulk(os_client, index_operations, max_retries=2)
    # Since we nuked the index, force a refresh after indexing
    os_client.indices.refresh(index=APPLE_NOTES_OPENSEARCH_INDEX)
    return indexed_count, errors


def query_apple_notes(os_client: OpenSearch, query: str, limit: int = 10) -> list[AppleNoteSearchHit]:
    response = os_client.search(
        index=APPLE_NOTES_OPENSEARCH_INDEX, body={"query": {"match": {"body": query}}, "size": limit}
    )
    return response["hits"]["hits"]


if __name__ == "__main__":
    os_client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}], use_ssl=False)

    apple_notes = read_apple_notes()
    indexed_count, errors = index_apple_notes(os_client, apple_notes)
    print(f"indexed {indexed_count} apple notes with {len(errors)} errors")

    queried_apple_notes = query_apple_notes(os_client, query="chief")
    print(queried_apple_notes)
