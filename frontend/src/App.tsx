import { useState } from "react";
import "./App.css";

function App() {
  const [searchText, setSearchText] = useState('')
  const [results, setResults] = useState([]);

  async function search(searchText: string) {
    const response = await fetch(`http://localhost:8000/search?query=${searchText}`);
    const data = await response.json();
    setResults(data.results);
  }

  async function reindex() {
    await fetch(`http://localhost:8000/reindex`, { method: 'POST' });
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
      <button type="button" onClick={reindex}>Reindex</button>
    </form>
    <div className="results">
      {results.map((result: any) => (
        <div className="result-card" key={result._id}>{result._source.text}</div>
      ))}
    </div>
  </div>
  );
}

export default App;
