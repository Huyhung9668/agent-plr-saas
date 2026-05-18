const app = document.querySelector(".app");
const chat = document.getElementById("chat");
const prompt = document.getElementById("prompt");
const sendBtn = document.getElementById("sendBtn");
const scrollBottomBtn = document.getElementById("scrollBottomBtn");
const jumpPrevBtn = document.getElementById("jumpPrevBtn");
const jumpNextBtn = document.getElementById("jumpNextBtn");
const promptJumpPrevBtn = document.getElementById("promptJumpPrevBtn");
const promptJumpNextBtn = document.getElementById("promptJumpNextBtn");
const clearBtn = document.getElementById("clearBtn");
const newChatBtn = document.getElementById("newChatBtn");
const threadList = document.getElementById("threadList");
const threadSearch = document.getElementById("threadSearch");
const themeToggleBtn = document.getElementById("themeToggleBtn");
const attachBtn = document.getElementById("attachBtn");
const fileInput = document.getElementById("fileInput");
const attachmentBar = document.getElementById("attachmentBar");
const statusBtn = document.getElementById("statusBtn");
const exportBtn = document.getElementById("exportBtn");
const statusPanel = document.getElementById("statusPanel");
const brainSummary = document.getElementById("brainSummary");
const appVersionBadges = document.querySelectorAll("[data-app-version]");
const quickActions = document.getElementById("quickActions");
const modeSelector = document.getElementById("modeSelector");
const toast = document.getElementById("toast");

const threadStorageKey = "master_agent_threads_v2";
const themeStorageKey = "master_agent_theme_v1";
const syncStorageKey = "master_agent_threads_file_sync_v1";
const modeStorageKey = "master_agent_response_mode_v1";
const translationHideDelayMs = 180;

let state = loadState();
let activeThreadId = state.activeThreadId;
let pendingAttachments = [];
let openThreadMenuId = null;
let serverSyncReady = false;
let saveTimer = null;
let isSavingState = false;
let isLoadingServerState = false;
let activeController = null;
let brainStatus = null;
let responseMode = loadResponseMode();
let isStreamingAnswer = false;
let lastStreamSaveAt = 0;
let lastLocalWriteAt = 0;
let activeModuleId = "";
let selectionTranslateTimer = null;
let selectionTooltip = null;
let hoverTooltipInstalled = false;

applyTheme(loadTheme());
applyResponseMode(responseMode);
init();

async function init() {
  await syncInitialState();
  removeInterruptedReplies();
  if (!state.threads.length) createThread("Chat mới", { skipRender: true });
  if (!activeThreadId || !state.threads.some((thread) => thread.id === activeThreadId)) {
    activeThreadId = state.threads[0]?.id || null;
  }
  saveLocalState();
  queueServerSave();
  renderThreads();
  renderActiveThread();
  installQuickActionTranslations();
  installSelectionTranslator();
  installBlackCopy();
  loadStatus();
  prompt.focus();
}

function loadTheme() {
  try {
    return localStorage.getItem(themeStorageKey) || "dark";
  } catch {
    return "dark";
  }
}

function applyTheme(theme) {
  app.dataset.theme = theme;
  themeToggleBtn.textContent = theme === "dark" ? "☀" : "☾";
  localStorage.setItem(themeStorageKey, theme);
}

function toggleTheme() {
  applyTheme(app.dataset.theme === "dark" ? "light" : "dark");
}

function loadResponseMode() {
  try {
    const saved = localStorage.getItem(modeStorageKey);
    return ["fast", "balanced", "deep"].includes(saved) ? saved : "fast";
  } catch {
    return "fast";
  }
}

function applyResponseMode(mode) {
  responseMode = ["fast", "balanced", "deep"].includes(mode) ? mode : "fast";
  try {
    localStorage.setItem(modeStorageKey, responseMode);
  } catch {
    // Ignore private mode/localStorage errors.
  }
  if (!modeSelector) return;
  for (const button of modeSelector.querySelectorAll("button[data-mode]")) {
    button.classList.toggle("active", button.dataset.mode === responseMode);
  }
}

function selectedResponseMode() {
  const activeButton = modeSelector?.querySelector("button.active[data-mode]");
  const selected = activeButton?.dataset?.mode || responseMode || "fast";
  return ["fast", "balanced", "deep"].includes(selected) ? selected : "fast";
}

function effectiveModeLabel(text, attachments) {
  const selected = selectedResponseMode();
  const compact = String(text || "").replace(/\s+/g, " ").trim().toLowerCase();
  const wantsDepth = ["chi tiết", "từng bước", "kế hoạch", "phân tích", "viết cho tôi", "tạo cho tôi", "làm cho tôi"].some((item) =>
    compact.includes(item)
  );
  const wantsAsset = ["sales page", "warriorplus", "funnel", "oto", "bonus stack", "email swipe", "offer", "analyze offer", "analyze plr", "analyze plr file", "product idea scoring", "idea scoring", "product depth checker", "depth check", "upgrade raw content", "upgrade raw ai", "buyer avatar", "product assets", "quality control checklist", "qc checklist", "export zip", "warriorplus listing", "jv page", "jv/affiliate", "affiliate swipe pack", "prospect tracker", "outreach messages", "affiliate tier", "review access", "traffic content", "email funnel", "saas potential", "saas mvp", "saas upgrade", "membership planner", "whitelabel license", "market gap", "competitor pattern", "scan plr library", "export product", "launch pack"].some((item) =>
    compact.includes(item)
  );
  if (wantsAsset && selected !== "deep") return "Tạo asset";
  if (selected !== "deep" && !attachments.length && compact.length <= 90 && !wantsDepth) return "Nhanh gọn";
  return { fast: "Nhanh", balanced: "Cân bằng", deep: "Sâu" }[selected] || "Nhanh";
}

function loadState() {
  try {
    const raw = localStorage.getItem(threadStorageKey);
    const parsed = raw ? JSON.parse(raw) : null;
    return normalizeState(parsed);
  } catch {
    return { threads: [], activeThreadId: null };
  }
}

async function syncInitialState() {
  const localState = state;
  const serverState = await fetchServerState();
  if (!serverState) {
    serverSyncReady = false;
    return;
  }

  const shouldImportLocal =
    !localStorage.getItem(syncStorageKey) &&
    localState.threads.some((thread) => thread.messages.length) &&
    !serverState.threads.some((thread) => thread.messages.length);
  const importBase = shouldImportLocal
    ? { threads: serverState.threads.filter((thread) => thread.messages.length), activeThreadId: serverState.activeThreadId }
    : serverState;
  const merged = !serverState.threads.length || shouldImportLocal ? mergeStates(importBase, localState) : serverState;
  state = merged;
  activeThreadId = merged.activeThreadId;
  serverSyncReady = true;
  localStorage.setItem(syncStorageKey, "1");
  saveLocalState();
  if (merged.threads.length !== serverState.threads.length || merged.activeThreadId !== serverState.activeThreadId) {
    queueServerSave();
  }
}

async function fetchServerState() {
  if (isLoadingServerState) return null;
  isLoadingServerState = true;
  try {
    const response = await fetch("/api/threads");
    const data = await response.json();
    if (!data.ok || !data.state) return null;
    return normalizeState(data.state);
  } catch {
    return null;
  } finally {
    isLoadingServerState = false;
  }
}

async function refreshFromServer() {
  if (!serverSyncReady || isSavingState || activeController || isStreamingAnswer) return;
  if (Date.now() - lastLocalWriteAt < 2500) return;
  const previousActiveThreadId = activeThreadId;
  const previousScrollTop = chat.scrollTop;
  const serverState = await fetchServerState();
  if (!serverState || !serverState.threads.length) return;
  state = serverState;
  activeThreadId = serverState.activeThreadId || serverState.threads[0].id;
  saveLocalState();
  renderThreads();
  if (activeThreadId === previousActiveThreadId) {
    renderActiveThread({ preserveScrollTop: previousScrollTop });
  } else {
    renderActiveThread();
  }
}

function normalizeState(raw) {
  if (!raw || !Array.isArray(raw.threads)) return { threads: [], activeThreadId: null };
  const threads = raw.threads.map(normalizeThread).sort(byRecent);
  const active = raw.activeThreadId && threads.some((thread) => thread.id === raw.activeThreadId)
    ? raw.activeThreadId
    : (threads[0]?.id || null);
  return { threads, activeThreadId: active };
}

