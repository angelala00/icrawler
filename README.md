# icrawler

Simple Python-based web crawler that downloads PDF files and converts web
pages to PDF. Provide seed URLs and the crawler will follow links on those
pages, downloading linked PDFs or rendering HTML pages to PDF files.

## Usage

```
python -m icrawler.crawler [--delay N] [--jitter M] <output_dir> <url1> [<url2> ...]
```

`--delay` specifies a minimum pause (in seconds) between HTTP requests while
`--jitter` adds a random extra wait time up to the given value. This helps
avoid hitting remote servers too aggressively.

See `requirements.txt` for dependencies.

## PBC 监管公告任务

`icrawler.pbc_monitor` 支持通过配置文件固化抓取任务（默认读取项目根目录下的
`pbc_config.json`）。示例：

```json
{
  "output_dir": "/opt/dl",
  "start_url": "http://www.pbc.gov.cn/zhengwugongkai/4081330/4406346/4406348/index.html",
  "state_file": "state.json",
  "artifact_dir": "artifacts"
}
```

执行一次巡检：

```
python -m icrawler.pbc_monitor --run-once
```

也可以传入其他配置：

```
python -m icrawler.pbc_monitor --config my_config.json --run-once
```

命令行参数会覆盖配置文件中的对应字段。

调试结构时可使用：

```
python -m icrawler.pbc_monitor --dump-structure structure.json
```

若不指定文件路径（仅写 `--dump-structure`），解析结果会直接打印到终端。
输出 JSON 中除了 `entries` 之外，还会包含 `pages` 列表，记录每页的
`pagination` 信息（如 `next`/`prev` 链接），便于判断是否还有后续分页。

确认结构后，可使用结构文件驱动下载，无需再次遍历网页：

```
python -m icrawler.pbc_monitor --download-from-structure
```

该命令会读取默认的结构 JSON（位于 `artifacts/structure/structure.json`），
根据其中的 `entries` 下载附件，并继续使用 `state.json` 标记已下载记录。
若需使用其他路径，可在命令后追加文件名。

为了避免频繁请求，可以先将起始页面下载到本地：

```
python -m icrawler.pbc_monitor --fetch-page page.html
```

同样支持不带参数直接输出 HTML 内容。

随后可以在本地多次解析，不再触发网络请求：

```
python -m icrawler.pbc_monitor --dump-from-file page.html
```

该命令会打印单页的结构和 `pagination` 元数据，并同步写入 `pages`
数组，后续可据此判断是否需要继续抓取下一页。

### 推荐工作流

1. 准备配置文件（例如 `pbc_config.json`），写入 `start_url`、`output_dir`、`state_file`
   等参数。
2. `--fetch-page` 抓取首页 HTML：
   `python -m icrawler.pbc_monitor --fetch-page page1.html`
   （若不带文件名将默认写入 `page.html`，传入 `-` 可输出到终端）
3. `--dump-from-file` 离线解析 `page1.html`，确认 `entries` 与 `pagination`：
   `python -m icrawler.pbc_monitor --dump-from-file page1.html`
   （若不带文件名默认读取 `page.html`，传入 `-` 可解析标准输入）
4. 若 `pagination.next` 存在，可选择：
   - 手动：继续 `--fetch-page page2.html` → `--dump-from-file page2.html`
     直到 `pagination.next` 为空；
   - 自动：
     - `python -m icrawler.pbc_monitor --dump-structure`（默认写入
       `structure.json`，可在命令后跟自定义路径，或传 `-` 输出到终端）
       该命令会在线遍历全部分页并把结构写入指定文件，其中 `pages`
       数组列出每页的分页信息。
    - `python -m icrawler.pbc_monitor --download-from-structure`：
      默认读取 `artifacts/structure/structure.json` 并下载附件，避免再次遍历网页
      （可在命令后指定其他结构文件）。命令会保存结构中的 HTML 详情页、WPS/Word
      及 PDF 等文件。
     - 或用 `python -m icrawler.pbc_monitor --run-once`：从配置的起始页面开始
       实时遍历分页并下载附件（同样包含 HTML 详情页），`state.json` 会记录已下载链接。
    - 若担心本地文件被手动删除，可追加 `--verify-local`，执行时会检查
       `state.json` 中记录的路径是否仍然存在，缺失则重新下载。
    - 历史附件如需切换到新的路径式命名，可运行
      `python scripts/normalize_filenames.py` 自动重命名并更新 `state.json`。
5. 结构确认无误后，可选择基于 `--download-from-structure` 的离线下载，或
   直接执行 `--run-once`（或循环模式）进行在线抓取。`state.json` 会记录已
   下载的链接，方便后续增量更新。

### 默认输出目录

- 所有中间文件默认写入 `--artifact-dir`（默认 `./artifacts`）下的子目录：
  - `pages/`：缓存抓取到的原始 HTML（`--fetch-page`、`--dump-structure`、
    `--run-once` 都会落到这里）。
  - `structure/`：`--dump-structure` 输出的结构化 JSON。
  - `state/`：`state.json` 持久化下载历史。
- 若未显式配置 `state_file`，默认位置为 `artifacts/state/state.json`。
- 手动传入自定义文件名时仍可使用绝对路径；若提供相对路径，则会挂在
  `artifact_dir` 对应子目录下。
- 可通过 `--artifact-dir`（或配置文件中的 `artifact_dir`）修改上述根目录。
