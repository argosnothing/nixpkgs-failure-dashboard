import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import "./App.scss";

interface Build {
  id: number;
  attrpath: string;
  status: "success" | "failed" | "timeout";
}

type ApiResponse = Build[];

function BuildEntry({ build }: { build: Build }) {
  return (
    <tr>
      <td className="attrpath">{build.attrpath}</td>
      <td className="status">
        {build.status}
      </td>
      <td>
        <a href={`/build-logs/${build.attrpath}.log`} target="_blank">
          view
        </a>
      </td>
    </tr>
  );
}

function BuildsTable() {
  const [data, setData] = useState<Build[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetch(`/api/builds`)
      .then((res) => res.json())
      .then((res: ApiResponse) => {
        setData(res);
        setTotal(res.length);
      });
  }, []);

  return (
    <>
      <h2>Builds ({total})</h2>

      <table>
        <thead>
          <tr>
            <th>Attrpath</th>
            <th>Status</th>
            <th>Log</th>
          </tr>
        </thead>
        <tbody>
          {data.map((b) => (
            <BuildEntry key={b.id} build={b} />
          ))}
        </tbody>
      </table>
    </>
  );
}

export default function App() {
  const [searchParams, _] = useSearchParams();
  console.log(searchParams);

  return (
      <BuildsTable />
  );
}