function mergeStates(serverState, localState) {
  const byId = new Map();
  for (const thread of [...serverState.threads, ...localState.threads]) {
    const existing = byId.get(thread.id);
    if (!existing || (thread.updatedAt || 0) >= (existing.updatedAt || 0)) byId.set(thread.id, thread);
  }
  const threads = Array.from(byId.values()).sort(byRecent);
  const active = localState.activeThreadId && threads.some((thread) => thread.id === localState.activeThreadId)
    ? localState.activeThreadId
    : (serverState.activeThreadId && threads.some((thread) => thread.id === serverState.activeThreadId)
      ? serverState.activeThreadId
      : (threads[0]?.id || null));
  return { threads, activeThreadId: active };
}

function normalizeThread(thread) {
  return {
    id: thread.id || crypto.randomUUID(),
    title: thread.title || "Chat mới",
    messages: Array.isArray(thread.messages) ? thread.messages.map(normalizeMessage) : [],
    pinned: Boolean(thread.pinned),
    createdAt: thread.createdAt || Date.now(),
    updatedAt: thread.updatedAt || Date.now(),
  };
}

function normalizeMessage(message) {
  return {
    role: message.role === "assistant" ? "assistant" : "user",
    content: stripSourceFooter(String(message.content || "")),
    createdAt: normalizeTimestamp(message.createdAt || message.timestamp),
  };
}

function normalizeTimestamp(value) {
  const number = Number(value || 0);
  return Number.isFinite(number) && number > 0 ? number : null;
}

function saveState() {
  state.threads.sort(byRecent);
  state.activeThreadId = activeThreadId;
  saveLocalState();
  queueServerSave();
}

function saveLocalState() {
  state.threads.sort(byRecent);
  state.activeThreadId = activeThreadId;
  lastLocalWriteAt = Date.now();
  localStorage.setItem(threadStorageKey, JSON.stringify(state));
}

function removeInterruptedReplies() {
  let changed = false;
  const stoppedTexts = new Set([
    "Đã dừng lượt trả lời này.",
    "ÄÃ£ dá»«ng lÆ°á»£t tráº£ lá»i nÃ y.",
  ]);
  for (const thread of state.threads) {
    const before = thread.messages.length;
    thread.messages = thread.messages.filter((message) => {
      return !(message.role === "assistant" && stoppedTexts.has(String(message.content || "").trim()));
    });
    if (thread.messages.length !== before) {
      thread.updatedAt = Date.now();
      changed = true;
    }
  }
  if (changed) {
    saveLocalState();
    queueServerSave();
  }
}

function queueServerSave() {
  if (!serverSyncReady) return;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(saveStateToServer, 180);
}

function persistStreamingDraft(force = false) {
  const now = Date.now();
  if (!force && now - lastStreamSaveAt < 900) return;
  lastStreamSaveAt = now;
  const thread = getActiveThread();
  if (thread) thread.updatedAt = now;
  state.activeThreadId = activeThreadId;
  saveLocalState();
  queueServerSave();
}

async function saveStateToServer() {
  if (!serverSyncReady) return;
  isSavingState = true;
  try {
    await fetch("/api/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state }),
    });
  } catch {
    // LocalStorage remains the fallback while the local server restarts.
  } finally {
    isSavingState = false;
  }
}

function getActiveThread() {
  return state.threads.find((thread) => thread.id === activeThreadId) || state.threads[0];
}

function createThread(title = "Chat mới", options = {}) {
  const thread = {
    id: crypto.randomUUID(),
    title,
    messages: [],
    pinned: false,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  state.threads.unshift(thread);
  activeThreadId = thread.id;
  saveState();
  if (!options.skipRender) {
    renderThreads();
    renderActiveThread();
    prompt.focus();
  }
}

function byRecent(a, b) {
  if (Boolean(a.pinned) !== Boolean(b.pinned)) return a.pinned ? -1 : 1;
  return (b.updatedAt || 0) - (a.updatedAt || 0);
}

function renderThreads() {
  state.threads.sort(byRecent);
  threadList.innerHTML = "";
  const query = (threadSearch?.value || "").trim().toLowerCase();
  const filtered = state.threads.filter((thread) => {
    if (!query) return true;
    const haystack = [thread.title, ...thread.messages.map((message) => message.content)].join(" ").toLowerCase();
    return haystack.includes(query);
  });

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "thread-empty";
    empty.textContent = "Không tìm thấy chat.";
    threadList.appendChild(empty);
    return;
  }

  for (const thread of filtered) {
    const item = document.createElement("div");
    item.className = `thread-item${thread.id === activeThreadId ? " active" : ""}${thread.pinned ? " pinned" : ""}`;

    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "thread-main";
    openButton.addEventListener("click", () => {
      activeThreadId = thread.id;
      openThreadMenuId = null;
      saveState();
      renderThreads();
      renderActiveThread();
    });

    const titleRow = document.createElement("div");
    titleRow.className = "thread-title-row";
    const title = document.createElement("div");
    title.className = "thread-title";
    title.textContent = thread.title;
    titleRow.appendChild(title);
    if (thread.pinned) {
      const badge = document.createElement("span");
      badge.className = "thread-pin-badge";
      badge.textContent = "Ghim";
      titleRow.appendChild(badge);
    }

    const preview = document.createElement("div");
    preview.className = "thread-preview";
    preview.textContent = previewText(thread);
    const time = document.createElement("div");
    time.className = "thread-time";
    time.textContent = `VN ${formatVietnamDateTime(latestThreadTime(thread))}`;
    openButton.appendChild(titleRow);
    openButton.appendChild(time);
    openButton.appendChild(preview);
    item.appendChild(openButton);

    const menuButton = document.createElement("button");
    menuButton.type = "button";
    menuButton.className = "thread-menu-btn";
    menuButton.title = "Tùy chọn chat";
    menuButton.setAttribute("aria-label", "Tùy chọn chat");
    menuButton.textContent = "⋯";
    menuButton.addEventListener("click", (event) => {
      event.stopPropagation();
      openThreadMenuId = openThreadMenuId === thread.id ? null : thread.id;
      renderThreads();
    });
    item.appendChild(menuButton);
    if (openThreadMenuId === thread.id) item.appendChild(renderThreadMenu(thread));
    threadList.appendChild(item);
  }
}

function renderThreadMenu(thread) {
  const menu = document.createElement("div");
  menu.className = "thread-menu";
  const actions = [
    ["Đổi tên", () => renameThread(thread.id), ""],
    [thread.pinned ? "Bỏ ghim" : "Ghim lên đầu", () => togglePinThread(thread.id), ""],
    ["Nhân bản", () => duplicateThread(thread.id), ""],
    ["Xóa chat", () => deleteThread(thread.id), "danger"],
  ];
  for (const [label, handler, className] of actions) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    if (className) button.className = className;
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      handler();
    });
    menu.appendChild(button);
  }
  return menu;
}

function renameThread(threadId) {
  const thread = state.threads.find((item) => item.id === threadId);
  if (!thread) return;
  const nextTitle = window.prompt("Đổi tên đoạn chat", thread.title);
  if (!nextTitle) {
    openThreadMenuId = null;
    renderThreads();
    return;
  }
  thread.title = nextTitle.replace(/\s+/g, " ").trim().slice(0, 80) || thread.title;
  thread.updatedAt = Date.now();
  openThreadMenuId = null;
  saveState();
  renderThreads();
}

function togglePinThread(threadId) {
  const thread = state.threads.find((item) => item.id === threadId);
  if (!thread) return;
  thread.pinned = !thread.pinned;
  thread.updatedAt = Date.now();
  openThreadMenuId = null;
  saveState();
  renderThreads();
}

