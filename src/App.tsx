import { useEffect, useLayoutEffect, useMemo, useState } from "react";
import { List, useListRef, type RowComponentProps } from "react-window";
import { useSearchParams } from "react-router-dom";

import "./App.scss";

interface Build {
  id: number;
  attrpath: string;
  hydra_id: number | null;
}

interface Commit {
  name: string;
  rev: string;
  date: string;
}

interface ApiResponse {
  builds: Build[];
  commit: Commit;
}

function BuildEntry({
  index,
  builds,
  selected,
  onSelect,
  style
}: RowComponentProps<{
  builds: Build[];
  selected: string | null;
  onSelect: (b: Build) => void }>
) {
  let entry = builds[index];
  let isCurrent = selected === entry.attrpath;

  return (
    <li style={style}>
      <button
        className={"build-entry " + (isCurrent ? "build-entry-current" : "")}
        onClick={() => onSelect(entry)}
      >
        <span className="attrpath">{entry.attrpath}</span>
      </button>
    </li>
  );
}

function BuildsTable({ builds, top, selected, onSelect }: {
  builds: Build[];
  top: string | null;
  selected: string | null;
  onSelect: (b: Build) => void;
}) {
  const listRef = useListRef(null);

  useLayoutEffect(() => {
    if (!top) return;

    const idx = builds.findIndex((b) => b.attrpath === top);
    if (idx === -1) return;

    requestAnimationFrame(() => {
      const list = listRef.current;

      list?.scrollToRow({
        align: "start",
        behavior: "smooth",
        index: idx,
      });
    });
  }, []);

  return (
    <List
      listRef={listRef}
      className="build-entries"
      rowComponent={BuildEntry}
      rowCount={builds.length}
      rowHeight={29}
      rowProps={{ builds, selected, onSelect }}
    />
  );
}

export default function App() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selected = searchParams.get("selected");

  const [data, setData] = useState<Build[]>([]);
  const [commit, setCommit] = useState<Commit | null>(null);

  const [selectedBuild, setSelectedBuild] = useState<Build | null>(null);
  const [logContent, setLogContent] = useState<string>("");

  useEffect(() => {
    fetch(`/api/builds`)
      .then((res) => res.json())
      .then((res: ApiResponse) => {
        setData(res.builds);
        if (!selected) return;
        let idx = res.builds.findIndex((b) => b.attrpath == selected);
        selectBuild(res.builds[idx]);
        setCommit(res.commit);
      });
  }, []);

  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"name" | "content">("name");
  const [searchResults, setSearchResults] = useState<Build[] | null>(null);

  const filteredData = useMemo(() => {
    if (!query || mode !== "name") return data;

    const q = query.toLowerCase();

    return data.filter((b) =>
      b.attrpath.toLowerCase().includes(q)
    );
  }, [data, query, mode]);

  const selectBuild = (b: Build) => {
    setSelectedBuild(b);
    setSearchParams({ selected: b.attrpath });

    fetch(`/build-logs/${b.attrpath}.log`)
      .then((res) => res.text())
      .then((text) => setLogContent(text))
  }

  const prettifyDate = (iso: string | null) => {
    if (iso === null) return "";
    const date = new Date(iso);
    return date.toDateString();
  }

  useEffect(() => {
    if (mode !== "content") return;
    if (query.length < 3) {
      setSearchResults(data);
      return;
    }

    const controller = new AbortController();

    const id = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        signal: controller.signal,
      })
        .then((res) => res.json())
        .then((res) => {
          const matched = new Set(res);
          setSearchResults(data.filter((b) => matched.has(b.attrpath)));
        })
        .catch((e) => {
          if (e.name !== "AbortError") console.error(e);
        });
    }, 300);

    return () => {
      controller.abort();
      clearTimeout(id);
    };
  }, [query, mode, data]);

  const displayed = useMemo(() => {
    if (mode === "content") {
      return searchResults ?? [];
    }
    return filteredData;
  }, [mode, filteredData, searchResults]);


  if (data.length === 0) {
    return (
      <div className="loading">
        <img className="spinning-nix" src="/nix.svg" height="24px" width="24px" alt=""/>
        <p>Loading (this might take a few seconds)...</p>
      </div>
    );
  }

  return (
    <div className="panel-hsplit">
      <div className="panel-dual-view">
        <div className="panel-left">
          <div className="panel panel-left-top">
            <label>Search</label>
            <input
              placeholder="hash mismatch"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              maxLength={64}
            />
            <div className="mode-type">
              mode:
              <button onClick={() =>
                setMode((m) => (m === "name" ? "content" : "name"))
              }>
              {mode === "name" ? "name" : "grep"}
            </button>

            </div>
          </div>
      
          <div className="panel panel-left-bottom">
            <h2>Builds ({displayed.length})</h2>
            <BuildsTable
              builds={displayed}
              top={selected}
              selected={selectedBuild?.attrpath ?? null}
              onSelect={selectBuild}
            />
          </div>
        </div>

        <div className="panel panel-right">
          <h2>Log Viewer</h2>
          {selectedBuild ? (
            <>
              <div className="log-meta">
                <p>
                  Viewing { selectedBuild.attrpath }
                </p>
                { selectedBuild.hydra_id &&
                  <a href={`https://hydra.nixos.org/build/${ selectedBuild.hydra_id }`}>hydra</a>
                }
              </div>
              <span className="separator"></span>
              <pre className="log-viewer">{logContent}</pre>
            </>
          ) : (
            <p>Select a build to view its log</p>
          )}
        </div>
      </div>
    
      <div className="info panel-vsplit">
        <div className="info">
          <p>Last index: {prettifyDate(commit?.date ?? null)}</p>
          @
          <a href={`https://github.com/NixOS/nixpkgs/commit/${commit?.rev}`}>{commit?.name}</a>
          -
          <p>All the derivations are built by my tiny server, locally. x86_64-linux only.</p>
        </div>
        <div className="info">
          Contribution is welcome.
          <a href="https://github.com/Sigmanificient/nixpkgs-failure-dashboard">GitHub</a>
          /
          <a href="https://github.com/Sigmanificient/nixpkgs-failure-dashboard/issues/new">Report an issue</a>
        </div>
      </div>
    </div>
  );
}
