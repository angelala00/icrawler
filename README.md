# icrawler

Simple Python-based web crawler that downloads PDF files and converts web
pages to PDF. Provide seed URLs and the crawler will follow links on those
pages, downloading linked PDFs or rendering HTML pages to PDF files.

## Command Line Entrypoints

### Unified portal (`python -m icrawler`)

Launch the combined monitoring portal – a FastAPI app that surfaces the live
dashboard and the policy search interface in one place:

```
python -m icrawler --host 0.0.0.0 --port 8000
```

By default the portal reads tasks from `pbc_config.json` and auto-refreshes
every 30 seconds. Useful options:

- `--config` / `--artifact-dir` / `--task` mirror the monitor CLI and scope the
  data that is displayed.
- `--refresh` controls the auto-refresh interval (set `0` to disable).
- `--disable-search` turns off the policy finder UI entirely.
- `--search-state task=/path/state.json` (repeatable) lets you point the search
  index at explicit state files when auto-discovery is not sufficient. Per-task
  flags such as `--search-zhengwugongkai-chinese-regulations` remain available
  for compatibility.
- `--search-default-topk` and `--search-max-topk` adjust the default/maximum
  result counts returned from the `/api/search` endpoint and the UI.
- `--once` renders the HTML snapshot once and exits; `--json` dumps the current
  task overview as JSON.

When the portal detects that the required state files are missing it keeps the
search tab visible but shows a message explaining why it is disabled. This
command is equivalent to the old `python -m icrawler.dashboard` behaviour.

### PDF crawler (`python -m icrawler.crawler`)

```
python -m icrawler.crawler [--delay N] [--jitter M] <output_dir> <url1> [<url2> ...]
```

`--delay` sets the base pause between requests, and `--jitter` adds up to that
many random seconds so servers are not hammered. Install the dependencies from
`requirements.txt` before running.

## PBC Monitor Quick Start

`icrawler.pbc_monitor` loads tasks from `pbc_config.json` (multi-task configs are
supported). Minimal example:

```json
{
  "artifact_dir": "artifacts",
  "tasks": [
    {
      "name": "zhengwugongkai_administrative_normative_documents",
      "start_url": "http://www.pbc.gov.cn/.../index.html",
      "parser": "icrawler.parser_policy"
    }
  ]
}
```

Common commands (CLI flags override config fields):

- `python -m icrawler.pbc_monitor --cache-start-page` – cache the starting page
  HTML (reuses the cached file unless you add `--refresh-pages`; pass `-` to
  stream to stdout).
- `python -m icrawler.pbc_monitor --preview-page-structure` – parse a cached
  page and preview its extracted entries (defaults to the file produced by
  `--cache-start-page`).
- `python -m icrawler.pbc_monitor --cache-listing` – cache every listing page
  under `artifacts/pages/<task>/` (reuses existing cached pages and only fetches
  missing ones unless you pass `--refresh-pages` / `--no-use-cached-pages`).
- `python -m icrawler.pbc_monitor --build-page-structure` – build a full
  listing snapshot. Cached HTML is reused by default.
- `--no-use-cached-pages` / `--refresh-pages` – force retrieval of fresh listing
  pages even when cached copies exist.
- `python -m icrawler.pbc_monitor --download-from-structure` – download
  attachments from an existing snapshot without recrawling listing pages.
- `python -m icrawler.pbc_monitor --run-once` – single monitoring pass that
  fetches listing pages online and downloads new attachments. If the
  starting listing page was cached earlier the same day, the cached copy is
  reused to avoid redundant network requests; older caches trigger a fresh
  fetch automatically. The continuous mode (no `--run-once`) reuses the same
  freshness rule before each iteration, so pages cached today are reused and
  anything older is refreshed when the loop wakes up. After each run, the
  tool logs a per-task summary that includes the number of pages processed,
  entries/documents observed, and how many files were freshly downloaded or
  reused from existing data.

### Typical Workflow

1. Define tasks in `pbc_config.json` (single-task JSON is also accepted).
2. Cache the first page for inspection:
   `python -m icrawler.pbc_monitor --cache-start-page`.
3. Preview that page offline:
   `python -m icrawler.pbc_monitor --preview-page-structure`.
4. Cache the full listing once (reuses existing cached pages by default):
   `python -m icrawler.pbc_monitor --cache-listing`.
5. Build the full structure snapshot:
   `python -m icrawler.pbc_monitor --build-page-structure`.
   Add `--refresh-pages` or `--no-use-cached-pages` if you need to bypass cached HTML.
6. Download attachments based on the snapshot:
   `python -m icrawler.pbc_monitor --download-from-structure`.
   Alternatively run `--run-once` (or loop without `--run-once`) for an online
   crawl that fetches fresh pages and downloads files in one go.

When detail页被下载时，程序会自动解析页面里的附件链接并一并下载，所有对应关系
会写入 `state.json`（含 `local_path`），方便后续追踪。

`output_dir` is optional; when omitted or set to a simple name, files default to
`<artifact_dir>/downloads/<task>/`. Provide an absolute path if you prefer a
custom location.

State tracking and structure snapshots also adopt per-task defaults:

- `state_file` → `<artifact_dir>/downloads/<task>_state.json`
- `structure_file` → `<artifact_dir>/structure/<task>_structure.json`

You can override these via config (`state_file` / `structure_file`) or CLI
(`--state-file`, `--build-page-structure`, `--download-from-structure`).

### Monitoring dashboard (`python -m icrawler.dashboard`)

Run the streamlined status board without the search tab:

```
python -m icrawler.dashboard
```

This entry point only serves the monitoring metrics (task progress, download
counts, cache freshness, scheduling windows, etc.) and exposes the same
`/api/tasks` JSON endpoint for automation. Search is intentionally disabled
here – use the unified portal (`python -m icrawler`) if you need the embedded
policy finder.

Useful flags:

- `--port` / `--host` – bind address for the web UI (default `0.0.0.0:8000`).
- `--refresh` – change the auto-refresh interval (set to `0` to disable).
- `--once` – render the HTML dashboard once to stdout, handy for static
  snapshots.
- `--json` – emit the current statistics as JSON and exit.
- `--task <name>` – focus on a single configured task.

### Artifacts

All generated files live under `artifact_dir` (default `./artifacts`):

- `pages/` – cached HTML from fetch/snapshot operations.
- `structure/` – JSON snapshots generated by `--build-page-structure`.
- `downloads/` – downloaded files and per-task state JSON.

Relative filenames supplied on the CLI are resolved inside these folders; use an
absolute path to opt out. Adjust the root via `--artifact-dir` or the config.

## Policy Finder API

The fuzzy policy search helper located in `searcher/policy_finder.py` can be
exposed over HTTP for integration with other services. Start the API server
with:

```
python -m searcher.api_server --host 0.0.0.0 --port 8001
```

By default the server automatically locates every task defined in
`pbc_config.json` (for example the six zhengwugongkai/tiaofasi monitors) using
the same rules as the CLI utility. Pass `--state task=/path/state.json` or the
per-task flags such as `--zhengwugongkai-chinese-regulations` (legacy aliases
`--policy-updates` / `--regulator-notice` are still accepted) to override the
discovery when needed.

Send either a GET or POST request to `/search` to run a query. Example GET
request:

```
curl "http://localhost:8001/search?query=中国人民银行公告"
```

POST requests accept JSON and support additional parameters:

```
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "金融稳定", "topk": 3, "include_documents": false}' \
     http://localhost:8001/search
```

Responses contain the matched entries sorted by score along with metadata such
as document number, year and resolved file path.