function duplicateThread(threadId) {
  const thread = state.threads.find((item) => item.id === threadId);
  if (!thread) return;
  const copy = {
    ...thread,
    id: crypto.randomUUID(),
    title: `${thread.title} - bản sao`.slice(0, 80),
    messages: thread.messages.map((message) => ({ ...message })),
    pinned: false,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  state.threads.unshift(copy);
  activeThreadId = copy.id;
  openThreadMenuId = null;
  saveState();
  renderThreads();
  renderActiveThread();
  showToast("Đã nhân bản chat.");
}

function deleteThread(threadId) {
  const thread = state.threads.find((item) => item.id === threadId);
  if (!thread) return;
  if (!window.confirm(`Xóa "${thread.title}"?`)) {
    openThreadMenuId = null;
    renderThreads();
    return;
  }
  state.threads = state.threads.filter((item) => item.id !== threadId);
  if (!state.threads.length) createThread("Chat mới", { skipRender: true });
  if (activeThreadId === threadId) {
    state.threads.sort(byRecent);
    activeThreadId = state.threads[0].id;
  }
  openThreadMenuId = null;
  saveState();
  renderThreads();
  renderActiveThread();
}

function previewText(thread) {
  const last = [...thread.messages].reverse().find((message) => message.role === "user" || message.role === "assistant");
  if (!last) return "Chưa có nội dung";
  return last.content.replace(/\s+/g, " ").trim().slice(0, 72) || "Chưa có nội dung";
}

function latestThreadTime(thread) {
  const last = [...(thread.messages || [])].reverse().find((message) => message.role === "user" || message.role === "assistant");
  return normalizeTimestamp(last?.createdAt) || normalizeTimestamp(thread.updatedAt) || normalizeTimestamp(thread.createdAt) || Date.now();
}

function messageTime(thread, message) {
  return normalizeTimestamp(message?.createdAt) || normalizeTimestamp(thread?.updatedAt) || normalizeTimestamp(thread?.createdAt) || Date.now();
}

function formatVietnamDateTime(value) {
  const timestamp = normalizeTimestamp(value) || Date.now();
  try {
    return new Intl.DateTimeFormat("vi-VN", {
      timeZone: "Asia/Ho_Chi_Minh",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(timestamp));
  } catch {
    const date = new Date(timestamp);
    const pad = (item) => String(item).padStart(2, "0");
    return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }
}

function renderActiveThread(options = {}) {
  const preserveScrollTop = Number.isFinite(options.preserveScrollTop) ? options.preserveScrollTop : null;
  const thread = getActiveThread();
  chat.innerHTML = "";
  if (!thread || !thread.messages.length) {
    renderWelcome();
    requestAnimationFrame(updateScrollBottomButton);
    return;
  }
  for (const [index, message] of thread.messages.entries()) {
    appendMessageToDom(message.role, message.content, index, false);
  }
  if (preserveScrollTop !== null) {
    requestAnimationFrame(() => {
      chat.scrollTop = preserveScrollTop;
    });
  } else {
    requestAnimationFrame(scrollChatToBottom);
  }
  requestAnimationFrame(updateScrollBottomButton);
}

function renderWelcome() {
  const starter = document.createElement("div");
  starter.className = "welcome";
  starter.innerHTML = `
    <div class="welcome-mark">M</div>
    <h1>Launch Command Center.</h1>
    <p>Chọn module bên dưới để phân tích PLR, nâng raw AI content thành product kit, viết sales page/funnel, tạo JV pack, hoặc lập kế hoạch SaaS/membership.</p>
  `;
  chat.appendChild(starter);
  updateScrollBottomButton();
}

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    if (!data.ok) return;
    brainStatus = data;
    const totals = (data.brains || []).reduce((acc, brain) => {
      acc.docs += brain.documents || 0;
      acc.chunks += brain.chunks || 0;
      return acc;
    }, { docs: 0, chunks: 0 });
    const thinking = data.reasoningEffort ? `Thinking ${String(data.reasoningEffort).toUpperCase()}` : "Thinking mặc định";
    const detail = data.answerDetail ? `Detail ${String(data.answerDetail).toUpperCase()}` : "Detail HIGH";
  const appVersion = data.appVersion || "1.04";
    for (const badge of appVersionBadges) badge.textContent = `v${appVersion}`;
    brainSummary.textContent = `v${appVersion} · ${data.apiReady ? "API 5.5 sẵn sàng" : "API chưa sẵn sàng"} · ${thinking} · ${detail} · ${formatNumber(totals.docs)} tài liệu · ${formatNumber(totals.chunks)} chunks`;
    renderStatusPanel();
  } catch {
    brainSummary.textContent = "Không đọc được trạng thái local.";
  }
}

function renderStatusPanel() {
  if (!brainStatus) return;
  statusPanel.innerHTML = "";
  const grid = document.createElement("div");
  grid.className = "status-grid";
  for (const brain of brainStatus.brains || []) {
    const card = document.createElement("div");
    card.className = "status-card";
    card.innerHTML = `
      <div class="status-card-title">${escapeHtml(brain.name)}</div>
      <div class="status-card-metrics">
        <span>${formatNumber(brain.documents)} docs</span>
        <span>${formatNumber(brain.chunks)} chunks</span>
        <span>${brain.textMb} MB text</span>
      </div>
      <div class="subagent-row">${(brain.subagents || []).map((item) => `<span>${escapeHtml(item.name)}</span>`).join("")}</div>
    `;
    grid.appendChild(card);
  }
  if (brainStatus.launchOs?.tables?.length) {
    const card = document.createElement("div");
    card.className = "status-card";
    const tableCount = brainStatus.launchOs.tables.length;
    const savedCount = Object.values(brainStatus.launchOs.counts || {}).reduce((sum, value) => sum + Number(value || 0), 0);
    card.innerHTML = `
      <div class="status-card-title">Launch OS Database</div>
      <div class="status-card-metrics">
        <span>${formatNumber(tableCount)} tables</span>
        <span>${formatNumber(savedCount)} records</span>
      </div>
      <div class="subagent-row">${brainStatus.launchOs.tables.slice(0, 10).map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>
    `;
    grid.appendChild(card);
  }
  if (brainStatus.activeProject?.product_name) {
    const project = brainStatus.activeProject;
    const doneAssets = (project.assets || []).filter((item) => item.status === "done").length;
    const totalAssets = (project.assets || []).length || 1;
    const nextActions = (project.next_actions || []).slice(0, 3);
    const missing = (project.missing_assets || []).slice(0, 6);
    const projectCard = document.createElement("div");
    projectCard.className = "status-card project-status-card";
    projectCard.innerHTML = `
      <div class="status-card-title">Active Project</div>
      <div class="project-name">${escapeHtml(project.product_name)}</div>
      <div class="project-meta">${escapeHtml(project.buyer || "Buyer chưa khóa")} · ${escapeHtml(project.price || "Price chưa khóa")}</div>
      <div class="project-progress" aria-label="Launch readiness">
        <span style="width:${Math.max(0, Math.min(100, Number(project.launch_readiness || 0) * 10))}%"></span>
      </div>
      <div class="status-card-metrics">
        <span>Readiness ${Number(project.launch_readiness || 0).toFixed(1)}/10</span>
        <span>${doneAssets}/${totalAssets} assets</span>
        <span>Status ${escapeHtml(project.status || "idea")}</span>
      </div>
      <div class="project-mini-list">
        <strong>Next:</strong> ${nextActions.map((item) => `<span>${escapeHtml(item)}</span>`).join("") || "<span>Review launch</span>"}
      </div>
      <div class="project-mini-list missing">
        <strong>Missing:</strong> ${missing.map((item) => `<span>${escapeHtml(item)}</span>`).join("") || "<span>None</span>"}
      </div>
    `;
    grid.appendChild(projectCard);
  }
  statusPanel.appendChild(grid);
}

function renderAttachments() {
  attachmentBar.innerHTML = "";
  for (const [index, attachment] of pendingAttachments.entries()) {
    const chip = document.createElement("div");
    chip.className = `attachment-chip ${attachment.type === "error" ? "error" : ""}`;
    const label = document.createElement("span");
    label.textContent = `${attachment.name} · ${attachment.notice || attachment.type}`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.title = "Bỏ file";
    remove.addEventListener("click", () => {
      pendingAttachments.splice(index, 1);
      renderAttachments();
    });
    chip.appendChild(label);
    chip.appendChild(remove);
    attachmentBar.appendChild(chip);
  }
}

