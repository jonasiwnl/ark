import sqlite3
from pathlib import Path

from opensearchpy import OpenSearch

IMESSAGE_OPENSEARCH_INDEX = "imessages"
IMESSAGE_DATA_PATH = Path.home() / "Library/Messages/chat.db"
LAST_TIMESTAMP_PATH = Path("imessage_last_timestamp.txt")
READ_NEW_IMESSAGES_QUERY = """
SELECT
    message.ROWID as message_id,
    message.date,
    message.text,
    message.is_from_me,
    handle.id as sender_id,
    chat.display_name as chat_display_name
FROM message
LEFT JOIN handle ON message.handle_id = handle.ROWID
LEFT JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
LEFT JOIN chat ON chat_message_join.chat_id = chat.ROWID
WHERE message.date > ?
ORDER BY message.date ASC
"""


def read_new_imessages() -> list[dict]:
    last_timestamp = LAST_TIMESTAMP_PATH.read_text() if LAST_TIMESTAMP_PATH.exists() else 0
    with sqlite3.connect(f"file:{IMESSAGE_DATA_PATH}?mode=ro", uri=True) as conn:
        # Make query results dicts instead of tuples
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(READ_NEW_IMESSAGES_QUERY, (last_timestamp,))
        raw_imessages = cursor.fetchall()
        if not raw_imessages:
            return []
        LAST_TIMESTAMP_PATH.write_text(str(raw_imessages[-1]["date"]))
        return [dict(raw_imessage) for raw_imessage in raw_imessages]


def index_imessages(os_client: OpenSearch, imessages: list[dict]):
    for imessage in imessages:
        document = {
            "text": imessage["text"],
            "date": imessage["date"],  # TODO: format date
            "is_from_me": imessage["is_from_me"],
            "sender_id": imessage["sender_id"],
            "chat_display_name": imessage["chat_display_name"],
        }
        os_client.index(index=IMESSAGE_OPENSEARCH_INDEX, id=imessage["message_id"], body=document)


if __name__ == "__main__":
    imessages = read_new_imessages()
    os_client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}], use_ssl=False)
    index_imessages(os_client, imessages)
