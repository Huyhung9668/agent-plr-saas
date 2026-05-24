from pathlib import Path
p=Path('web_ui/app.js')
text=p.read_text(encoding='utf-8')
insert = r'''

function repairVietnameseUiText() {
  const setText = (selector, value) => {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  };
  const setAttr = (selector, name, value) => {
    const element = document.querySelector(selector);
    if (element) element.setAttribute(name, value);
  };
  setText('.sidebar-close-btn', '×');
  setAttr('.sidebar-close-btn', 'title', 'Đóng lịch sử chat');
  setAttr('.sidebar-close-btn', 'aria-label', 'Đóng lịch sử chat');
  setAttr('#sidebarBackdrop', 'aria-label', 'Đóng lịch sử chat');
  setAttr('#workspaceTabs', 'aria-label', 'Chọn kênh chat');
  setText('#newChatBtn', '+ Chat mới');
  setText('.search-box span', 'Tìm');
  setAttr('#threadSearch', 'placeholder', 'Tìm chủ đề...');
  setText('.section-label', 'Gần đây');
  setText('.user-name', 'Người dùng');
  setText('#brainSummary', 'Đang kiểm tra brain...');
  setText('.ps-label', 'Dự án:');
  setText('#psProjectName', '—');
  setText('#psNextAction', '—');
  setAttr('#psRefreshBtn', 'title', 'Refresh trạng thái dự án');
  setAttr('.topbar-controls', 'aria-label', 'Cấu hình chat');
  setText('label:has(#modelSelect) span', 'Chế độ AI');
  setText('label:has(#toolModeSelect) span', 'Công cụ');
  const modelLabels = { agent: 'Agent chủ', planner: 'Planner sâu', creator: 'Dựng nội dung', critic: 'Phản biện launch' };
  for (const option of document.querySelectorAll('#modelSelect option')) option.textContent = modelLabels[option.value] || option.textContent;
  const toolLabels = { auto: 'Tự động', files: 'File/RAG', case: 'Case Study Brain', launch: 'Launch OS', none: 'Tắt' };
  for (const option of document.querySelectorAll('#toolModeSelect option')) option.textContent = toolLabels[option.value] || option.textContent;
  setText('#moreMenuBtn', '⋯');
  setText('#promptLibraryBtn', 'Thư viện prompt');
  setText('#statusBtn', 'Trạng thái brain');
  setText('#exportBtn', 'Xuất chat Markdown');
  setText('#themeToggleBtn', 'Đổi sáng/tối');
  setText('#clearBtn', 'Xóa chat');
  setText('#quickActionsToggle', 'Thư viện prompt');
  setText('#messageCount', '0 tin nhắn');
  setText('#activeModeLabel', 'Nhanh');
  setText('#replyStatus', 'Đang trả lời...');
  setText('#retryLastBtn', 'Gửi lại lỗi');
  setAttr('#modeSelector', 'aria-label', 'Chế độ trả lời');
  setAttr('[data-mode="fast"]', 'title', 'FAST: topK thấp, không benchmark/export');
  setAttr('[data-mode="balanced"]', 'title', 'BALANCED: dùng skill + brain vừa đủ');
  setAttr('[data-mode="deep"]', 'title', 'DEEP: chậm hơn, dùng nhiều RAG/audit/export');
  setAttr('.prompt-nav', 'aria-label', 'Điều hướng câu hỏi');
  setText('#promptJumpPrevBtn', '↑');
  setText('#promptJumpNextBtn', '↓');
  setAttr('#promptJumpPrevBtn', 'title', 'Lên câu hỏi trước');
  setAttr('#promptJumpNextBtn', 'title', 'Xuống câu hỏi tiếp theo');
  setAttr('#attachBtn', 'title', 'Đính kèm file');
  setAttr('#prompt', 'placeholder', 'Nhập câu hỏi, dán ảnh, hoặc kéo file vào đây...');
  setText('#sendBtn', '➤');
  setAttr('#sendBtn', 'title', 'Gửi');
  setAttr('#artifactPanel', 'aria-label', 'Canvas kết quả');
  setText('.artifact-label', 'Canvas kết quả');
  setText('#artifactTitle', 'Nội dung trả lời');
  setText('#artifactCopyBtn', '⧉');
  setText('#artifactDownloadBtn', '⇩');
  setText('#artifactCloseBtn', '×');
  setAttr('#artifactCopyBtn', 'title', 'Copy canvas');
  setAttr('#artifactDownloadBtn', 'title', 'Tải Markdown');
  setAttr('#artifactCloseBtn', 'title', 'Đóng canvas');
}
'''
if 'function repairVietnameseUiText()' not in text:
    text += insert
    text = text.replace('bootstrap();', 'repairVietnameseUiText();\nbootstrap();\nsetTimeout(repairVietnameseUiText, 100);')
# fix one known mojibake literal
text=text.replace('"Ä\x90Ã£ dá»«ng lÆ°á»£t tráº£ lá»\x9di nÃ\xa0y."', '"Đã dừng lượt trả lời này."')
p.write_text(text, encoding='utf-8')