async function uploadFiles(files) {
  const selected = Array.from(files || []);
  if (!selected.length) return;
  const loading = { name: `${selected.length} file`, type: "loading", text: "", notice: "Đang đọc file..." };
  pendingAttachments.push(loading);
  renderAttachments();
  try {
    const payloadFiles = [];
    for (const file of selected.slice(0, 12)) {
      payloadFiles.push({ name: file.name, type: file.type, dataBase64: await readFileBase64(file) });
    }
    const response = await fetch("/api/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ files: payloadFiles }),
    });
    const data = await response.json();
    pendingAttachments = pendingAttachments.filter((item) => item !== loading);
    if (!data.ok) {
      pendingAttachments.push({ name: "Upload lỗi", type: "error", text: "", notice: data.error || "Không upload được file." });
    } else {
      pendingAttachments.push(...(data.attachments || []));
      showToast("Đã đọc file.");
    }
  } catch (error) {
    pendingAttachments = pendingAttachments.filter((item) => item !== loading);
    pendingAttachments.push({ name: "Upload lỗi", type: "error", text: "", notice: friendlyFetchError(error) });
  }
  fileInput.value = "";
  renderAttachments();
}

function readFileBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || "");
      resolve(result.includes(",") ? result.split(",").pop() : result);
    };
    reader.onerror = () => reject(reader.error || new Error("Không đọc được file."));
    reader.readAsDataURL(file);
  });
}

function appendMessageToDom(role, content, messageIndex = null, shouldScroll = true) {
  const displayContent = role === "assistant" ? stripSourceFooter(content) : content;
  const thread = getActiveThread();
  const savedMessage = thread && Number.isInteger(messageIndex) ? thread.messages[messageIndex] : null;
  const el = document.createElement("div");
  el.className = `msg ${role}`;

  const header = document.createElement("div");
  header.className = "msg-actions";
  const copyBtn = document.createElement("button");
  copyBtn.className = "copy-btn";
  copyBtn.type = "button";
  copyBtn.title = role === "assistant" ? "Copy toàn bộ trả lời" : "Copy câu hỏi";
  copyBtn.textContent = "⧉";
  copyBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(currentMessageContent(messageIndex, displayContent));
    copyBtn.textContent = "✓";
    showToast("Đã copy.");
    setTimeout(() => (copyBtn.textContent = "⧉"), 900);
  });
  header.appendChild(copyBtn);

  if (role === "assistant") {
    const fileBtn = document.createElement("button");
    fileBtn.className = "file-btn";
    fileBtn.type = "button";
    fileBtn.title = "Tạo file từ trả lời này";
    fileBtn.textContent = "⇩";
    fileBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      showFileMenu(fileBtn, currentMessageContent(messageIndex, displayContent));
    });
    header.appendChild(fileBtn);
  }

  if (Number.isInteger(messageIndex)) {
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-msg-btn";
    deleteBtn.type = "button";
    deleteBtn.title = "Xóa mẩu chat này";
    deleteBtn.textContent = "×";
    deleteBtn.addEventListener("click", () => deleteMessage(messageIndex));
    header.appendChild(deleteBtn);
  }

  el.appendChild(header);

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = `${role === "assistant" ? "Agent" : "Bạn"} · VN ${formatVietnamDateTime(messageTime(thread, savedMessage))}`;
  el.appendChild(meta);

  const body = document.createElement("div");
  body.className = "msg-body";
  body.innerHTML = renderMarkdown(escapeHtml(displayContent));
  el.appendChild(body);
  chat.appendChild(el);
  if (shouldScroll) {
    scrollChatToBottom();
  } else {
    updateScrollBottomButton();
  }
  return { el, body };
}

function currentMessageContent(messageIndex, fallback) {
  const thread = getActiveThread();
  if (thread && Number.isInteger(messageIndex) && thread.messages[messageIndex]) {
    return stripSourceFooter(thread.messages[messageIndex].content || fallback || "");
  }
  return stripSourceFooter(fallback || "");
}

function showFileMenu(anchor, content) {
  closeFileMenus();
  if (!content.trim()) {
    showToast("Chưa có nội dung để tạo file.");
    return;
  }
  const menu = document.createElement("div");
  menu.className = "file-menu";
  const formats = [
    ["md", "Markdown"],
    ["txt", "Text"],
    ["html", "HTML"],
    ["docx", "Word"],
    ["pdf", "PDF"],
    ["json", "JSON"],
    ["csv", "CSV"],
  ];
  for (const [format, label] of formats) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", async (event) => {
      event.stopPropagation();
      await createFileFromContent(content, format);
      closeFileMenus();
    });
    menu.appendChild(button);
  }
  anchor.closest(".msg-actions")?.appendChild(menu);
}

function closeFileMenus() {
  document.querySelectorAll(".file-menu").forEach((menu) => menu.remove());
}

async function createFileFromContent(content, format) {
  const thread = getActiveThread();
  const title = safeDownloadName(thread?.title || "agent-output");
  showToast(`Đang tạo file ${format.toUpperCase()}...`);
  try {
    const response = await fetch("/api/create_file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, format, title }),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Không tạo được file.");
    downloadBase64File(data.dataBase64, data.fileName, data.mime);
    showToast(`Đã tạo ${data.fileName}`);
  } catch (error) {
    showToast(friendlyFetchError(error));
  }
}

