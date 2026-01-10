let socket = null;
let currentSessionId = null;
let originalGraphData = null;
let generatedGraphData = null;
let originalMetrics = null;
let generatedMetrics = null;
let originalMotifData = null;
let generatedMotifData = null;
let isGenerating = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        uploadArea.style.borderColor = '#4a5568';
        uploadArea.style.background = '#edf2f7';
    }

    function unhighlight() {
        uploadArea.style.borderColor = '#cbd5e0';
        uploadArea.style.background = '#f7fafc';
    }

    uploadArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        handleFiles(e.target.files);
    }
});

// обработка загруженного графа
async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    showLoading('Uploading and analyzing graph...');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            originalGraphData = data.graph;
            originalMetrics = data.metrics;

            // сброс данных о сгенерированном графе
            generatedGraphData = null;
            generatedMetrics = null;
            generatedMotifData = null;

            displayGraphComparison();
            enableOriginalGraphControls();
            disableGeneratedGraphControls();
            showSuccess('Graph uploaded successfully!');
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        showError('Error uploading graph: ' + error.message);
    } finally {
        hideLoading();
    }
}

// загрузка примера графа
async function loadSampleData() {
    showLoading('Loading sample dataset...');

    try {
        const response = await fetch('/api/sample', {
            method: 'GET'
        });

        const data = await response.json();

        if (data.success) {
            originalGraphData = data.graph;
            originalMetrics = data.metrics;

            // сброс данных о сгенерированном графе
            generatedGraphData = null;
            generatedMetrics = null;
            generatedMotifData = null;

            displayGraphComparison();
            enableOriginalGraphControls();
            disableGeneratedGraphControls();
            showSuccess('Sample dataset loaded successfully!');
        } else {
            throw new Error(data.error || 'Failed to load sample');
        }
    } catch (error) {
        showError('Error loading sample: ' + error.message);
    } finally {
        hideLoading();
    }
}

// анализ мотивов исходного графа
async function analyzeGraph() {
    if (!originalGraphData) return;

    showLoading('Analyzing triplet motifs for the original graph...');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: originalGraphData
            })
        });

        const data = await response.json();

        if (data.success) {
            originalMotifData = data;
            displayMotifComparison();
            showSuccess('Original graph motif analysis completed!');
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Error analyzing motifs: ' + error.message);
    } finally {
        hideLoading();
    }
}

// анализ мотивов сгенерированного графа
async function analyzeGeneratedGraph() {
    if (!generatedGraphData) return;

    showLoading('Analyzing triplet motifs for the generated graph...');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: generatedGraphData
            })
        });

        const data = await response.json();

        if (data.success) {
            generatedMotifData = data;
            displayMotifComparison();
            showSuccess('Generated graph motif analysis completed!');
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Error analyzing motifs: ' + error.message);
    } finally {
        hideLoading();
    }
}

// генерация графа
async function generateGraph() {
    if (!originalGraphData || isGenerating) return;

    isGenerating = true;
    currentSessionId = Date.now().toString();

    const totalEdges = originalGraphData.edges.length;

    // прогресс бар
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressPercentage').textContent = '0%';
        document.getElementById('progressText').textContent = `0 / ${totalEdges}`;
        document.getElementById('progressDetails').textContent = 'Starting generation...';
    }

    // отключение кнопку генерации
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    }

    try {
        const response = await fetch('/api/generate_stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original_graph: originalGraphData,
                session_id: currentSessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to start generation');
        }

        console.log(`Generation started for session: ${currentSessionId}, target edges: ${totalEdges}`);

    } catch (error) {
        showError('Error starting generation: ' + error.message);
        resetGenerateButton();
        document.getElementById('progressContainer').style.display = 'none';
        isGenerating = false;
    }
}

// скачивание edgelist
async function downloadTxt(graphType) {
    const graphData = graphType === 'original' ? originalGraphData : generatedGraphData;
    if (!graphData) return;

    showLoading(`Preparing ${graphType} graph edgelist download...`);

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: graphData,
                format: 'txt'
            })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${graphType}_graph_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess(`${graphType.charAt(0).toUpperCase() + graphType.slice(1)} graph edgelist download started!`);
    } catch (error) {
        showError('Error downloading: ' + error.message);
    } finally {
        hideLoading();
    }
}

