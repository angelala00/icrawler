(function () {
  const config = window.__PBC_CONFIG__ || {};
  const staticSnapshot = Boolean(config.staticSnapshot);
  const apiBase = typeof config.apiBase === "string" ? config.apiBase : "";

  const generatedAtEls = document.querySelectorAll("[data-generated-at]");
  const titleEl = document.getElementById("entries-title");
  const subtitleEl = document.getElementById("entries-subtitle");
  const metaEl = document.getElementById("entries-meta");
  const messageEl = document.getElementById("entries-message");
  const bodyEl = document.getElementById("entries-body");

  const params = new URLSearchParams(window.location.search);
  const slugParam = params.get("slug");
  const slug = slugParam ? slugParam.trim() : "";
  const fallbackNameParam = params.get("name");
  const fallbackName = fallbackNameParam ? fallbackNameParam.trim() : "";
  const fallbackCountParam = params.get("count");
  const fallbackCount = fallbackCountParam ? fallbackCountParam.trim() : "";

  function buildUrl(base, path) {
    if (!base) {
      return path;
    }
    return base.replace(/\/+$/, "") + path;
  }

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

  function setGeneratedAt(value) {
    const formatted = formatDate(value);
    generatedAtEls.forEach((el) => {
      el.textContent = formatted;
    });
  }

  function clearMessage() {
    if (!messageEl) {
      return;
    }
    messageEl.textContent = "";
    messageEl.classList.add("hidden");
    messageEl.classList.remove("info");
  }

  function showMessage(text, kind = "error") {
    if (!messageEl) {
      return;
    }
    messageEl.textContent = text;
    messageEl.classList.remove("hidden");
    messageEl.classList.toggle("info", kind === "info");
  }

  function updateHeader(task, entries) {
    const info = task && typeof task === "object" ? task : null;
    const name = info && info.name ? String(info.name) : fallbackName;
    const slugDisplay = slug || (info && info.slug) || "";
    if (titleEl) {
      titleEl.textContent = name || "条目详情";
    }
    document.title = name ? `${name} · 条目详情` : "任务条目详情";
    if (subtitleEl) {
      const parts = [];
      if (slugDisplay) {
        parts.push(`任务标识 ${slugDisplay}`);
      }
      let entriesCount = null;
      if (Array.isArray(entries)) {
        entriesCount = entries.length;
      } else if (info && typeof info.entries_total === "number") {
        entriesCount = info.entries_total;
      } else if (fallbackCount) {
        entriesCount = fallbackCount;
      }
      if (entriesCount !== null && entriesCount !== "") {
        parts.push(`条目数 ${entriesCount}`);
      }
      subtitleEl.textContent = parts.join(" · ");
    }
  }

  function updateMeta(task, entries) {
    if (!metaEl) {
      return;
    }
    const info = task && typeof task === "object" ? task : null;
    const parts = [];
    let count = null;
    if (Array.isArray(entries)) {
      count = entries.length;
    } else if (info && typeof info.entries_total === "number") {
      count = info.entries_total;
    } else if (fallbackCount) {
      count = fallbackCount;
    }
    if (count !== null && count !== "") {
      parts.push(`条目 ${count}`);
    }
    if (info && typeof info.documents_total === "number") {
      parts.push(`文档 ${info.documents_total}`);
    }
    if (info && typeof info.downloaded_total === "number") {
      parts.push(`已下载 ${info.downloaded_total}`);
    }
    if (info && typeof info.pending_total === "number") {
      parts.push(`待下载 ${info.pending_total}`);
    }
    if (info && info.state_last_updated) {
      parts.push(`更新 ${formatDate(info.state_last_updated)}`);
    }
    metaEl.textContent = parts.join(" · ") || "—";
  }

  function renderEntriesList(entries) {
    if (!Array.isArray(entries) || entries.length === 0) {
      return '<p class="empty">暂无条目。</p>';
    }
    const items = entries
      .map((entry, index) => {
        const serialValue =
          entry && typeof entry.serial === "number" && Number.isFinite(entry.serial)
            ? entry.serial
            : index + 1;
        const serialHtml =
          '<span class="entries-list__serial">#' + escapeHtml(serialValue) + "</span>";
        const titleText = entry && entry.title ? entry.title : "未命名条目";
        const titleHtml =
          '<span class="entries-list__title">' + escapeHtml(titleText) + "</span>";
        const header =
          '<div class="entries-list__header">' + serialHtml + titleHtml + "</div>";
        const remarkHtml =
          entry && entry.remark
            ? '<div class="entries-list__remark">' + escapeHtml(entry.remark) + "</div>"
            : "";
        const documents = Array.isArray(entry && entry.documents)
          ? entry.documents
          : [];
        let documentsHtml;
        if (documents.length) {
          const docItems = documents
            .map((doc) => {
              const titleValue =
                doc && doc.title
                  ? doc.title
                  : doc && doc.url
                  ? doc.url
                  : "未命名文档";
              const link =
                doc && doc.url
                  ? '<a href="' +
                    escapeHtml(doc.url) +
                    '" target="_blank" rel="noopener">' +
                    escapeHtml(titleValue) +
                    "</a>"
                  : '<span>' + escapeHtml(titleValue) + "</span>";
              const metaPieces = [];
              if (doc && doc.type) {
                metaPieces.push(
                  '<span class="entries-documents__meta">' +
                    escapeHtml(doc.type) +
                    "</span>"
                );
              }
              if (doc && doc.local_path) {
                metaPieces.push(
                  '<span class="entries-documents__meta"><code>' +
                    escapeHtml(doc.local_path) +
                    "</code></span>"
                );
              }
              if (doc && doc.downloaded) {
                metaPieces.push('<span class="entries-documents__badge">已下载</span>');
              }
              const metaHtml = metaPieces.length ? " " + metaPieces.join(" ") : "";
              return `<li>${link}${metaHtml}</li>`;
            })
            .join("");
          documentsHtml = `<ul class="entries-documents">${docItems}</ul>`;
        } else {
          documentsHtml =
            '<div class="entries-documents entries-documents--empty">暂无关联文档</div>';
        }
        return `<li class="entries-list__item">${header}${remarkHtml}${documentsHtml}</li>`;
      })
      .join("");
    return `<ol class="entries-list">${items}</ol>`;
  }

  function showLoading() {
    if (bodyEl) {
      bodyEl.innerHTML = '<p class="empty">正在加载条目…</p>';
    }
    clearMessage();
  }

  function showEmpty() {
    if (bodyEl) {
      bodyEl.innerHTML = '<p class="empty">暂无条目信息。</p>';
    }
  }

  async function fetchTaskEntries(slugValue) {
    const response = await fetch(
      buildUrl(apiBase, `/api/tasks/${encodeURIComponent(slugValue)}/entries`),
      {
        headers: { Accept: "application/json" },
        cache: "no-store",
      },
    );
    if (!response.ok) {
      let errorDetail = `${response.status} ${response.statusText}`;
      try {
        const errorPayload = await response.json();
        if (errorPayload && typeof errorPayload.error === "string") {
          errorDetail = errorPayload.error;
        }
      } catch (error) {
        // ignore JSON parsing issues
      }
      throw new Error(errorDetail);
    }
    const payload = await response.json();
    const entries = Array.isArray(payload.entries) ? payload.entries : [];
    const taskInfo = payload && typeof payload.task === "object" ? payload.task : null;
    return { entries, task: taskInfo };
  }

  async function loadEntries() {
    if (!slug) {
      showMessage("缺少任务标识，无法加载条目。");
      showEmpty();
      return;
    }
    if (staticSnapshot) {
      showMessage("当前页面基于静态快照，无法查看条目明细。", "info");
      if (bodyEl) {
        bodyEl.innerHTML =
          '<p class="empty">静态快照不包含条目明细，请返回仪表盘查看概览。</p>';
      }
      updateMeta(null, null);
      return;
    }

    showLoading();
    try {
      const { entries, task } = await fetchTaskEntries(slug);
      updateHeader(task, entries);
      updateMeta(task, entries);
      if (bodyEl) {
        bodyEl.innerHTML = renderEntriesList(entries);
      }
      clearMessage();
    } catch (error) {
      console.error("Unable to load entries", error);
      showMessage(`无法加载条目：${error.message || error}`);
      updateMeta(null, null);
      showEmpty();
    }
  }

  function init() {
    setGeneratedAt(config.generatedAt || null);
    updateHeader(null, null);
    updateMeta(null, null);
    loadEntries();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
