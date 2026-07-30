// ============================
// VLearn AI Tutor — Frontend Logic
// ============================

let currentLevel = null;
let slidesData = [];
let isMinimized = false;
let isLoading = false;
let currentQuizData = null;
let currentSlideIndex = 0;

const LEVEL_LABELS = {
    'coban': '🌱 Cơ bản',
    'thongthao': '🌿 Thông thạo',
    'nangcao': '🌳 Nâng cao'
};

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch('/api/slides');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        slidesData = data.slides || data || [];
        renderSlides(slidesData);
    } catch (error) {
        console.error('Error fetching slides:', error);
        document.getElementById('slides-container').innerHTML =
            '<div class="loading-slides">⚠️ Lỗi khi tải nội dung bài giảng. Vui lòng đảm bảo backend đang chạy.</div>';
    }

    // Show welcome message
    showWelcomeMessage();
}

function getSlideDiagram(title) {
    const t = (title || '').toLowerCase();
    
    if (t.includes('bài toán') || t.includes('yêu cầu mơ hồ')) {
        return `
        <div class="slide-graphic-box">
            <svg viewBox="0 0 500 110" xmlns="http://www.w3.org/2000/svg">
                <rect x="10" y="20" width="130" height="70" rx="8" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>
                <text x="75" y="50" font-size="12" font-weight="bold" fill="#475569" text-anchor="middle">Yêu cầu mơ hồ</text>
                <text x="75" y="70" font-size="10" fill="#64748b" text-anchor="middle">"Anh muốn làm AI support"</text>
                
                <path d="M 140 55 L 185 55" stroke="#0f766e" stroke-width="3" marker-end="url(#arrow1)"/>
                
                <rect x="190" y="15" width="140" height="80" rx="8" fill="#0f766e" stroke="#0d9488" stroke-width="2"/>
                <text x="260" y="47" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Bóc tách Bài toán</text>
                <text x="260" y="67" font-size="10" fill="#ccfbf1" text-anchor="middle">Product Mindset (70% People)</text>
                
                <path d="M 330 55 L 375 55" stroke="#0f766e" stroke-width="3" marker-end="url(#arrow1)"/>
                
                <rect x="380" y="20" width="110" height="70" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2"/>
                <text x="435" y="50" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Giải pháp cụ thể</text>
                <text x="435" y="70" font-size="10" fill="#166534" text-anchor="middle">AI Agent / VLearn Tutor</text>
                
                <defs>
                    <marker id="arrow1" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#0f766e"/>
                    </marker>
                </defs>
            </svg>
            <div class="slide-graphic-caption">📊 Sơ đồ bóc tách bài toán AI từ mục tiêu mơ hồ thành giải pháp thực thi</div>
        </div>`;
    }
    
    if (t.includes('product manager') || t.includes('project manager')) {
        return `
        <div class="slide-graphic-box">
            <svg viewBox="0 0 500 110" xmlns="http://www.w3.org/2000/svg">
                <circle cx="180" cy="55" r="45" fill="#e0f2fe" fill-opacity="0.75" stroke="#0284c7" stroke-width="2"/>
                <text x="160" y="50" font-size="11" font-weight="bold" fill="#0369a1" text-anchor="middle">Product Manager</text>
                <text x="160" y="66" font-size="9" fill="#0c4a6e" text-anchor="middle">User-centered · Tìm bài toán</text>
                
                <circle cx="320" cy="55" r="45" fill="#fef3c7" fill-opacity="0.75" stroke="#d97706" stroke-width="2"/>
                <text x="340" y="50" font-size="11" font-weight="bold" fill="#b45309" text-anchor="middle">Project Manager</text>
                <text x="340" y="66" font-size="9" fill="#78350f" text-anchor="middle">Budget & Tiến độ · Delivery</text>
                
                <text x="250" y="58" font-size="11" font-weight="bold" fill="#0f766e" text-anchor="middle">Generalist</text>
            </svg>
            <div class="slide-graphic-caption">⚖️ Phân định bộ kỹ năng giữa Product Manager và Project Manager</div>
        </div>`;
    }

    if (t.includes('tư duy') || t.includes('hệ thống')) {
        return `
        <div class="slide-graphic-box">
            <svg viewBox="0 0 500 110" xmlns="http://www.w3.org/2000/svg">
                <rect x="25" y="25" width="200" height="60" rx="8" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
                <text x="125" y="50" font-size="12" font-weight="bold" fill="#b91c1c" text-anchor="middle">Tư duy Hệ thống 1 (Nhanh)</text>
                <text x="125" y="68" font-size="10" fill="#991b1b" text-anchor="middle">Phản xạ bản năng · Nhảy vào giải pháp</text>
                
                <rect x="275" y="25" width="200" height="60" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2"/>
                <text x="375" y="50" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Tư duy Hệ thống 2 (Chậm)</text>
                <text x="375" y="68" font-size="10" fill="#166534" text-anchor="middle">Phản biện · Đặt câu hỏi · Product Mindset</text>
            </svg>
            <div class="slide-graphic-caption">🧠 Mô hình 2 kiểu tư duy (Thinking, Fast and Slow) trong làm sản phẩm</div>
        </div>`;
    }

    return `
    <div class="slide-graphic-box">
        <svg viewBox="0 0 500 100" xmlns="http://www.w3.org/2000/svg">
            <rect x="20" y="20" width="110" height="60" rx="6" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>
            <text x="75" y="47" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">Dữ liệu Đầu vào (X)</text>
            <text x="75" y="63" font-size="9" fill="#64748b" text-anchor="middle">Features / Prompt</text>
            
            <path d="M 130 50 L 175 50" stroke="#0f766e" stroke-width="2" stroke-dasharray="4,4"/>
            
            <rect x="175" y="15" width="150" height="70" rx="8" fill="#0f766e" stroke="#115e59" stroke-width="2"/>
            <text x="250" y="45" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Mô hình AI / Context Engine</text>
            <text x="250" y="63" font-size="9" fill="#ccfbf1" text-anchor="middle">f(X) → Y · Trích dẫn [Txx-NNN]</text>
            
            <path d="M 325 50 L 370 50" stroke="#0f766e" stroke-width="2"/>
            
            <rect x="370" y="20" width="110" height="60" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
            <text x="425" y="47" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">Đầu ra (Y / Output)</text>
            <text x="425" y="63" font-size="9" fill="#166534" text-anchor="middle">Dự đoán / Trợ lý AI</text>
        </svg>
        <div class="slide-graphic-caption">💡 Sơ đồ Luồng dữ liệu và Kiến trúc Hệ thống AI</div>
    </div>`;
}

