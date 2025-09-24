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
    searchQuery: "",
    searchTokens: [],
    searchTopk: searchDefaultTopk,
    searchIncludeDocuments: searchIncludeDocumentsDefault,
  };
  const slugButtons = new Map();
  const entriesCache = new Map();
  const pendingLoads = new Map();
  const searchConfig =
    config && typeof config.search === "object" && config.search
      ? config.search
      : {};
  const searchEnabled = Boolean(searchConfig.enabled) && !staticSnapshot;
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

  function normaliseSearchText(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value)
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function extractSearchTokens(query) {
    if (!query) {
      return [];
    }
    return query
      .split(/[\s,;；，。]+/)
      .map((part) => normaliseSearchText(part))
      .filter(Boolean);
  }

  function entryMatchesTokens(entry, tokens) {
    if (!tokens.length) {
      return true;
    }
    if (!entry || typeof entry !== "object") {
      return false;
    }
    const pieces = [];
    const addPiece = (value) => {
      const normalised = normaliseSearchText(value);
      if (normalised) {
        pieces.push(normalised);
      }
    };
    addPiece(entry.title);
    addPiece(entry.remark);
    addPiece(entry.__taskName);
    addPiece(entry.__taskSlug);
    const documents = Array.isArray(entry.documents) ? entry.documents : [];
    documents.forEach((doc) => {
      if (!doc || typeof doc !== "object") {
        return;
      }
      addPiece(doc.title);
      addPiece(doc.type);
      addPiece(doc.url);
      addPiece(doc.local_path);
    });
    if (!pieces.length) {
      return false;
    }
    const haystack = pieces.join(" ");
    return tokens.every((token) => haystack.includes(token));
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

  function parseBooleanParam(value) {
    if (value === null || value === undefined) {
      return null;
    }
    const normalized = String(value).trim().toLowerCase();
    if (!normalized) {
      return true;
    }
    if (["1", "true", "yes", "on"].includes(normalized)) {
      return true;
    }
    if (["0", "false", "no", "off"].includes(normalized)) {
      return false;
    }
    return null;
  }

  function updateSearchParams(query, topk, includeDocuments) {
    if (typeof window === "undefined" || typeof window.history === "undefined") {
      return;
    }
    try {
      const url = new URL(window.location.href);
      if (query) {
        url.searchParams.set("query", query);
      } else {
        url.searchParams.delete("query");
      }
      if (Number.isFinite(topk) && topk > 0) {
        url.searchParams.set("topk", String(topk));
      } else {
        url.searchParams.delete("topk");
      }
      if (includeDocuments) {
        url.searchParams.set("include_documents", "on");
      } else {
        url.searchParams.set("include_documents", "off");
      }
      window.history.replaceState(null, "", url.toString());
    } catch (error) {
      // Ignore failures updating the URL (e.g. invalid base URL in older browsers).
    }
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
    if (!searchEnabled) {
      searchStatusEl.textContent = "";
      searchStatusEl.classList.add("hidden");
      searchStatusEl.classList.remove("info");
      return;
    }
    searchStatusEl.textContent = "输入关键词并点击“开始检索”后，将直接筛选左侧条目列表。";
    searchStatusEl.classList.remove("hidden");
    searchStatusEl.classList.add("info");
  }

  function updateSearchStatusSummary(searchActive, query, totalMatches, displayedMatches) {
    if (!searchStatusEl || !searchEnabled) {
      return;
    }
    if (!searchActive) {
      hideSearchStatus();
      return;
    }
    let message = "";
    if (!totalMatches) {
      message = `关键词“${query || ""}”未找到匹配条目。`;
    } else if (displayedMatches < totalMatches) {
      message = `关键词“${query || ""}”匹配 ${totalMatches} 条条目，已显示前 ${displayedMatches} 条。`;
    } else {
      message = `关键词“${query || ""}”匹配 ${totalMatches} 条条目。`;
    }
    searchStatusEl.textContent = message;
    searchStatusEl.classList.remove("hidden");
    searchStatusEl.classList.add("info");
  }

  async function handleSearchSubmit(event) {
    event.preventDefault();
    if (!searchEnabled) {
      return;
    }
    const query = searchQueryInput ? searchQueryInput.value.trim() : "";
    const tokens = extractSearchTokens(query);

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

    state.searchQuery = query;
    state.searchTokens = tokens;
    state.searchTopk = topk;
    state.searchIncludeDocuments = includeDocuments;

    const topkParam = tokens.length ? topk : null;
    updateSearchParams(query, topkParam, includeDocuments);
    await refreshEntries();
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
    }

    const initialQueryParam = params.get("query");
    const initialQuery = initialQueryParam ? initialQueryParam.trim() : "";

    let initialTopk = searchDefaultTopk;
    if (params.has("topk")) {
      const topkParam = params.get("topk");
      try {
        initialTopk = clampTopk(topkParam);
      } catch (error) {
        initialTopk = searchDefaultTopk;
      }
    }
    if (searchTopkInput) {
      searchTopkInput.value = String(initialTopk);
    }
    let initialIncludeDocuments = searchIncludeDocumentsDefault;
    if (params.has("include_documents")) {
      const parsed = parseBooleanParam(params.get("include_documents"));
      if (parsed !== null) {
        initialIncludeDocuments = parsed;
      }
    }
    if (searchIncludeDocumentsInput) {
      searchIncludeDocumentsInput.checked = Boolean(initialIncludeDocuments);
    }
    if (searchQueryInput) {
      searchQueryInput.value = initialQuery;
    }
    if (searchResultsList) {
      searchResultsList.innerHTML =
        '<li class="empty">搜索条件会直接作用于左侧条目列表。</li>';
    }

    state.searchQuery = initialQuery;
    state.searchTokens = extractSearchTokens(initialQuery);
    state.searchTopk = initialTopk;
    state.searchIncludeDocuments = Boolean(initialIncludeDocuments);

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
    const showDocuments = settings.showDocuments !== false;
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
        if (showDocuments) {
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
        } else if (documents.length) {
          documentsHtml =
            '<div class="entries-documents entries-documents--collapsed">已匹配 ' +
            escapeHtml(documents.length) +
            ' 个关联文档，未展开显示。</div>';
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

  function updateSelectionSummary(
    activeSlugs,
    combinedEntries,
    abolishFiltered,
    searchFiltered,
    displayEntries,
  ) {
    const totalEntriesCount = combinedEntries.length;
    const abolishCount = abolishFiltered.length;
    const searchCount = searchFiltered.length;
    const displayedCount = displayEntries.length;
    const docsTotal = computeDocsCount(combinedEntries);
    const docsAbolish = computeDocsCount(abolishFiltered);
    const docsSearch = computeDocsCount(searchFiltered);
    const docsDisplayed = computeDocsCount(displayEntries);
    const filterActive = state.showAbolishOnly;
    const searchActive = Boolean(state.searchTokens.length);
    const limitActive =
      searchActive &&
      Number.isFinite(state.searchTopk) &&
      state.searchTopk > 0 &&
      displayedCount < searchCount;

    if (activeSlugs.length === 1) {
      const slugValue = activeSlugs[0];
      const cached = entriesCache.get(slugValue);
      const task = cached ? cached.task : null;
      let entriesForHeader = [];
      if (searchActive) {
        entriesForHeader = searchFiltered;
      } else if (filterActive && cached) {
        entriesForHeader = abolishFiltered;
      } else if (cached && Array.isArray(cached.entries)) {
        entriesForHeader = cached.entries;
      }
      updateHeader(task, entriesForHeader);
      if (subtitleEl) {
        let subtitle = subtitleEl.textContent || "";
        if (filterActive && abolishCount !== totalEntriesCount) {
          const suffix = `筛选后 ${abolishCount} 条目`;
          subtitle = subtitle ? `${subtitle} · ${suffix}` : suffix;
        }
        if (searchActive) {
          let searchSuffix = `关键词匹配 ${searchCount} 条`;
          if (limitActive) {
            searchSuffix = `关键词匹配 ${displayedCount}/${searchCount} 条`;
          }
          subtitle = subtitle ? `${subtitle} · ${searchSuffix}` : searchSuffix;
        }
        subtitleEl.textContent = subtitle;
      }
      updateMeta(task, cached && Array.isArray(cached.entries) ? cached.entries : []);
      if (metaEl) {
        const base = metaEl.textContent || "";
        const additions = [];
        if (filterActive && abolishCount !== totalEntriesCount) {
          let addition = `筛选 ${abolishCount} 条`;
          if (docsTotal && docsAbolish !== docsTotal) {
            addition += ` / ${docsAbolish} 个文档`;
          }
          additions.push(addition);
        }
        if (searchActive) {
          let addition = `关键词 ${state.searchQuery || ""}`.trim();
          addition = addition.replace(/\s+/g, " ");
          if (addition === "关键词") {
            addition = "关键词";
          }
          if (searchCount) {
            addition += addition === "关键词" ? "匹配" : " 匹配";
            if (limitActive) {
              addition += ` ${displayedCount}/${searchCount} 条`;
            } else {
              addition += ` ${searchCount} 条`;
            }
            if (docsSearch) {
              if (docsDisplayed !== docsSearch) {
                addition += ` / 文档 ${docsDisplayed}/${docsSearch}`;
              } else {
                addition += ` / 文档 ${docsSearch}`;
              }
            }
          } else {
            addition += addition === "关键词" ? "未匹配到条目" : " 未匹配到条目";
          }
          additions.push(addition);
        }
        if (additions.length) {
          metaEl.textContent = base ? `${base} · ${additions.join(" · ")}` : additions.join(" · ");
        } else {
          metaEl.textContent = base;
        }
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
      const pieces = [tasksLabel];
      if (filterActive && abolishCount !== totalEntriesCount) {
        pieces.push(`条目 ${abolishCount}/${totalEntriesCount}`);
      } else {
        pieces.push(`条目 ${displayedCount}`);
      }
      if (searchActive) {
        if (searchCount) {
          const searchLabel = limitActive
            ? `关键词匹配 ${displayedCount}/${searchCount} 条`
            : `关键词匹配 ${searchCount} 条`;
          pieces.push(searchLabel);
        } else {
          pieces.push("关键词未匹配条目");
        }
      }
      subtitleEl.textContent = pieces.join(" · ");
    }

    if (metaEl) {
      const pieces = [];
      const totalTasks = activeSlugs.length || state.slugOptions.length;
      if (totalTasks) {
        pieces.push(`任务 ${totalTasks}`);
      }
      if (filterActive && abolishCount !== totalEntriesCount) {
        pieces.push(`条目 ${abolishCount}/${totalEntriesCount}`);
      } else if (searchActive) {
        pieces.push(`条目 ${displayedCount}`);
      } else {
        pieces.push(`条目 ${displayedCount}`);
      }
      if (docsTotal) {
        if (filterActive && docsAbolish !== docsTotal) {
          pieces.push(`文档 ${docsAbolish}/${docsTotal}`);
        } else if (searchActive && docsSearch) {
          if (docsDisplayed !== docsSearch) {
            pieces.push(`文档 ${docsDisplayed}/${docsSearch}`);
          } else {
            pieces.push(`文档 ${docsSearch}`);
          }
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
    const abolishFiltered = state.showAbolishOnly
      ? combinedEntries.filter((entry) => entry && entry.__isAbolish)
      : combinedEntries;
    const searchTokens = Array.isArray(state.searchTokens)
      ? state.searchTokens
      : [];
    const searchActive = Boolean(searchTokens.length);
    const searchFiltered = searchActive
      ? abolishFiltered.filter((entry) => entryMatchesTokens(entry, searchTokens))
      : abolishFiltered;
    const topkLimit =
      searchActive && Number.isFinite(state.searchTopk) && state.searchTopk > 0
        ? state.searchTopk
        : null;
    const displayEntries =
      topkLimit !== null ? searchFiltered.slice(0, topkLimit) : searchFiltered;

    if (!displayEntries.length) {
      if (bodyEl) {
        let message;
        if (!combinedEntries.length && !state.showAbolishOnly && !searchActive) {
          message = '<p class="empty">暂无条目。</p>';
        } else if (!searchFiltered.length && searchActive) {
          message = '<p class="empty">没有符合搜索条件的条目。</p>';
        } else if (!abolishFiltered.length && state.showAbolishOnly) {
          message = '<p class="empty">没有符合筛选条件的条目。</p>';
        } else if (!combinedEntries.length) {
          message = '<p class="empty">暂无条目。</p>';
        } else {
          message = '<p class="empty">没有符合筛选条件的条目。</p>';
        }
        bodyEl.innerHTML = message;
      }
    } else if (bodyEl) {
      const showSourceBadges =
        state.selectedSlugs.size > 1 ||
        (!state.selectedSlugs.size && usableSlugs.length > 1);
      bodyEl.innerHTML = renderEntriesList(displayEntries, {
        showSource: showSourceBadges,
        highlightAbolish: true,
        showDocuments: !searchActive || state.searchIncludeDocuments,
      });
    }

    updateSelectionSummary(
      usableSlugs,
      combinedEntries,
      abolishFiltered,
      searchFiltered,
      displayEntries,
    );
    updateSearchStatusSummary(
      searchActive,
      state.searchQuery,
      searchFiltered.length,
      displayEntries.length,
    );
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
