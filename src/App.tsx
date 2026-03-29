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
  onSelect,
  style
}: RowComponentProps<{ builds: Build[]; onSelect: (b: Build) => void }>) {
  let entry = builds[index];

  return (
    <div className="build-entry" style={style} onClick={() => onSelect(entry)}>
      <span>{entry.attrpath}</span>
      <span>({entry.status})</span>
    </div>
  );
}

function BuildsTable({ builds, top, onSelect }: {
  builds: Build[];
  top: string | null;
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
      rowHeight={25}
      rowProps={{ builds, onSelect }}
    />
  );
}

export default function App() {
  const [searchParams] = useSearchParams();
  const selected = searchParams.get("selected");

  const [data, setData] = useState<Build[]>([]);
  const [selectedLog, setSelectedLog] = useState<string | null>(null);
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
      .then((text) => setLogContent(text));
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
          onSelect={(b) => setSelectedLog(b.attrpath)}
        />
      </div>

      <div className="panel-right">
        <h2>Log Viewer</h2>
        {selectedLog ? (
          <>
            <p>viewing { selectedLog }</p>
            <pre className="log-viewer">{logContent}</pre>
          </>
        ) : (
          <p>Select a build to view its log</p>
        )}
      </div>
    </div>
  );
}
