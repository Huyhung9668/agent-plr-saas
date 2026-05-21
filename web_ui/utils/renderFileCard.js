const FILE_PATTERN = /\b([\w.-]+\.(?:md|txt|pdf|json|csv|js|ts|py|html|zip))\b/gi;
const CODEBLOCK_FILE_PATTERN = /```[\w-]*\s+(?:filename=["']?([\w.-]+)["']?)[^\n]*\n([\s\S]+?)```/gi;
const DECLARED_FILE_PATTERN = /(?:^|\n)(?:file|tên file|filename)[:\s]+[`"]?([\w.-]+\.(?:md|txt|pdf|json|csv|js|ts|py|html|zip))[`"]?/gi;
const DECLARED_FILE_BLOCK_PATTERN = /(?:^|\n)FILE:\s*[`"]?([\w.-]+\.(?:md|txt|pdf|json|csv|js|ts|py|html|zip))[`"]?\s*\n(?:DESC:\s*([^\n]+)\s*\n)?---\s*\n([\s\S]*)/i;
const CODE_BLOCK_PATTERN = /```(\w+)?(?:[^\n]*)\n([\s\S]+?)```/g;

const FILE_EXTENSIONS = new Set(["md", "txt", "pdf", "json", "csv", "js", "ts", "py", "html", "zip"]);
const FILE_ICONS = {
  md: "MD",
  txt: "TXT",
  pdf: "PDF",
  json: "{}",
  csv: "CSV",
  js: "JS",
  ts: "TS",
  py: "PY",
  html: "HTML",
  zip: "ZIP",
  default: "FILE",
};

function createFileCard(filename, content, description = "") {
  const ext = String(filename || "").split(".").pop().toLowerCase();
  const icon = FILE_ICONS[ext] || FILE_ICONS.default;
  const card = document.createElement("div");
  card.className = "file-card file-download-card";

  const iconEl = document.createElement("span");
  iconEl.className = "file-card-icon file-icon";
  iconEl.textContent = icon;
  card.appendChild(iconEl);

  const info = document.createElement("div");
  info.className = "file-card-info file-info";

  const name = document.createElement("div");
  name.className = "file-card-name file-name";
  name.textContent = filename;
  name.title = filename;
  info.appendChild(name);

  if (description) {
    const desc = document.createElement("div");
    desc.className = "file-card-desc file-desc";
    desc.textContent = description;
    info.appendChild(desc);
  }

  card.appendChild(info);

  const actions = document.createElement("div");
  actions.className = "file-card-actions file-actions";

  const copy = document.createElement("button");
  copy.className = "fc-btn fc-btn-copy btn-copy";
  copy.type = "button";
  copy.textContent = "Copy";
  copy.addEventListener("click", async () => {
    await copyFileCardContent(content);
    copy.textContent = "Copied";
    notifyFileCard("Đã copy nội dung file.");
    setTimeout(() => (copy.textContent = "Copy"), 900);
  });
  actions.appendChild(copy);

  const download = document.createElement("button");
  download.className = "fc-btn fc-btn-dl btn-download";
  download.type = "button";
  download.textContent = "Download";
  download.addEventListener("click", () => {
    downloadFileCardContent(filename, content, ext);
    notifyFileCard(`Đã tải ${filename}.`);
  });
  actions.appendChild(download);

  card.appendChild(actions);
  return card;
}

function parseMessageFileParts(content, messageId = "output") {
  const text = String(content || "");
  const declaredBlock = text.match(DECLARED_FILE_BLOCK_PATTERN);
  if (declaredBlock) {
    const start = declaredBlock.index || 0;
    const before = text.slice(0, start).trim();
    const [, filename, description = "", fileContent = ""] = declaredBlock;
    return [
      ...(before ? [{ type: "text", content: before }] : []),
      {
        type: "file",
        filename,
        description: description.trim(),
        content: fileContent.trimStart(),
      },
    ];
  }

  const parts = [];
  let lastIndex = 0;
  let match;
  CODE_BLOCK_PATTERN.lastIndex = 0;
  while ((match = CODE_BLOCK_PATTERN.exec(text)) !== null) {
    const [fullMatch, lang = "", code = ""] = match;
    if (match.index > lastIndex) {
      parts.push({ type: "text", content: text.slice(lastIndex, match.index) });
    }

    const filename = filenameFromCodeBlockHeader(fullMatch) || filenameFromCodeFirstLine(code);
    if (filename || code.length > 300) {
      const safeExt = extensionFromFilename(filename) || normalizeLanguageExtension(lang) || "txt";
      parts.push({
        type: "file",
        filename: filename || `output-${messageId}.${safeExt}`,
        description: descriptionForFile(text.slice(0, match.index), filename),
        content: code.trim(),
      });
    } else {
      parts.push({ type: "text", content: fullMatch });
    }
    lastIndex = match.index + fullMatch.length;
  }

  if (lastIndex < text.length) parts.push({ type: "text", content: text.slice(lastIndex) });

  if (!parts.some((part) => part.type === "file")) {
    const declared = firstDeclaredFilename(text);
    const mentioned = declared || firstMentionedFilename(text);
    if (mentioned) {
      return [
        { type: "text", content: text },
        {
          type: "file",
          filename: mentioned,
          description: descriptionForFile(text, mentioned),
          content: text.trim(),
        },
      ];
    }
  }

  return parts.length ? parts : [{ type: "text", content: text }];
}

function filenameFromCodeBlockHeader(block) {
  CODEBLOCK_FILE_PATTERN.lastIndex = 0;
  const match = CODEBLOCK_FILE_PATTERN.exec(block);
  return match?.[1] || "";
}

function filenameFromCodeFirstLine(code) {
  const firstLine = String(code || "").trim().split("\n")[0] || "";
  return firstLine.match(/^#\s*([\w.-]+\.(?:md|txt|json|csv|js|ts|py|html|zip))\b/i)?.[1] || "";
}

function firstDeclaredFilename(text) {
  DECLARED_FILE_PATTERN.lastIndex = 0;
  const match = DECLARED_FILE_PATTERN.exec(text);
  return stripFilenameToken(match?.[1] || "");
}

function firstMentionedFilename(text) {
  FILE_PATTERN.lastIndex = 0;
  let match;
  while ((match = FILE_PATTERN.exec(text)) !== null) {
    const candidate = stripFilenameToken(match[1]);
    if (candidate && FILE_EXTENSIONS.has(extensionFromFilename(candidate))) return candidate;
  }
  return "";
}

function descriptionForFile(text, filename = "") {
  const lines = String(text || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const descLine = lines.find((line) => /^DESC:/i.test(line));
  if (descLine) return descLine.replace(/^DESC:\s*/i, "").slice(0, 120);
  const fileLineIndex = lines.findIndex((line) => filename && line.includes(filename));
  if (fileLineIndex >= 0 && lines[fileLineIndex + 1]) {
    return lines[fileLineIndex + 1].replace(/^[-*: ]+/, "").slice(0, 120);
  }
  return "";
}

function stripFilenameToken(value) {
  return String(value || "").replace(/^[`"']+|[`"',.]+$/g, "");
}

function extensionFromFilename(filename) {
  const ext = String(filename || "").split(".").pop().toLowerCase();
  return FILE_EXTENSIONS.has(ext) ? ext : "";
}

function normalizeLanguageExtension(lang) {
  const value = String(lang || "").toLowerCase();
  if (value === "markdown") return "md";
  if (value === "javascript") return "js";
  if (value === "typescript") return "ts";
  if (value === "python") return "py";
  return FILE_EXTENSIONS.has(value) ? value : "txt";
}

function downloadFileCardContent(filename, content, ext = "") {
  const mime = ext === "html" ? "text/html;charset=utf-8" : "text/plain;charset=utf-8";
  const blob = new Blob([content || ""], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "agent-output.txt";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function copyFileCardContent(content) {
  const value = String(content || "");
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

function notifyFileCard(message) {
  if (typeof window.showToast === "function") {
    window.showToast(message);
  }
}

window.createFileCard = createFileCard;
window.parseMessageFileParts = parseMessageFileParts;
