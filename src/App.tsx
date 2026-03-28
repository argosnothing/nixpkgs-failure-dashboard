import { useEffect, useState } from "react";
import { List, type RowComponentProps } from "react-window";

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

function BuildsTable({ builds }: { builds: Build[]; }) {
    return (
      <List
        className="builds-table"
        rowComponent={BuildEntry}
        rowCount={builds.length}
        rowHeight={25}
        rowProps={{ builds }}
      />
    )
}

export default function App() {
  // const [searchParams, _] = useSearchParams();
  // console.log(searchParams);

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

  console.log(data.length);

  return (
    <>
      <h2>Builds ({data.length})</h2>
      <BuildsTable builds={data} />
    </>
  );
}