function renderSlides(slides) {
    const container = document.getElementById('slides-container');
    container.innerHTML = '';

    if (!slides || slides.length === 0) {
        container.innerHTML = '<div class="loading-slides">Không có dữ liệu bài giảng.</div>';
        return;
    }

    slides.forEach((slide, index) => {
        const slideEl = document.createElement('div');
        slideEl.className = 'slide-card' + (index === 0 ? ' active' : '');
        slideEl.id = slide.id;

        const contentText = slide.content || 'Nội dung đang tải...';
        const sourceLabel = slide.source
            ? slide.source.replace('transcript-', 'Buổi ').replace('-clean.md', '')
            : '';

        const diagramHtml = getSlideDiagram(slide.title);

        slideEl.innerHTML = `
            <div class="slide-brand-bar">
                <span>🎓 VLEARN ACADEMY — AI IN ACTION</span>
                <span>BẢN SẠCH CHUẨN TRÍCH DẪN [TXX-NNN]</span>
            </div>
            <div class="slide-header">
                <span class="slide-title">${slide.title}</span>
                <span class="slide-number">${sourceLabel} · Slide ${index + 1} / ${slides.length}</span>
            </div>
            ${diagramHtml}
            <div class="slide-content">
                <p>${contentText}</p>
                <div class="slide-takeaway-box">
                    📌 <b>Điểm cốt lõi:</b> Đọc kỹ nội dung và xem trích dẫn mã <code>[Txx-NNN]</code> để chuẩn bị làm bài Test năng lực cùng AI Tutor.
                </div>
            </div>
            <div class="slide-footer-bar">
                <span>Tài liệu bài giảng VLearn • VinUniversity</span>
                <span>Trang ${index + 1} / ${slides.length}</span>
            </div>
        `;
        container.appendChild(slideEl);
    });

    currentSlideIndex = 0;
    const navBar = document.getElementById('slide-nav-bar');
    if (navBar) navBar.style.display = 'flex';
    updateSlideNav();
}

