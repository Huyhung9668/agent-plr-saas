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
const promptLibraryBtn = document.getElementById("promptLibraryBtn");
const sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
const sidebarBackdrop = document.getElementById("sidebarBackdrop");
const quickActionsToggle = document.getElementById("quickActionsToggle");
const modelSelect = document.getElementById("modelSelect");
const toolModeSelect = document.getElementById("toolModeSelect");
const messageCount = document.getElementById("messageCount");
const activeModeLabel = document.getElementById("activeModeLabel");
const retryLastBtn = document.getElementById("retryLastBtn");
const artifactPanel = document.getElementById("artifactPanel");
const artifactTitle = document.getElementById("artifactTitle");
const artifactBody = document.getElementById("artifactBody");
const artifactCopyBtn = document.getElementById("artifactCopyBtn");
const artifactDownloadBtn = document.getElementById("artifactDownloadBtn");
const artifactCloseBtn = document.getElementById("artifactCloseBtn");
const statusPanel = document.getElementById("statusPanel");
const brainSummary = document.getElementById("brainSummary");
const appVersionBadges = document.querySelectorAll("[data-app-version]");
const workspaceBadge = document.getElementById("workspaceBadge");
const workspaceTabs = document.getElementById("workspaceTabs");
const quickActions = document.getElementById("quickActions");
const modeSelector = document.getElementById("modeSelector");
const toast = document.getElementById("toast");

const publicServerBaseUrl = "http://103.82.26.216:8088";
const workspaceId = detectWorkspaceId();
const workspaceSuffix = workspaceId === "default" ? "" : `_${workspaceId}`;
const threadStorageKey = `master_agent_threads_v2${workspaceSuffix}`;
const themeStorageKey = "master_agent_theme_v1";
const syncStorageKey = `master_agent_threads_file_sync_v1${workspaceSuffix}`;
const modeStorageKey = "master_agent_response_mode_v2";
const modelStorageKey = "master_agent_model_persona_v1";
const toolModeStorageKey = "master_agent_tool_mode_v1";
const sidebarStorageKey = "master_agent_sidebar_collapsed_v1";
const promptLibraryStorageKey = "master_agent_prompt_library_open_v1";
const translationHideDelayMs = 180;
const streamStallTimeoutMs = 120000;

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
let selectedModelPersona = loadSelectValue(modelStorageKey, "agent");
let selectedToolMode = loadSelectValue(toolModeStorageKey, "auto");
let activeArtifactContent = "";
let activeRequestId = "";
let streamRenderTimer = null;
let lastStreamRenderedText = "";
let streamStallTimer = null;
let lastRetryDraft = null;
let userScrollLocked = false;
let programmaticScrollUntil = 0;
const streamingTextStates = new WeakMap();

applyTheme(loadTheme());
applyResponseMode(responseMode);
applyShellPreferences();
init();

function initWorkspaceUi() {
  const label = workspaceId === "default" ? "Chat chính" : `Chat ${workspaceId}`;
  if (workspaceBadge) workspaceBadge.textContent = label;
  document.title = `${label} · Agent chủ`;
  workspaceTabs?.querySelectorAll("[data-workspace-tab]").forEach((tab) => {
    const isActive = tab.dataset.workspaceTab === workspaceId;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-current", isActive ? "page" : "false");
  });
}

function detectWorkspaceId() {
  const firstSegment = decodeURIComponent(window.location.pathname || "")
    .split("/")
    .filter(Boolean)[0];
  if (!firstSegment || ["api", "app.js", "styles.css", "favicon.ico"].includes(firstSegment)) return "default";
  return firstSegment.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 48) || "default";
}

function workspaceApiUrl(path) {
  const separator = path.includes("?") ? "&" : "?";
  return apiUrl(`${path}${separator}workspace=${encodeURIComponent(workspaceId)}`);
}

function apiUrl(path) {
  if (window.location.protocol === "file:") {
    return `${publicServerBaseUrl}${path}`;
  }
  return path;
}

