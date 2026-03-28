import { useEffect, useLayoutEffect, useState } from "react";
import { List, useListRef, type RowComponentProps } from "react-window";

import "./App.scss";
import { useSearchParams } from "react-router-dom";

interface Build {
  id: number;
  attrpath: string;
  status: "success" | "failed" | "timeout";
}

type ApiResponse = Build[];

function BuildEntry({
  index,
  builds,
  style
}: RowComponentProps<{
  builds: Build[];
}>) {
  let entry = builds[index];

  return (
    <div className="builds-entry" style={style}>
      <a href={`/build-logs/${entry.attrpath}.log`} target="_blank">
        { builds[index].attrpath }
      </a>
      <span>({ builds[index].status })</span>
    </div>
  );
}

function BuildsTable({ builds, top }: {
  builds: Build[];
  top: string | null;
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
      className="builds-table"
      rowComponent={BuildEntry}
      rowCount={builds.length}
      rowHeight={25}
      rowProps={{ builds }}
    />
  );
}

export default function App() {
  const [searchParams, _] = useSearchParams();
  let selected = searchParams.get("selected");

  const [data, setData] = useState<Build[]>([]);

  useEffect(() => {
    fetch(`/api/builds`)
      .then((res) => res.json())
      .then((res: ApiResponse) => {
        setData(res);
      });
  }, []);

  if (data.length == 0)
    return <p>Loading...</p>;

  return (
    <>
      <h2>Builds ({data.length})</h2>
      <BuildsTable top={selected} builds={data} />
    </>
  );
}