// скачивание JSON
async function downloadJson(graphType) {
    const graphData = graphType === 'original' ? originalGraphData : generatedGraphData;
    const metrics = graphType === 'original' ? originalMetrics : generatedMetrics;

    if (!graphData || !metrics) return;

    showLoading(`Preparing ${graphType} graph JSON download...`);

    try {
        // анализ мотивов
        let motifAnalysis = null;
        try {
            const analysisResponse = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    graph: graphData
                })
            });

            if (analysisResponse.ok) {
                motifAnalysis = await analysisResponse.json();
            }
        } catch (error) {
            console.warn('Could not get motif analysis for JSON:', error);
        }

        // Создаем полный объект с данными
        const fullData = {
            graph: graphData,
            metrics: metrics,
            motifAnalysis: motifAnalysis?.success ? motifAnalysis : null,
            metadata: {
                graphType: graphType,
                generatedAt: new Date().toISOString(),
                nodesCount: graphData.nodes.length,
                edgesCount: graphData.edges.length,
                fileName: `${graphType}_graph_complete_${new Date().toISOString().split('T')[0]}.json`
            }
        };

        // создание и скачивание JSON
        const dataStr = JSON.stringify(fullData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(dataBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fullData.metadata.fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess(`${graphType.charAt(0).toUpperCase() + graphType.slice(1)} graph complete information download started!`);
    } catch (error) {
        showError('Error downloading JSON: ' + error.message);
    } finally {
        hideLoading();
    }
}

