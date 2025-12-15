/**
 * BookLayout - Frontend Application
 * Gerencia interface e comunicação com backend
 */

const API_BASE = '/api';

// Estado da aplicação
const appState = {
    manuscript: null,
    config: {},
    templates: [],
    currentTemplate: null
};

// Elementos do DOM
const elements = {
    uploadArea: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    textInput: document.getElementById('text-input'),
    processTextBtn: document.getElementById('process-text-btn'),
    uploadStatus: document.getElementById('uploadStatus'),
    statusText: document.getElementById('statusText'),
    manuscriptInfo: document.getElementById('manuscriptInfo'),
    navItems: document.querySelectorAll('.nav-item'),
    sections: document.querySelectorAll('.section'),
    templatesGrid: document.getElementById('templatesGrid'),
    generatePreviewBtn: document.getElementById('generatePreviewBtn'),
    previewContainer: document.getElementById('previewContainer'),
    previewPages: document.getElementById('previewPages'),
    exportPdfBtn: document.getElementById('exportPdfBtn'),
    exportEpubBtn: document.getElementById('exportEpubBtn'),
    loadingModal: document.getElementById('loadingModal'),
    loadingText: document.getElementById('loadingText')
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadTemplates();
    setupColorInputs();
});

/**
 * Inicializa listeners de eventos
 */
function initializeEventListeners() {
    // Text Processing
    if (elements.processTextBtn) {
        elements.processTextBtn.addEventListener('click', handleTextSubmit);
    }

    // Upload
    if (elements.uploadArea) {
        elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
        elements.uploadArea.addEventListener('dragover', handleDragOver);
        elements.uploadArea.addEventListener('dragleave', handleDragLeave);
        elements.uploadArea.addEventListener('drop', handleDrop);
    }

    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    // Navegação
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => switchSection(item.dataset.section));
    });

    // Preview
    elements.generatePreviewBtn.addEventListener('click', () => {
        generatePreview().catch(err => {
            console.error(err);
            alert('Erro ao gerar preview: ' + (err.message || err.error || 'Erro desconhecido'));
        });
    });

    // Export
    elements.exportPdfBtn.addEventListener('click', exportPDF);
    elements.exportEpubBtn.addEventListener('click', exportEPub);
}

/**
 * Carrega templates de design
 */
