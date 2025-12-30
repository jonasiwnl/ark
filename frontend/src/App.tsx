import { useState } from "react";
import "./App.css";

// TYPES //
interface IndexedIMessage {
  text: string | null;
  date: string;
  is_from_me: boolean;
  sender_id: string | null;
  chat_display_name: string | null;
}

interface IndexedAppleNote {
  name: string;
  body: string;
}

interface IMessageSearchHit {
  _index: "imessages";
  _id: string;
  _score: number | null;
  _source: IndexedIMessage;
  sort?: number[];
}

interface AppleNoteSearchHit {
  _index: "apple_notes";
  _id: string;
  _score: number | null;
  _source: IndexedAppleNote;
}

type SearchHit = IMessageSearchHit | AppleNoteSearchHit;
// END TYPES //

function isIMessage(hit: SearchHit): hit is IMessageSearchHit {
  return hit._index === "imessages";
}

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleString();
}

function App() {
  const [searchText, setSearchText] = useState("");
  const [results, setResults] = useState<SearchHit[]>([]);

  async function search(searchText: string) {
    const response = await fetch(
      `http://localhost:8000/search?query=${encodeURIComponent(searchText)}`
    );
    const data = await response.json();
    setResults(data.results);
  }

  async function reindex() {
    await fetch(`http://localhost:8000/reindex`, { method: "POST" });
  }

  return (
    <div className="app-container">
      <form
        className="search-bar"
        onSubmit={(e) => {
          e.preventDefault();
          search(searchText);
        }}
      >
        <input
          className="search-input"
          type="text"
          placeholder="Search…"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <button type="submit">Search</button>
        <button type="button" onClick={reindex}>
          Reindex
        </button>
      </form>
      <div className="results">
        {results.map((hit) =>
          isIMessage(hit) ? (
            <div className="result-card" key={hit._id}>
              <div className="result-meta">
                <span className="result-type">iMessage</span>
                <span className="result-date">{formatDate(hit._source.date)}</span>
              </div>
              <div className="result-sender">
                {hit._source.is_from_me ? "You" : hit._source.sender_id || "Unknown"}
                {hit._source.chat_display_name && ` · ${hit._source.chat_display_name}`}
              </div>
              <div className="result-text">{hit._source.text}</div>
            </div>
          ) : (
            <div className="result-card" key={hit._id}>
              <div className="result-meta">
                <span className="result-type">Note</span>
              </div>
              <div className="result-title">{hit._source.name}</div>
              <div className="result-text">{hit._source.body}</div>
            </div>
          )
        )}
      </div>
    </div>
  );
}

export default App;