// отображение сравнения графов
function displayGraphComparison() {
    const comparisonDiv = document.getElementById('graphComparison');

    if (!originalGraphData) {
        comparisonDiv.innerHTML = `
            <div class="comparison-placeholder">
                <i class="fas fa-balance-scale fa-3x"></i>
                <p>Upload a graph to see comparison</p>
            </div>
        `;
        return;
    }

    const hasGeneratedGraph = generatedGraphData && generatedMetrics;

    const formatValue = (value, decimalPlaces = 2) => {
        if (value === undefined || value === null) return 'N/A';
        if (typeof value === 'number') {
            return value.toFixed(decimalPlaces);
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return value;
    };

    let html = `
        <div class="comparison-container">
            <div class="comparison-header">
                <div class="header-column">Metric</div>
                <div class="header-column">Original Graph</div>
                <div class="header-column">Generated Graph</div>
            </div>

            <div class="comparison-table">
    `;

    // Основные метрики
    const metricsToCompare = [
        { label: 'Number of Vertices', key: 'num_nodes', formatter: v => v || (v === 0 ? '0' : '-') },
        { label: 'Number of Arcs', key: 'num_edges', formatter: v => v || (v === 0 ? '0' : '-') },
        { label: 'Graph Density', key: 'density', formatter: v => formatValue(v, 4) },
        { label: 'Min In-Degree', key: 'min_in_degree', formatter: v => v || '0' },
        { label: 'Max In-Degree', key: 'max_in_degree', formatter: v => v || '0' },
        { label: 'Min Out-Degree', key: 'min_out_degree', formatter: v => v || '0' },
        { label: 'Max Out-Degree', key: 'max_out_degree', formatter: v => v || '0' },
        { label: 'Weakly Connected', key: 'weakly_connected', formatter: formatBoolean },
        { label: 'Strongly Connected', key: 'strongly_connected', formatter: formatBoolean },
        { label: 'Vertices in Largest SCC', key: 'strongly_connected_nodes', formatter: v => v || '0' },
        { label: 'Transitivity', key: 'transitivity', formatter: v => formatValue(v, 3) },
        { label: 'Reciprocity', key: 'reciprocity', formatter: v => formatValue(v, 3) },
        { label: 'Avg Clustering', key: 'avg_clustering', formatter: v => formatValue(v, 3) },
    ];

    metricsToCompare.forEach(metric => {
        const origValue = originalMetrics ? metric.formatter(originalMetrics[metric.key]) : '-';
        const genValue = hasGeneratedGraph ? metric.formatter(generatedMetrics[metric.key]) : '-';

        html += `
            <div class="comparison-row">
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value original">${origValue}</div>
                <div class="metric-value generated">${genValue}</div>
            </div>
        `;
    });

    html += `
            </div>

            ${!hasGeneratedGraph ? `
            <div class="no-generated-data">
                <i class="fas fa-info-circle"></i>
                <p>No generated graph yet. Click "Generate New Graph" to create one.</p>
            </div>
            ` : ''}
        </div>
    `;

    comparisonDiv.innerHTML = html;
}

// отображение сравнения мотивов
function displayMotifComparison() {
    const comparisonDiv = document.getElementById('motifComparison');

    if (!originalMotifData) {
        comparisonDiv.innerHTML = `
            <div class="comparison-placeholder">
                <i class="fas fa-chart-pie fa-3x"></i>
                <p>Click "Analyze Motifs" to see comparison</p>
            </div>
        `;
        return;
    }

    const hasGeneratedMotifs = generatedMotifData;

    let html = `
        <div class="comparison-container">
            <div class="motif-table-container">
                <div class="motif-table-header">
                    <div class="header-column">Motif ID</div>
                    <div class="header-column">Original Count</div>
                    <div class="header-column">Original Percentage</div>
                    <div class="header-column">Generated Count</div>
                    <div class="header-column">Generated Percentage</div>
                </div>

                <div class="motif-table-content">
    `;

    const sortedOriginalMotifs = [...(originalMotifData.motifs || [])].sort((a, b) => a.id - b.id);
    const originalMotifMap = new Map(sortedOriginalMotifs.map(m => [m.id, m]));

    if (hasGeneratedMotifs) {
        const sortedGeneratedMotifs = [...(generatedMotifData.motifs || [])].sort((a, b) => a.id - b.id);
        const generatedMotifMap = new Map(sortedGeneratedMotifs.map(m => [m.id, m]));

        const allMotifIds = new Set([
            ...sortedOriginalMotifs.map(m => m.id),
            ...sortedGeneratedMotifs.map(m => m.id)
        ]);

        Array.from(allMotifIds).sort((a, b) => a - b).forEach(motifId => {
            const origMotif = originalMotifMap.get(motifId);
            const genMotif = generatedMotifMap.get(motifId);

            const origCount = origMotif ? origMotif.count : 0;
            const genCount = genMotif ? genMotif.count : 0;

            const origPercent = originalMotifData.total_motifs > 0 ? ((origCount / originalMotifData.total_motifs) * 100).toFixed(2) : '0.00';
            const genPercent = generatedMotifData.total_motifs > 0 ? ((genCount / generatedMotifData.total_motifs) * 100).toFixed(2) : '0.00';

            html += `
                <div class="motif-row">
                    <div class="motif-id"><strong>M${motifId}</strong></div>

                    <div class="motif-value original-count">
                        ${origCount}
                    </div>
                    <div class="motif-value original-percent">
                        ${origPercent}%
                    </div>

                    <div class="motif-value generated-count">
                        ${genCount}
                    </div>
                    <div class="motif-value generated-percent">
                        ${genPercent}%
                    </div>
                </div>
            `;
        });
    } else {
        sortedOriginalMotifs.forEach(motif => {
            const percent = originalMotifData.total_motifs > 0 ? ((motif.count / originalMotifData.total_motifs) * 100).toFixed(2) : '0.00';
            html += `
                <div class="motif-row">
                    <div class="motif-id"><strong>M${motif.id}</strong></div>

                    <div class="motif-value original-count">
                        ${motif.count}
                    </div>
                    <div class="motif-value original-percent">
                        ${percent}%
                    </div>

                    <div class="motif-value generated-count">
                        -
                    </div>
                    <div class="motif-value generated-percent">
                        -
                    </div>
                </div>
            `;
        });
    }

    html += `
                </div>
            </div>
        </div>
    `;

    comparisonDiv.innerHTML = html;
}

// включение кнопок для исходного графа
function enableOriginalGraphControls() {
    const analyzeBtn = document.getElementById('analyzeOriginalBtn');
    const downloadTxtBtn = document.getElementById('downloadOriginalTxtBtn');
    const downloadJsonBtn = document.getElementById('downloadOriginalJsonBtn');
    const generateBtn = document.getElementById('generateBtn');

    if (analyzeBtn) analyzeBtn.disabled = false;
    if (downloadTxtBtn) downloadTxtBtn.disabled = false;
    if (downloadJsonBtn) downloadJsonBtn.disabled = false;
    if (generateBtn) generateBtn.disabled = false;
}

// включение кнопок для сгенерированного графа
function enableGeneratedGraphControls() {
    const analyzeBtn = document.getElementById('analyzeGeneratedBtn');
    const downloadTxtBtn = document.getElementById('downloadGeneratedTxtBtn');
    const downloadJsonBtn = document.getElementById('downloadGeneratedJsonBtn');

    if (analyzeBtn) analyzeBtn.disabled = false;
    if (downloadTxtBtn) downloadTxtBtn.disabled = false;
    if (downloadJsonBtn) downloadJsonBtn.disabled = false;
}

// отключение кнопок для сгенерированного графа
function disableGeneratedGraphControls() {
    const analyzeBtn = document.getElementById('analyzeGeneratedBtn');
    const downloadTxtBtn = document.getElementById('downloadGeneratedTxtBtn');
    const downloadJsonBtn = document.getElementById('downloadGeneratedJsonBtn');

    if (analyzeBtn) analyzeBtn.disabled = true;
    if (downloadTxtBtn) downloadTxtBtn.disabled = true;
    if (downloadJsonBtn) downloadJsonBtn.disabled = true;
}

// инициализация WebSocket
function initializeWebSocket() {
    if (!socket) {
        socket = io('http://' + window.location.hostname + ':5000');

        socket.on('connect', function() {
            console.log('Connected to WebSocket server');
        });

        socket.on('generation_progress', function(data) {
            if (data.session_id === currentSessionId) {
                const progressFill = document.getElementById('progressFill');
                const progressPercentage = document.getElementById('progressPercentage');
                const progressText = document.getElementById('progressText');
                const progressDetails = document.getElementById('progressDetails');

                if (progressFill && progressPercentage && progressText && progressDetails) {
                    progressFill.style.width = data.progress + '%';
                    progressPercentage.textContent = data.progress + '%';
                    progressText.textContent = data.current + ' / ' + data.total;
                    progressDetails.textContent = `Generating: ${data.current} edges out of ${data.total}`;
                }
            }
        });

        socket.on('generation_complete', function(data) {
            if (data.session_id === currentSessionId) {
                handleGenerationComplete(data);
            }
        });

        socket.on('generation_error', function(data) {
            if (data.session_id === currentSessionId) {
                handleGenerationError(data);
            }
        });
    }
}

// обработка завершения генерации
function handleGenerationComplete(data) {
    if (data.success) {
        generatedGraphData = data.graph;
        generatedMetrics = data.metrics;

        // Обновляем сравнение
        displayGraphComparison();

        // Включаем контроллы для сгенерированного графа
        enableGeneratedGraphControls();

        // Обновляем прогресс-бар
        updateProgressDisplay(100, data.edges_generated, data.edges_target);
        document.getElementById('progressDetails').textContent =
            `Generation complete! ${data.edges_generated} edges generated`;

        // Скрываем прогресс-бар через 3 секунды
        setTimeout(() => {
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }, 3000);

        showSuccess(`New graph generated successfully! ${data.edges_generated} edges created.`);
    }

    resetGenerateButton();
    currentSessionId = null;
    isGenerating = false;
}

// Обработка ошибки генерации
function handleGenerationError(data) {
    showError('Error generating graph: ' + data.error);
    resetGenerateButton();

    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }

    currentSessionId = null;
    isGenerating = false;
}

// сброс кнопки генерации
function resetGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-play-circle"></i> Generate New Graph';
    }
}

// обновление отображения прогресса
function updateProgressDisplay(percentage, current, total) {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressText = document.getElementById('progressText');

    if (progressFill && progressPercentage && progressText) {
        progressFill.style.width = percentage + '%';
        progressPercentage.textContent = percentage + '%';
        progressText.textContent = current + ' / ' + total;
    }
}

function formatBoolean(value) {
    if (value === undefined || value === null) return 'N/A';
    return value === true ? 'Yes' : 'No';
}

function showLoading(message) {
    const loadingMessage = document.getElementById('loadingMessage');
    const loadingModal = document.getElementById('loadingModal');

    if (loadingMessage) loadingMessage.textContent = message;
    if (loadingModal) loadingModal.classList.add('active');
}

function hideLoading() {
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) loadingModal.classList.remove('active');
}

function showSuccess(message) {
    console.log('Success:', message);
}

function showError(message) {
    console.error('Error:', message);
    alert('Error: ' + message);
}