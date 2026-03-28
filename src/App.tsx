import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import "./App.scss";

const LIMIT_PER_PAGE = 100;

interface Build {
  id: number;
  attrpath: string;
  status: "success" | "failed" | "timeout";
}

interface ApiResponse {
  total: number;
  results: Build[];
}

function Pager({
  page,
  totalPages,
  onPrev,
  onNext,
}: {
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
}) {
  return (
    <div className="pager">
      <button disabled={page === 1} onClick={onPrev}>
        prev
      </button>

      <span id="page-number">
        page {page} / {totalPages}
      </span>

      <button disabled={page === totalPages} onClick={onNext}>
        next
      </button>
    </div>
  );
}

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

function BuildsTable({
  currentPage,
  setPage,
}: {
  currentPage: number,
  setPage: (page: number) => void
}) {
  const [data, setData] = useState<Build[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetch(`/api/builds?page=${currentPage}`)
      .then((res) => res.json())
      .then((res: ApiResponse) => {
        setData(res.results);
        setTotal(res.total);
      });
  }, [currentPage]);

  const totalPages = Math.ceil(total / LIMIT_PER_PAGE);

  return (
    <>
      <h2>Builds ({total})</h2>

      <Pager
        page={currentPage}
        totalPages={totalPages}
        onPrev={() => setPage(currentPage - 1)}
        onNext={() => setPage(currentPage + 1)}
      />

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
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get("page") || 1);

  const setPage = (p: number) => {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(p));
    setSearchParams(params);
  };

  return (
      <BuildsTable currentPage={page} setPage={setPage} />
  );
}
