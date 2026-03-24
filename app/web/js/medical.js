/**
 * VanceSender EMS — Medical Features Module
 * Handles: Tab switching, Medical templates, Glossary, Quick phrases,
 *          Vitals generator, SBAR report, Preset combos, Vitals panel rendering
 */
(function () {
    'use strict';

    const API_BASE = '/api/v1';

    function apiHeaders() {
        if (typeof window._apiHeaders === 'function') return window._apiHeaders();
        return {};
    }

    // ── Tab Switching ─────────────────────────────────────────────────────

    function setupTabs() {
        document.querySelectorAll('.med-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                // Deactivate all tabs and content
                document.querySelectorAll('.med-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.med-tab-content').forEach(c => c.classList.remove('active'));
                // Activate clicked
                tab.classList.add('active');
                const content = document.getElementById(target);
                if (content) content.classList.add('active');
            });
        });
    }

    // ── Medical Template Loading ──────────────────────────────────────────

    let _medicalTemplates = null;

    async function loadMedicalTemplates() {
        try {
            const res = await fetch(`${API_BASE}/medical/templates`, { headers: apiHeaders() });
            if (!res.ok) return;
            const data = await res.json();
            _medicalTemplates = data.templates;
            populateTemplateSelects();
        } catch (e) {
            console.warn('[Medical] Failed to load templates:', e);
        }
    }

    function populateTemplateSelects() {
        const selects = [
            document.getElementById('ai-medical-template'),
            document.getElementById('conv-tree-medical-template'),
        ];
        selects.forEach(sel => {
            if (!sel || !_medicalTemplates) return;
            while (sel.options.length > 1) sel.remove(1);
            for (const [category, items] of Object.entries(_medicalTemplates)) {
                const group = document.createElement('optgroup');
                group.label = category;
                items.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = item.name;
                    opt.dataset.scenario = item.scenario;
                    group.appendChild(opt);
                });
                sel.appendChild(group);
            }
        });
    }

    function setupTemplateListeners() {
        const pairs = [
            ['ai-medical-template', 'ai-scenario'],
            ['conv-tree-medical-template', 'conv-tree-scenario'],
        ];
        pairs.forEach(([selId, textId]) => {
            const sel = document.getElementById(selId);
            const textarea = document.getElementById(textId);
            if (sel && textarea) {
                sel.addEventListener('change', () => {
                    const opt = sel.selectedOptions[0];
                    if (opt && opt.dataset.scenario) {
                        textarea.value = opt.dataset.scenario;
                        textarea.dispatchEvent(new Event('input'));
                    }
                });
            }
        });
    }

    // ── Glossary ──────────────────────────────────────────────────────────

    async function loadGlossary(query, category) {
        try {
            const params = new URLSearchParams();
            if (query) params.set('q', query);
            if (category) params.set('category', category);
            const res = await fetch(`${API_BASE}/medical/glossary?${params}`, { headers: apiHeaders() });
            if (!res.ok) return;
            const data = await res.json();
            renderGlossary(data.items, data.total);
        } catch (e) { console.warn('[Medical] Glossary load error:', e); }
    }

    async function loadGlossaryCategories() {
        try {
            const res = await fetch(`${API_BASE}/medical/glossary/categories`, { headers: apiHeaders() });
            if (!res.ok) return;
            const data = await res.json();
            const sel = document.getElementById('glossary-category');
            if (sel) {
                while (sel.options.length > 1) sel.remove(1);
                data.categories.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat;
                    sel.appendChild(opt);
                });
            }
        } catch (e) { console.warn('[Medical] Categories load error:', e); }
    }

    function renderGlossary(items, total) {
        const grid = document.getElementById('glossary-grid');
        const countEl = document.getElementById('glossary-count');
        if (!grid) return;
        if (countEl) countEl.textContent = `共 ${total} 个术语`;
        if (!items || items.length === 0) {
            grid.innerHTML = '<div class="empty-state small"><div class="empty-icon">🔍</div><p>没有找到匹配的术语</p></div>';
            return;
        }
        grid.innerHTML = items.map(item => `
            <div class="glossary-card" title="点击复制术语" data-term="${esc(item.term)}">
                <div class="glossary-card-header">
                    <span class="glossary-term">${esc(item.term)}</span>
                    <span class="glossary-category-badge">${esc(item.category)}</span>
                </div>
                <div class="glossary-full-name">${esc(item.full)}</div>
                <div class="glossary-cn-name">${esc(item.cn)}</div>
                <div class="glossary-desc">${esc(item.desc)}</div>
            </div>`).join('');
        grid.querySelectorAll('.glossary-card').forEach(card => {
            card.addEventListener('click', () => {
                const term = card.dataset.term;
                navigator.clipboard.writeText(term).then(() => showToast(`已复制: ${term}`, 'success')).catch(() => {});
            });
        });
    }

    function setupGlossaryListeners() {
        const searchInput = document.getElementById('glossary-search');
        const categorySelect = document.getElementById('glossary-category');
        let timer = null;
        function doSearch() {
            loadGlossary(searchInput?.value.trim() || null, categorySelect?.value || null);
        }
        if (searchInput) searchInput.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(doSearch, 250); });
        if (categorySelect) categorySelect.addEventListener('change', doSearch);
    }

    // ── Quick Phrases ─────────────────────────────────────────────────────

    async function loadQuickPhrases() {
        try {
            const res = await fetch(`${API_BASE}/medical/quick-phrases`, { headers: apiHeaders() });
            if (!res.ok) return;
            const data = await res.json();
            renderQuickPhrases(data.phrases);
        } catch (e) { console.warn('[Medical] Quick phrases load error:', e); }
    }

    function renderQuickPhrases(phrasesByCategory) {
        const grid = document.getElementById('quick-phrases-grid');
        if (!grid) return;
        let html = '';
        for (const [cat, phrases] of Object.entries(phrasesByCategory)) {
            html += `<div class="quick-phrase-category">${esc(cat)}</div>`;
            phrases.forEach(p => {
                const icon = p.name.match(/^(\S+)/)?.[1] || '🩺';
                const label = p.name.replace(/^\S+\s*/, '');
                html += `<button class="quick-phrase-btn" data-phrase-id="${esc(p.id)}" title="点击复制到剪贴板">
                    <span class="phrase-icon">${icon}</span>${esc(label)}</button>`;
            });
        }
        grid.innerHTML = html;

        // Flatten for lookup
        const allPhrases = Object.values(phrasesByCategory).flat();
        grid.querySelectorAll('.quick-phrase-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const phrase = allPhrases.find(p => p.id === btn.dataset.phraseId);
                if (!phrase) return;
                const texts = phrase.texts.map(t => `/${t.type} ${t.content}`).join('\n');
                navigator.clipboard.writeText(texts).then(() => {
                    showToast(`已复制: ${phrase.name}`, 'success');
                    btn.style.borderColor = 'rgba(13,148,136,0.6)';
                    setTimeout(() => { btn.style.borderColor = ''; }, 800);
                }).catch(() => {});
            });
        });
    }

    // ── Vitals Generator ──────────────────────────────────────────────────

    function setupVitalsGenerator() {
        const btn = document.getElementById('vitals-gen-btn');
        if (!btn) return;
        btn.addEventListener('click', async () => {
            const severity = document.querySelector('input[name="vitals-severity"]:checked')?.value || 'moderate';
            btn.disabled = true;
            btn.textContent = '⏳ 生成中...';
            try {
                const res = await fetch(`${API_BASE}/medical/random-vitals?severity=${severity}`, { headers: apiHeaders() });
                if (!res.ok) throw new Error('生成失败');
                const data = await res.json();
                renderVitalsGenResult(data);
            } catch (e) {
                showToast(e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '🎲 随机生成体征';
            }
        });
    }

    function renderVitalsGenResult(data) {
        const resultEl = document.getElementById('vitals-gen-result');
        const textsEl = document.getElementById('vitals-gen-texts');
        if (!resultEl || !textsEl) return;

        // Render vitals panel
        resultEl.innerHTML = window.renderVitalsPanel ? window.renderVitalsPanel(data) : '';

        // Render /do text lines
        const doTexts = data.do_texts || [];
        let html = doTexts.map(t => `
            <div class="vitals-gen-text-line" title="点击复制此行" data-text="/${t.type} ${esc(t.content)}">
                <span class="vitals-gen-text-type type-${t.type}">/${t.type}</span>
                <span class="vitals-gen-text-content">${esc(t.content)}</span>
            </div>`).join('');
        html += `<button class="vitals-gen-copy-all" title="复制全部体征文本">📋 复制全部 /do 文本</button>`;
        textsEl.innerHTML = html;

        // Click to copy individual lines
        textsEl.querySelectorAll('.vitals-gen-text-line').forEach(line => {
            line.addEventListener('click', () => {
                navigator.clipboard.writeText(line.dataset.text).then(() => {
                    showToast('已复制', 'success');
                }).catch(() => {});
            });
        });

        // Copy all button
        const copyAllBtn = textsEl.querySelector('.vitals-gen-copy-all');
        if (copyAllBtn) {
            copyAllBtn.addEventListener('click', () => {
                const allText = doTexts.map(t => `/${t.type} ${t.content}`).join('\n');
                navigator.clipboard.writeText(allText).then(() => {
                    showToast('已复制全部体征文本', 'success');
                }).catch(() => {});
            });
        }
    }

    // ── SBAR Report ───────────────────────────────────────────────────────

    function setupSBAR() {
        const btn = document.getElementById('sbar-gen-btn');
        if (!btn) return;
        btn.addEventListener('click', async () => {
            const s = document.getElementById('sbar-situation')?.value.trim();
            const b = document.getElementById('sbar-background')?.value.trim();
            const a = document.getElementById('sbar-assessment')?.value.trim();
            const r = document.getElementById('sbar-recommendation')?.value.trim();
            if (!s || !b || !a || !r) {
                showToast('请填写所有 SBAR 字段', 'error');
                return;
            }
            btn.disabled = true;
            btn.textContent = '⏳ 生成中...';
            try {
                const res = await fetch(`${API_BASE}/medical/sbar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', ...apiHeaders() },
                    body: JSON.stringify({ situation: s, background: b, assessment: a, recommendation: r }),
                });
                if (!res.ok) throw new Error('生成失败');
                const data = await res.json();
                renderSBARResult(data);
            } catch (e) {
                showToast(e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '📝 生成 SBAR 交接报告';
            }
        });
    }

    function renderSBARResult(data) {
        const el = document.getElementById('sbar-result');
        if (!el) return;
        const texts = data.texts || [];
        let html = texts.map(t => `
            <div class="vitals-gen-text-line" title="点击复制" data-text="/${t.type} ${esc(t.content)}">
                <span class="vitals-gen-text-type type-${t.type}">/${t.type}</span>
                <span class="vitals-gen-text-content">${esc(t.content)}</span>
            </div>`).join('');
        html += `<button class="vitals-gen-copy-all">📋 复制全部 SBAR 交接文本</button>`;
        el.innerHTML = html;

        el.querySelectorAll('.vitals-gen-text-line').forEach(line => {
            line.addEventListener('click', () => {
                navigator.clipboard.writeText(line.dataset.text).then(() => showToast('已复制', 'success')).catch(() => {});
            });
        });
        const copyBtn = el.querySelector('.vitals-gen-copy-all');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const all = texts.map(t => `/${t.type} ${t.content}`).join('\n');
                navigator.clipboard.writeText(all).then(() => showToast('已复制全部 SBAR 文本', 'success')).catch(() => {});
            });
        }
    }

    // ── Combos ────────────────────────────────────────────────────────────

    async function loadCombos() {
        try {
            const res = await fetch(`${API_BASE}/medical/combos`, { headers: apiHeaders() });
            if (!res.ok) return;
            const data = await res.json();
            renderCombos(data.combos);
        } catch (e) { console.warn('[Medical] Combos load error:', e); }
    }

    function renderCombos(combos) {
        const grid = document.getElementById('combos-grid');
        if (!grid) return;
        if (!combos || combos.length === 0) {
            grid.innerHTML = '<div class="empty-state small"><p>暂无连招定义</p></div>';
            return;
        }
        grid.innerHTML = combos.map(c => `
            <div class="combo-card">
                <div class="combo-card-name">${esc(c.name)}</div>
                <div class="combo-card-desc">${esc(c.description)}</div>
                <div class="combo-card-presets">
                    ${c.presets.map(p => `<span class="combo-preset-tag">${esc(p)}</span>`).join(' → ')}
                </div>
                <button class="combo-send-btn" data-combo-id="${esc(c.id)}">📋 复制全部预设名称</button>
            </div>`).join('');

        grid.querySelectorAll('.combo-send-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const combo = combos.find(c => c.id === btn.dataset.comboId);
                if (combo) {
                    const text = combo.presets.join(' → ');
                    navigator.clipboard.writeText(text).then(() => {
                        showToast(`已复制连招: ${combo.name}`, 'success');
                    }).catch(() => {});
                }
            });
        });
    }

    // ── Vitals Panel Rendering (for Conversation Tree) ────────────────────

    window.renderVitalsPanel = function (vitals) {
        if (!vitals) return '';
        const fields = [
            { key: 'heart_rate', label: '心率 (HR)', icon: '❤️' },
            { key: 'blood_pressure', label: '血压 (BP)', icon: '🩸' },
            { key: 'spo2', label: '血氧 (SpO2)', icon: '💨' },
            { key: 'respiratory_rate', label: '呼吸 (RR)', icon: '🫁' },
            { key: 'temperature', label: '体温 (T)', icon: '🌡️' },
            { key: 'gcs', label: 'GCS', icon: '🧠' },
            { key: 'consciousness', label: '意识', icon: '👁️' },
            { key: 'pupil', label: '瞳孔', icon: '🔦' },
            { key: 'skin', label: '皮肤', icon: '🖐️' },
        ];
        let html = '<div class="vitals-panel">';
        fields.forEach(f => {
            const val = vitals[f.key];
            if (!val) return;
            const statusClass = getVitalStatus(f.key, val);
            html += `<div class="vitals-item">
                <span class="vitals-label">${f.icon} ${f.label}</span>
                <span class="vitals-value ${statusClass}">${esc(val)}</span>
            </div>`;
        });
        if (vitals.summary) {
            html += `<div class="vitals-summary">📋 ${esc(vitals.summary)}</div>`;
        }
        html += '</div>';
        return html;
    };

    function getVitalStatus(key, val) {
        if (!val || val === '--' || val === '待评估') return '';
        const s = String(val).toLowerCase();
        if (s.includes('危') || s.includes('严重') || s.includes('停止') || s.includes('消失') || s.includes('无反应') || s.includes('散大')) return 'status-critical';
        if (s.includes('偏低') || s.includes('偏高') || s.includes('偏快') || s.includes('过速') || s.includes('过缓')
            || s.includes('不稳') || s.includes('嗜睡') || s.includes('迟钝') || s.includes('减弱')) return 'status-warning';
        if (s.includes('正常') || s.includes('稳定') || s.includes('清醒') || s.includes('灵敏')) return 'status-normal';
        if (key === 'spo2') {
            const num = parseInt(val);
            if (!isNaN(num)) {
                if (num < 90) return 'status-critical';
                if (num < 95) return 'status-warning';
                return 'status-normal';
            }
        }
        return '';
    }

    // ── Quick Send Panel — Medical Actions ──────────────────────────────

    // Phrase data cache for quick send buttons (loaded from API)
    let _quickPhraseData = null;

    async function loadQuickPhraseData() {
        if (_quickPhraseData) return _quickPhraseData;
        try {
            const res = await fetch(`${API_BASE}/medical/quick-phrases`, { headers: apiHeaders() });
            if (!res.ok) return null;
            const data = await res.json();
            // Flatten all phrases into a map by id
            const map = {};
            for (const phrases of Object.values(data.phrases || {})) {
                phrases.forEach(p => { map[p.id] = p; });
            }
            _quickPhraseData = map;
            return map;
        } catch (e) { return null; }
    }

    /**
     * Send a single text line to FiveM via /api/v1/send.
     * This mirrors sendTextNow() in app.js but is accessible here.
     */
    async function sendToGame(text, source) {
        try {
            const res = await fetch(`${API_BASE}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...apiHeaders() },
                body: JSON.stringify({ text, source: source || 'webui' }),
            });
            const data = await res.json().catch(() => ({}));
            return res.ok && data.success;
        } catch (e) { return false; }
    }

    /**
     * Send multiple text lines sequentially with delay.
     */
    async function sendTextsSequentially(texts, delay) {
        delay = delay || 1500;
        for (let i = 0; i < texts.length; i++) {
            const ok = await sendToGame(texts[i]);
            if (!ok) {
                showToast(`第 ${i + 1} 条发送失败`, 'error');
                return false;
            }
            if (i < texts.length - 1) {
                await new Promise(r => setTimeout(r, delay));
            }
        }
        return true;
    }

    function setupQuickSendActions() {
        // Wire up all med-quick-btn buttons
        document.querySelectorAll('.med-quick-btn[data-med-action]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const actionId = btn.dataset.medAction;
                if (!actionId) return;

                // Ensure phrase data is loaded
                const phrases = await loadQuickPhraseData();
                if (!phrases || !phrases[actionId]) {
                    showToast('短语数据加载失败', 'error');
                    return;
                }

                const phrase = phrases[actionId];
                const textsToSend = phrase.texts.map(t => `/${t.type} ${t.content}`);

                btn.classList.add('sending');
                const originalText = btn.textContent;
                btn.textContent = '⏳ 发送中...';

                const ok = await sendTextsSequentially(textsToSend, 1200);

                btn.classList.remove('sending');
                btn.textContent = originalText;

                if (ok) {
                    btn.classList.add('sent-ok');
                    showToast(`已发送: ${phrase.name}`, 'success');
                    setTimeout(() => btn.classList.remove('sent-ok'), 1000);
                }
            });
        });
    }

    function setupQuickVitalsGenerator() {
        const btn = document.getElementById('med-quick-vitals-btn');
        const severitySelect = document.getElementById('med-quick-severity');
        const previewEl = document.getElementById('med-quick-vitals-preview');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            const severity = severitySelect?.value || 'moderate';
            btn.disabled = true;
            btn.textContent = '⏳ 生成中...';

            try {
                const res = await fetch(`${API_BASE}/medical/random-vitals?severity=${severity}`, { headers: apiHeaders() });
                if (!res.ok) throw new Error('生成失败');
                const data = await res.json();
                const doTexts = data.do_texts || [];

                // Show preview
                if (previewEl) {
                    previewEl.innerHTML = doTexts.map(t =>
                        `<div class="vitals-gen-text-line" style="cursor:default;"><span class="vitals-gen-text-type type-do">/do</span><span class="vitals-gen-text-content">${esc(t.content)}</span></div>`
                    ).join('');
                }

                // Send all vitals to game sequentially
                btn.textContent = '📡 发送中...';
                const textsToSend = doTexts.map(t => `/${t.type} ${t.content}`);
                const ok = await sendTextsSequentially(textsToSend, 1200);

                if (ok) {
                    showToast(`已发送 ${doTexts.length} 条体征数据 (${data.severity_label})`, 'success');
                    btn.classList.add('sent-ok');
                    setTimeout(() => btn.classList.remove('sent-ok'), 1000);
                }
            } catch (e) {
                showToast(e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '🎲 生成并发送体征';
            }
        });
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    function showToast(msg, type) {
        if (typeof window.showToast === 'function') { window.showToast(msg, type); return; }
        console.log(`[Toast] ${type}: ${msg}`);
    }

    // ── Initialization ────────────────────────────────────────────────────

    function init() {
        setupTabs();
        setupTemplateListeners();
        setupGlossaryListeners();
        setupVitalsGenerator();
        setupSBAR();
        setupQuickSendActions();
        setupQuickVitalsGenerator();

        setTimeout(() => {
            loadMedicalTemplates();
            loadGlossaryCategories();
            loadGlossary();
            loadQuickPhrases();
            loadCombos();
            loadQuickPhraseData(); // Pre-cache for quick send buttons
        }, 500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