function showWelcomeMessage() {
    const welcomeHtml = `
        <span class="badge badge-tutor">🤖 AI Tutor</span>
        <p>Chào bạn! Mình là <b>VLearn AI Tutor</b> — trợ lý học tập theo ngữ cảnh.</p>
        <p>Mình nhận thấy bạn đang xem <b>nội dung bài giảng</b> bên trái. Để giúp bạn nắm chắc kiến thức mà không bị ngợp, <b>hãy cho mình biết mức độ hiểu bài hiện tại của bạn:</b></p>
        <div class="level-buttons">
            <button class="btn-level-chat" onclick="selectLevel('coban')">🌱 Cơ bản</button>
            <button class="btn-level-chat" onclick="selectLevel('thongthao')">🌿 Thông thạo</button>
            <button class="btn-level-chat" onclick="selectLevel('nangcao')">🌳 Nâng cao</button>
        </div>
    `;
    addMessage('bot', welcomeHtml);
}

async function selectLevel(levelKey) {
    if (isLoading) return;

    currentLevel = levelKey;
    const label = LEVEL_LABELS[levelKey] || levelKey;

    addMessage('user', `Tôi chọn mức độ: ${label}`);
    showTypingIndicator();

    try {
        const slideIds = slidesData.map(s => s.id);
        const response = await fetch('/api/suggest-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ level: levelKey, slide_ids: slideIds })
        });

        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        removeTypingIndicator();

        const levelInfo = data.level_info || { label: label, badge_class: 'badge-coban', emoji: '🌱' };
        const questions = data.questions || [];

        // Build question buttons
        const questionsHtml = questions.map(q => {
            const escapedQ = q.replace(/'/g, "\\'").replace(/"/g, "&quot;");
            return `<button class="btn-suggestion" onclick="askQuestion('${escapedQ}')">❓ ${q}</button>`;
        }).join('');

        const botHtml = `
            <span class="badge ${levelInfo.badge_class}">${levelInfo.emoji} Mức độ: ${levelInfo.label}</span>
            <p>Dưới đây là <b>${questions.length} câu hỏi gợi ý</b> mức <b>${levelInfo.label}</b> và bài Test đánh giá nhanh từ nội dung bài giảng:</p>
            <div class="suggestions-container">
                ${questionsHtml}
                <button class="btn-test-action" onclick="startQuiz()">📝 Làm bài Test đánh giá năng lực (Mức độ ${levelInfo.label})</button>
            </div>
        `;

        addMessage('bot', botHtml);
    } catch (error) {
        removeTypingIndicator();
        addMessage('bot', `<span class="badge badge-test">⚠️ Lỗi</span><p>Đã xảy ra lỗi khi tải câu hỏi gợi ý. Vui lòng thử lại.</p>`);
        console.error('Error suggesting questions:', error);
    }
}

async function askQuestion(questionText) {
    if (isLoading) return;

    // Clean the question text
    questionText = questionText.replace(/&quot;/g, '"');

    addMessage('user', questionText);
    showTypingIndicator();

    try {
        const slideIds = slidesData.map(s => s.id);
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: questionText,
                level: currentLevel || 'coban',
                slide_ids: slideIds
            })
        });

        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        removeTypingIndicator();

        let answerContent = data.answer || 'Không có câu trả lời.';

        // Add citations if available
        if (data.citations && data.citations.length > 0) {
            const citationLinks = data.citations.map(c => {
                const code = typeof c === 'string' ? c : c.id || c;
                return `<span class="citation-link" onclick="findAndScrollToChunk('${code}')">[${code}]</span>`;
            }).join(' ');
            answerContent += `<br><br><small><i>📌 Nguồn tham khảo: ${citationLinks}</i></small>`;
        }

        const badge = data.badge || { class: 'badge-tutor', label: 'AI Tutor' };

        const botHtml = `
            <span class="badge ${badge.class}">${badge.label}</span>
            <p>${answerContent}</p>
            <div style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px;">
                <div class="suggestion-title" style="font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;">Bạn có muốn đổi mức độ khác không?</div>
                <div class="level-buttons">
                    <button class="btn-level-chat" onclick="selectLevel('coban')">🌱 Cơ bản</button>
                    <button class="btn-level-chat" onclick="selectLevel('thongthao')">🌿 Thông thạo</button>
                    <button class="btn-level-chat" onclick="selectLevel('nangcao')">🌳 Nâng cao</button>
                </div>
            </div>
        `;

        addMessage('bot', botHtml);
    } catch (error) {
        removeTypingIndicator();
        addMessage('bot', `<span class="badge badge-test">⚠️ Lỗi</span><p>Đã xảy ra lỗi khi kết nối với AI Tutor. Vui lòng thử lại.</p>`);
        console.error('Error chatting:', error);
    }
}