async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/templates`);
        const data = await response.json();
        appState.templates = data.templates;
        renderTemplates();
    } catch (error) {
        console.error('Erro ao carregar templates:', error);
    }
}

/**
 * Renderiza templates de design
 */
function renderTemplates() {
    elements.templatesGrid.innerHTML = '';

    appState.templates.forEach(template => {
        const card = document.createElement('div');
        card.className = 'template-card';
        card.innerHTML = `
            <h4>${template.name}</h4>
            <p>${template.description}</p>
        `;

        card.addEventListener('click', () => selectTemplate(template));
        elements.templatesGrid.appendChild(card);
    });
}

/**
 * Seleciona um template
 */
function selectTemplate(template) {
    appState.currentTemplate = template;

    // Atualizar UI
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('active');
    });
    event.target.closest('.template-card').classList.add('active');

    // Aplicar configurações do template
    applyTemplateConfig(template.config);
}

/**
 * Aplica configurações do template
 */
function applyTemplateConfig(config) {
    document.getElementById('fontFamily').value = config.font_family;
    document.getElementById('fontSize').value = config.font_size;
    document.getElementById('lineHeight').value = config.line_height;
    document.getElementById('marginTop').value = config.margin_top;
    document.getElementById('marginBottom').value = config.margin_bottom;
    document.getElementById('marginLeft').value = config.margin_left;
    document.getElementById('marginRight').value = config.margin_right;
    document.getElementById('primaryColor').value = config.primary_color;
    document.getElementById('accentColor').value = config.accent_color;
    document.getElementById('backgroundColor').value = config.background_color;

    updateColorValues();
}

/**
 * Configura inputs de cor
 */
function setupColorInputs() {
    const colorInputs = ['primaryColor', 'accentColor', 'backgroundColor'];

    colorInputs.forEach(id => {
        const input = document.getElementById(id);
        input.addEventListener('change', updateColorValues);
    });
}

/**
 * Atualiza valores de cor exibidos
 */
function updateColorValues() {
    document.getElementById('primaryColorValue').textContent =
        document.getElementById('primaryColor').value;
    document.getElementById('accentColorValue').textContent =
        document.getElementById('accentColor').value;
    document.getElementById('backgroundColorValue').textContent =
        document.getElementById('backgroundColor').value;
}

/**
 * Alterna seção ativa
 */
function switchSection(sectionId) {
    // Atualizar nav items
    elements.navItems.forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionId) {
            item.classList.add('active');
        }
    });

    // Atualizar seções
    elements.sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionId) {
            section.classList.add('active');
        }
    });
}

/**
 * Manipula drag over
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadArea.style.borderColor = '#8b7355';
    elements.uploadArea.style.backgroundColor = 'rgba(139, 115, 85, 0.05)';
}

/**
 * Manipula drag leave
 */
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadArea.style.borderColor = '#e0e0e0';
    elements.uploadArea.style.backgroundColor = 'white';
}

/**
 * Manipula drop de arquivo
 */
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }

    elements.uploadArea.style.borderColor = '#e0e0e0';
    elements.uploadArea.style.backgroundColor = 'white';
}

/**
 * Manipula seleção de arquivo
 */
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

/**
 * Faz upload do arquivo
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showLoading('Processando manuscrito...');

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            // Check if response is JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                throw await response.json();
            } else {
                // Not JSON (likely HTML 404/500/502 from proxy or static site)
                const text = await response.text();
                throw new Error(`Erro do Servidor (${response.status}): ${text.substring(0, 100)}...`);
            }
        }

        const data = await response.json();
        appState.manuscript = data.manuscript;

        displayManuscriptInfo(data.manuscript);
        hideLoading();

    } catch (error) {
        handleUploadError(error);
    }
}

/**
 * Processa envio de texto direto
 */
async function handleTextSubmit() {
    const text = elements.textInput.value;

    if (!text.trim()) {
        alert('Por favor, cole algum texto antes de processar.');
        return;
    }

    // UI Feedback
    elements.processTextBtn.disabled = true;
    elements.processTextBtn.textContent = 'Processando...';
    showLoading('Processando texto...');

    try {
        const response = await fetch(`${API_BASE}/upload-text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            // Check if response is JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                throw await response.json();
            } else {
                // Not JSON (likely HTML 404/500/502 from proxy or static site)
                const text = await response.text();
                throw new Error(`Erro do Servidor (${response.status}): O backend não respondeu corretamente. Verifique se você está na URL correta (Web Service vs Static Site).`);
            }
        }

        const data = await response.json();
        appState.manuscript = data.manuscript;

        displayManuscriptInfo(data.manuscript);

        // Auto-generate preview
        showLoading('Gerando preview automático...');
        await generatePreview();

        // Switch to preview tab
        switchSection('preview');

        // Feedback subtle
        console.log('Texto processado e preview gerado');

    } catch (error) {
        // Agora qualquer erro (upload ou preview) cai aqui e mostra alerta
        handleUploadError(error);
    } finally {
        // Restore UI
        elements.processTextBtn.disabled = false;
        elements.processTextBtn.textContent = 'Processar Texto';
        hideLoading();
    }
}

async function handleUploadError(error) {
    console.error('Erro:', error);

    let errorMsg = error.message || "Erro desconhecido";

    // Tenta extrair mensagem se for um objeto Response
    if (error.json) {
        try {
            const errData = await error.json();
            errorMsg = errData.error || errorMsg;
            if (errData.traceback) {
                console.error('Backend Traceback:', errData.traceback);
                errorMsg += `\n\nDetalhes Técnicos:\n${errData.type}: ${errData.error}`;
            }
        } catch (e) {
            // Falha ao parsear
        }
    }

    alert('Erro ao processar:\n' + errorMsg);
}

/**
 * Exibe informações do manuscrito
 */
function displayManuscriptInfo(manuscript) {
    document.getElementById('wordCount').textContent = manuscript.word_count;
    document.getElementById('charCount').textContent = manuscript.char_count;
    document.getElementById('chapterCount').textContent =
        (manuscript.structure.chapters || []).length;
    document.getElementById('sectionCount').textContent =
        (manuscript.structure.sections || []).length;

    elements.manuscriptInfo.style.display = 'block';
}

/**
 * Coleta configurações do formulário
 */
