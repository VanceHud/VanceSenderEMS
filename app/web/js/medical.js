/**
 * VanceSender EMS — Medical Features Module
 * Handles: Tab switching, Medical templates, Glossary, Quick phrases,
 *          Vitals generator, SBAR report, Preset combos, Vitals panel rendering
 */
(function () {
    'use strict';

    const API_BASE = '/api/v1';
    const CASE_STORAGE_KEY = 'vancesender_medical_current_case';

    let _medicalTemplates = null;
    let _quickPhraseData = null;
    let _comboCache = [];
    let _comboCacheReady = false;
    let currentCase = createDefaultCase();

    function apiHeaders() {
        const token = (typeof window.localStorage !== 'undefined')
            ? String(window.localStorage.getItem('vs_token') || '').trim()
            : '';
        if (token) return { 'Authorization': 'Bearer ' + token };
        return {};
    }

    function createDefaultCase() {
        return {
            templateId: '',
            templateName: '',
            scene: '',
            patientLabel: '',
            ageGender: '',
            chiefComplaint: '',
            severity: '',
            severityLabel: '',
            vitalsSummary: '',
            assessment: '',
            interventions: '',
            handoffStatus: '',
            activeComboId: '',
            activeComboName: '',
            comboStepIndex: 0,
        };
    }

    function normalizeCurrentCase(raw) {
        const fallback = createDefaultCase();
        const next = (raw && typeof raw === 'object') ? { ...fallback, ...raw } : fallback;
        next.comboStepIndex = Number.isFinite(next.comboStepIndex) && next.comboStepIndex >= 0
            ? Math.floor(next.comboStepIndex)
            : 0;
        return next;
    }

    function loadStoredCurrentCase() {
        try {
            const raw = window.localStorage.getItem(CASE_STORAGE_KEY);
            return raw ? normalizeCurrentCase(JSON.parse(raw)) : createDefaultCase();
        } catch {
            return createDefaultCase();
        }
    }

    function persistCurrentCase() {
        try {
            window.localStorage.setItem(CASE_STORAGE_KEY, JSON.stringify(currentCase));
        } catch {
            // Ignore storage errors.
        }
    }

    function updateCurrentCase(patch = {}, options = {}) {
        currentCase = normalizeCurrentCase({ ...currentCase, ...patch });
        persistCurrentCase();
        renderCurrentCase();
        if (options.rerenderCombos !== false) renderCombos(_comboCache);
    }

    function resetCurrentCase(options = {}) {
        currentCase = createDefaultCase();
        persistCurrentCase();
        renderCurrentCase();
        renderCombos(_comboCache);
        if (!options.silent) showToast('当前病例已清空', 'success');
    }

    function severityValueToLabel(value) {
        const map = {
            mild: '🟢 轻伤',
            moderate: '🟡 中等',
            severe: '🟠 重伤',
            critical: '🔴 危重',
        };
        return map[String(value || '').trim()] || '未分级';
    }

    function stripEmojiLabel(text) {
        return String(text || '').replace(/^\S+\s*/, '').trim() || String(text || '').trim();
    }

    function mergeInterventions(existing, label) {
        const items = String(existing || '')
            .split('；')
            .map(item => item.trim())
            .filter(Boolean);
        const next = String(label || '').trim();
        if (!next) return items.join('； ');
        if (!items.includes(next)) items.push(next);
        return items.join('； ');
    }

    function composeAssessmentFromVitals(vitals) {
        const parts = [];
        if (vitals.heart_rate) parts.push(`HR ${vitals.heart_rate}`);
        if (vitals.blood_pressure) parts.push(`BP ${vitals.blood_pressure}`);
        if (vitals.spo2) parts.push(`SpO2 ${vitals.spo2}`);
        if (vitals.respiratory_rate) parts.push(`RR ${vitals.respiratory_rate}`);
        if (vitals.gcs) parts.push(`GCS ${vitals.gcs}`);
        if (vitals.summary) parts.push(vitals.summary);
        return parts.join('，');
    }

    function inferChiefComplaint(scene) {
        const text = String(scene || '').trim();
        if (!text) return '';
        const parts = text.split(/[，。]/).map(item => item.trim()).filter(Boolean);
        if (parts.length > 1) return parts.slice(1, 3).join('，').slice(0, 60);
        return text.slice(0, 60);
    }

    function setElementText(id, value, fallback) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = value || fallback || '';
    }

    function syncInputValue(id, value) {
        const el = document.getElementById(id);
        if (!el || el.value === value) return;
        el.value = value;
    }

    function getPresetMap() {
        const bridge = window.VanceSenderMedicalBridge;
        const presets = bridge && typeof bridge.getPresets === 'function' ? bridge.getPresets() : [];
        return presets.reduce((map, preset) => {
            map[preset.id] = preset;
            return map;
        }, {});
    }

    function getComboById(comboId) {
        return _comboCache.find(item => item.id === comboId) || null;
    }

    function getPresetDisplayName(presetId) {
        const presetMap = getPresetMap();
        return presetMap[presetId]?.name || presetId;
    }

    function syncActiveComboState() {
        if (!currentCase.activeComboId) {
            if (!currentCase.activeComboName && !currentCase.comboStepIndex) return;
            currentCase = normalizeCurrentCase({
                ...currentCase,
                activeComboName: '',
                comboStepIndex: 0,
            });
            persistCurrentCase();
            return;
        }

        const combo = getComboById(currentCase.activeComboId);
        if (!combo) {
            if (!_comboCacheReady) return;
            currentCase = normalizeCurrentCase({
                ...currentCase,
                activeComboId: '',
                activeComboName: '',
                comboStepIndex: 0,
            });
            persistCurrentCase();
            return;
        }

        const total = Array.isArray(combo.presets) ? combo.presets.length : 0;
        const nextStepIndex = Math.min(currentCase.comboStepIndex || 0, total);
        const nextComboName = combo.name || currentCase.activeComboName;
        if (currentCase.activeComboName === nextComboName && currentCase.comboStepIndex === nextStepIndex) return;

        currentCase = normalizeCurrentCase({
            ...currentCase,
            activeComboName: nextComboName,
            comboStepIndex: nextStepIndex,
        });
        persistCurrentCase();
    }

    function formatCurrentFlow() {
        const combo = getComboById(currentCase.activeComboId);
        if (!combo) {
            if (currentCase.activeComboId && !_comboCacheReady) {
                return currentCase.activeComboName
                    ? `${currentCase.activeComboName} · 流程加载中...`
                    : '流程加载中...';
            }
            return '未选择流程。';
        }
        const total = Array.isArray(combo.presets) ? combo.presets.length : 0;
        const completed = Math.min(currentCase.comboStepIndex || 0, total);
        if (total === 0) return `${currentCase.activeComboName || combo.name} · 暂无流程步骤`;
        if (completed >= total) return `${currentCase.activeComboName || combo.name} · 已完成 ${total}/${total} 步`;
        const nextStep = combo.presets[completed];
        return `${currentCase.activeComboName || combo.name} · 已完成 ${completed}/${total} 步，下一步：${getPresetDisplayName(nextStep)}`;
    }

    function renderCurrentCase() {
        syncActiveComboState();
        syncInputValue('med-case-patient-label', currentCase.patientLabel || '');
        syncInputValue('med-case-age-gender', currentCase.ageGender || '');
        syncInputValue('med-case-chief-complaint', currentCase.chiefComplaint || '');
        syncInputValue('med-case-handoff-status', currentCase.handoffStatus || '');

        const templatePill = document.getElementById('medical-case-template-pill');
        if (templatePill) templatePill.textContent = currentCase.templateName || '未选择模板';

        const severityPill = document.getElementById('medical-case-severity-pill');
        if (severityPill) {
            severityPill.textContent = currentCase.severityLabel || severityValueToLabel(currentCase.severity);
            severityPill.dataset.severity = currentCase.severity || '';
        }

        setElementText('medical-case-scene', currentCase.scene, '选择医疗模板后会自动写入当前病例。');
        setElementText('medical-case-vitals', currentCase.vitalsSummary, '尚未生成体征。');
        setElementText('medical-case-assessment', currentCase.assessment, '尚未记录评估。');
        setElementText('medical-case-interventions', currentCase.interventions, '尚未记录操作。');
        setElementText('medical-case-flow', formatCurrentFlow(), '未选择流程。');

        const severitySummary = currentCase.severityLabel || (currentCase.severity ? severityValueToLabel(currentCase.severity) : '');
        const summaryBits = [
            currentCase.templateName,
            currentCase.chiefComplaint,
            severitySummary,
            currentCase.vitalsSummary,
            currentCase.activeComboId ? formatCurrentFlow() : '',
        ].filter(Boolean);
        setElementText(
            'med-quick-case-summary-text',
            summaryBits.join(' · '),
            '尚未建立病例，先在医疗助手中选择模板或填写基本信息。'
        );
    }

    function activateTab(tabId) {
        document.querySelectorAll('.med-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabId);
        });
        document.querySelectorAll('.med-tab-content').forEach(content => {
            content.classList.toggle('active', content.id === tabId);
        });
    }

    function fillSBARFromCurrentCase(options = {}) {
        const hasUsefulData = Boolean(
            currentCase.scene
            || currentCase.chiefComplaint
            || currentCase.vitalsSummary
            || currentCase.assessment
            || currentCase.interventions
        );
        if (!hasUsefulData) {
            showToast('当前病例内容还不够，先选择模板或生成体征', 'error');
            return;
        }

        const situation = [
            currentCase.patientLabel,
            currentCase.ageGender,
            currentCase.chiefComplaint,
            currentCase.severityLabel || severityValueToLabel(currentCase.severity),
        ].filter(Boolean).join('，');

        const background = currentCase.scene || '现场背景待补充';
        const assessment = currentCase.assessment || currentCase.vitalsSummary || '已完成初步评估';
        const recommendation = currentCase.interventions
            ? `${currentCase.interventions}，请继续接诊与后续处理`
            : (currentCase.handoffStatus || '请继续评估与处理');

        syncInputValue('sbar-situation', situation);
        syncInputValue('sbar-background', background);
        syncInputValue('sbar-assessment', assessment);
        syncInputValue('sbar-recommendation', recommendation);

        if (options.activateTab) activateTab('tab-sbar');
        if (!options.silent) showToast('已将当前病例填入 SBAR', 'success');
    }

    function seedCurrentCaseFromTemplate(templateId, templateName, scene) {
        currentCase = normalizeCurrentCase({
            ...createDefaultCase(),
            patientLabel: currentCase.patientLabel || '',
            ageGender: currentCase.ageGender || '',
            templateId,
            templateName,
            scene,
            chiefComplaint: inferChiefComplaint(scene),
            handoffStatus: '待评估',
        });
        persistCurrentCase();
        renderCurrentCase();
        renderCombos(_comboCache);
        showToast(`已建立当前病例：${templateName}`, 'success');
    }

    function updateCaseFromVitals(data, options = {}) {
        const patch = {
            severity: data.severity || currentCase.severity,
            severityLabel: data.severity_label || severityValueToLabel(data.severity),
            vitalsSummary: data.summary || composeAssessmentFromVitals(data),
            assessment: composeAssessmentFromVitals(data) || data.summary || currentCase.assessment,
            handoffStatus: currentCase.handoffStatus && currentCase.handoffStatus !== '待评估'
                ? currentCase.handoffStatus
                : '已完成体征评估',
        };
        if (options.recordAction !== false) {
            patch.interventions = mergeInterventions(currentCase.interventions, '完成生命体征评估');
        }
        updateCurrentCase(patch);
    }

    function setupCaseWorkbench() {
        currentCase = loadStoredCurrentCase();
        renderCurrentCase();

        [
            ['med-case-patient-label', 'patientLabel'],
            ['med-case-age-gender', 'ageGender'],
            ['med-case-chief-complaint', 'chiefComplaint'],
            ['med-case-handoff-status', 'handoffStatus'],
        ].forEach(([id, key]) => {
            const input = document.getElementById(id);
            if (!input) return;
            input.addEventListener('input', () => {
                updateCurrentCase({ [key]: input.value.trim() }, { rerenderCombos: false });
            });
        });

        document.getElementById('medical-clear-case-btn')?.addEventListener('click', () => resetCurrentCase());
        document.getElementById('medical-fill-sbar-btn')?.addEventListener('click', () => fillSBARFromCurrentCase({ activateTab: true }));
        document.getElementById('sbar-fill-from-case-btn')?.addEventListener('click', () => fillSBARFromCurrentCase());

        document.addEventListener('vancesender:presets-updated', () => {
            renderCombos(_comboCache);
            renderCurrentCase();
        });
    }

    // ── Tab Switching ─────────────────────────────────────────────────────

    function setupTabs() {
        document.querySelectorAll('.med-tab').forEach(tab => {
            tab.addEventListener('click', () => activateTab(tab.dataset.tab));
        });
    }

    // ── Medical Template Loading ──────────────────────────────────────────

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
                    if (opt && opt.value) {
                        seedCurrentCaseFromTemplate(opt.value, opt.textContent.trim(), opt.dataset.scenario || '');
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
                updateCaseFromVitals(data);
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

        resultEl.innerHTML = window.renderVitalsPanel ? window.renderVitalsPanel(data) : '';

        const doTexts = data.do_texts || [];
        let html = doTexts.map(t => `
            <div class="vitals-gen-text-line" title="点击复制此行" data-text="/${t.type} ${esc(t.content)}">
                <span class="vitals-gen-text-type type-${t.type}">/${t.type}</span>
                <span class="vitals-gen-text-content">${esc(t.content)}</span>
            </div>`).join('');
        html += '<button class="vitals-gen-copy-all" title="复制全部体征文本">📋 复制全部 /do 文本</button>';
        textsEl.innerHTML = html;

        textsEl.querySelectorAll('.vitals-gen-text-line').forEach(line => {
            line.addEventListener('click', () => {
                navigator.clipboard.writeText(line.dataset.text).then(() => {
                    showToast('已复制', 'success');
                }).catch(() => {});
            });
        });

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
                updateCurrentCase({ handoffStatus: '已生成 SBAR 交接' }, { rerenderCombos: false });
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
        html += '<button class="vitals-gen-copy-all">📋 复制全部 SBAR 交接文本</button>';
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
        _comboCacheReady = false;
        try {
            const res = await fetch(`${API_BASE}/medical/combos`, { headers: apiHeaders() });
            if (!res.ok) {
                _comboCache = [];
                _comboCacheReady = true;
                renderCombos(_comboCache);
                renderCurrentCase();
                return;
            }
            const data = await res.json();
            _comboCache = Array.isArray(data.combos) ? data.combos : [];
            _comboCacheReady = true;
            renderCombos(_comboCache);
            renderCurrentCase();
        } catch (e) {
            _comboCache = [];
            _comboCacheReady = true;
            console.warn('[Medical] Combos load error:', e);
            renderCombos(_comboCache);
            renderCurrentCase();
        }
    }

    function startCombo(comboId) {
        const combo = getComboById(comboId);
        if (!combo) return;
        updateCurrentCase({
            activeComboId: combo.id,
            activeComboName: combo.name,
            comboStepIndex: 0,
            handoffStatus: currentCase.handoffStatus || '流程进行中',
        });
        showToast(`已开始流程：${combo.name}`, 'success');
    }

    function openComboStep(comboId, stepIndex, options = {}) {
        const combo = getComboById(comboId);
        if (!combo || !Array.isArray(combo.presets)) return;
        const presetId = combo.presets[stepIndex];
        if (!presetId) return;

        const bridge = window.VanceSenderMedicalBridge;
        if (!bridge || typeof bridge.openQuickSendPreset !== 'function') {
            showToast('预设桥接未就绪，请稍后重试', 'error');
            return;
        }

        const presetMap = getPresetMap();
        if (!presetMap[presetId]) {
            showToast(`缺少预设：${presetId}`, 'error');
            return;
        }

        const opened = bridge.openQuickSendPreset(presetId);
        if (!opened) return;

        const nextIndex = options.advance === false ? stepIndex : Math.min(stepIndex + 1, combo.presets.length);
        updateCurrentCase({
            activeComboId: combo.id,
            activeComboName: combo.name,
            comboStepIndex: nextIndex,
            handoffStatus: nextIndex >= combo.presets.length ? '流程已完成，可执行交接' : '流程进行中',
        });
        showToast(`已加载流程步骤：${getPresetDisplayName(presetId)}`, 'success');
    }

    function loadNextComboStep(comboId) {
        const combo = getComboById(comboId);
        if (!combo || !Array.isArray(combo.presets) || combo.presets.length === 0) return;
        const nextIndex = currentCase.activeComboId === comboId ? (currentCase.comboStepIndex || 0) : 0;
        if (nextIndex >= combo.presets.length) {
            showToast('该流程已全部完成', 'success');
            return;
        }
        openComboStep(comboId, nextIndex);
    }

    function renderCombos(combos) {
        const grid = document.getElementById('combos-grid');
        if (!grid) return;
        if (!combos || combos.length === 0) {
            grid.innerHTML = '<div class="empty-state small"><p>暂无连招定义</p></div>';
            return;
        }

        const presetMap = getPresetMap();
        grid.innerHTML = combos.map(combo => {
            const isActive = currentCase.activeComboId === combo.id;
            const totalSteps = Array.isArray(combo.presets) ? combo.presets.length : 0;
            const completed = isActive ? Math.min(currentCase.comboStepIndex || 0, totalSteps) : 0;
            const progressText = isActive
                ? (completed >= totalSteps ? `已完成 ${totalSteps}/${totalSteps} 步` : `已完成 ${completed}/${totalSteps} 步`)
                : `共 ${totalSteps} 步`;
            const nextLabel = completed < totalSteps ? getPresetDisplayName(combo.presets[completed]) : '流程已完成';

            return `
                <div class="combo-card ${isActive ? 'combo-card-active' : ''}">
                    <div class="combo-card-name">${esc(combo.name)}</div>
                    <div class="combo-card-desc">${esc(combo.description)}</div>
                    <div class="combo-progress-text">${esc(progressText)}${completed < totalSteps ? ` · 下一步：${esc(nextLabel)}` : ''}</div>
                    <div class="combo-steps">
                        ${combo.presets.map((presetId, index) => {
                            const missing = !presetMap[presetId];
                            const completedStep = isActive && index < completed;
                            const currentStep = isActive && index === completed && completed < totalSteps;
                            const statusText = missing ? '缺少预设' : (completedStep ? '已完成' : (currentStep ? '下一步' : '待执行'));
                            return `
                                <button type="button" class="combo-step ${completedStep ? 'is-completed' : ''} ${currentStep ? 'is-current' : ''} ${missing ? 'is-missing' : ''}" data-combo-step="${esc(combo.id)}:${index}">
                                    <span class="combo-step-index">${index + 1}</span>
                                    <span class="combo-step-body">
                                        <span class="combo-step-name">${esc(getPresetDisplayName(presetId))}</span>
                                        <span class="combo-step-status">${esc(statusText)}</span>
                                    </span>
                                </button>`;
                        }).join('')}
                    </div>
                    <div class="combo-card-actions">
                        <button type="button" class="combo-primary-btn" data-combo-start="${esc(combo.id)}">${isActive ? '重新开始流程' : '开始流程'}</button>
                        <button type="button" class="combo-send-btn" data-combo-next="${esc(combo.id)}" ${completed >= totalSteps ? 'disabled' : ''}>加载下一步到快捷发送</button>
                    </div>
                </div>`;
        }).join('');

        grid.querySelectorAll('[data-combo-start]').forEach(btn => {
            btn.addEventListener('click', () => startCombo(btn.dataset.comboStart));
        });
        grid.querySelectorAll('[data-combo-next]').forEach(btn => {
            btn.addEventListener('click', () => loadNextComboStep(btn.dataset.comboNext));
        });
        grid.querySelectorAll('[data-combo-step]').forEach(btn => {
            btn.addEventListener('click', () => {
                const [comboId, stepIndex] = String(btn.dataset.comboStep || '').split(':');
                openComboStep(comboId, Number(stepIndex), { advance: false });
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
            const num = parseInt(val, 10);
            if (!isNaN(num)) {
                if (num < 90) return 'status-critical';
                if (num < 95) return 'status-warning';
                return 'status-normal';
            }
        }
        return '';
    }

    // ── Quick Send Panel — Medical Actions ──────────────────────────────

    async function loadQuickPhraseData() {
        if (_quickPhraseData) return _quickPhraseData;
        try {
            const res = await fetch(`${API_BASE}/medical/quick-phrases`, { headers: apiHeaders() });
            if (!res.ok) return null;
            const data = await res.json();
            const map = {};
            for (const phrases of Object.values(data.phrases || {})) {
                phrases.forEach(p => { map[p.id] = p; });
            }
            _quickPhraseData = map;
            return map;
        } catch (e) { return null; }
    }

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
        document.querySelectorAll('.med-quick-btn[data-med-action]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const actionId = btn.dataset.medAction;
                if (!actionId) return;

                const phrases = await loadQuickPhraseData();
                if (!phrases || !phrases[actionId]) {
                    showToast('短语数据加载失败', 'error');
                    return;
                }

                const phrase = phrases[actionId];
                const textsToSend = phrase.texts.map(t => `/${t.type} ${t.content}`);

                btn.disabled = true;
                btn.classList.add('sending');
                const originalText = btn.textContent;
                btn.textContent = '⏳ 发送中...';

                try {
                    const ok = await sendTextsSequentially(textsToSend, 1200);
                    if (ok) {
                        btn.classList.add('sent-ok');
                        updateCurrentCase({
                            interventions: mergeInterventions(currentCase.interventions, stripEmojiLabel(phrase.name)),
                            handoffStatus: currentCase.handoffStatus || '处理中',
                        }, { rerenderCombos: false });
                        showToast(`已发送: ${phrase.name}`, 'success');
                        setTimeout(() => btn.classList.remove('sent-ok'), 1000);
                    }
                } finally {
                    btn.disabled = false;
                    btn.classList.remove('sending');
                    btn.textContent = originalText;
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
                updateCaseFromVitals(data);

                if (previewEl) {
                    previewEl.innerHTML = doTexts.map(t =>
                        `<div class="vitals-gen-text-line" style="cursor:default;"><span class="vitals-gen-text-type type-do">/do</span><span class="vitals-gen-text-content">${esc(t.content)}</span></div>`
                    ).join('');
                }

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
        setupCaseWorkbench();
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
            loadQuickPhraseData();
        }, 500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