async function startQuiz() {
    if (isLoading) return;

    const label = currentLevel ? LEVEL_LABELS[currentLevel] : 'Cơ bản';
    addMessage('user', `📝 Làm bài Test đánh giá năng lực (${label})`);
    showTypingIndicator();

    try {
        const slideIds = slidesData.map(s => s.id);
        const response = await fetch('/api/generate-quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: currentLevel || 'coban',
                slide_ids: slideIds
            })
        });

        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        currentQuizData = data;
        removeTypingIndicator();

        const options = data.options || [];
        const optionsHtml = options.map((opt, idx) =>
            `<button class="btn-option" onclick="submitQuizAnswer(${idx})"><b>${String.fromCharCode(65 + idx)}.</b> ${opt}</button>`
        ).join('');

        const botHtml = `
            <span class="badge badge-test">📝 Bài Test: ${label}</span>
            <p><b>Câu hỏi:</b> ${data.question}</p>
            <div class="suggestions-container" style="margin-top: 10px;">
                ${optionsHtml}
            </div>
        `;

        addMessage('bot', botHtml);
    } catch (error) {
        removeTypingIndicator();
        addMessage('bot', `<span class="badge badge-test">⚠️ Lỗi</span><p>Đã xảy ra lỗi khi tạo bài test. Vui lòng thử lại.</p>`);
        console.error('Error generating quiz:', error);
    }
}

function submitQuizAnswer(selectedIdx) {
    if (!currentQuizData) return;

    const selectedOption = currentQuizData.options[selectedIdx];
    addMessage('user', `${String.fromCharCode(65 + selectedIdx)}. ${selectedOption}`);

    const isCorrect = selectedIdx === currentQuizData.correct_index;
    let botHtml = '';

    if (isCorrect) {
        botHtml = `
            <div class="quiz-result-correct">🎉 Kết quả: 10/10 — Chính xác!</div>
            <p><b>Nhận xét:</b> ${currentQuizData.feedback_correct || 'Xuất sắc! Bạn đã nắm vững kiến thức ở mức độ này.'}</p>
            <div style="margin-top: 12px; border-top: 1px dashed #ccc; padding-top: 10px;">
                <p style="font-size: 0.85rem; color: #4b5563; margin-bottom: 8px;">Bạn có thể thử thách bản thân với mức độ cao hơn:</p>
                <div class="level-buttons">
                    <button class="btn-level-chat" onclick="selectLevel('thongthao')">🌿 Thông thạo</button>
                    <button class="btn-level-chat" onclick="selectLevel('nangcao')">🌳 Nâng cao</button>
                </div>
            </div>
        `;
    } else {
        const correctOption = currentQuizData.options[currentQuizData.correct_index];
        const correctLetter = String.fromCharCode(65 + currentQuizData.correct_index);

        botHtml = `
            <div class="quiz-result-wrong">❌ Kết quả: Chưa chính xác (0/10)</div>
            <p><b>Đáp án đúng là:</b> ${correctLetter}. ${correctOption}</p>
            <p style="margin-top: 8px;"><b>Điểm cần cải thiện:</b> ${currentQuizData.feedback_wrong || 'Hãy xem lại nội dung bài giảng liên quan.'}</p>
            ${currentQuizData.slide_target ? `
            <div style="margin-top: 12px; background: #fffaf0; border: 1px solid #fed7aa; padding: 10px; border-radius: 8px;">
                <p style="font-size: 0.85rem; font-weight: 600; color: #9a3412; margin-bottom: 6px;">👉 Tài liệu cải thiện:</p>
                <button class="btn-suggestion" style="width:100%; border-color:#ea580c; color:#ea580c; font-weight:600;" onclick="findAndScrollByTitle('${currentQuizData.slide_target.replace(/'/g, "\\'")}')">
                    📖 Đọc lại: ${currentQuizData.slide_name || currentQuizData.slide_target}
                </button>
            </div>
            ` : ''}
        `;
    }

    addMessage('bot', botHtml);
    currentQuizData = null;
}

// ===== SLIDE NAVIGATION =====
function changeSlide(direction) {
    const newIndex = currentSlideIndex + direction;
    if (newIndex < 0 || newIndex >= slidesData.length) return;
    goToSlide(newIndex);
}

