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
  <div>
    <input type="text" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
    <button onClick={() => search(searchText)}>Search</button>
    <button onClick={reindex}>Reindex</button>
    <div>
      {results.map((result: any) => (
        <div key={result._id}>{result._source.text}</div>
      ))}
    </div>
  </div>
  );
}

export default App;