function getConfig() {
    return {
        page_width: 210,
        page_height: 297,
        margin_top: parseFloat(document.getElementById('marginTop').value),
        margin_bottom: parseFloat(document.getElementById('marginBottom').value),
        margin_left: parseFloat(document.getElementById('marginLeft').value),
        margin_right: parseFloat(document.getElementById('marginRight').value),
        font_family: document.getElementById('fontFamily').value,
        font_size: parseFloat(document.getElementById('fontSize').value),
        line_height: parseFloat(document.getElementById('lineHeight').value),
        primary_color: document.getElementById('primaryColor').value,
        accent_color: document.getElementById('accentColor').value,
        background_color: document.getElementById('backgroundColor').value
    };
}

/**
 * Gera preview do layout
 */
async function generatePreview() {
    if (!appState.manuscript) {
        throw new Error('Por favor, envie um manuscrito primeiro');
    }

    // Nota: O loading deve ser gerenciado por quem chama esta função, 
    // ou garantimos que não conflite com o loading do processo principal.
    // Mas para manter compatibilidade com o botão direto de "Gerar Preview":
    const isAutoProcess = elements.loadingModal.style.display === 'flex';
    if (!isAutoProcess) showLoading('Gerando preview...');

    try {
        const response = await fetch(`${API_BASE}/preview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                manuscript: appState.manuscript,
                config: getConfig()
            })
        });

        if (!response.ok) {
            throw await response.json(); // Tenta pegar erro detalhado
        }

        const data = await response.json();
        displayPreview(data.layout);

        if (!isAutoProcess) hideLoading();
        return true;

    } catch (error) {
        if (!isAutoProcess) hideLoading();
        throw error; // Propaga erro para ser tratado no handleTextSubmit ou no clique do botão
    }
}

/**
 * Exibe preview do layout
 */
function displayPreview(layout) {
    elements.previewPages.innerHTML = '';
    document.getElementById('totalPages').textContent = layout.total_pages;

    // Obter configuração atual para aplicar fonte
    const currentConfig = getConfig();
    const fontFamily = currentConfig.font_family;

    // Mostrar apenas as primeiras 5 páginas no preview
    const pagesToShow = Math.min(5, layout.pages.length);

    for (let i = 0; i < pagesToShow; i++) {
        const page = layout.pages[i];
        const pageDiv = document.createElement('div');
        pageDiv.className = 'preview-page';

        // Determinar fallback correto
        let fallback = 'serif';
        if (fontFamily === 'Inter' || fontFamily === 'Segoe UI' || fontFamily === 'Arial') {
            fallback = 'sans-serif';
        }

        // Aplicar fonte dinâmica
        pageDiv.style.fontFamily = `"${fontFamily}", ${fallback}`;

        let content = '';

        if (page.type === 'cover') {
            // Capa agora usa classes CSS
            const title = page.content.find(i => i.type === 'title')?.text || 'Título';
            const subtitle = page.content.find(i => i.type === 'subtitle')?.text || '';
            content = `
                <div style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <h1 style="font-size: 3em; margin-bottom: 0.5em; color: var(--secondary-color);">${title}</h1>
                    <p style="font-size: 1.5em; color: var(--primary-color);">${subtitle}</p>
                </div>
            `;
        } else if (page.type === 'title_page') {
            const title = page.content.find(i => i.type === 'text' && i.font_size > 20)?.text || 'Título';
            const author = page.content.find(i => i.type === 'text' && i.font_size < 20)?.text || 'Autor';
            content = `
                <div style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <h1 style="font-size: 2em; margin-bottom: 2em; color: var(--primary-color);">${title}</h1>
                    <p style="font-size: 1.2em;">${author}</p>
                </div>
            `;
        } else if (page.type === 'toc') {
            content = '<h2 style="text-align: center; margin-bottom: 2em;">Sumário</h2>';
            page.content.forEach(item => {
                if (item.type === 'toc_entry') {
                    const indent = item.indent ? '2em' : '0';
                    const weight = item.indent ? 'normal' : 'bold';
                    content += `<p style="margin-left: ${indent}; font-weight: ${weight}; text-indent: 0;">${item.text}</p>`;
                }
            });
        } else {
            page.content.forEach(item => {
                if (item.type === 'text') {
                    content += `<p>${item.text}</p>`;
                } else if (item.type === 'heading') {
                    content += `<h2>${item.text}</h2>`;
                } else if (item.type === 'chapter_title') {
                    // Tentar extrair número para efeito "Big Number"
                    // Ex: "Capítulo 1", "1. Introdução"
                    const match = item.text.match(/(\d+)/);
                    const number = match ? match[0] : '';
                    // Remove numero e palavras comuns do título visual
                    const text = item.text.replace(/capítulo/gi, '').replace(number, '').replace(/^[.\-\s]+/, '').trim();

                    if (number) {
                        content += `
                            <div class="chapter-header-container">
                                <div class="big-chapter-number">${number.padStart(2, '0')}</div>
                                <div class="chapter-title-text">${text || 'Capítulo'}</div>
                            </div>
                        `;
                    } else {
                        // Sem número, renderiza normal mas elegante
                        content += `<h2 style="font-size: 2.5em; text-align: center; margin-bottom: 2em; font-family: 'Playfair Display', serif;">${item.text}</h2>`;
                    }
                } else if (item.type === 'tool_block') {
                    // Renderizar Ferramenta
                    const tool = item.data;
                    let toolContent = `<div class="tool-box"><div class="tool-title">${tool.title.replace(/Exercício:|Ferramenta:|Checklist:/i, '').trim()}</div>`;

                    tool.content.forEach(toolItem => {
                        if (toolItem.type === 'instruction') {
                            toolContent += `<div class="tool-instruction">${toolItem.text}</div>`;
                        } else if (toolItem.type === 'checklist_item') {
                            toolContent += `
                                <div class="checklist-item">
                                    <div class="checkbox-box"></div>
                                    <span>${toolItem.text}</span>
                                </div>`;
                        } else if (toolItem.type === 'writing_line') {
                            toolContent += `
                                <div class="writing-line-container">
                                    <p>${toolItem.text}</p>
                                    <div class="writing-line"></div>
                                </div>`;
                        } else if (toolItem.type === 'rating_scale') {
                            let circles = '';
                            for (let j = 1; j <= toolItem.max; j++) {
                                circles += `<div class="rating-circle">${j}</div>`;
                            }
                            toolContent += `
                                <div style="text-align:center; margin-top:10px;">${toolItem.text}</div>
                                <div class="rating-scale">${circles}</div>`;
                        }
                    });

                    toolContent += `</div>`;
                    content += toolContent;
                }
            });
        }

        pageDiv.innerHTML = content + `<div class="preview-page-number">${page.page_number}</div>`;
        elements.previewPages.appendChild(pageDiv);
    }

    elements.previewContainer.style.display = 'flex'; // Changed to flex for new CSS
}

/**
 * Exporta para PDF
 */
async function exportPDF() {
    if (!appState.manuscript) {
        alert('Por favor, envie um manuscrito primeiro');
        return;
    }

    const title = document.getElementById('bookTitle').value || 'Livro';

    showLoading('Gerando PDF...');

    try {
        const response = await fetch(`${API_BASE}/generate-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                manuscript: appState.manuscript,
                config: getConfig(),
                title: title
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao gerar PDF');
        }

        const blob = await response.blob();
        downloadFile(blob, `${title}.pdf`);
        hideLoading();

    } catch (error) {
        console.error('Erro:', error);
        hideLoading();
        alert('Erro ao gerar PDF: ' + error.message);
    }
}

/**
 * Exporta para ePub
 */
async function exportEPub() {
    if (!appState.manuscript) {
        alert('Por favor, envie um manuscrito primeiro');
        return;
    }

    const title = document.getElementById('bookTitle').value || 'Livro';
    const author = document.getElementById('bookAuthor').value || 'Autor';

    showLoading('Gerando ePub...');

    try {
        const response = await fetch(`${API_BASE}/generate-epub`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                manuscript: appState.manuscript,
                config: getConfig(),
                title: title,
                author: author
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao gerar ePub');
        }

        const blob = await response.blob();
        downloadFile(blob, `${title}.epub`);
        hideLoading();

    } catch (error) {
        console.error('Erro:', error);
        hideLoading();
        alert('Erro ao gerar ePub: ' + error.message);
    }
}

/**
 * Faz download de arquivo
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * Mostra modal de carregamento
 */
function showLoading(text = 'Processando...') {
    elements.loadingText.textContent = text;
    elements.loadingModal.style.display = 'flex';
}

/**
 * Esconde modal de carregamento
 */
function hideLoading() {
    elements.loadingModal.style.display = 'none';
}