function goToSlide(index) {
    const slides = document.querySelectorAll('.slide-card');
    slides.forEach(s => { s.classList.remove('active'); s.classList.remove('highlight'); });
    currentSlideIndex = index;
    if (slides[currentSlideIndex]) {
        slides[currentSlideIndex].classList.add('active');
    }
    updateSlideNav();
}

function updateSlideNav() {
    const total = slidesData.length || 1;
    const indicator = document.getElementById('slide-indicator');
    if (indicator) indicator.textContent = `Trang ${currentSlideIndex + 1} / ${total}`;
    const btnPrev = document.getElementById('btn-prev-slide');
    const btnNext = document.getElementById('btn-next-slide');
    if (btnPrev) btnPrev.disabled = (currentSlideIndex === 0);
    if (btnNext) btnNext.disabled = (currentSlideIndex >= total - 1);
}

// Scroll to slide by ID — now switches to the page
function scrollToSlide(slideId) {
    const slides = document.querySelectorAll('.slide-card');
    slides.forEach((s, idx) => {
        if (s.id === slideId) {
            goToSlide(idx);
        }
    });
    // Highlight
    const slideEl = document.getElementById(slideId);
    if (slideEl) highlightSlide(slideEl);
}

// Find slide by chunk code and scroll to it
function findAndScrollToChunk(chunkCode) {
    const slide = slidesData.find(s =>
        s.chunk_codes && s.chunk_codes.includes(chunkCode)
    );
    if (slide) {
        scrollToSlide(slide.id);
    } else {
        // Fallback: first slide
        if (slidesData.length > 0) goToSlide(0);
    }
}

// Find slide by title and scroll to it
function findAndScrollByTitle(title) {
    const titleLower = title.toLowerCase();
    const slide = slidesData.find(s =>
        s.title && s.title.toLowerCase().includes(titleLower)
    );
    if (slide) {
        scrollToSlide(slide.id);
    } else {
        const slideByContent = slidesData.find(s =>
            s.content && s.content.toLowerCase().includes(titleLower)
        );
        if (slideByContent) {
            scrollToSlide(slideByContent.id);
        }
    }
}

function highlightSlide(slideEl) {
    document.querySelectorAll('.slide-card').forEach(el => el.classList.remove('highlight'));
    slideEl.classList.add('highlight');
    setTimeout(() => {
        slideEl.classList.remove('highlight');
    }, 4000);
}

function toggleChat() {
    const chatSection = document.getElementById('chat-section');
    const container = document.getElementById('main-container');
    const btnToggle = document.getElementById('btn-toggle-chat');

    isMinimized = !isMinimized;

    if (isMinimized) {
        chatSection.classList.add('minimized');
        container.classList.add('chat-minimized');
        btnToggle.innerText = '[+] Mở rộng';
    } else {
        chatSection.classList.remove('minimized');
        container.classList.remove('chat-minimized');
        btnToggle.innerText = '[-] Thu nhỏ';
        scrollToBottom();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const inputEl = document.getElementById('user-input');
    const text = inputEl.value.trim();
    if (text === '' || isLoading) return;
    inputEl.value = '';
    askQuestion(text);
}

function addMessage(type, content) {
    const chatMessages = document.getElementById('chat-messages');
    const msgEl = document.createElement('div');
    msgEl.className = `message ${type}`;

    if (type === 'bot') {
        msgEl.innerHTML = content;
    } else {
        msgEl.innerText = content;
    }

    chatMessages.appendChild(msgEl);
    scrollToBottom();
}

function showTypingIndicator() {
    isLoading = true;
    // Update status
    const statusEl = document.getElementById('current-status-display');
    if (statusEl) {
        statusEl.textContent = '⏳ Đang xử lý...';
        statusEl.style.color = '#f59e0b';
    }

    const chatMessages = document.getElementById('chat-messages');
    const indicatorEl = document.createElement('div');
    indicatorEl.className = 'typing-indicator';
    indicatorEl.id = 'typing-indicator';
    indicatorEl.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(indicatorEl);
    scrollToBottom();
}

function removeTypingIndicator() {
    isLoading = false;
    // Update status
    const statusEl = document.getElementById('current-status-display');
    if (statusEl) {
        statusEl.textContent = '● Sẵn sàng';
        statusEl.style.color = '#10b981';
    }

    const indicatorEl = document.getElementById('typing-indicator');
    if (indicatorEl) {
        indicatorEl.remove();
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}
