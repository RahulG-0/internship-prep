"use client";

import { FormEvent, useMemo, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type JsonRecord = Record<string, unknown>;

type ApiState = {
  title: string;
  data: unknown;
};

type FieldRow = {
  name: string;
  value: unknown;
  confidence: number | null;
};

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function formatLabel(value: string) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "Missing";
  if (Array.isArray(value)) return `${value.length} item${value.length === 1 ? "" : "s"}`;
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function getRecordString(record: JsonRecord | null, key: string, fallback = "Unknown") {
  const value = record?.[key];
  return typeof value === "string" && value.trim() ? value : fallback;
}

function getRecordNumber(record: JsonRecord | null, key: string) {
  const value = record?.[key];
  return typeof value === "number" ? value : null;
}

function getDocumentData(source: unknown): JsonRecord | null {
  if (!isRecord(source)) return null;
  if (isRecord(source.data)) return source.data;
  if (isRecord(source.extracted_data)) return source.extracted_data;
  return null;
}

function getConfidenceScores(source: unknown): JsonRecord {
  if (!isRecord(source) || !isRecord(source.confidence_scores)) return {};
  return source.confidence_scores;
}

function getFieldRows(source: unknown): FieldRow[] {
  const documentData = getDocumentData(source);
  const confidenceScores = getConfidenceScores(source);

  if (!documentData) return [];

  return Object.entries(documentData)
    .filter(([name]) => !["doc_type", "classification_confidence", "classification_reasoning"].includes(name))
    .map(([name, field]) => {
      if (isRecord(field) && "value" in field) {
        const confidence = typeof field.confidence === "number" ? field.confidence : null;
        return { name, value: field.value, confidence };
      }

      const score = confidenceScores[name];
      return {
        name,
        value: field,
        confidence: typeof score === "number" ? score : null,
      };
    });
}

function confidenceTone(confidence: number | null) {
  if (confidence === null) return "border-neutral-200 bg-neutral-50 text-neutral-600";
  if (confidence >= 0.85) return "border-emerald-200 bg-emerald-50 text-emerald-800";
  if (confidence >= 0.65) return "border-amber-200 bg-amber-50 text-amber-800";
  return "border-rose-200 bg-rose-50 text-rose-800";
}

function confidenceText(confidence: number | null) {
  return confidence === null ? "n/a" : `${Math.round(confidence * 100)}%`;
}

function statusTone(record: JsonRecord) {
  return record.needs_review === 1 || record.needs_review === true
    ? "border-amber-200 bg-amber-50 text-amber-800"
    : "border-emerald-200 bg-emerald-50 text-emerald-800";
}

function humanState(record: JsonRecord) {
  if (typeof record.state === "string") return formatLabel(record.state);
  return record.needs_review === 1 || record.needs_review === true ? "Needs Review" : "Approved";
}

function FieldTable({ source }: { source: unknown }) {
  const rows = getFieldRows(source);

  if (rows.length === 0) {
    return (
      <div className="rounded border border-neutral-200 bg-white p-4 text-sm text-neutral-600">
        No extracted fields available.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded border border-neutral-200 bg-white">
      <div className="grid grid-cols-[minmax(120px,0.9fr)_minmax(0,1.4fr)_96px] border-b border-neutral-200 bg-neutral-100 px-4 py-2 text-xs font-semibold uppercase text-neutral-600">
        <span>Field</span>
        <span>Value</span>
        <span>Confidence</span>
      </div>
      <div className="divide-y divide-neutral-100">
        {rows.map((row) => (
          <div
            key={row.name}
            className="grid grid-cols-[minmax(120px,0.9fr)_minmax(0,1.4fr)_96px] items-center gap-3 px-4 py-3 text-sm"
          >
            <span className="font-medium text-neutral-800">{formatLabel(row.name)}</span>
            <span className="min-w-0 break-words text-neutral-700">{formatValue(row.value)}</span>
            <span
              className={`w-fit rounded border px-2 py-1 text-xs font-semibold ${confidenceTone(row.confidence)}`}
            >
              {confidenceText(row.confidence)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function JobList({
  title,
  jobs,
  onSelect,
}: {
  title: string;
  jobs: JsonRecord[];
  onSelect: (job: JsonRecord) => void;
}) {
  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">{title}</h2>
        <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-semibold text-neutral-600">
          {jobs.length}
        </span>
      </div>
      <div className="flex flex-col gap-2">
        {jobs.length === 0 ? (
          <div className="rounded border border-neutral-200 bg-white p-4 text-sm text-neutral-600">
            No jobs in this queue.
          </div>
        ) : (
          jobs.map((job) => (
            <button
              key={String(job.id)}
              onClick={() => onSelect(job)}
              className="rounded border border-neutral-200 bg-white p-4 text-left hover:border-neutral-400"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-neutral-900">
                    {getRecordString(job, "filename", `Job ${String(job.id)}`)}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    {formatLabel(getRecordString(job, "doc_type"))} · #{String(job.id)}
                  </p>
                </div>
                <span className={`shrink-0 rounded border px-2 py-1 text-xs font-semibold ${statusTone(job)}`}>
                  {humanState(job)}
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </section>
  );
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [jobs, setJobs] = useState<JsonRecord[]>([]);
  const [result, setResult] = useState<ApiState>({
    title: "Ready",
    data: null,
  });

  const selectedRecord = isRecord(result.data) ? result.data : null;
  const reviewJobs = useMemo(
    () => jobs.filter((job) => job.needs_review === 1 || job.needs_review === true),
    [jobs],
  );
  const completedJobs = useMemo(
    () => jobs.filter((job) => job.needs_review !== 1 && job.needs_review !== true),
    [jobs],
  );

  async function readJsonResponse(response: Response) {
    const text = await response.text();
    let data: unknown = null;

    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { detail: text || "Unexpected response from API." };
    }

    if (!response.ok) {
      const detail = isRecord(data) ? data.detail : null;
      throw new Error(typeof detail === "string" ? detail : `Request failed with ${response.status}`);
    }

    return data;
  }

  async function refreshJobs(nextTitle = "GET /jobs", updateResult = true) {
    setLoading(nextTitle);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/jobs`);
      const data = await readJsonResponse(response);
      const nextJobs = Array.isArray(data) ? data.filter(isRecord) : [];
      setJobs(nextJobs);
      if (updateResult) setResult({ title: nextTitle, data });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading("");
    }
  }

  async function callRoute(title: string, path: string) {
    setLoading(title);
    setError("");

    try {
      const response = await fetch(`${API_BASE}${path}`);
      const data = await readJsonResponse(response);
      if (Array.isArray(data)) setJobs(data.filter(isRecord));
      setResult({ title, data });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading("");
    }
  }

  async function processFile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!file) {
      setError("Choose a PDF file first.");
      return;
    }

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF uploads are supported.");
      return;
    }

    setLoading("Processing file");
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/process`, {
        method: "POST",
        body: formData,
      });
      const data = await readJsonResponse(response);
      setResult({ title: "Processed Document", data });
      await refreshJobs("GET /jobs", false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading("");
    }
  }

  function lookupJob() {
    const trimmed = jobId.trim();
    if (!trimmed) {
      setError("Enter a job ID.");
      return;
    }

    callRoute(`GET /jobs/${trimmed}`, `/jobs/${trimmed}`);
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-4 py-6 text-neutral-950 sm:px-6">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-neutral-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-teal-700">IDP Pipeline</p>
            <h1 className="text-3xl font-semibold">Document review console</h1>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="rounded border border-neutral-200 bg-white px-4 py-3">
              <p className="text-2xl font-semibold">{jobs.length}</p>
              <p className="text-xs font-medium text-neutral-500">Total</p>
            </div>
            <div className="rounded border border-amber-200 bg-amber-50 px-4 py-3">
              <p className="text-2xl font-semibold text-amber-900">{reviewJobs.length}</p>
              <p className="text-xs font-medium text-amber-800">Review</p>
            </div>
            <div className="rounded border border-emerald-200 bg-emerald-50 px-4 py-3">
              <p className="text-2xl font-semibold text-emerald-900">{completedJobs.length}</p>
              <p className="text-xs font-medium text-emerald-800">Done</p>
            </div>
          </div>
        </header>

        {error && (
          <div className="rounded border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800">
            {error}
          </div>
        )}

        <section className="grid gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
          <div className="flex flex-col gap-5">
            <form
              onSubmit={processFile}
              className="flex flex-col gap-4 rounded border border-neutral-200 bg-white p-5"
            >
              <label className="flex flex-col gap-2 text-sm font-medium">
                PDF file
                <input
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(event) => {
                    const nextFile = event.target.files?.[0] ?? null;
                    if (
                      nextFile &&
                      nextFile.type !== "application/pdf" &&
                      !nextFile.name.toLowerCase().endsWith(".pdf")
                    ) {
                      setFile(null);
                      setError("Only PDF uploads are supported.");
                      return;
                    }
                    setFile(nextFile);
                    setError("");
                  }}
                  className="rounded border border-neutral-300 bg-white px-3 py-2 text-sm file:mr-4 file:rounded file:border-0 file:bg-neutral-900 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white"
                />
              </label>

              <button
                type="submit"
                disabled={loading !== ""}
                className="rounded bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-400"
              >
                {loading === "Processing file" ? "Processing..." : "Process PDF"}
              </button>
            </form>

            <div className="flex flex-col gap-3 rounded border border-neutral-200 bg-white p-5">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => refreshJobs()}
                  disabled={loading !== ""}
                  className="rounded border border-neutral-300 px-3 py-2 text-sm font-semibold hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Refresh Jobs
                </button>
                <button
                  onClick={() => callRoute("GET /jobs/exceptions", "/jobs/exceptions")}
                  disabled={loading !== ""}
                  className="rounded border border-neutral-300 px-3 py-2 text-sm font-semibold hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Review Queue
                </button>
              </div>

              <div className="flex flex-col gap-2 sm:flex-row">
                <input
                  value={jobId}
                  onChange={(event) => setJobId(event.target.value)}
                  placeholder="Job ID"
                  className="h-10 min-w-0 rounded border border-neutral-300 px-3 text-sm outline-none focus:border-teal-700"
                />
                <button
                  onClick={lookupJob}
                  disabled={loading !== ""}
                  className="rounded border border-neutral-300 px-3 py-2 text-sm font-semibold hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Open Job
                </button>
              </div>
            </div>

            <JobList title="Needs review" jobs={reviewJobs} onSelect={(job) => setResult({ title: "Selected Job", data: job })} />
            <JobList title="Completed" jobs={completedJobs} onSelect={(job) => setResult({ title: "Selected Job", data: job })} />
          </div>

          <section className="flex flex-col gap-4">
            <div className="rounded border border-neutral-200 bg-white p-5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-neutral-500">{result.title}</p>
                  <h2 className="truncate text-2xl font-semibold">
                    {getRecordString(selectedRecord, "filename", "No document selected")}
                  </h2>
                  <p className="mt-1 text-sm text-neutral-600">
                    {formatLabel(getRecordString(selectedRecord, "doc_type"))}
                    {getRecordNumber(getDocumentData(result.data), "classification_confidence") !== null
                      ? ` · ${confidenceText(getRecordNumber(getDocumentData(result.data), "classification_confidence"))} classification`
                      : ""}
                  </p>
                </div>
                {selectedRecord && (
                  <span className={`w-fit rounded border px-3 py-1.5 text-sm font-semibold ${statusTone(selectedRecord)}`}>
                    {humanState(selectedRecord)}
                  </span>
                )}
              </div>
            </div>

            <FieldTable source={result.data} />

            <details className="rounded border border-neutral-200 bg-white p-4">
              <summary className="cursor-pointer text-sm font-semibold text-neutral-700">
                Raw response
              </summary>
              <pre className="mt-4 max-h-[420px] overflow-auto rounded bg-neutral-950 p-4 text-xs leading-5 text-neutral-100">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </details>
          </section>
        </section>
      </div>
    </main>
  );
}