function downloadBase64File(dataBase64, fileName, mime) {
  const binary = atob(dataBase64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  const blob = new Blob([bytes], { type: mime || "application/octet-stream" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = fileName || "agent-output";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

function deleteMessage(messageIndex) {
  const thread = getActiveThread();
  if (!thread || !Number.isInteger(messageIndex)) return;
  if (messageIndex < 0 || messageIndex >= thread.messages.length) return;
  thread.messages.splice(messageIndex, 1);
  if (!thread.messages.length) {
    thread.title = "Chat mới";
  }
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  renderActiveThread();
  showToast("Đã xóa mẩu chat.");
}

function appendThinking(label = null) {
  const el = document.createElement("div");
  el.className = "msg assistant thinking";
  const labels = { fast: "Nhanh", balanced: "Cân bằng", deep: "Sâu" };
  el.innerHTML = `<span class="dot-pulse"></span><span>Đang trả lời chế độ ${label || labels[responseMode] || "Nhanh"}...</span>`;
  chat.appendChild(el);
  scrollChatToBottom();
  updateScrollBottomButton();
  return () => el.remove();
}

async function fetchStreamingAnswer(payload, onDelta) {
  const response = await fetch("/api/chat_stream", {
    method: "POST",
    signal: activeController.signal,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Server stream lỗi: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() || "";
    for (const block of blocks) {
      const event = parseSseBlock(block);
      if (!event) continue;
      if (event.type === "delta" && event.data?.text) onDelta(event.data.text);
      if (event.type === "error") throw new Error(event.data?.error || "Stream lỗi.");
    }
    if (done) break;
  }
}

function parseSseBlock(block) {
  const lines = String(block || "").split("\n");
  let type = "message";
  const dataLines = [];
  for (const line of lines) {
    if (line.startsWith("event:")) type = line.slice(6).trim();
    if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
  }
  if (!dataLines.length) return null;
  try {
    return { type, data: JSON.parse(dataLines.join("\n")) };
  } catch {
    return null;
  }
}

async function sendMessage() {
  if (activeController) {
    showToast("Agent đang trả lời, đợi chút...");
    return;
  }

  const text = prompt.value.trim();
  if (!text && !pendingAttachments.length) return;
  const thread = getActiveThread();
  if (!thread) {
    createThread(text || "Chat mới");
    return sendMessage();
  }

  if (!thread.messages.length && ["Chat mới", "Đoạn chat mới"].includes(thread.title)) {
    thread.title = createThreadTitle(text || pendingAttachments[0]?.name || "Phân tích file");
  }

  const attachmentSummary = formatAttachmentSummary(pendingAttachments);
  const userContent = attachmentSummary ? `${text || "Hãy phân tích file này."}\n\n${attachmentSummary}` : text;
  const attachmentsForRequest = pendingAttachments.filter((item) => item.type !== "loading");
  const requestMode = selectedResponseMode();
  const requestModule = activeModuleId || "";
  responseMode = requestMode;
  applyResponseMode(requestMode);
  const thinkingLabel = effectiveModeLabel(text, attachmentsForRequest);
  thread.messages.push({ role: "user", content: userContent, createdAt: Date.now() });
  const userMessageIndex = thread.messages.length - 1;
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  appendMessageToDom("user", userContent, userMessageIndex);
  prompt.value = "";
  pendingAttachments = [];
  renderAttachments();
  autoResize();

  activeController = new AbortController();
  isStreamingAnswer = true;
  lastStreamSaveAt = 0;
  sendBtn.textContent = "■";
  sendBtn.title = "Đang trả lời...";
  sendBtn.disabled = true;
  sendBtn.classList.add("is-running");
  let stopThinking = appendThinking(thinkingLabel);
  let assistantMessageIndex = null;
  let assistantRendered = null;
  let streamedAnswer = "";
  const ensureAssistantMessage = () => {
    if (assistantMessageIndex !== null) return;
    if (stopThinking) {
      stopThinking();
      stopThinking = null;
    }
    thread.messages.push({ role: "assistant", content: "", createdAt: Date.now() });
    assistantMessageIndex = thread.messages.length - 1;
    assistantRendered = appendMessageToDom("assistant", "", assistantMessageIndex);
    persistStreamingDraft(true);
  };
  try {
    await fetchStreamingAnswer(
      {
        question: text || "Hãy phân tích file người dùng vừa gửi.",
        history: thread.messages.slice(-10),
        attachments: attachmentsForRequest,
        mode: requestMode,
        module: requestModule,
      },
      (delta) => {
        ensureAssistantMessage();
        streamedAnswer += delta;
        const clean = stripSourceFooter(streamedAnswer);
        thread.messages[assistantMessageIndex].content = clean;
        if (assistantRendered?.body) {
          assistantRendered.body.innerHTML = renderMarkdown(escapeHtml(clean));
        }
        persistStreamingDraft(false);
        if (isChatNearBottom()) scrollChatToBottom();
        updateScrollBottomButton();
      }
    );
    if (stopThinking) {
      stopThinking();
      stopThinking = null;
    }
    if (assistantMessageIndex === null) {
      appendAssistantMessage(thread, "Model chưa trả nội dung.");
    } else {
      const clean = stripSourceFooter(streamedAnswer);
      thread.messages[assistantMessageIndex].content = clean;
      if (assistantRendered?.body) assistantRendered.body.innerHTML = renderMarkdown(escapeHtml(clean));
      persistStreamingDraft(true);
    }
  } catch (error) {
    if (stopThinking) {
      stopThinking();
      stopThinking = null;
    }
    if (error?.name === "AbortError") {
      if (assistantMessageIndex !== null && streamedAnswer.trim()) {
        persistStreamingDraft(true);
      }
      if (assistantMessageIndex === null) {
        showToast("Kết nối bị ngắt, hãy gửi lại.");
      }
    } else {
      if (assistantMessageIndex !== null && streamedAnswer.trim()) {
        persistStreamingDraft(true);
      }
      appendAssistantMessage(thread, friendlyFetchError(error));
    }
  } finally {
    isStreamingAnswer = false;
    activeController = null;
    sendBtn.textContent = "➤";
    sendBtn.title = "Gửi";
    sendBtn.disabled = false;
    sendBtn.classList.remove("is-running");
    persistStreamingDraft(true);
    saveState();
    renderThreads();
    activeModuleId = "";
    loadStatus();
    prompt.focus();
  }
}

function appendAssistantMessage(thread, content) {
  const clean = stripSourceFooter(content);
  thread.messages.push({ role: "assistant", content: clean, createdAt: Date.now() });
  const assistantMessageIndex = thread.messages.length - 1;
  thread.updatedAt = Date.now();
  saveState();
  appendMessageToDom("assistant", clean, assistantMessageIndex);
}

function formatAttachmentSummary(attachments) {
  const ready = attachments.filter((item) => item.type !== "loading");
  if (!ready.length) return "";
  return ready.map((item, index) => `File ${index + 1}: ${item.name}\nGhi chú: ${item.notice || item.type}`).join("\n\n");
}

function friendlyFetchError(error) {
  const message = String(error || "");
  if (message.includes("Failed to fetch")) {
    return "Không kết nối được server local. Hãy chạy lại web server rồi refresh trang: uv run --with-requirements requirements.txt python web_app.py --host 127.0.0.1 --port 8088";
  }
  return message;
}

function createThreadTitle(text) {
  return text.replace(/\s+/g, " ").trim().slice(0, 42) || "Chat mới";
}

function autoResize() {
  prompt.style.height = "auto";
  prompt.style.height = `${Math.min(prompt.scrollHeight, 180)}px`;
}

function scrollChatToBottom() {
  chat.scrollTo({ top: chat.scrollHeight, behavior: "auto" });
  updateScrollBottomButton();
}

function isChatNearBottom() {
  const distance = chat.scrollHeight - chat.scrollTop - chat.clientHeight;
  return distance < 120;
}

function updateScrollBottomButton() {
  if (!scrollBottomBtn) return;
  const canScroll = chat.scrollHeight > chat.clientHeight + 40;
  scrollBottomBtn.classList.toggle("show", canScroll && !isChatNearBottom());
  updateJumpButtons();
}

function messageJumpTargets() {
  return Array.from(chat.querySelectorAll(".msg.user, .msg.assistant:not(.thinking)"));
}

function jumpToMessage(direction) {
  const targets = messageJumpTargets();
  if (!targets.length) return;
  const current = chat.scrollTop;
  const tolerance = 12;
  let target = null;
  if (direction < 0) {
    for (let index = targets.length - 1; index >= 0; index -= 1) {
      if (targets[index].offsetTop < current - tolerance) {
        target = targets[index];
        break;
      }
    }
    target ||= targets[0];
  } else {
    target = targets.find((item) => item.offsetTop > current + tolerance) || targets[targets.length - 1];
  }
  chat.scrollTo({ top: Math.max(0, target.offsetTop - 18), behavior: "smooth" });
  target.classList.add("jump-highlight");
  setTimeout(() => target.classList.remove("jump-highlight"), 720);
  updateJumpButtons();
}

function updateJumpButtons() {
  const targets = messageJumpTargets();
  const canJump = targets.length > 1;
  for (const button of [jumpPrevBtn, jumpNextBtn, promptJumpPrevBtn, promptJumpNextBtn]) {
    if (button) button.disabled = !canJump;
  }
}

function exportActiveThread() {
  const thread = getActiveThread();
  if (!thread) return;
  const lines = [`# ${thread.title}`, "", `Export: ${new Date().toLocaleString("vi-VN")}`, ""];
  for (const message of thread.messages) {
    lines.push(`## ${message.role === "user" ? "Bạn" : "Agent chủ"}`, "", message.content, "");
  }
  const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${safeDownloadName(thread.title)}.md`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Đã xuất Markdown.");
}

function safeDownloadName(value) {
  return value.replace(/[<>:"/\\|?*\x00-\x1f]+/g, "_").trim().slice(0, 80) || "agent-chat";
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 1500);
}

function formatNumber(value) {
  return new Intl.NumberFormat("vi-VN").format(value || 0);
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderMarkdown(text) {
  const lines = text.split("\n");
  const out = [];
  let list = null;
  let inCode = false;
  const closeList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };
  const inline = (value) =>
    value.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
  const isTableRow = (value) => {
    const trimmed = value.trim();
    return trimmed.startsWith("|") && trimmed.endsWith("|") && trimmed.split("|").length >= 4;
  };
  const isTableDivider = (value) => {
    const cells = splitTableCells(value);
    return cells.length > 1 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.trim()));
  };
  const splitTableCells = (value) => value.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
  const renderTable = (startIndex) => {
    const header = splitTableCells(lines[startIndex]);
    const rows = [];
    let index = startIndex + 2;
    while (index < lines.length && isTableRow(lines[index])) {
      rows.push(splitTableCells(lines[index]));
      index += 1;
    }
    const columnCount = Math.max(header.length, ...rows.map((row) => row.length));
    const normalize = (row) => Array.from({ length: columnCount }, (_, cellIndex) => row[cellIndex] || "");
    out.push('<div class="table-wrap"><table>');
    out.push(`<thead><tr>${normalize(header).map((cell) => `<th>${inline(cell)}</th>`).join("")}</tr></thead>`);
    out.push("<tbody>");
    for (const row of rows) {
      out.push(`<tr>${normalize(row).map((cell) => `<td>${inline(cell)}</td>`).join("")}</tr>`);
    }
    out.push("</tbody></table></div>");
    return index;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) {
      closeList();
      out.push(inCode ? "</code></pre>" : "<pre><code>");
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      out.push(`${line}\n`);
      continue;
    }
    if (!trimmed) {
      closeList();
      continue;
    }
    if (
      index + 1 < lines.length &&
      isTableRow(lines[index]) &&
      isTableRow(lines[index + 1]) &&
      isTableDivider(lines[index + 1])
    ) {
      closeList();
      index = renderTable(index) - 1;
      continue;
    }
    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      closeList();
      const level = Math.min(heading[1].length + 1, 4);
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }
    const unordered = trimmed.match(/^[-*]\s+(.+)$/);
    if (unordered) {
      if (list !== "ul") {
        closeList();
        list = "ul";
        out.push("<ul>");
      }
      out.push(`<li>${inline(unordered[1])}</li>`);
      continue;
    }
    const ordered = trimmed.match(/^\d+\.\s+(.+)$/);
    if (ordered) {
      if (list !== "ol") {
        closeList();
        list = "ol";
        out.push("<ol>");
      }
      out.push(`<li>${inline(ordered[1])}</li>`);
      continue;
    }
    closeList();
    out.push(`<p>${inline(trimmed)}</p>`);
  }
  closeList();
  if (inCode) out.push("</code></pre>");
  return out.join("");
}

function stripSourceFooter(text) {
  const stopPrefixes = [
    "Nguồn brain hữu ích",
    "Nguon brain huu ich",
    "Nguồn hữu ích",
    "Brain/source hữu ích",
    "Sources used",
    "Useful brain sources",
    "Nếu bạn muốn",
    "Neu ban muon",
  ];
  const lines = String(text || "").split("\n");
  const kept = [];
  for (const line of lines) {
    const normalized = line.trim().replace(/^#+\s*/, "").replace(/^[-*]\s*/, "").trim();
    if (stopPrefixes.some((prefix) => normalized.startsWith(prefix))) break;
    kept.push(line);
  }
  return kept.join("\n").trim();
}

function filesFromClipboard(clipboardData) {
  if (!clipboardData) return [];
  const files = Array.from(clipboardData.files || []);
  if (files.length) return files;
  const itemFiles = [];
  for (const item of Array.from(clipboardData.items || [])) {
    if (item.kind !== "file") continue;
    const file = item.getAsFile();
    if (!file) continue;
    const extension = file.type.split("/").pop() || "png";
    const name = file.name || `clipboard-image-${Date.now()}.${extension}`;
    itemFiles.push(new File([file], name, { type: file.type || "application/octet-stream" }));
  }
  return itemFiles;
}

sendBtn.addEventListener("click", sendMessage);
newChatBtn.addEventListener("click", () => createThread("Chat mới"));
scrollBottomBtn?.addEventListener("click", scrollChatToBottom);
jumpPrevBtn?.addEventListener("click", () => jumpToMessage(-1));
jumpNextBtn?.addEventListener("click", () => jumpToMessage(1));
promptJumpPrevBtn?.addEventListener("click", () => jumpToMessage(-1));
promptJumpNextBtn?.addEventListener("click", () => jumpToMessage(1));
attachBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => uploadFiles(fileInput.files));
themeToggleBtn.addEventListener("click", toggleTheme);
exportBtn.addEventListener("click", exportActiveThread);
statusBtn.addEventListener("click", () => {
  statusPanel.hidden = !statusPanel.hidden;
  if (!brainStatus) loadStatus();
});
threadSearch.addEventListener("input", renderThreads);
chat.addEventListener("scroll", updateScrollBottomButton);
quickActions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-prompt]");
  if (!button) return;
  if (button.dataset.module === "true") {
    prompt.value = button.dataset.prompt;
    activeModuleId = button.dataset.moduleId || moduleIdFromLabel(button.textContent);
    applyResponseMode("balanced");
    autoResize();
    prompt.focus();
    showToast(`Module: ${button.textContent.trim()}`);
    return;
  }
  const label = button.textContent.trim().toLowerCase();
  const moduleLabels = ["analyze offer", "analyze plr", "upgrade kit", "buyer avatar", "product assets", "qc checklist", "oto/funnel", "w+ listing", "jv pack", "traffic content", "email funnel", "saas upgrade", "export zip", "launch pack"];
  if (moduleLabels.some((item) => label.includes(item))) {
    prompt.value = button.dataset.prompt;
    applyResponseMode("balanced");
  } else if (label.includes("sales page")) {
    prompt.value = "Viết sales page hoàn chỉnh bằng tiếng Việt cho AI PLR Rebrand Kit để bán trên WarriorPlus. Yêu cầu: không claim thu nhập, có headline mạnh, subheadline, problem, agitate, solution, what you get, 5 bonus, who it is for, who it is not for, FAQ, refund/guarantee language, CTA và cảnh báo license rõ ràng.";
    activeModuleId = "sales_page";
    applyResponseMode("balanced");
  } else if (label.includes("funnel")) {
    prompt.value = button.dataset.prompt;
    activeModuleId = "funnel_plan";
    applyResponseMode("balanced");
  } else {
    prompt.value = button.dataset.prompt;
    activeModuleId = "";
  }
  autoResize();
  prompt.focus();
});

function moduleIdFromLabel(value) {
  const label = String(value || "").trim().toLowerCase();
  const map = {
    "analyze plr": "analyze_plr",
    "idea score": "idea_score",
    "depth check": "depth_check",
    "upgrade kit": "upgrade_kit",
    "product assets": "product_assets",
    "deep assets": "deep_create_product_assets",
    "deep file": "deep_write_file",
    "qc checklist": "qc_checklist",
    "completeness": "asset_completeness",
    "readiness": "launch_readiness",
    "export zip": "export_zip",
    "launch pack": "launch_pack",
    "offer angle": "offer_angle",
    "sales page": "sales_page",
    "objections": "objections",
    "funnel plan": "funnel_plan",
    "w+ listing": "warriorplus_listing",
    "proof": "proof",
    "delivery": "delivery_page",
    "onboarding": "onboarding",
    "jv page": "jv_page",
    "swipe pack": "swipe_pack",
    "prospects": "prospects",
    "outreach": "outreach",
    "tiers": "tiers",
    "review access": "review_access",
    "saas potential": "saas_potential",
    "mvp plan": "mvp_plan",
    "membership": "membership",
    "whitelabel": "whitelabel",
    "product line": "product_line",
    "scan library": "scan_library",
    "market gap": "market_gap",
    "competitor": "competitor",
    "platform fit": "platform_fit",
    "localize en": "translate_english",
    "storage report": "storage_report",
    "optimize storage": "optimize_storage",
  };
  return map[label] || "";
}

function installQuickActionTranslations() {
  const labelMap = {
    "Build Product": "Xây sản phẩm",
    "Sale Page / Funnel": "Trang bán hàng / Phễu bán hàng",
    "JV Manager": "Quản lý JV / tiếp thị liên kết",
    "SaaS / Membership": "SaaS / Gói thành viên",
    "Market Research": "Nghiên cứu thị trường",
    "Analyze PLR": "Phân tích PLR",
    "Idea Score": "Chấm điểm ý tưởng",
    "Depth Check": "Kiểm tra độ sâu sản phẩm",
    "Upgrade Kit": "Nâng cấp thành bộ sản phẩm",
    "Product Assets": "Tài sản sản phẩm",
    "Deep Assets": "Viết sâu toàn bộ file sản phẩm",
    "Deep File": "Viết sâu một file cụ thể",
    "QC Checklist": "Checklist kiểm chất lượng",
    "Completeness": "Kiểm tra đủ file chưa",
    "Readiness": "Độ sẵn sàng launch",
    "Export ZIP": "Xuất file ZIP",
    "Launch Pack": "Bộ launch",
    "Full Launch Pack": "Bộ launch đầy đủ",
    "Offer Angle": "Góc chào bán",
    "Sales Page": "Trang bán hàng",
    "Objections": "Xử lý phản đối",
    "Funnel Plan": "Kế hoạch phễu",
    "W+ Listing": "Listing WarriorPlus",
    "Proof": "Bằng chứng thay thế",
    "Delivery": "Trang giao hàng",
    "Onboarding": "Email hướng dẫn sau mua",
    "JV Page": "Trang JV",
    "Swipe Pack": "Bộ email/post quảng bá",
    "Prospects": "Danh sách JV tiềm năng",
    "Outreach": "Tin nhắn tiếp cận",
    "Tiers": "Tầng hoa hồng affiliate",
    "Review Access": "Quyền truy cập review",
    "SaaS Potential": "Tiềm năng SaaS",
    "MVP Plan": "Kế hoạch MVP",
    "Membership": "Gói thành viên",
    "Whitelabel": "Giấy phép whitelabel",
    "Product Line": "Dòng sản phẩm",
    "Scan Library": "Quét thư viện",
    "Market Gap": "Khoảng trống thị trường",
    "Competitor": "Đối thủ",
    "Platform Fit": "Độ hợp nền tảng",
    "Localize EN": "Bản địa hóa sang thị trường tiếng Anh",
    "Storage Report": "Báo cáo dung lượng",
    "Optimize Storage": "Tối ưu dung lượng",
    "Nhanh": "Trả lời nhanh",
    "Cân bằng": "Cân bằng tốc độ và độ sâu",
    "Sâu": "Phân tích sâu nhất",
  };
  for (const item of document.querySelectorAll(".quick-group-title, .quick-actions button, .mode-selector button")) {
    const label = item.textContent.trim();
    const vi = labelMap[label] || translateEnglishText(label);
    if (!vi || vi.toLowerCase() === label.toLowerCase()) continue;
    item.dataset.viLabel = vi;
    item.setAttribute("title", `${label} → ${vi}`);
  }
  if (hoverTooltipInstalled) return;
  hoverTooltipInstalled = true;
  document.addEventListener("mouseover", (event) => {
    const target = event.target.closest("[data-vi-label]");
    if (!target || !document.body.contains(target)) return;
    showFloatingTranslation(target.dataset.viLabel, target.getBoundingClientRect(), "hover");
  });
  document.addEventListener("mouseout", (event) => {
    if (!event.target.closest("[data-vi-label]")) return;
    hideFloatingTranslationSoon();
  });
}

function installSelectionTranslator() {
  document.addEventListener("selectionchange", scheduleSelectionTranslation);
  document.addEventListener("mouseup", scheduleSelectionTranslation);
  document.addEventListener("pointerup", scheduleSelectionTranslation);
  document.addEventListener("dblclick", scheduleSelectionTranslation);
  document.addEventListener("touchend", scheduleSelectionTranslation);
  document.addEventListener("keyup", (event) => {
    if (event.key === "Shift" || event.key.startsWith("Arrow")) scheduleSelectionTranslation();
  });
}

function installBlackCopy() {
  document.addEventListener("copy", (event) => {
    const selection = window.getSelection();
    const text = selection?.toString() || "";
    if (!text.trim() || !selectionInsideApp(selection)) return;
    event.preventDefault();
    event.clipboardData?.setData("text/plain", text);
    event.clipboardData?.setData(
      "text/html",
      `<div style="color:#000000;background:#ffffff;font-family:Segoe UI,Arial,sans-serif;line-height:1.55;">${escapeHtml(text).replaceAll("\n", "<br>")}</div>`
    );
  });
}

function scheduleSelectionTranslation() {
  clearTimeout(selectionTranslateTimer);
  selectionTranslateTimer = setTimeout(showSelectionTranslation, 25);
}

function showSelectionTranslation() {
  const selection = window.getSelection();
  const text = selection?.toString().replace(/\s+/g, " ").trim() || "";
  if (!text || text.length > 90 || !selectionInsideApp(selection)) {
    hideFloatingTranslation();
    return;
  }
  const translated = translateEnglishText(text);
  if (!translated || translated.toLowerCase() === text.toLowerCase()) {
    hideFloatingTranslation();
    return;
  }
  const range = selection.rangeCount ? selection.getRangeAt(0) : null;
  const rect = range?.getBoundingClientRect();
  if (!rect || (!rect.width && !rect.height)) return;
  showFloatingTranslation(translated, rect, "selection");
}

function selectionInsideApp(selection) {
  if (!selection || !selection.rangeCount) return false;
  const node = selection.anchorNode?.nodeType === Node.ELEMENT_NODE ? selection.anchorNode : selection.anchorNode?.parentElement;
  return Boolean(node?.closest?.(".app"));
}

function showFloatingTranslation(text, rect, mode = "selection") {
  const tooltip = floatingTranslationEl();
  clearTimeout(tooltip.hideTimer);
  tooltip.textContent = text;
  tooltip.dataset.mode = mode;
  tooltip.classList.add("show");
  const padding = 10;
  const left = Math.min(window.innerWidth - tooltip.offsetWidth - padding, Math.max(padding, rect.left + rect.width / 2 - tooltip.offsetWidth / 2));
  const top = Math.max(padding, rect.top - tooltip.offsetHeight - 9);
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function hideFloatingTranslationSoon() {
  const tooltip = floatingTranslationEl();
  clearTimeout(tooltip.hideTimer);
  tooltip.hideTimer = setTimeout(hideFloatingTranslation, translationHideDelayMs);
}

function hideFloatingTranslation() {
  if (selectionTooltip) selectionTooltip.classList.remove("show");
}

function floatingTranslationEl() {
  if (selectionTooltip) return selectionTooltip;
  selectionTooltip = document.createElement("div");
  selectionTooltip.className = "translation-popover";
  selectionTooltip.addEventListener("mouseenter", () => clearTimeout(selectionTooltip.hideTimer));
  selectionTooltip.addEventListener("mouseleave", hideFloatingTranslationSoon);
  document.body.appendChild(selectionTooltip);
  return selectionTooltip;
}

function translateEnglishText(value) {
  const original = String(value || "").trim();
  if (!original || /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(original)) {
    return "";
  }
  const normalized = normalizeTranslationKey(original);
  const phraseMap = translationDictionary();
  if (phraseMap[normalized]) return phraseMap[normalized];

  const words = normalized.match(/[a-z0-9+]+/g) || [];
  if (!words.length) return "";
  const translatedWords = [];
  let known = 0;
  for (let index = 0; index < words.length; index += 1) {
    const four = words.slice(index, index + 4).join(" ");
    const three = words.slice(index, index + 3).join(" ");
    const two = words.slice(index, index + 2).join(" ");
    if (phraseMap[four]) {
      translatedWords.push(phraseMap[four]);
      known += 4;
      index += 3;
    } else if (phraseMap[three]) {
      translatedWords.push(phraseMap[three]);
      known += 3;
      index += 2;
    } else if (phraseMap[two]) {
      translatedWords.push(phraseMap[two]);
      known += 2;
      index += 1;
    } else if (lookupTranslatedWord(words[index], phraseMap)) {
      translatedWords.push(lookupTranslatedWord(words[index], phraseMap));
      known += 1;
    } else {
      translatedWords.push(words[index]);
    }
  }
  if (!known) return "";
  const coverage = known / words.length;
  if (words.length > 1 && coverage < 0.35) return "";
  return translatedWords.join(" ");
}

function lookupTranslatedWord(word, phraseMap) {
  if (phraseMap[word]) return phraseMap[word];
  const candidates = [];
  if (word.endsWith("ies") && word.length > 4) candidates.push(`${word.slice(0, -3)}y`);
  if (word.endsWith("es") && word.length > 3) candidates.push(word.slice(0, -2));
  if (word.endsWith("s") && word.length > 3) candidates.push(word.slice(0, -1));
  if (word.endsWith("ing") && word.length > 5) candidates.push(word.slice(0, -3), `${word.slice(0, -3)}e`);
  if (word.endsWith("ed") && word.length > 4) candidates.push(word.slice(0, -2), `${word.slice(0, -1)}`);
  for (const candidate of candidates) {
    if (phraseMap[candidate]) return phraseMap[candidate];
  }
  return "";
}

function normalizeTranslationKey(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201c\u201d]/g, '"')
    .replace(/[^a-z0-9+/\s-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function translationDictionary() {
  return {
    "agent": "tác nhân AI",
    "affiliate": "tiếp thị liên kết",
    "affiliate marketer": "người làm affiliate",
    "affiliate disclosure": "thông báo có link affiliate",
    "ai": "trí tuệ nhân tạo",
    "angle": "góc tiếp cận",
    "analyze": "phân tích",
    "analyze offer": "phân tích offer",
    "analyze plr": "phân tích PLR",
    "asset": "tài sản",
    "assets": "tài sản",
    "build": "xây dựng",
    "build product": "xây sản phẩm",
    "buyer": "người mua",
    "buyer avatar": "chân dung khách hàng",
    "bank": "ngân hàng mẫu",
    "bonus": "quà tặng kèm",
    "campaign": "chiến dịch",
    "campaign map": "bản đồ chiến dịch",
    "check": "kiểm tra",
    "checklist": "danh sách kiểm tra",
    "commission": "hoa hồng",
    "commissions": "hoa hồng",
    "competitor": "đối thủ",
    "compliance": "tuân thủ",
    "completeness": "độ đầy đủ",
    "content": "nội dung",
    "copy": "sao chép",
    "cta": "lời kêu gọi hành động",
    "delivery": "giao hàng",
    "depth": "độ sâu",
    "depth check": "kiểm tra độ sâu",
    "digital": "kỹ thuật số",
    "digital product": "sản phẩm số",
    "digital product vendor": "người bán sản phẩm số",
    "email": "email",
    "example": "ví dụ",
    "examples": "ví dụ",
    "export": "xuất",
    "export zip": "xuất ZIP",
    "facebook": "Facebook",
    "fake urgency": "khẩn cấp giả",
    "file": "tệp",
    "files": "các tệp",
    "fe": "sản phẩm đầu phễu",
    "funnel": "phễu bán hàng",
    "funnel plan": "kế hoạch phễu",
    "full launch pack": "bộ launch đầy đủ",
    "idea": "ý tưởng",
    "idea score": "chấm điểm ý tưởng",
    "implementation": "triển khai",
    "income": "thu nhập",
    "income guarantee": "cam kết thu nhập",
    "jv": "đối tác liên doanh",
    "jv manager": "quản lý JV",
    "jv page": "trang JV",
    "jv pack": "bộ tài liệu JV",
    "launch": "ra mắt",
    "launch pack": "bộ launch",
    "listing": "trang listing",
    "localize": "bản địa hóa",
    "market": "thị trường",
    "market gap": "khoảng trống thị trường",
    "market research": "nghiên cứu thị trường",
    "membership": "gói thành viên",
    "mvp": "bản tối thiểu có thể bán/thử",
    "mvp plan": "kế hoạch MVP",
    "objection": "phản đối",
    "objections": "xử lý phản đối",
    "offer": "lời chào bán",
    "offer angle": "góc chào bán",
    "onboarding": "hướng dẫn sau mua",
    "oto": "upsell sau khi mua",
    "outreach": "tiếp cận",
    "outreach tracker": "bảng theo dõi tiếp cận",
    "overbuild": "xây quá mức / làm quá sớm trước khi kiểm chứng",
    "platform": "nền tảng",
    "platform fit": "độ hợp nền tảng",
    "plr": "quyền nhãn riêng PLR",
    "planner": "bảng lập kế hoạch",
    "promo": "quảng bá",
    "promo date": "ngày quảng bá",
    "promise": "lời hứa kết quả",
    "prompt": "câu lệnh prompt",
    "prompts": "các câu lệnh prompt",
    "product": "sản phẩm",
    "product assets": "tài sản sản phẩm",
    "product line": "dòng sản phẩm",
    "product vendor": "người bán sản phẩm",
    "proof": "bằng chứng",
    "prospects": "khách/JV tiềm năng",
    "qc": "kiểm chất lượng",
    "qc checklist": "checklist kiểm chất lượng",
    "readiness": "độ sẵn sàng",
    "review": "xem xét",
    "review access": "quyền truy cập review",
    "risk": "rủi ro",
    "saas": "phần mềm dạng dịch vụ",
    "saas potential": "tiềm năng SaaS",
    "sales": "bán hàng",
    "sales page": "trang bán hàng",
    "sales page angle": "góc trang bán hàng",
    "scan": "quét",
    "scan library": "quét thư viện",
    "score": "điểm",
    "sent": "đã gửi",
    "soft": "mềm / thử nghiệm nhẹ",
    "soft launch": "ra mắt thử nghiệm nhẹ",
    "status": "trạng thái",
    "storage": "dung lượng lưu trữ",
    "storage report": "báo cáo dung lượng",
    "subject line": "tiêu đề email",
    "subject bank": "ngân hàng tiêu đề email",
    "swipe": "mẫu quảng bá tham khảo",
    "swipe pack": "bộ mẫu quảng bá",
    "template": "mẫu",
    "templates": "các mẫu",
    "tiers": "các tầng",
    "traffic": "lưu lượng truy cập",
    "upgrade": "nâng cấp",
    "upgrade kit": "nâng cấp thành bộ sản phẩm",
    "validation": "kiểm chứng thị trường",
    "vendor": "người bán",
    "warriorplus": "nền tảng WarriorPlus",
    "warriorplus listing": "listing WarriorPlus",
    "w+ listing": "listing WarriorPlus",
    "whitelabel": "giấy phép bán lại dưới thương hiệu riêng",
    "workflow": "quy trình làm việc",
    "zip": "tệp nén ZIP",
  };
}
modeSelector?.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-mode]");
  if (!button) return;
  applyResponseMode(button.dataset.mode);
  const label = button.textContent.trim() || "Nhanh";
  showToast(`Chế độ: ${label}`);
});

clearBtn.addEventListener("click", () => {
  const thread = getActiveThread();
  if (!thread) return;
  if (thread.messages.length && !window.confirm("Xóa nội dung chat hiện tại?")) return;
  thread.messages = [];
  thread.title = "Chat mới";
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  renderActiveThread();
});

window.addEventListener("dragover", (event) => event.preventDefault());
window.addEventListener("drop", (event) => {
  event.preventDefault();
  if (event.dataTransfer?.files?.length) uploadFiles(event.dataTransfer.files);
});
window.addEventListener("paste", (event) => {
  const pastedFiles = filesFromClipboard(event.clipboardData);
  if (pastedFiles.length) {
    event.preventDefault();
    uploadFiles(pastedFiles);
  }
});
document.addEventListener("click", () => {
  closeFileMenus();
  if (!openThreadMenuId) return;
  openThreadMenuId = null;
  renderThreads();
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !openThreadMenuId) return;
  openThreadMenuId = null;
  renderThreads();
});
window.addEventListener("focus", refreshFromServer);
setInterval(refreshFromServer, 5000);

prompt.addEventListener("input", autoResize);
prompt.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

installTextRepair();

function installTextRepair() {
  repairVisibleText(document.body);
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "characterData") {
        repairTextNode(mutation.target);
        continue;
      }
      for (const node of mutation.addedNodes) repairVisibleText(node);
    }
  });
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
}

function repairVisibleText(root) {
  if (!root) return;
  if (root.nodeType === Node.TEXT_NODE) {
    repairTextNode(root);
    return;
  }
  if (root.nodeType !== Node.ELEMENT_NODE) return;
  for (const attr of ["title", "aria-label", "placeholder", "value"]) {
    if (root.hasAttribute?.(attr)) {
      const value = root.getAttribute(attr);
      const repaired = repairMojibake(value);
      if (repaired !== value) root.setAttribute(attr, repaired);
    }
  }
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    repairTextNode(node);
    node = walker.nextNode();
  }
}

function repairTextNode(node) {
  const repaired = repairMojibake(node.nodeValue);
  if (repaired !== node.nodeValue) node.nodeValue = repaired;
}

function repairMojibake(value) {
  const text = String(value || "");
  if (!/[ÃÂÄÆâáºá»]/.test(text)) return text;
  const cp1252 = {
    0x20ac: 0x80,
    0x201a: 0x82,
    0x0192: 0x83,
    0x201e: 0x84,
    0x2026: 0x85,
    0x2020: 0x86,
    0x2021: 0x87,
    0x02c6: 0x88,
    0x2030: 0x89,
    0x0160: 0x8a,
    0x2039: 0x8b,
    0x0152: 0x8c,
    0x017d: 0x8e,
    0x2018: 0x91,
    0x2019: 0x92,
    0x201c: 0x93,
    0x201d: 0x94,
    0x2022: 0x95,
    0x2013: 0x96,
    0x2014: 0x97,
    0x02dc: 0x98,
    0x2122: 0x99,
    0x0161: 0x9a,
    0x203a: 0x9b,
    0x0153: 0x9c,
    0x017e: 0x9e,
    0x0178: 0x9f,
  };
  try {
    const bytes = Array.from(text, (char) => {
      const code = char.charCodeAt(0);
      return cp1252[code] ?? (code <= 255 ? code : null);
    });
    if (bytes.some((byte) => byte === null)) return text;
    const decoded = new TextDecoder("utf-8", { fatal: true }).decode(new Uint8Array(bytes));
    return decoded;
  } catch {
    return text;
  }
}

