import { useEffect, useState, type RefObject } from "react";
import { List, useListRef, type ListImperativeAPI, type RowComponentProps } from "react-window";

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

function BuildsTable({ builds, listRef }: {
  builds: Build[];
  listRef: RefObject<ListImperativeAPI | null> }
) {
    return (
      <List
        listRef={listRef}
        className="builds-table"
        rowComponent={BuildEntry}
        rowCount={builds.length}
        rowHeight={25}
        rowProps={{ builds }}
      />
    )
}

export default function App() {
  const [searchParams, _] = useSearchParams();
  let selected = searchParams.get("selected");

  const [data, setData] = useState<Build[]>([]);
  const listRef = useListRef(null);

  useEffect(() => {
    fetch(`/api/builds`)
      .then((res) => res.json())
      .then((res: ApiResponse) => {
        setData(res);

        if (selected == null) return;
        let idx = res.findIndex((b => b.attrpath == selected), res);
        if (idx == -1) return;

        const list = listRef.current;
        list?.scrollToRow({
          align: "start",
          behavior: "smooth",
          index: idx
        });
      });
  }, []);

  if (data.length == 0)
    return <p>Loading...</p>;

  return (
    <>
      <h2>Builds ({data.length})</h2>
      <BuildsTable listRef={listRef} builds={data} />
    </>
  );
}
