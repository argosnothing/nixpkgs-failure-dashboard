import { useEffect, useLayoutEffect, useState } from "react";
import { List, useListRef, type RowComponentProps } from "react-window";
import { useSearchParams } from "react-router-dom";

import "./App.scss";

interface Build {
  id: number;
  attrpath: string;
  status: "success" | "failed" | "timeout";
}

type ApiResponse = Build[];

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
        <span className="status">({entry.status})</span>
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
  const [selectedLog, setSelectedLog] = useState<string | null>(selected);
  const [logContent, setLogContent] = useState<string>("");

  useEffect(() => {
    fetch(`/api/builds`)
      .then((res) => res.json())
      .then((res: ApiResponse) => setData(res));
  }, []);

  useEffect(() => {
    if (!selectedLog) return;

    fetch(`/build-logs/${selectedLog}.log`)
      .then((res) => res.text())
      .then((text) => setLogContent(text))
      .then(() => setSearchParams({ selected: selectedLog }));
  }, [selectedLog]);

  if (data.length === 0)
    return <p>Loading...</p>;

  return (
    <div className="panel-dual-view">
      <div className="panel-left">
        <h2>Builds ({data.length})</h2>
        <BuildsTable
          builds={data}
          top={selected}
          selected={selectedLog}
          onSelect={(b) => setSelectedLog(b.attrpath)}
        />
      </div>

      <div className="panel-right">
        <h2>Log Viewer</h2>
        {selectedLog ? (
          <>
            <p>Viewing { selectedLog }</p>
            <span className="separator"></span>
            <pre className="log-viewer">{logContent}</pre>
          </>
        ) : (
          <p>Select a build to view its log</p>
        )}
      </div>
    </div>
  );
}