async function init() {
  initWorkspaceUi();
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
  focusPrompt();
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

function loadSelectValue(key, fallback) {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

function saveSelectValue(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Ignore private mode/localStorage errors.
  }
}

function applyShellPreferences() {
  let storedSidebarState = null;
  try {
    storedSidebarState = localStorage.getItem(sidebarStorageKey);
  } catch {
    storedSidebarState = null;
  }
  const mobileDefaultCollapsed = window.matchMedia?.("(max-width: 760px)")?.matches;
  const sidebarCollapsed = storedSidebarState === null ? mobileDefaultCollapsed : storedSidebarState === "1";
  const libraryOpen = loadSelectValue(promptLibraryStorageKey, "0") === "1";
  app.classList.toggle("sidebar-collapsed", sidebarCollapsed);
  updateSidebarA11y();
  quickActions?.classList.toggle("collapsed", !libraryOpen);
  if (quickActionsToggle) quickActionsToggle.textContent = libraryOpen ? "Ẩn thư viện prompt" : "Thư viện prompt";
  if (modelSelect) modelSelect.value = selectedModelPersona;
  if (toolModeSelect) toolModeSelect.value = selectedToolMode;
}

function toggleSidebar() {
  const collapsed = !app.classList.contains("sidebar-collapsed");
  setSidebarCollapsed(collapsed);
}

function setSidebarCollapsed(collapsed) {
  app.classList.toggle("sidebar-collapsed", Boolean(collapsed));
  saveSelectValue(sidebarStorageKey, collapsed ? "1" : "0");
  updateSidebarA11y();
}

function updateSidebarA11y() {
  const collapsed = app.classList.contains("sidebar-collapsed");
  sidebarToggleBtn?.setAttribute("aria-expanded", collapsed ? "false" : "true");
  sidebarCloseBtn?.setAttribute("aria-hidden", collapsed ? "true" : "false");
  sidebarBackdrop?.setAttribute("aria-hidden", collapsed ? "true" : "false");
}

function togglePromptLibrary(forceOpen = null) {
  const willOpen = forceOpen === null ? quickActions.classList.contains("collapsed") : Boolean(forceOpen);
  quickActions.classList.toggle("collapsed", !willOpen);
  if (quickActionsToggle) quickActionsToggle.textContent = willOpen ? "Ẩn thư viện prompt" : "Thư viện prompt";
  saveSelectValue(promptLibraryStorageKey, willOpen ? "1" : "0");
}

function selectedPersonaInstruction() {
  const modelMap = {
    agent: "",
    planner: "Persona: Planner sâu. Trả lời như chiến lược gia sản phẩm, ưu tiên roadmap, rủi ro, checklist hành động.",
    creator: "Persona: Content builder. Tạo nội dung hoàn chỉnh, có cấu trúc file, ví dụ dùng được ngay, không chỉ outline.",
    critic: "Persona: Launch critic. Audit thẳng tay, tìm lỗi bán hàng, thiếu proof, license risk, missing assets, rồi đưa fix list.",
  };
  const toolMap = {
    auto: "Tool mode: Auto. Tự dùng brain, project memory và file đính kèm khi hữu ích.",
    files: "Tool mode: Files/RAG. Ưu tiên nội dung file đính kèm, Case Study Brain từ dữ liệu cũ, và brain/source đã index.",
    case: "Tool mode: Case Study Brain. Ưu tiên kho dữ liệu cũ G:\\file_backup để rút pattern, case study, sales page, funnel, JV, KDP/kids printable; không copy nguyên văn.",
    launch: "Tool mode: Launch OS. Ưu tiên active project, launch readiness, asset checklist, funnel/JV/export status.",
    none: "Tool mode: Off. Trả lời trực tiếp, chỉ dùng ngữ cảnh chat khi đủ.",
  };
  return [modelMap[selectedModelPersona] || "", toolMap[selectedToolMode] || ""].filter(Boolean).join("\n");
}

function requestQuestionWithControls(text) {
  const instruction = selectedPersonaInstruction();
  return instruction ? `${instruction}\n\n${text}` : text;
}

function loadResponseMode() {
  try {
    const saved = localStorage.getItem(modeStorageKey);
    return ["auto", "fast", "balanced", "deep"].includes(saved) ? saved : "auto";
  } catch {
    return "auto";
  }
}

function applyResponseMode(mode) {
  responseMode = ["auto", "fast", "balanced", "deep"].includes(mode) ? mode : "auto";
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
  return ["auto", "fast", "balanced", "deep"].includes(selected) ? selected : "auto";
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
  return { auto: "Auto", fast: "Nhanh", balanced: "Cân bằng", deep: "Sâu" }[selected] || "Auto";
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
    const response = await fetch(workspaceApiUrl("/api/threads"));
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
  const wasNearBottom = isChatNearBottom();
  const serverState = await fetchServerState();
  if (!serverState || !serverState.threads.length) return;
  state = serverState;
  activeThreadId = serverState.activeThreadId || serverState.threads[0].id;
  saveLocalState();
  renderThreads();
  if (activeThreadId === previousActiveThreadId) {
    renderActiveThread({ preserveScrollTop: previousScrollTop, stickToBottom: wasNearBottom });
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
    id: thread.id || createClientId(),
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

function createClientId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  const randomPart = Math.random().toString(36).slice(2, 12);
  return `thread_${Date.now().toString(36)}_${randomPart}`;
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
    await fetch(workspaceApiUrl("/api/threads"), {
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
    id: createClientId(),
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
    focusPrompt();
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
    id: createClientId(),
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
  const stickToBottom = options.stickToBottom === true;
  const thread = getActiveThread();
  chat.innerHTML = "";
  if (!thread || !thread.messages.length) {
    renderWelcome();
    updateSessionMetrics();
    requestAnimationFrame(updateScrollBottomButton);
    return;
  }
  for (const [index, message] of thread.messages.entries()) {
    appendMessageToDom(message.role, message.content, index, false);
  }
  if (stickToBottom) {
    requestAnimationFrame(scrollChatToBottom);
  } else if (preserveScrollTop !== null) {
    requestAnimationFrame(() => {
      chat.scrollTop = preserveScrollTop;
      updateScrollBottomButton();
    });
  } else {
    requestAnimationFrame(scrollChatToBottom);
  }
  updateSessionMetrics();
  requestAnimationFrame(updateScrollBottomButton);
}

function renderWelcome() {
  const starter = document.createElement("div");
  starter.className = "welcome";
  starter.innerHTML = `
    <div class="welcome-mark">M</div>
    <h1>Hôm nay build offer nào?</h1>
    <p>Chọn một prompt mẫu hoặc nhập trực tiếp để phân tích PLR, tạo product kit, sales page, funnel, JV pack và kế hoạch SaaS.</p>
    <div class="starter-grid">
      <button type="button" data-starter-prompt="Phân tích 3 ý tưởng sản phẩm PLR + SaaS dễ bán trên WarriorPlus nhất dựa trên brain hiện tại. Với mỗi ý tưởng: buyer pain, deliverables, FE/OTO, SaaS angle, risk, next action.">Ý tưởng có thể bán</button>
      <button type="button" data-starter-prompt="Audit active project hiện tại. Chấm điểm launch readiness, liệt kê missing assets, rủi ro license/compliance, và 10 việc cần làm tiếp theo theo thứ tự ưu tiên.">Audit launch</button>
      <button type="button" data-starter-prompt="Tạo full launch pack cho AI PLR Rebrand Kit: product assets, sales page, WarriorPlus listing, JV pack, email funnel, traffic content, delivery page, export checklist.">Full launch pack</button>
      <button type="button" data-starter-prompt="Nâng nội dung thô/PLR này thành product kit bán được. Hãy tạo workflow, checklist, examples, prompts, planner, compliance note, pricing, bump/OTO và ZIP structure. Nội dung: ">Nâng content thô</button>
    </div>
  `;
  chat.appendChild(starter);
  updateScrollBottomButton();
}

function updateSessionMetrics() {
  const thread = getActiveThread();
  const count = thread?.messages?.length || 0;
  if (messageCount) messageCount.textContent = `${count} tin nhắn`;
  if (activeModeLabel) {
    const labels = { auto: "Auto", quick: "Nhanh gọn", fast: "Nhanh", asset: "Tạo asset", balanced: "Cân bằng", deep: "Sâu" };
    const modelLabels = { agent: "Agent chủ", planner: "Planner sâu", creator: "Dựng nội dung", critic: "Phản biện" };
    activeModeLabel.textContent = `${modelLabels[selectedModelPersona] || "Agent"} · ${labels[selectedResponseMode()] || "Nhanh"}`;
  }
}

async function loadStatus() {
  try {
    const response = await fetch(apiUrl("/api/status"));
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
  const appVersion = data.appVersion || "1.09";
    for (const badge of appVersionBadges) badge.textContent = `v${appVersion}`;
    const caseDocs = Number(data.caseStudyBrain?.documents || 0);
    const caseChunks = Number(data.caseStudyBrain?.chunks || 0);
    const caseLabel = caseDocs ? ` · Case ${formatNumber(caseDocs)} docs/${formatNumber(caseChunks)} chunks` : " · Case Brain chưa index";
    brainSummary.textContent = `v${appVersion} · ${data.apiReady ? "API 5.5 sẵn sàng" : "API chưa sẵn sàng"} · ${thinking} · ${detail} · ${formatNumber(totals.docs)} tài liệu · ${formatNumber(totals.chunks)} chunks${caseLabel}`;
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
  if (brainStatus.caseStudyBrain) {
    const item = brainStatus.caseStudyBrain;
    const categories = (item.categories || []).filter((category) => Number(category.count || 0) > 0).slice(0, 8);
    const card = document.createElement("div");
    card.className = "status-card";
    card.innerHTML = `
      <div class="status-card-title">Case Study Brain</div>
      <div class="project-meta">${escapeHtml(item.training_mode || "RAG memory")} · ${item.source_exists ? "source OK" : "missing source"}</div>
      <div class="status-card-metrics">
        <span>${formatNumber(item.documents || 0)} docs</span>
        <span>${formatNumber(item.chunks || 0)} chunks</span>
        <span>${item.text_mb || 0} MB text</span>
      </div>
      <div class="subagent-row">${categories.map((category) => `<span>${escapeHtml(category.category)}: ${formatNumber(category.count)}</span>`).join("") || "<span>Chưa index dữ liệu cũ</span>"}</div>
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
    label.textContent = attachment.name || "file";
    label.title = attachment.notice || attachment.type || attachment.name || "file";
    chip.appendChild(label);
    if (attachment.url) {
      chip.appendChild(createIconLink("↗", apiUrl(attachment.url), "Mở đọc file", "attachment-open-btn"));
      chip.appendChild(createIconLink("↓", apiUrl(attachment.url), "Tải file về máy", "attachment-download-btn", attachment.name || "file"));
    }
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.title = "Bỏ file";
    remove.addEventListener("click", () => {
      pendingAttachments.splice(index, 1);
      renderAttachments();
    });
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
    const formData = new FormData();
    for (const file of selected.slice(0, 10)) {
      formData.append("files", file, file.name);
    }
    const response = await fetch(workspaceApiUrl("/api/upload"), {
      method: "POST",
      body: formData,
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

function appendMessageToDom(role, content, messageIndex = null, shouldScroll = true) {
  const scrollIntent = captureChatScroll();
  const thread = getActiveThread();
  const savedMessage = thread && Number.isInteger(messageIndex) ? thread.messages[messageIndex] : null;
  const hasSavedAttachments = Array.isArray(savedMessage?.attachments) && savedMessage.attachments.length > 0;
  let displayContent = role === "assistant" ? stripSourceFooter(content) : (hasSavedAttachments ? stripAttachmentSummary(content) : content);
  if (role === "assistant" && savedMessage?.fileOutputCollapsed && Array.isArray(savedMessage.files) && savedMessage.files.length) {
    displayContent = `**${inferArtifactTitle(displayContent)}**`;
  }
  const el = document.createElement("div");
  el.className = `msg ${role}`;

  const header = document.createElement("div");
  header.className = "msg-actions";
  if (role === "user" && Number.isInteger(messageIndex)) {
    const editBtn = document.createElement("button");
    editBtn.className = "edit-msg-btn";
    editBtn.type = "button";
    editBtn.title = "Sửa và gửi lại";
    editBtn.textContent = "✎";
    editBtn.addEventListener("click", () => editUserMessage(messageIndex));
    header.appendChild(editBtn);
  }
  if (role === "assistant" && Number.isInteger(messageIndex)) {
    const canvasBtn = document.createElement("button");
    canvasBtn.className = "artifact-msg-btn";
    canvasBtn.type = "button";
    canvasBtn.title = "Mở canvas kết quả";
    canvasBtn.textContent = "▣";
    canvasBtn.addEventListener("click", () => openArtifactPanel(currentMessageContent(messageIndex, displayContent)));
    header.appendChild(canvasBtn);

    const retryBtn = document.createElement("button");
    retryBtn.className = "retry-msg-btn";
    retryBtn.type = "button";
    retryBtn.title = "Tạo lại câu trả lời";
    retryBtn.textContent = "↻";
    retryBtn.addEventListener("click", () => regenerateAssistantMessage(messageIndex));
    header.appendChild(retryBtn);
  }
  const copyBtn = document.createElement("button");
  copyBtn.className = "copy-btn";
  copyBtn.type = "button";
  copyBtn.title = role === "assistant" ? "Copy toàn bộ trả lời" : "Copy câu hỏi";
  copyBtn.textContent = "⧉";
  copyBtn.addEventListener("click", async () => {
    try {
      await copyText(currentMessageContent(messageIndex, displayContent));
      copyBtn.textContent = "✓";
      showToast("Đã copy.");
      setTimeout(() => (copyBtn.textContent = "⧉"), 900);
    } catch (error) {
      showToast(friendlyFetchError(error));
    }
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
      showFileMenu(fileBtn, currentMessageContent(messageIndex, displayContent), messageIndex);
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

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = `${role === "assistant" ? "Agent" : "Bạn"} · VN ${formatVietnamDateTime(messageTime(thread, savedMessage))}`;
  el.appendChild(meta);

  const body = document.createElement("div");
  body.className = "msg-body";
  renderMessageBody(body, displayContent, messageIndex);
  el.appendChild(body);
  const fileChips = renderMessageFiles(savedMessage, messageIndex, displayContent);
  if (fileChips) el.appendChild(fileChips);
  el.appendChild(header);
  chat.appendChild(el);
  if (shouldScroll && shouldStickToBottom(scrollIntent)) {
    scrollChatToBottom();
  } else {
    restoreChatScroll(scrollIntent);
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

function renderMessageBody(target, content, messageIndex = null) {
  stopStreamingText(target);
  const parser = window.parseMessageFileParts;
  const createCard = window.createFileCard;
  if (typeof parser !== "function" || typeof createCard !== "function") {
    target.innerHTML = renderMarkdown(escapeHtml(content));
    return;
  }

  const parts = parser(content, Number.isInteger(messageIndex) ? messageIndex + 1 : Date.now());
  const hasFile = parts.some((part) => part.type === "file");
  if (!hasFile) {
    target.innerHTML = renderMarkdown(escapeHtml(content));
    return;
  }

  target.innerHTML = "";
  for (const part of parts) {
    if (part.type === "file") {
      target.appendChild(createCard(part.filename, part.content, part.description));
      continue;
    }
    if (!String(part.content || "").trim()) continue;
    const textWrap = document.createElement("div");
    textWrap.innerHTML = renderMarkdown(escapeHtml(part.content));
    target.appendChild(textWrap);
  }
}

function stopStreamingText(target) {
  const state = streamingTextStates.get(target);
  if (!state) return;
  if (state.timer) clearTimeout(state.timer);
  streamingTextStates.delete(target);
}

function showFileMenu(anchor, content, messageIndex = null) {
  closeFileMenus();
  if (!content.trim()) {
    showToast("Chưa có nội dung để tạo file.");
    return;
  }
  const menu = document.createElement("div");
  menu.className = "file-menu";
  const compactButton = document.createElement("button");
  compactButton.type = "button";
  compactButton.textContent = "Prompt gọn MD";
  compactButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await createFileFromContent(compactPromptContent(content), "md", "prompt-gon", messageIndex);
    closeFileMenus();
  });
  menu.appendChild(compactButton);
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
      await createFileFromContent(content, format, "", messageIndex);
      closeFileMenus();
    });
    menu.appendChild(button);
  }
  anchor.closest(".msg-actions")?.appendChild(menu);
}

function closeFileMenus() {
  document.querySelectorAll(".file-menu").forEach((menu) => menu.remove());
}

function createIconLink(text, href, title, className, downloadName = "") {
  const link = document.createElement("a");
  link.className = className;
  link.href = href;
  link.title = title;
  link.setAttribute("aria-label", title);
  link.textContent = text;
  if (downloadName) link.download = downloadName;
  if (!downloadName) link.target = "_blank";
  if (!downloadName) link.rel = "noopener";
  return link;
}

function renderMessageFiles(message, messageIndex, fallbackContent = "") {
  const attachments = Array.isArray(message?.attachments) ? message.attachments : [];
  const generatedFiles = Array.isArray(message?.files) ? message.files : [];
  if (!attachments.length && !generatedFiles.length) return null;

  const wrap = document.createElement("div");
  wrap.className = "message-file-list";
  for (const attachment of attachments) {
    if (!attachment?.name) continue;
    wrap.appendChild(renderFileChip({
      name: attachment.name,
      url: attachment.url,
      openTitle: "Mở đọc file gốc",
      downloadTitle: "Tải file gốc",
    }));
  }
  for (const file of generatedFiles) {
    if (!file?.fileName) continue;
    const chip = renderFileChip({
      name: file.fileName,
      url: file.url,
      openTitle: "Mở đọc nội dung",
      downloadTitle: "Tải file về máy",
    });
    chip.querySelector("[data-open-file]")?.addEventListener("click", (event) => {
      event.preventDefault();
      openArtifactPanel(currentMessageContent(messageIndex, fallbackContent));
    });
    wrap.appendChild(chip);
  }
  return wrap.childElementCount ? wrap : null;
}

function renderFileChip({ name, url, openTitle, downloadTitle }) {
  const chip = document.createElement("div");
  chip.className = "message-file-chip";
  const fileName = document.createElement("span");
  fileName.className = "message-file-name";
  fileName.textContent = name;
  fileName.title = name;
  chip.appendChild(fileName);

  if (url) {
    const open = createIconLink("↗", apiUrl(`${url}${url.includes("?") ? "&" : "?"}view=1`), openTitle, "message-file-icon");
    open.dataset.openFile = "true";
    chip.appendChild(open);
    chip.appendChild(createIconLink("↓", apiUrl(url), downloadTitle, "message-file-icon", name));
  }
  return chip;
}

function openArtifactPanel(content) {
  activeArtifactContent = stripSourceFooter(content || "");
  if (!activeArtifactContent.trim()) {
    showToast("Chưa có nội dung để mở canvas.");
    return;
  }
  const title = inferArtifactTitle(activeArtifactContent);
  artifactTitle.textContent = title;
  artifactBody.innerHTML = renderMarkdown(escapeHtml(activeArtifactContent));
  artifactPanel.hidden = false;
  artifactPanel.classList.add("show");
}

function closeArtifactPanel() {
  artifactPanel.classList.remove("show");
  artifactPanel.hidden = true;
}

function inferArtifactTitle(content) {
  const firstHeading = String(content || "").split("\n").find((line) => /^#{1,3}\s+\S/.test(line.trim()));
  if (firstHeading) return firstHeading.replace(/^#{1,3}\s+/, "").trim().slice(0, 80);
  const firstLine = String(content || "").split("\n").find((line) => line.trim());
  return (firstLine || "Nội dung trả lời").replace(/[*`#]/g, "").trim().slice(0, 80) || "Nội dung trả lời";
}

async function copyArtifact() {
  if (!activeArtifactContent.trim()) return;
  await copyText(activeArtifactContent);
  showToast("Đã copy canvas.");
}

function downloadArtifactMarkdown() {
  if (!activeArtifactContent.trim()) return;
  const blob = new Blob([activeArtifactContent], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${safeDownloadName(artifactTitle.textContent || "agent-canvas")}.md`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Đã tải Markdown.");
}

async function copyText(text) {
  const value = String(text || "");
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
      return true;
    }
  } catch {
    // Fallback below handles HTTP/insecure clipboard restrictions.
  }
  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  textarea.style.top = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const ok = document.execCommand("copy");
  textarea.remove();
  if (!ok) throw new Error("Trình duyệt chặn copy tự động.");
  return true;
}

function compactPromptContent(content) {
  const clean = stripSourceFooter(String(content || ""))
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  const lines = clean.split("\n");
  const kept = [];
  let inPromptBlock = false;
  for (const line of lines) {
    const normalized = line.trim().toLowerCase();
    if (/^(#{1,4}\s*)?(prompt|prompts|master prompt|system prompt|user prompt|copy prompt|file prompt|prompt sử dụng|prompt su dung)\b/.test(normalized)) {
      inPromptBlock = true;
    }
    if (inPromptBlock) kept.push(line);
    if (inPromptBlock && kept.length > 20 && /^#{1,3}\s+\S/.test(line.trim()) && !/prompt/i.test(line)) {
      kept.pop();
      break;
    }
  }
  const body = (kept.join("\n").trim() || clean).slice(0, 60000);
  return `# Prompt gon\n\n${body}\n`;
}

async function createFileFromContent(content, format, titleOverride = "", messageIndex = null) {
  const thread = getActiveThread();
  const title = safeDownloadName(titleOverride || thread?.title || "agent-output");
  showToast(`Đang tạo file ${format.toUpperCase()}...`);
  try {
    const response = await fetch(apiUrl("/api/create_file"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, format, title }),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Không tạo được file.");
    attachGeneratedFileToMessage(messageIndex, data);
    showToast(`Đã tạo ${data.fileName}. Bấm icon ↓ để tải.`);
  } catch (error) {
    showToast(friendlyFetchError(error));
  }
}

function attachGeneratedFileToMessage(messageIndex, file) {
  const thread = getActiveThread();
  if (!thread || !Number.isInteger(messageIndex) || !thread.messages[messageIndex]) return;
  const message = thread.messages[messageIndex];
  message.files = Array.isArray(message.files) ? message.files : [];
  message.files.push({
    fileName: file.fileName,
    format: file.format,
    mime: file.mime,
    url: file.url,
    createdAt: Date.now(),
  });
  message.fileOutputCollapsed = true;
  thread.updatedAt = Date.now();
  saveState();
  renderActiveThread({ stickToBottom: true });
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

function editUserMessage(messageIndex) {
  const thread = getActiveThread();
  const message = thread?.messages?.[messageIndex];
  if (!message || message.role !== "user") return;
  prompt.value = stripAttachmentSummary(message.content || "");
  pendingAttachments = [];
  thread.messages = thread.messages.slice(0, messageIndex);
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  renderActiveThread();
  autoResize();
  focusPrompt();
  showToast("Đã đưa câu hỏi về ô nhập.");
}

function regenerateAssistantMessage(messageIndex) {
  const thread = getActiveThread();
  if (!thread || !Number.isInteger(messageIndex)) return;
  const previousUserIndex = findPreviousUserMessageIndex(thread, messageIndex);
  if (previousUserIndex < 0) {
    showToast("Không tìm thấy câu hỏi để tạo lại.");
    return;
  }
  const userText = stripAttachmentSummary(thread.messages[previousUserIndex].content || "");
  thread.messages = thread.messages.slice(0, previousUserIndex);
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  renderActiveThread();
  prompt.value = userText;
  autoResize();
  sendMessage();
}

function findPreviousUserMessageIndex(thread, fromIndex) {
  for (let index = fromIndex - 1; index >= 0; index -= 1) {
    if (thread.messages[index]?.role === "user") return index;
  }
  return -1;
}

function stripAttachmentSummary(text) {
  return String(text || "").split("\n\nFile 1:")[0].trim();
}

function appendThinking(label = null) {
  const scrollIntent = captureChatScroll();
  const el = document.createElement("div");
  el.className = "msg assistant thinking";
  el.innerHTML = `
    <div class="typing-indicator" aria-label="Agent đang nhập">
      <div class="ai-avatar">M</div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
  `;
  chat.appendChild(el);
  if (shouldStickToBottom(scrollIntent)) {
    scrollChatToBottom();
  } else {
    restoreChatScroll(scrollIntent);
    updateScrollBottomButton();
  }
  return () => el.remove();
}

async function fetchStreamingAnswer(payload, onDelta) {
  const response = await fetch(apiUrl("/api/chat_stream"), {
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
      if (event.type === "meta" && event.data?.mode) {
        responseMode = event.data.mode;
        updateSessionMetrics();
      }
      if (event.type === "error") throw new Error(event.data?.error || "Stream lỗi.");
    }
    if (done) break;
  }
}

function requestCancel() {
  const requestId = activeRequestId;
  if (activeController) activeController.abort();
  activeController = null;
  isStreamingAnswer = false;
  sendBtn.textContent = "➤";
  sendBtn.title = "Gửi";
  sendBtn.disabled = false;
  sendBtn.classList.remove("is-running");
  flushStreamRender();
  clearStreamStallWatchdog();
  if (requestId) {
    fetch(apiUrl("/api/cancel"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requestId }),
    }).catch(() => {});
  }
  markRetryAvailable("Đã hủy. Có thể gửi lại câu hỏi vừa rồi.");
  showToast("Đã hủy lượt trả lời.");
}

function setLastRetryDraft(draft) {
  lastRetryDraft = draft ? {
    ...draft,
    attachments: (draft.attachments || []).map((item) => ({ ...item })),
    createdAt: Date.now(),
  } : null;
  updateRetryButton();
}

function markRetryAvailable(message = "Có thể gửi lại câu hỏi vừa rồi.") {
  if (lastRetryDraft) {
    lastRetryDraft.failedAt = Date.now();
    lastRetryDraft.failureMessage = message;
  }
  updateRetryButton();
}

function clearRetryAvailable() {
  if (lastRetryDraft) {
    lastRetryDraft.failedAt = null;
    lastRetryDraft.failureMessage = "";
  }
  updateRetryButton();
}

function updateRetryButton() {
  if (!retryLastBtn) return;
  const canRetry = Boolean(lastRetryDraft?.failedAt || lastRetryDraft?.allowManualRetry);
  retryLastBtn.hidden = !canRetry;
  retryLastBtn.title = lastRetryDraft?.failureMessage || "Gửi lại câu hỏi gần nhất";
}

function clearStreamStallWatchdog() {
  if (streamStallTimer) {
    clearTimeout(streamStallTimer);
    streamStallTimer = null;
  }
}

function resetStreamStallWatchdog() {
  clearStreamStallWatchdog();
  const requestId = activeRequestId;
  streamStallTimer = setTimeout(() => {
    if (!activeController || requestId !== activeRequestId) return;
    requestCancel();
    markRetryAvailable("Kết nối/model không trả thêm nội dung trong 120 giây. Bấm gửi lại để chạy lại.");
    showToast("Lượt trả lời bị treo quá lâu, đã dừng.");
  }, streamStallTimeoutMs);
}

function retryLastRequest() {
  if (!lastRetryDraft) {
    showToast("Chưa có câu hỏi nào để gửi lại.");
    return;
  }
  if (activeController) requestCancel();
  const thread = state.threads.find((item) => item.id === lastRetryDraft.threadId) || getActiveThread();
  if (!thread) return;
  activeThreadId = thread.id;
  removeLastFailedAttempt(thread, lastRetryDraft.userContent, Boolean(lastRetryDraft.allowManualRetry));
  prompt.value = lastRetryDraft.text || "";
  pendingAttachments = (lastRetryDraft.attachments || []).map((item) => ({ ...item }));
  activeModuleId = lastRetryDraft.module || "";
  applyResponseMode(lastRetryDraft.mode || "auto");
  clearRetryAvailable();
  saveState();
  renderThreads();
  renderActiveThread();
  renderAttachments();
  autoResize();
  focusPrompt();
  sendMessage();
}

function removeLastFailedAttempt(thread, userContent, forceAssistantRemoval = false) {
  if (!thread?.messages?.length) return;
  while (thread.messages.length && thread.messages.at(-1)?.role === "assistant") {
    const content = String(thread.messages.at(-1)?.content || "").trim();
    if (forceAssistantRemoval || !content || content.includes("Kết nối bị ngắt") || content.includes("API model đang tạm lỗi") || content.includes("Model chưa trả nội dung")) {
      thread.messages.pop();
      forceAssistantRemoval = false;
      continue;
    }
    break;
  }
  const last = thread.messages.at(-1);
  if (last?.role === "user" && String(last.content || "") === String(userContent || "")) {
    thread.messages.pop();
  }
  thread.updatedAt = Date.now();
}

function scheduleStreamRender(thread, assistantMessageIndex, assistantRendered, getText) {
  if (streamRenderTimer) return;
  streamRenderTimer = setTimeout(() => {
    streamRenderTimer = null;
    const scrollIntent = captureChatScroll();
    const clean = stripSourceFooter(getText());
    if (clean === lastStreamRenderedText) return;
    lastStreamRenderedText = clean;
    thread.messages[assistantMessageIndex].content = clean;
    if (assistantRendered?.body) {
      renderStreamingText(assistantRendered.body, clean);
    }
    persistStreamingDraft(false);
    if (shouldStickToBottom(scrollIntent)) {
      scrollChatToBottom();
    } else {
      restoreChatScroll(scrollIntent);
    }
    updateScrollBottomButton();
  }, 140);
}

function renderStreamingText(target, text) {
  let state = streamingTextStates.get(target);
  if (!state) {
    target.innerHTML = "";
    const paragraph = document.createElement("p");
    paragraph.className = "streaming-text";
    target.appendChild(paragraph);
    state = { full: "", shown: "", paragraph, timer: null };
    streamingTextStates.set(target, state);
  }
  state.full = text;
  if (state.timer) return;
  const tick = () => {
    const scrollIntent = captureChatScroll();
    if (state.shown.length < state.full.length) {
      const remaining = state.full.length - state.shown.length;
      const batch = Math.min(remaining, Math.floor(Math.random() * 3) + 1);
      state.shown = state.full.slice(0, state.shown.length + batch);
    }
    state.paragraph.innerHTML = `${escapeHtml(state.shown).replace(/\n/g, "<br>")}<span class="stream-cursor"></span>`;
    if (shouldStickToBottom(scrollIntent)) {
      scrollChatToBottom();
    } else {
      restoreChatScroll(scrollIntent);
    }
    const delay = Math.max(10, 30 - Math.floor(state.full.length / 50));
    state.timer = state.shown.length < state.full.length ? setTimeout(tick, delay) : null;
  };
  tick();
}

function flushStreamRender() {
  if (streamRenderTimer) {
    clearTimeout(streamRenderTimer);
    streamRenderTimer = null;
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
    requestCancel();
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
  setLastRetryDraft({
    threadId: thread.id,
    text,
    userContent,
    attachments: attachmentsForRequest,
    mode: requestMode,
    module: requestModule,
    allowManualRetry: false,
  });
  responseMode = requestMode;
  applyResponseMode(requestMode);
  const thinkingLabel = effectiveModeLabel(text, attachmentsForRequest);
  thread.messages.push({
    role: "user",
    content: userContent,
    createdAt: Date.now(),
    attachments: attachmentsForRequest.map((item) => ({ ...item, text: "" })),
  });
  const userMessageIndex = thread.messages.length - 1;
  thread.updatedAt = Date.now();
  saveState();
  renderThreads();
  releaseChatScrollLock();
  appendMessageToDom("user", userContent, userMessageIndex);
  prompt.value = "";
  pendingAttachments = [];
  renderAttachments();
  autoResize();

  activeController = new AbortController();
  activeRequestId = createClientId();
  isStreamingAnswer = true;
  lastStreamSaveAt = 0;
  sendBtn.textContent = "■";
  sendBtn.title = "Dừng trả lời";
  sendBtn.disabled = false;
  sendBtn.classList.add("is-running");
  resetStreamStallWatchdog();
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
        question: requestQuestionWithControls(text || "Hãy phân tích file người dùng vừa gửi."),
        requestId: activeRequestId,
        history: thread.messages.slice(-10),
        attachments: attachmentsForRequest,
        mode: requestMode,
        module: requestModule,
      },
      (delta) => {
        resetStreamStallWatchdog();
        ensureAssistantMessage();
        streamedAnswer += delta;
        scheduleStreamRender(thread, assistantMessageIndex, assistantRendered, () => streamedAnswer);
      }
    );
    flushStreamRender();
    if (stopThinking) {
      stopThinking();
      stopThinking = null;
    }
    if (assistantMessageIndex === null) {
      appendAssistantMessage(thread, "Model chưa trả nội dung.");
      markRetryAvailable("Model chưa trả nội dung. Bấm gửi lại để chạy lại.");
    } else {
      const clean = stripSourceFooter(streamedAnswer);
      thread.messages[assistantMessageIndex].content = clean;
      if (assistantRendered?.body) {
        const scrollIntent = captureChatScroll();
        renderMessageBody(assistantRendered.body, clean, assistantMessageIndex);
        if (shouldStickToBottom(scrollIntent)) {
          scrollChatToBottom();
        } else {
          restoreChatScroll(scrollIntent);
          updateScrollBottomButton();
        }
      }
      persistStreamingDraft(true);
      lastRetryDraft = lastRetryDraft ? { ...lastRetryDraft, allowManualRetry: true, failedAt: null, failureMessage: "" } : null;
      updateRetryButton();
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
        markRetryAvailable("Kết nối bị ngắt hoặc bạn đã hủy. Bấm gửi lại để chạy lại.");
        showToast("Kết nối bị ngắt, có thể gửi lại.");
      } else {
        markRetryAvailable("Câu trả lời bị ngắt giữa chừng. Bấm gửi lại để chạy lại từ câu hỏi cũ.");
      }
    } else {
      if (assistantMessageIndex !== null && streamedAnswer.trim()) {
        persistStreamingDraft(true);
      }
      appendAssistantMessage(thread, friendlyFetchError(error));
      markRetryAvailable("Có lỗi khi trả lời. Bấm gửi lại để chạy lại.");
    }
  } finally {
    flushStreamRender();
    clearStreamStallWatchdog();
    isStreamingAnswer = false;
    activeController = null;
    activeRequestId = "";
    lastStreamRenderedText = "";
    sendBtn.textContent = "➤";
    sendBtn.title = "Gửi";
    sendBtn.disabled = false;
    sendBtn.classList.remove("is-running");
    persistStreamingDraft(true);
    saveState();
    renderThreads();
    updateSessionMetrics();
    activeModuleId = "";
    loadStatus();
    focusPrompt();
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
    return `Không kết nối được server ${publicServerBaseUrl}. Hãy chạy lại web server rồi refresh trang: uv run --with-requirements requirements.txt python web_app.py --host 0.0.0.0 --port 8088`;
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

function focusPrompt() {
  try {
    prompt.focus({ preventScroll: true });
  } catch {
    prompt.focus();
  }
}

function captureChatScroll() {
  return {
    top: chat.scrollTop,
    height: chat.scrollHeight,
    nearBottom: isChatNearBottom(),
    locked: userScrollLocked,
  };
}

function shouldStickToBottom(intent) {
  return !userScrollLocked && !intent?.locked && intent?.nearBottom;
}

function restoreChatScroll(intent) {
  if (!intent) return;
  setChatScrollTop(intent.top);
}

function setChatScrollTop(top) {
  programmaticScrollUntil = Date.now() + 180;
  chat.scrollTop = Math.max(0, top);
}

function releaseChatScrollLock() {
  userScrollLocked = false;
}

function handleChatScroll() {
  if (Date.now() < programmaticScrollUntil) {
    updateScrollBottomButton();
    return;
  }
  userScrollLocked = !isChatNearBottom();
  updateScrollBottomButton();
}

function scrollChatToBottom() {
  releaseChatScrollLock();
  programmaticScrollUntil = Date.now() + 180;
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
retryLastBtn?.addEventListener("click", retryLastRequest);
sidebarToggleBtn?.addEventListener("click", toggleSidebar);
sidebarCloseBtn?.addEventListener("click", () => setSidebarCollapsed(true));
sidebarBackdrop?.addEventListener("click", () => setSidebarCollapsed(true));
quickActionsToggle?.addEventListener("click", () => togglePromptLibrary());
promptLibraryBtn?.addEventListener("click", () => togglePromptLibrary(true));
artifactCloseBtn?.addEventListener("click", closeArtifactPanel);
artifactCopyBtn?.addEventListener("click", copyArtifact);
artifactDownloadBtn?.addEventListener("click", downloadArtifactMarkdown);
modelSelect?.addEventListener("change", () => {
  selectedModelPersona = modelSelect.value;
  saveSelectValue(modelStorageKey, selectedModelPersona);
  updateSessionMetrics();
  showToast(`Chế độ AI: ${modelSelect.options[modelSelect.selectedIndex]?.text || selectedModelPersona}`);
});
toolModeSelect?.addEventListener("change", () => {
  selectedToolMode = toolModeSelect.value;
  saveSelectValue(toolModeStorageKey, selectedToolMode);
  showToast(`Công cụ: ${toolModeSelect.options[toolModeSelect.selectedIndex]?.text || selectedToolMode}`);
});
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
chat.addEventListener("scroll", handleChatScroll, { passive: true });
chat.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-starter-prompt]");
  if (!button) return;
  prompt.value = button.dataset.starterPrompt || "";
  applyResponseMode(button.textContent.toLowerCase().includes("audit") ? "deep" : "balanced");
  autoResize();
  focusPrompt();
});
quickActions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-prompt]");
  if (!button) return;
  if (button.dataset.module === "true") {
    prompt.value = button.dataset.prompt;
    activeModuleId = button.dataset.moduleId || moduleIdFromLabel(button.textContent);
    applyResponseMode("balanced");
    autoResize();
    focusPrompt();
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
  focusPrompt();
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
    "train 300 files": "train_case_study_brain",
    "train full 1000": "train_full_case_study_brain",
    "search case study": "case_study_search",
    "extract patterns": "case_study_patterns",
    "training status": "training_status",
    "training report": "export_training_report",
    "30-step workflow": "workflow_30",
    "ai workflow": "ai_workflow_20",
    "kdp prompt pack": "case_study_search",
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
    "Training / Case Study Brain": "Huấn luyện nhẹ / Kho case study",
    "Train 300 Files": "Index thử 300 file cũ",
    "Train Full 1000": "Index sâu 1000 file cũ",
    "Search Case Study": "Tìm trong kho case study",
    "Extract Patterns": "Rút pattern từ case study",
    "Training Status": "Trạng thái training brain",
    "Training Report": "Xuất báo cáo training",
    "30-Step Workflow": "Quy trình hoàn thành 30 bước",
    "AI Workflow": "Quy trình ra lệnh AI 20 bước",
    "KDP Prompt Pack": "Ngách KDP Prompt & Template Pack",
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
  if (event.key !== "Escape") return;
  if (!app.classList.contains("sidebar-collapsed") && window.matchMedia?.("(max-width: 760px)")?.matches) {
    setSidebarCollapsed(true);
    return;
  }
  if (!artifactPanel?.hidden) closeArtifactPanel();
  if (openThreadMenuId) {
    openThreadMenuId = null;
    renderThreads();
  }
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
  const repairElementAttributes = (element) => {
    for (const attr of ["title", "aria-label", "placeholder", "value"]) {
      if (element.hasAttribute?.(attr)) {
        const value = element.getAttribute(attr);
        const repaired = repairMojibake(value);
        if (repaired !== value) element.setAttribute(attr, repaired);
      }
    }
  };
  repairElementAttributes(root);
  for (const element of root.querySelectorAll?.("*") || []) {
    repairElementAttributes(element);
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

