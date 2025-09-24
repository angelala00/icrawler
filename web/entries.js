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
  const filtersSection = document.getElementById("entries-filters");
  const slugFiltersContainer = document.getElementById("entries-slug-tags");
  const abolishFilterButton = document.getElementById("entries-filter-abolish");
  const searchSection = document.getElementById("search-panel");
  const searchForm = document.getElementById("search-form");
  const searchQueryInput = document.getElementById("search-query");
  const searchTopkInput = document.getElementById("search-topk");
  const searchIncludeDocumentsInput = document.getElementById(
    "search-include-documents",
  );
  const searchSubmitButton = document.getElementById("search-submit");
  const searchResultsList = document.getElementById("search-results");
  const searchStatusEl = document.getElementById("search-status");

  const params = new URLSearchParams(window.location.search);
  const slugParams = params.getAll("slug");
  const slugValues =
    slugParams.length > 0
      ? slugParams
      : params.get("slug")
      ? [params.get("slug")]
      : [];
  const initialSlugs = slugValues
    .join(",")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  const primarySlug = initialSlugs.length ? initialSlugs[0] : "";
  const fallbackNameParam = params.get("name");
  const fallbackName = fallbackNameParam ? fallbackNameParam.trim() : "";
  const fallbackCountParam = params.get("count");
  const fallbackCount = fallbackCountParam ? fallbackCountParam.trim() : "";

  const state = {
    selectedSlugs: new Set(initialSlugs),
    slugOptions: [],
    showAbolishOnly: false,
  };
  const slugButtons = new Map();
  const entriesCache = new Map();
  const pendingLoads = new Map();
  const searchConfig =
    config && typeof config.search === "object" && config.search
      ? config.search
      : {};
  const searchEnabled = Boolean(searchConfig.enabled) && !staticSnapshot;
  const searchEndpoint = buildUrl(
    apiBase,
    typeof searchConfig.endpoint === "string" && searchConfig.endpoint
      ? searchConfig.endpoint
      : "/api/search",
  );
  const searchDefaultTopk =
    typeof searchConfig.defaultTopk === "number" && searchConfig.defaultTopk > 0
      ? searchConfig.defaultTopk
      : 5;
  const searchMaxTopk =
    typeof searchConfig.maxTopk === "number" && searchConfig.maxTopk > 0
      ? searchConfig.maxTopk
      : 50;
  const searchIncludeDocumentsDefault =
    searchConfig.includeDocuments === false ? false : true;
  const searchDisabledReason = staticSnapshot
    ? "静态快照模式下无法检索政策条目。"
    : typeof searchConfig.reason === "string"
    ? searchConfig.reason
    : "";
  const searchSubmitLabel = searchSubmitButton
    ? searchSubmitButton.textContent
    : "";

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

  function registerKnownSlug(slugValue, task) {
    if (!slugValue && slugValue !== 0) {
      return;
    }
    const slugString = String(slugValue).trim();
    if (!slugString) {
      return;
    }
    const name =
      task && typeof task === "object" && task.name ? String(task.name) : "";
    const existingIndex = state.slugOptions.findIndex(
      (item) => item.slug === slugString,
    );
    if (existingIndex >= 0) {
      if (name && !state.slugOptions[existingIndex].name) {
        state.slugOptions[existingIndex].name = name;
      }
      return;
    }
    state.slugOptions.push({ slug: slugString, name });
  }

  function updateSlugButtonsState() {
    slugButtons.forEach((button, slugValue) => {
      if (state.selectedSlugs.has(slugValue)) {
        button.classList.add("is-active");
      } else {
        button.classList.remove("is-active");
      }
    });
  }

  function handleSlugToggle(slugValue) {
    const slugString = String(slugValue);
    if (state.selectedSlugs.has(slugString)) {
      state.selectedSlugs.delete(slugString);
    } else {
      state.selectedSlugs.add(slugString);
    }
    updateSlugButtonsState();
    refreshEntries();
  }

  function renderSlugFilters() {
    if (!slugFiltersContainer) {
      return;
    }
    slugFiltersContainer.innerHTML = "";
    slugButtons.clear();

    if (!state.slugOptions.length) {
      const empty = document.createElement("p");
      empty.className = "entries-filters__hint";
      empty.textContent = "暂无任务数据。";
      slugFiltersContainer.appendChild(empty);
      return;
    }

    state.slugOptions.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "entries-filter-tag";
      button.dataset.slug = option.slug;
      const labelParts = [];
      if (option.name) {
        labelParts.push(option.name);
      }
      labelParts.push(option.slug);
      button.textContent = labelParts.join(" · ");
      button.addEventListener("click", () => handleSlugToggle(option.slug));
      slugFiltersContainer.appendChild(button);
      slugButtons.set(option.slug, button);
    });

    updateSlugButtonsState();
  }

  function containsKeyword(value, keyword) {
    return typeof value === "string" && value.includes(keyword);
  }

  function isAbolishEntry(entry) {
    if (!entry || typeof entry !== "object") {
      return false;
    }
    const keyword = "废止";
    if (containsKeyword(entry.title, keyword)) {
      return true;
    }
    if (containsKeyword(entry.remark, keyword)) {
      return true;
    }
    const documents = Array.isArray(entry.documents) ? entry.documents : [];
    return documents.some((doc) =>
      containsKeyword(doc && doc.title, keyword) ||
      containsKeyword(doc && doc.remark, keyword) ||
      containsKeyword(doc && doc.local_path, keyword) ||
      containsKeyword(doc && doc.url, keyword),
    );
  }

  function normalizeEntries(entries, slugValue, task) {
    const list = Array.isArray(entries) ? entries : [];
    return list.map((entry, index) => {
      const data = entry && typeof entry === "object" ? entry : {};
      const serial =
        typeof data.serial === "number" && Number.isFinite(data.serial)
          ? data.serial
          : index + 1;
      const documents = Array.isArray(data.documents) ? data.documents : [];
      const taskName =
        task && typeof task === "object" && task.name ? String(task.name) : "";
      return {
        ...data,
        serial,
        documents,
        __taskSlug: slugValue,
        __taskName: taskName,
        __isAbolish: isAbolishEntry(data),
      };
    });
  }

  function computeDocsCount(entries) {
    if (!Array.isArray(entries)) {
      return 0;
    }
    return entries.reduce((acc, entry) => {
      const docs = Array.isArray(entry && entry.documents) ? entry.documents : [];
      return acc + docs.length;
    }, 0);
  }

  function formatScore(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "—";
    }
    return value.toFixed(3);
  }

  function clampTopk(value) {
    if (value === null || value === undefined || value === "") {
      return searchDefaultTopk;
    }
    const parsed = Number.parseInt(value, 10);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      throw new Error("invalid_topk");
    }
    return Math.max(1, Math.min(searchMaxTopk, parsed));
  }

  function showSearchStatus(text, kind = "error") {
    if (!searchStatusEl) {
      return;
    }
    searchStatusEl.textContent = text;
    searchStatusEl.classList.remove("hidden", "info");
    searchStatusEl.classList.toggle("info", kind === "info");
  }

  function hideSearchStatus() {
    if (!searchStatusEl) {
      return;
    }
    searchStatusEl.textContent = "";
    searchStatusEl.classList.add("hidden");
    searchStatusEl.classList.remove("info");
  }

  function setSearchLoading(isLoading) {
    if (searchSubmitButton) {
      searchSubmitButton.disabled = Boolean(isLoading);
      searchSubmitButton.textContent = isLoading
        ? "检索中…"
        : searchSubmitLabel;
    }
    if (searchForm) {
      searchForm.classList.toggle("is-loading", Boolean(isLoading));
    }
  }

  function renderSearchResults(results) {
    if (!searchResultsList) {
      return;
    }
    if (!Array.isArray(results) || results.length === 0) {
      searchResultsList.innerHTML =
        '<li class="empty">未找到匹配结果。</li>';
      return;
    }

    const items = results
      .map((result) => {
        const title = escapeHtml(result.title || "未命名条目");
        const score = escapeHtml(formatScore(result.score));
        const pills = [];
        if (result.doc_no) {
          pills.push(`<span class="pill">文号 ${escapeHtml(result.doc_no)}</span>`);
        }
        if (result.year) {
          pills.push(`<span class="pill">${escapeHtml(result.year)}</span>`);
        }
        if (result.doctype) {
          pills.push(`<span class="pill">${escapeHtml(result.doctype)}</span>`);
        }
        if (result.agency) {
          pills.push(`<span class="pill">${escapeHtml(result.agency)}</span>`);
        }
        const meta = pills.length
          ? `<div class="result-meta">${pills.join(" ")}</div>`
          : "";
        const remark = result.remark
          ? `<div class="result-remark">${escapeHtml(result.remark)}</div>`
          : "";
        const bestPath = result.best_path
          ? `<div class="result-path"><span class="label">最佳路径</span><code>${escapeHtml(
              result.best_path,
            )}</code></div>`
          : "";

        let documentsHtml = "";
        if (Array.isArray(result.documents) && result.documents.length) {
          const documents = result.documents
            .map((doc) => {
              const parts = [];
              if (doc.title) {
                parts.push(`<span class="doc-title">${escapeHtml(doc.title)}</span>`);
              }
              if (doc.type) {
                parts.push(`<span class="doc-type">${escapeHtml(doc.type)}</span>`);
              }
              if (doc.url) {
                parts.push(
                  `<a href="${escapeHtml(doc.url)}" target="_blank" rel="noopener">原文</a>`,
                );
              }
              if (!parts.length && doc.local_path) {
                parts.push(`<code>${escapeHtml(doc.local_path)}</code>`);
              }
              return `<li>${parts.join(" · ") || "文档"}</li>`;
            })
            .join("");
          documentsHtml = `
            <details class="result-documents">
              <summary>相关文档 (${escapeHtml(result.documents.length)})</summary>
              <ul>${documents}</ul>
            </details>
          `;
        }

        return `
          <li class="search-result">
            <div class="result-header">
              <div class="result-title">${title}</div>
              <div class="result-score">相似度 ${score}</div>
            </div>
            ${meta}
            ${remark}
            ${bestPath}
            ${documentsHtml}
          </li>
        `;
      })
      .join("");

    searchResultsList.innerHTML = items;
  }

  async function performSearch(query, topk, includeDocuments) {
    if (!searchEnabled) {
      return;
    }
    setSearchLoading(true);
    showSearchStatus("检索中…", "info");
    try {
      const response = await fetch(searchEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          query,
          topk,
          include_documents: includeDocuments,
        }),
      });
      if (!response.ok) {
        let message = `${response.status} ${response.statusText}`;
        try {
          const errorPayload = await response.json();
          if (errorPayload && typeof errorPayload === "object") {
            if (typeof errorPayload.reason === "string") {
              message = `${errorPayload.error || "error"}: ${errorPayload.reason}`;
            } else if (errorPayload.error) {
              message = String(errorPayload.error);
            }
          }
        } catch (parseError) {
          // Ignore JSON parsing errors for error responses.
        }
        throw new Error(message);
      }
      const payload = await response.json();
      if (!payload || typeof payload !== "object") {
        throw new Error("Unexpected response format");
      }
      const results = Array.isArray(payload.results) ? payload.results : [];
      renderSearchResults(results);
      const count =
        typeof payload.result_count === "number"
          ? payload.result_count
          : results.length;
      showSearchStatus(`共返回 ${count} 条结果。`, "info");
    } catch (error) {
      console.error("Search request failed", error);
      showSearchStatus(`检索失败：${error.message || error}`);
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleSearchSubmit(event) {
    event.preventDefault();
    if (!searchEnabled) {
      return;
    }
    const query = searchQueryInput ? searchQueryInput.value.trim() : "";
    if (!query) {
      showSearchStatus("请输入关键词。");
      if (searchResultsList) {
        searchResultsList.innerHTML =
          '<li class="empty">请输入关键词开始检索。</li>';
      }
      if (searchQueryInput) {
        searchQueryInput.focus();
      }
      return;
    }

    let topk = searchDefaultTopk;
    if (searchTopkInput) {
      try {
        topk = clampTopk(searchTopkInput.value);
      } catch (error) {
        showSearchStatus(`返回数量范围为 1 - ${searchMaxTopk}`);
        searchTopkInput.focus();
        return;
      }
    }

    const includeDocuments = searchIncludeDocumentsInput
      ? Boolean(searchIncludeDocumentsInput.checked)
      : searchIncludeDocumentsDefault;

    await performSearch(query, topk, includeDocuments);
  }

  function initSearch() {
    if (!searchSection) {
      return;
    }

    if (!searchEnabled) {
      searchSection.classList.add("search-panel--disabled");
      if (searchForm) {
        searchForm.classList.add("hidden");
      }
      if (searchStatusEl) {
        const reason = searchDisabledReason || "检索功能当前不可用。";
        searchStatusEl.textContent = reason;
        searchStatusEl.classList.remove("hidden");
        searchStatusEl.classList.add("info");
      }
      return;
    }

    if (searchTopkInput) {
      searchTopkInput.min = "1";
      searchTopkInput.max = String(searchMaxTopk);
      searchTopkInput.value = String(searchDefaultTopk);
    }
    if (searchIncludeDocumentsInput) {
      searchIncludeDocumentsInput.checked = Boolean(
        searchIncludeDocumentsDefault,
      );
    }
    if (searchResultsList) {
      searchResultsList.innerHTML =
        '<li class="empty">输入关键词后开始检索。</li>';
    }
    hideSearchStatus();

    if (searchForm) {
      searchForm.addEventListener("submit", handleSearchSubmit);
    }
  }

  async function fetchTasksList() {
    const response = await fetch(buildUrl(apiBase, "/api/tasks"), {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`;
      try {
        const payload = await response.json();
        if (payload && typeof payload.error === "string") {
          detail = payload.error;
        }
      } catch (error) {
        // ignore
      }
      throw new Error(detail);
    }
    try {
      const payload = await response.json();
      return Array.isArray(payload) ? payload : [];
    } catch (error) {
      throw new Error("无法解析任务列表响应");
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
    const taskInfo =
      payload && typeof payload.task === "object" ? payload.task : null;
    return { entries, task: taskInfo };
  }

  async function loadEntriesForSlug(slugValue) {
    if (!slugValue && slugValue !== 0) {
      return null;
    }
    const slugString = String(slugValue);
    if (!slugString) {
      return null;
    }
    if (entriesCache.has(slugString)) {
      return entriesCache.get(slugString);
    }
    if (pendingLoads.has(slugString)) {
      return pendingLoads.get(slugString);
    }
    const promise = (async () => {
      const { entries, task } = await fetchTaskEntries(slugString);
      registerKnownSlug(slugString, task);
      const normalized = normalizeEntries(entries, slugString, task);
      const cacheValue = { entries: normalized, task: task || null };
      entriesCache.set(slugString, cacheValue);
      return cacheValue;
    })();
    pendingLoads.set(slugString, promise);
    try {
      return await promise;
    } finally {
      pendingLoads.delete(slugString);
    }
  }

  async function ensureEntriesForSlugs(slugs) {
    const unique = Array.from(new Set(slugs.filter(Boolean)));
    if (!unique.length) {
      return { succeeded: [], failed: [] };
    }
    const results = await Promise.all(
      unique.map((slugValue) =>
        loadEntriesForSlug(slugValue)
          .then(() => ({ slug: slugValue, status: "fulfilled" }))
          .catch((error) => ({ slug: slugValue, status: "rejected", error })),
      ),
    );
    const succeeded = [];
    const failed = [];
    results.forEach((result) => {
      if (result.status === "fulfilled") {
        succeeded.push(result.slug);
      } else {
        failed.push(result);
      }
    });
    return { succeeded, failed };
  }

  function collectEntries(slugs) {
    const combined = [];
    slugs.forEach((slugValue) => {
      const cached = entriesCache.get(slugValue);
      if (!cached || !Array.isArray(cached.entries)) {
        return;
      }
      combined.push(...cached.entries);
    });
    return combined;
  }

  function getActiveSlugs() {
    if (state.selectedSlugs.size) {
      return Array.from(state.selectedSlugs);
    }
    if (state.slugOptions.length) {
      return state.slugOptions.map((item) => item.slug);
    }
    if (primarySlug) {
      return [primarySlug];
    }
    return [];
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

  function renderEntriesList(entries, options) {
    if (!Array.isArray(entries) || entries.length === 0) {
      return '<p class="empty">暂无条目。</p>';
    }
    const settings = options || {};
    const showSource = Boolean(settings.showSource);
    const highlightAbolish = settings.highlightAbolish !== false;
    const items = entries
      .map((entry, index) => {
        if (!entry || typeof entry !== "object") {
          return "";
        }
        const serialValue =
          typeof entry.serial === "number" && Number.isFinite(entry.serial)
            ? entry.serial
            : index + 1;
        const serialHtml =
          '<span class="entries-list__serial">#' + escapeHtml(serialValue) + "</span>";
        const titleText = entry.title ? entry.title : "未命名条目";
        const titleHtml =
          '<span class="entries-list__title">' + escapeHtml(titleText) + "</span>";
        const badges = [];
        if (showSource && entry.__taskSlug) {
          const sourcePieces = [];
          if (entry.__taskName) {
            sourcePieces.push(entry.__taskName);
          }
          sourcePieces.push(entry.__taskSlug);
          badges.push(
            '<span class="entries-list__badge">' +
              escapeHtml(sourcePieces.join(" · ")) +
              "</span>",
          );
        }
        if (highlightAbolish && entry.__isAbolish) {
          badges.push(
            '<span class="entries-list__badge entries-list__badge--highlight">含“废止”</span>',
          );
        }
        const badgesHtml = badges.length
          ? '<span class="entries-list__badges">' + badges.join("") + "</span>"
          : "";
        const titleGroupHtml =
          '<div class="entries-list__title-group">' +
          titleHtml +
          badgesHtml +
          "</div>";
        const header =
          '<div class="entries-list__header">' + serialHtml + titleGroupHtml + "</div>";
        const remarkHtml =
          entry && entry.remark
            ? '<div class="entries-list__remark">' +
              escapeHtml(entry.remark) +
              "</div>"
            : "";
        const documents = Array.isArray(entry.documents) ? entry.documents : [];
        let documentsHtml;
        if (documents.length) {
          const docItems = documents
            .map((doc) => {
              const titleValue =
                doc && doc.title
                  ? doc.title
                  : doc && doc.url
                  ? doc.url
                  : doc && doc.local_path
                  ? doc.local_path
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
                    "</span>",
                );
              }
              if (doc && doc.local_path) {
                metaPieces.push(
                  '<span class="entries-documents__meta"><code>' +
                    escapeHtml(doc.local_path) +
                    "</code></span>",
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
      .filter(Boolean)
      .join("");
    return `<ol class="entries-list">${items}</ol>`;
  }

  function updateHeader(task, entries) {
    const info = task && typeof task === "object" ? task : null;
    const name = info && info.name ? String(info.name) : fallbackName;
    const slugDisplay = primarySlug || (info && info.slug) || "";
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

  function updateSelectionSummary(activeSlugs, combinedEntries, filteredEntries) {
    const totalEntriesCount = combinedEntries.length;
    const filteredCount = filteredEntries.length;
    const docsTotal = computeDocsCount(combinedEntries);
    const docsFiltered = computeDocsCount(filteredEntries);
    const filterActive = state.showAbolishOnly;

    if (activeSlugs.length === 1) {
      const slugValue = activeSlugs[0];
      const cached = entriesCache.get(slugValue);
      const task = cached ? cached.task : null;
      let entriesForHeader = [];
      if (filterActive && cached) {
        entriesForHeader = filteredEntries;
      } else if (cached && Array.isArray(cached.entries)) {
        entriesForHeader = cached.entries;
      }
      updateHeader(task, entriesForHeader);
      if (filterActive && subtitleEl && filteredCount !== totalEntriesCount) {
        const suffix = `筛选后 ${filteredCount} 条目`;
        subtitleEl.textContent = subtitleEl.textContent
          ? `${subtitleEl.textContent} · ${suffix}`
          : suffix;
      }
      updateMeta(task, cached && Array.isArray(cached.entries) ? cached.entries : []);
      if (metaEl && filterActive) {
        const base = metaEl.textContent || "";
        let addition = `筛选 ${filteredCount} 条`;
        if (docsTotal && docsFiltered !== docsTotal) {
          addition += ` / ${docsFiltered} 个文档`;
        }
        metaEl.textContent = base ? `${base} · ${addition}` : addition;
      }
      return;
    }

    if (titleEl) {
      titleEl.textContent = "条目详情";
    }
    document.title = "任务条目详情";

    if (subtitleEl) {
      const tasksLabel = activeSlugs.length
        ? `已选 ${activeSlugs.length} 个任务`
        : "全部任务";
      let entriesPart = `条目数 ${filteredCount}`;
      if (filterActive && filteredCount !== totalEntriesCount) {
        entriesPart = `条目数 ${filteredCount}/${totalEntriesCount}`;
      }
      subtitleEl.textContent = `${tasksLabel} · ${entriesPart}`;
    }

    if (metaEl) {
      const pieces = [];
      const totalTasks = activeSlugs.length || state.slugOptions.length;
      if (totalTasks) {
        pieces.push(`任务 ${totalTasks}`);
      }
      if (filterActive && filteredCount !== totalEntriesCount) {
        pieces.push(`条目 ${filteredCount}/${totalEntriesCount}`);
      } else {
        pieces.push(`条目 ${filteredCount}`);
      }
      if (docsTotal) {
        if (filterActive && docsFiltered !== docsTotal) {
          pieces.push(`文档 ${docsFiltered}/${docsTotal}`);
        } else {
          pieces.push(`文档 ${docsTotal}`);
        }
      }
      metaEl.textContent = pieces.join(" · ") || "—";
    }
  }

  async function refreshEntries() {
    if (staticSnapshot) {
      return;
    }
    const activeSlugs = getActiveSlugs();
    if (!activeSlugs.length) {
      showEmpty();
      showMessage("暂无可筛选的任务，请稍后重试。", "info");
      return;
    }

    const needsLoad = activeSlugs.some((slug) => !entriesCache.has(slug));
    if (needsLoad) {
      showLoading();
    }

    let loadResult;
    try {
      loadResult = await ensureEntriesForSlugs(activeSlugs);
    } catch (error) {
      showMessage(`加载条目时发生错误：${error.message || error}`);
      showEmpty();
      return;
    }
    const { succeeded, failed } = loadResult;

    if (failed.length) {
      const firstError = failed[0];
      const reason =
        firstError.error && firstError.error.message
          ? firstError.error.message
          : firstError.error || "未知错误";
      showMessage(`无法加载任务 ${firstError.slug} 的条目：${reason}`);
    } else if (state.showAbolishOnly) {
      showMessage('已启用“废止”筛选，仅展示相关条目。', "info");
    } else {
      clearMessage();
    }

    const usableSlugs = succeeded.length
      ? succeeded
      : activeSlugs.filter((slug) => entriesCache.has(slug));

    if (!usableSlugs.length) {
      showEmpty();
      return;
    }

    const combinedEntries = collectEntries(usableSlugs);
    const filteredEntries = state.showAbolishOnly
      ? combinedEntries.filter((entry) => entry && entry.__isAbolish)
      : combinedEntries;

    if (!filteredEntries.length) {
      if (bodyEl) {
        const message =
          !combinedEntries.length && !state.showAbolishOnly
            ? '<p class="empty">暂无条目。</p>'
            : '<p class="empty">没有符合筛选条件的条目。</p>';
        bodyEl.innerHTML = message;
      }
    } else if (bodyEl) {
      const showSourceBadges =
        state.selectedSlugs.size > 1 ||
        (!state.selectedSlugs.size && usableSlugs.length > 1);
      bodyEl.innerHTML = renderEntriesList(filteredEntries, {
        showSource: showSourceBadges,
        highlightAbolish: true,
      });
    }

    updateSelectionSummary(usableSlugs, combinedEntries, filteredEntries);
  }

  async function init() {
    setGeneratedAt(config.generatedAt || null);
    updateHeader(null, null);
    updateMeta(null, null);
    initSearch();

    if (filtersSection) {
      filtersSection.classList.toggle("hidden", staticSnapshot);
    }

    if (abolishFilterButton) {
      abolishFilterButton.addEventListener("click", () => {
        if (staticSnapshot) {
          return;
        }
        state.showAbolishOnly = !state.showAbolishOnly;
        abolishFilterButton.classList.toggle(
          "is-active",
          state.showAbolishOnly,
        );
        refreshEntries();
      });
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

    initialSlugs.forEach((slugValue) => {
      const name = slugValue === primarySlug ? fallbackName : "";
      registerKnownSlug(slugValue, { name });
    });

    try {
      const tasks = await fetchTasksList();
      tasks.forEach((task) => {
        if (task && task.slug) {
          registerKnownSlug(task.slug, task);
        }
      });
    } catch (error) {
      console.error("Unable to load tasks list", error);
    }

    renderSlugFilters();
    updateSlugButtonsState();

    await refreshEntries();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      init().catch((error) => {
        console.error("Failed to initialise entries page", error);
        showMessage(`初始化失败：${error.message || error}`);
      });
    });
  } else {
    init().catch((error) => {
      console.error("Failed to initialise entries page", error);
      showMessage(`初始化失败：${error.message || error}`);
    });
  }
})();
