(function () {
  const config = window.__PBC_CONFIG__ || {};
  const autoRefreshValue =
    typeof config.autoRefresh === "number" ? config.autoRefresh : null;
  const staticSnapshot = Boolean(config.staticSnapshot);
  const apiBase = typeof config.apiBase === "string" ? config.apiBase : "";
  const initialData = Array.isArray(config.initialData)
    ? config.initialData
    : null;

  const summaryEl = document.getElementById("summary");
  const tableBody = document.getElementById("tasks-body");
  const messageEl = document.getElementById("status-message");
  const generatedAtEls = document.querySelectorAll("[data-generated-at]");
  const autoRefreshEls = document.querySelectorAll("[data-auto-refresh]");
  const filtersSection = document.getElementById("task-filters");
  const filtersForm = document.getElementById("task-filter-form");
  const filterQueryInput = document.getElementById("task-filter-query");
  const filterStatusSelect = document.getElementById("task-filter-status");
  const filterStatusText = document.getElementById("task-filter-status-text");

  let currentData = null;
  const taskFilters = {
    query: "",
    status: "all",
  };

  function buildUrl(base, path) {
    if (!base) {
      return path;
    }
    return base.replace(/\/+$/, "") + path;
  }

  const tasksEndpoint = buildUrl(apiBase, "/api/tasks");
  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatDate(value) {
    if (!value) {
      return "—";
    }
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "—";
    }
    const pad = (num) => String(num).padStart(2, "0");
    return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate()) +
      " " +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes()) +
      ":" +
      pad(date.getSeconds())
    );
  }

  function summarizeUrl(url) {
    try {
      const parsed = new URL(url);
      let path = parsed.pathname || "";
      if (parsed.search) {
        path += parsed.search;
      }
      if (parsed.hash) {
        path += parsed.hash;
      }
      let display = (parsed.host || "") + path;
      if (!display) {
        display = url;
      }
      const maxLength = 60;
      if (display.length > maxLength) {
        display = display.slice(0, maxLength - 1) + "…";
      }
      return { display, full: parsed.href };
    } catch (error) {
      return { display: url, full: url };
    }
  }

  function hasActiveTaskFilters() {
    return Boolean(taskFilters.query) || taskFilters.status !== "all";
  }

  function applyTaskFilters(tasks) {
    if (!Array.isArray(tasks) || !tasks.length) {
      return [];
    }
    const query = taskFilters.query;
    const status = taskFilters.status;
    return tasks.filter((task) => {
      if (!task || typeof task !== "object") {
        return false;
      }
      if (status !== "all" && task.status !== status) {
        return false;
      }
      if (!query) {
        return true;
      }
      const pieces = [];
      if (task.name) {
        pieces.push(String(task.name));
      }
      if (task.slug) {
        pieces.push(String(task.slug));
      }
      if (task.start_url) {
        pieces.push(String(task.start_url));
      }
      if (!pieces.length) {
        return false;
      }
      return pieces
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }

  function updateFilterStatus(totalCount, filteredCount) {
    if (!filterStatusText) {
      return;
    }
    if (!totalCount) {
      filterStatusText.textContent = "暂无任务数据。";
      return;
    }
    if (!hasActiveTaskFilters()) {
      filterStatusText.textContent = `共 ${totalCount} 个任务。`;
      return;
    }
    if (filteredCount) {
      filterStatusText.textContent = `共 ${totalCount} 个任务 · 已筛选出 ${filteredCount} 个。`;
    } else {
      filterStatusText.textContent = `共 ${totalCount} 个任务 · 没有符合筛选条件的任务。`;
    }
  }

  function renderFilteredTasks() {
    const data = Array.isArray(currentData) ? currentData : [];
    const totalCount = data.length;
    const filtered = applyTaskFilters(data);
    const hasFilters = hasActiveTaskFilters();
    let emptyMessage = "No tasks found";
    if (hasFilters && totalCount) {
      emptyMessage = "没有符合筛选条件的任务";
    }
    renderSummary(filtered);
    renderTasks(filtered, emptyMessage);
    updateFilterStatus(totalCount, filtered.length);
  }

  function initTaskFilters() {
    if (!filtersSection) {
      return;
    }
    updateFilterStatus(0, 0);

    if (filterQueryInput) {
      filterQueryInput.addEventListener("input", () => {
        const value = filterQueryInput.value.trim().toLowerCase();
        if (taskFilters.query === value) {
          return;
        }
        taskFilters.query = value;
        if (Array.isArray(currentData)) {
          renderFilteredTasks();
        }
      });
    }

    if (filterStatusSelect) {
      filterStatusSelect.addEventListener("change", () => {
        const value = filterStatusSelect.value || "all";
        if (taskFilters.status === value) {
          return;
        }
        taskFilters.status = value;
        if (Array.isArray(currentData)) {
          renderFilteredTasks();
        }
      });
    }

    if (filtersForm) {
      filtersForm.addEventListener("reset", (event) => {
        event.preventDefault();
        taskFilters.query = "";
        taskFilters.status = "all";
        if (filterQueryInput) {
          filterQueryInput.value = "";
        }
        if (filterStatusSelect) {
          filterStatusSelect.value = "all";
        }
        if (Array.isArray(currentData)) {
          renderFilteredTasks();
        } else {
          updateFilterStatus(0, 0);
        }
      });
    }
  }

  function renderSummary(tasks) {
    if (!summaryEl) {
      return;
    }
    const totals = tasks.reduce(
      (acc, task) => {
        acc.entries += task.entries_total || 0;
        acc.documents += task.documents_total || 0;
        acc.pending += task.pending_total || 0;
        acc.tracked += task.tracked_files || 0;
        return acc;
      },
      { entries: 0, documents: 0, pending: 0, tracked: 0 }
    );

    const cards = [
      { label: "Tasks", value: tasks.length },
      { label: "Entries", value: totals.entries },
      { label: "Documents", value: totals.documents },
      { label: "Pending", value: totals.pending },
      { label: "Tracked files", value: totals.tracked },
    ]
      .map(
        (card) =>
          '<div class="card"><div class="label">' +
          escapeHtml(card.label) +
          "</div><div class=\"value\">" +
          escapeHtml(card.value) +
          "</div></div>"
      )
      .join("");

    summaryEl.innerHTML = cards;
  }

  function setTableState(message, className) {
    const cellClass = className ? ` class="${className}"` : "";
    tableBody.innerHTML =
      `<tr><td colspan="12"${cellClass}>${escapeHtml(message)}</td></tr>`;
  }

  const STATUS_CLASS = {
    ok: "status-ok",
    attention: "status-attention",
    waiting: "status-waiting",
    stale: "status-stale",
  };

  function renderTasks(tasks, emptyMessage = "No tasks found") {
    if (!Array.isArray(tasks) || !tasks.length) {
      setTableState(emptyMessage, "empty");
      return;
    }

    const rows = tasks
      .map((task) => {
        const documentTypes = Object.entries(task.document_type_counts || {})
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([key, value]) => `${escapeHtml(key)}:${escapeHtml(value)}`)
          .join(", ");
        const docTypesDisplay = documentTypes || "—";

        const nextWindow =
          task.next_run_earliest && task.next_run_latest
            ? `${formatDate(task.next_run_earliest)} ↔ ${formatDate(
                task.next_run_latest
              )}`
            : "—";

        const statusClass = STATUS_CLASS[task.status] || "status-waiting";

        let urlHtml = "—";
        if (task.start_url) {
          const summary = summarizeUrl(task.start_url);
          urlHtml =
            `<a href="${escapeHtml(task.start_url)}" target="_blank" rel="noopener" title="${escapeHtml(
              summary.full
            )}">` +
            `<span class="url-text">${escapeHtml(summary.display)}</span>` +
            '<span class="external-icon" aria-hidden="true">↗</span>' +
            "</a>";
        }

        const cacheInfo = `${
          task.pages_cached || 0
        } pages${task.page_cache_fresh ? " (fresh today)" : ""}`;
        const outputInfo = `${task.output_files || 0} files / ${
          task.output_size_bytes || 0
        } bytes`;
        const entriesValueRaw = task.entries_total;
        let entriesCount = 0;
        if (typeof entriesValueRaw === "number" && Number.isFinite(entriesValueRaw)) {
          entriesCount = entriesValueRaw;
        } else if (typeof entriesValueRaw === "string") {
          const parsed = Number.parseInt(entriesValueRaw, 10);
          if (Number.isFinite(parsed)) {
            entriesCount = parsed;
          }
        }
        const entriesString = String(entriesCount);
        const entriesLabel = escapeHtml(entriesString);
        let entriesCellHtml = entriesLabel;
        if (task.slug && !staticSnapshot) {
          const params = new URLSearchParams();
          params.set("slug", String(task.slug));
          if (task.name) {
            params.set("name", String(task.name));
          }
          params.set("count", entriesString);
          const titleText = task.name
            ? `${task.name} · 条目详情`
            : "条目详情";
          const href = `entries.html?${params.toString()}`;
          entriesCellHtml =
            `<a class="entries-link" href="${escapeHtml(href)}" title="${escapeHtml(
              titleText,
            )}">` +
            `${entriesLabel}</a>`;
        }

        return `
          <tr>
            <td class="task-name">
              <div class="name">${escapeHtml(task.name || "—")}</div>
              <div class="url">${urlHtml}</div>
            </td>
            <td class="metric">${entriesCellHtml}</td>
            <td class="metric">${escapeHtml(task.documents_total || 0)}</td>
            <td class="metric">${escapeHtml(task.downloaded_total || 0)}</td>
            <td class="metric">${escapeHtml(task.pending_total || 0)}</td>
            <td class="metric">${escapeHtml(task.tracked_files || 0)}</td>
            <td class="status-cell"><span class="${statusClass}">${escapeHtml(
          task.status_reason || "—"
        )}</span></td>
            <td class="datetime">${escapeHtml(
              formatDate(task.state_last_updated)
            )}</td>
            <td class="datetime">${escapeHtml(nextWindow)}</td>
            <td class="cache">${escapeHtml(cacheInfo)}</td>
            <td class="output">${escapeHtml(outputInfo)}</td>
            <td class="doc-types">${docTypesDisplay}</td>
          </tr>
        `;
      })
      .join("");

    tableBody.innerHTML = rows;
  }

  function renderDashboard(tasks) {
    if (!Array.isArray(tasks)) {
      currentData = null;
      renderSummary([]);
      setTableState("No tasks found", "empty");
      updateFilterStatus(0, 0);
      return;
    }
    currentData = tasks.slice();
    renderFilteredTasks();
  }

  function setGeneratedAt(value) {
    const formatted = formatDate(value);
    generatedAtEls.forEach((el) => {
      el.textContent = formatted;
    });
  }

  function setAutoRefreshDisplay(value) {
    let display;
    if (staticSnapshot) {
      display = "snapshot";
    } else if (typeof value === "number" && value > 0) {
      display = String(value);
    } else {
      display = "∞";
    }
    autoRefreshEls.forEach((el) => {
      el.textContent = display;
    });
  }

  function showMessage(text, kind = "error") {
    if (!messageEl) {
      return;
    }
    messageEl.textContent = text;
    messageEl.classList.remove("hidden", "info");
    if (kind === "info") {
      messageEl.classList.add("info");
    }
  }

  function hideMessage() {
    if (!messageEl) {
      return;
    }
    messageEl.textContent = "";
    messageEl.classList.add("hidden");
    messageEl.classList.remove("info");
  }

  async function loadData() {
    if (staticSnapshot) {
      return;
    }

    if (!currentData) {
      setTableState("Loading…", "empty");
    }

    try {
      const response = await fetch(tasksEndpoint, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      const payload = await response.json();
      if (!Array.isArray(payload)) {
        throw new Error("Unexpected response format");
      }
      renderDashboard(payload);
      hideMessage();
      setGeneratedAt(new Date());
    } catch (error) {
      console.error("Failed to load dashboard data", error);
      showMessage(`Failed to load dashboard data: ${error.message || error}`);
      if (!currentData) {
        setTableState("Unable to load data", "empty");
      }
    }
  }

  function init() {
    setAutoRefreshDisplay(autoRefreshValue);
    setGeneratedAt(config.generatedAt || null);
    initTaskFilters();

    if (initialData && initialData.length) {
      renderDashboard(initialData);
    } else if (initialData) {
      renderDashboard(initialData);
      setTableState("No tasks found", "empty");
    } else if (staticSnapshot) {
      setTableState("No data available", "empty");
    }

    if (!staticSnapshot) {
      loadData();
      if (autoRefreshValue && autoRefreshValue > 0) {
        setInterval(loadData, autoRefreshValue * 1000);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
