from pathlib import Path
# Fix app default placeholder and add repeated repair for dynamic UI.
p=Path('web_ui/app.js')
s=p.read_text(encoding='utf-8')
s=s.replace('const defaultPromptPlaceholder = prompt?.getAttribute("placeholder") || "Nhập câu hỏi, dán ảnh, hoặc kéo file vào đây...";', 'const defaultPromptPlaceholder = "Nhập câu hỏi, dán ảnh, hoặc kéo file vào đây...";')
if 'scheduleVietnameseUiRepair();' not in s:
    s=s.replace('installCleanUiUpgrade();\n  repairVietnameseUiText();\n  installReadingModeToggle();', 'installCleanUiUpgrade();\n  repairVietnameseUiText();\n  scheduleVietnameseUiRepair();\n  installReadingModeToggle();')
if 'function scheduleVietnameseUiRepair()' not in s:
    s += r'''

function scheduleVietnameseUiRepair() {
  const delays = [0, 80, 250, 600, 1200, 2200];
  for (const delay of delays) {
    setTimeout(() => {
      repairVisibleText(document.body);
      repairVietnameseUiText();
      if (prompt) prompt.placeholder = defaultPromptPlaceholder;
    }, delay);
  }
}
'''
p.write_text(s, encoding='utf-8')
# Fix file card labels.
p=Path('web_ui/utils/renderFileCard.js')
s=p.read_text(encoding='utf-8')
s=s.replace('copy.textContent = "Copy";', 'copy.textContent = "Sao chép";')
s=s.replace('copy.textContent = "Copied";', 'copy.textContent = "Đã chép";')
s=s.replace('copy.textContent = "Copy"), 900', 'copy.textContent = "Sao chép"), 900')
s=s.replace('download.textContent = "Download";', 'download.textContent = "Tải";')
p.write_text(s, encoding='utf-8')
# Bump all cache strings.
p=Path('web_ui/index.html')
s=p.read_text(encoding='utf-8')
import re
s=re.sub(r'v1\.14-vendor-ready-builder\.\d+', 'v1.14-vendor-ready-builder.6', s)
s=re.sub(r'v=1\.14-vendor-ready-builder\.\d+', 'v=1.14-vendor-ready-builder.6', s)
p.write_text(s, encoding='utf-8')
