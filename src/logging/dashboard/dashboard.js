/**
 * Agent Investment Platform - Log Dashboard JavaScript
 * Handles real-time log streaming, filtering, and visualization
 */

class LogDashboard {
    constructor() {
        this.wsConnection = null;
        this.isConnected = false;
        this.logBuffer = [];
        this.currentPage = 1;
        this.logsPerPage = 50;
        this.totalLogs = 0;
        this.filters = {};
        this.chart = null;
        this.chartData = {
            labels: [],
            datasets: [{
                label: 'Logs per minute',
                data: [],
                borderColor: 'rgb(37, 99, 235)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4
            }]
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initChart();
        this.connectWebSocket();
        this.loadComponents();
        this.applyDefaultFilters();
    }

    setupEventListeners() {
        // Connection and refresh
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());

        // Filters
        document.getElementById('timeRange').addEventListener('change', (e) => this.handleTimeRangeChange(e));
        document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
        document.getElementById('clearFilters').addEventListener('click', () => this.clearFilters());

        // Real-time toggle
        document.getElementById('realtimeToggle').addEventListener('change', (e) => this.toggleRealtime(e.target.checked));

        // Pagination
        document.getElementById('prevPage').addEventListener('click', () => this.previousPage());
        document.getElementById('nextPage').addEventListener('click', () => this.nextPage());

        // Log actions
        document.getElementById('exportLogs').addEventListener('click', () => this.exportLogs());
        document.getElementById('clearLogTable').addEventListener('click', () => this.clearLogTable());

        // Modal
        document.getElementById('closeModal').addEventListener('click', () => this.closeModal());
        document.getElementById('logDetailModal').addEventListener('click', (e) => {
            if (e.target.id === 'logDetailModal') this.closeModal();
        });

        // Chart controls
        document.getElementById('chartZoomIn').addEventListener('click', () => this.zoomChart(1.2));
        document.getElementById('chartZoomOut').addEventListener('click', () => this.zoomChart(0.8));

        // Toast close
        document.querySelector('.toast-close').addEventListener('click', () => this.hideToast());
    }

    initChart() {
        const ctx = document.getElementById('logChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:8765`;

        this.updateConnectionStatus('connecting');

        try {
            this.wsConnection = new WebSocket(wsUrl);

            this.wsConnection.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                this.sendFilters();
            };

            this.wsConnection.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');

                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };

            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };

        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            this.updateConnectionStatus('disconnected');
        }
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'log_entry':
                this.handleNewLogEntry(message.data);
                break;
            case 'stats':
                this.updateStatistics(message.data);
                break;
            case 'connected':
                console.log('WebSocket handshake completed:', message.data);
                break;
            case 'error':
                this.showToast(`WebSocket error: ${message.data.message}`, 'error');
                break;
        }
    }

    handleNewLogEntry(logEntry) {
        if (document.getElementById('realtimeToggle').checked) {
            this.logBuffer.unshift(logEntry);

            // Limit buffer size
            if (this.logBuffer.length > 1000) {
                this.logBuffer = this.logBuffer.slice(0, 1000);
            }

            this.updateLogTable();
            this.updateChartData();
            this.updateLogCounts();
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('span');

        indicator.className = `fas fa-circle status-indicator ${status}`;

        switch (status) {
            case 'connected':
                text.textContent = 'Connected';
                break;
            case 'connecting':
                text.textContent = 'Connecting...';
                break;
            case 'disconnected':
                text.textContent = 'Disconnected';
                break;
        }
    }

    sendFilters() {
        if (!this.isConnected || !this.wsConnection) return;

        const levels = Array.from(document.getElementById('levelFilter').selectedOptions).map(opt => opt.value);
        const components = Array.from(document.getElementById('componentFilter').selectedOptions).map(opt => opt.value).filter(Boolean);
        const searchText = document.getElementById('searchFilter').value;

        const filterMessage = {
            type: 'set_filters',
            data: {
                levels: levels.length > 0 ? levels : null,
                components: components.length > 0 ? components : null,
                message_contains: searchText || null,
                min_timestamp: this.getStartTimeFromRange()
            }
        };

        this.wsConnection.send(JSON.stringify(filterMessage));
    }

    getStartTimeFromRange() {
        const timeRange = document.getElementById('timeRange').value;
        const now = new Date();

        switch (timeRange) {
            case '5m':
                return new Date(now.getTime() - 5 * 60 * 1000).toISOString();
            case '15m':
                return new Date(now.getTime() - 15 * 60 * 1000).toISOString();
            case '1h':
                return new Date(now.getTime() - 60 * 60 * 1000).toISOString();
            case '6h':
                return new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString();
            case '24h':
                return new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();
            case 'custom':
                const startTime = document.getElementById('startTime').value;
                return startTime ? new Date(startTime).toISOString() : null;
            default:
                return null;
        }
    }

    handleTimeRangeChange(event) {
        const customRange = document.getElementById('customTimeRange');
        if (event.target.value === 'custom') {
            customRange.style.display = 'block';
        } else {
            customRange.style.display = 'none';
            this.sendFilters();
        }
    }

    applyFilters() {
        this.sendFilters();
        this.queryHistoricalLogs();
    }

    clearFilters() {
        document.getElementById('levelFilter').selectedIndex = -1;
        document.getElementById('componentFilter').selectedIndex = -1;
        document.getElementById('searchFilter').value = '';
        document.getElementById('timeRange').value = '1h';
        document.getElementById('customTimeRange').style.display = 'none';

        // Select default levels
        const levelOptions = document.getElementById('levelFilter').options;
        for (let option of levelOptions) {
            if (['INFO', 'WARNING', 'ERROR', 'CRITICAL'].includes(option.value)) {
                option.selected = true;
            }
        }

        this.applyFilters();
    }

    applyDefaultFilters() {
        // Set default time range
        document.getElementById('timeRange').value = '1h';

        // Select default log levels
        const levelOptions = document.getElementById('levelFilter').options;
        for (let option of levelOptions) {
            if (['INFO', 'WARNING', 'ERROR', 'CRITICAL'].includes(option.value)) {
                option.selected = true;
            }
        }

        this.applyFilters();
    }

    toggleRealtime(enabled) {
        if (enabled && this.isConnected) {
            this.sendFilters();
        }
    }

    async loadComponents() {
        try {
            const response = await fetch('/api/logs/components');
            const data = await response.json();

            const componentFilter = document.getElementById('componentFilter');

            // Clear existing options except "All Components"
            while (componentFilter.children.length > 1) {
                componentFilter.removeChild(componentFilter.lastChild);
            }

            // Add component options
            data.components.forEach(component => {
                const option = document.createElement('option');
                option.value = component;
                option.textContent = component;
                componentFilter.appendChild(option);
            });

        } catch (error) {
            console.error('Error loading components:', error);
        }
    }

    async queryHistoricalLogs() {
        this.showLoading();

        try {
            const params = new URLSearchParams();

            // Time range
            const startTime = this.getStartTimeFromRange();
            if (startTime) params.set('start_time', startTime);

            const timeRange = document.getElementById('timeRange').value;
            if (timeRange === 'custom') {
                const endTime = document.getElementById('endTime').value;
                if (endTime) params.set('end_time', new Date(endTime).toISOString());
            }

            // Filters
            const levels = Array.from(document.getElementById('levelFilter').selectedOptions).map(opt => opt.value);
            if (levels.length > 0) params.set('level', levels.join(','));

            const components = Array.from(document.getElementById('componentFilter').selectedOptions).map(opt => opt.value).filter(Boolean);
            if (components.length > 0) params.set('component', components.join(','));

            const searchText = document.getElementById('searchFilter').value;
            if (searchText) params.set('message_contains', searchText);

            // Pagination
            params.set('limit', this.logsPerPage.toString());
            params.set('offset', ((this.currentPage - 1) * this.logsPerPage).toString());

            const response = await fetch(`/api/logs?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.logBuffer = data.logs;
                this.totalLogs = data.count;
                this.updateLogTable();
                this.updatePagination();
            } else {
                this.showToast(`Error querying logs: ${data.error}`, 'error');
            }

        } catch (error) {
            console.error('Error querying logs:', error);
            this.showToast('Error querying logs', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadStatistics() {
        try {
            const params = new URLSearchParams();
            const startTime = this.getStartTimeFromRange();
            if (startTime) params.set('start_time', startTime);

            const response = await fetch(`/api/logs/stats?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.updateStatistics(data);
            }

        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateStatistics(stats) {
        // Update stat cards
        const levels = stats.levels || [];

        let errorCount = 0, warningCount = 0, infoCount = 0;

        levels.forEach(level => {
            switch (level.key.toUpperCase()) {
                case 'ERROR':
                case 'CRITICAL':
                    errorCount += level.doc_count;
                    break;
                case 'WARNING':
                    warningCount += level.doc_count;
                    break;
                case 'INFO':
                    infoCount += level.doc_count;
                    break;
            }
        });

        document.getElementById('errorCount').textContent = errorCount.toLocaleString();
        document.getElementById('warningCount').textContent = warningCount.toLocaleString();
        document.getElementById('infoCount').textContent = infoCount.toLocaleString();
        document.getElementById('totalCount').textContent = (stats.total || 0).toLocaleString();

        // Update chart with timeline data
        if (stats.timeline) {
            this.updateChartWithTimeline(stats.timeline);
        }
    }

    updateChartWithTimeline(timeline) {
        const labels = timeline.map(bucket => new Date(bucket.key));
        const data = timeline.map(bucket => bucket.doc_count);

        this.chartData.labels = labels;
        this.chartData.datasets[0].data = data;

        this.chart.update();
    }

    updateChartData() {
        const now = new Date();
        const currentMinute = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes());

        // Add current minute if not exists
        if (this.chartData.labels.length === 0 || this.chartData.labels[this.chartData.labels.length - 1].getTime() !== currentMinute.getTime()) {
            this.chartData.labels.push(currentMinute);
            this.chartData.datasets[0].data.push(1);
        } else {
            // Increment current minute count
            this.chartData.datasets[0].data[this.chartData.datasets[0].data.length - 1]++;
        }

        // Keep only last 60 minutes
        if (this.chartData.labels.length > 60) {
            this.chartData.labels.shift();
            this.chartData.datasets[0].data.shift();
        }

        this.chart.update('none');
    }

    updateLogTable() {
        const tbody = document.getElementById('logsTableBody');
        tbody.innerHTML = '';

        const startIndex = (this.currentPage - 1) * this.logsPerPage;
        const endIndex = Math.min(startIndex + this.logsPerPage, this.logBuffer.length);

        for (let i = startIndex; i < endIndex; i++) {
            const log = this.logBuffer[i];
            const row = this.createLogRow(log, i);
            tbody.appendChild(row);
        }

        this.updateLogCounts();
    }

    createLogRow(log, index) {
        const row = document.createElement('tr');

        // Format timestamp
        const timestamp = new Date(log.timestamp).toLocaleString();

        // Truncate message
        const message = log.message.length > 100 ? log.message.substring(0, 100) + '...' : log.message;

        row.innerHTML = `
            <td class="col-timestamp">${timestamp}</td>
            <td class="col-level">
                <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
            </td>
            <td class="col-component">${log.component}</td>
            <td class="col-logger">${log.logger_name}</td>
            <td class="col-message">
                <div class="log-message" title="${this.escapeHtml(log.message)}">${this.escapeHtml(message)}</div>
            </td>
            <td class="col-actions">
                <button class="action-btn" onclick="dashboard.showLogDetail(${index})" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;

        return row;
    }

    showLogDetail(index) {
        const log = this.logBuffer[index];
        if (!log) return;

        const modal = document.getElementById('logDetailModal');
        const content = document.getElementById('logDetailContent');

        content.innerHTML = `
            <div class="log-detail">
                <div class="log-detail-section">
                    <h4>Basic Information</h4>
                    <div class="log-detail-grid">
                        <div class="log-detail-key">Timestamp:</div>
                        <div class="log-detail-value">${new Date(log.timestamp).toLocaleString()}</div>
                        <div class="log-detail-key">Level:</div>
                        <div class="log-detail-value">
                            <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
                        </div>
                        <div class="log-detail-key">Component:</div>
                        <div class="log-detail-value">${log.component}</div>
                        <div class="log-detail-key">Logger:</div>
                        <div class="log-detail-value">${log.logger_name}</div>
                        <div class="log-detail-key">Module:</div>
                        <div class="log-detail-value">${log.module}</div>
                        <div class="log-detail-key">Function:</div>
                        <div class="log-detail-value">${log.function}</div>
                        <div class="log-detail-key">Line:</div>
                        <div class="log-detail-value">${log.line_number}</div>
                    </div>
                </div>

                <div class="log-detail-section">
                    <h4>Message</h4>
                    <div class="log-detail-json">${this.escapeHtml(log.message)}</div>
                </div>

                <div class="log-detail-section">
                    <h4>System Information</h4>
                    <div class="log-detail-grid">
                        <div class="log-detail-key">Hostname:</div>
                        <div class="log-detail-value">${log.hostname}</div>
                        <div class="log-detail-key">Process ID:</div>
                        <div class="log-detail-value">${log.process_id}</div>
                        <div class="log-detail-key">Thread ID:</div>
                        <div class="log-detail-value">${log.thread_id}</div>
                        ${log.trace_id ? `
                            <div class="log-detail-key">Trace ID:</div>
                            <div class="log-detail-value">${log.trace_id}</div>
                        ` : ''}
                        ${log.span_id ? `
                            <div class="log-detail-key">Span ID:</div>
                            <div class="log-detail-value">${log.span_id}</div>
                        ` : ''}
                    </div>
                </div>

                ${log.exception ? `
                    <div class="log-detail-section">
                        <h4>Exception</h4>
                        <div class="log-detail-grid">
                            <div class="log-detail-key">Type:</div>
                            <div class="log-detail-value">${log.exception.type}</div>
                            <div class="log-detail-key">Message:</div>
                            <div class="log-detail-value">${this.escapeHtml(log.exception.message)}</div>
                        </div>
                        <h4>Traceback</h4>
                        <div class="log-detail-json">${this.escapeHtml(log.exception.traceback.join(''))}</div>
                    </div>
                ` : ''}

                ${log.extra ? `
                    <div class="log-detail-section">
                        <h4>Extra Data</h4>
                        <div class="log-detail-json">${JSON.stringify(log.extra, null, 2)}</div>
                    </div>
                ` : ''}
            </div>
        `;

        modal.classList.add('show');
    }

    closeModal() {
        document.getElementById('logDetailModal').classList.remove('show');
    }

    updateLogCounts() {
        const total = this.logBuffer.length;
        const displayed = Math.min(this.logsPerPage, total - (this.currentPage - 1) * this.logsPerPage);
        document.getElementById('logCount').textContent = `${displayed} of ${total} logs`;
    }

    updatePagination() {
        const totalPages = Math.ceil(this.totalLogs / this.logsPerPage);

        document.getElementById('currentPage').textContent = this.currentPage;
        document.getElementById('totalPages').textContent = totalPages;

        document.getElementById('prevPage').disabled = this.currentPage <= 1;
        document.getElementById('nextPage').disabled = this.currentPage >= totalPages;
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.queryHistoricalLogs();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.totalLogs / this.logsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.queryHistoricalLogs();
        }
    }

    clearLogTable() {
        this.logBuffer = [];
        this.updateLogTable();
        this.updatePagination();
    }

    exportLogs() {
        const csvContent = this.convertLogsToCSV(this.logBuffer);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    convertLogsToCSV(logs) {
        const headers = ['Timestamp', 'Level', 'Component', 'Logger', 'Module', 'Function', 'Line', 'Message'];
        const csvRows = [headers.join(',')];

        logs.forEach(log => {
            const row = [
                log.timestamp,
                log.level,
                log.component,
                log.logger_name,
                log.module,
                log.function,
                log.line_number,
                `"${log.message.replace(/"/g, '""')}"`
            ];
            csvRows.push(row.join(','));
        });

        return csvRows.join('\n');
    }

    zoomChart(factor) {
        const chart = this.chart;
        const currentMin = chart.scales.x.min;
        const currentMax = chart.scales.x.max;
        const range = currentMax - currentMin;
        const center = (currentMin + currentMax) / 2;
        const newRange = range / factor;

        chart.options.scales.x.min = center - newRange / 2;
        chart.options.scales.x.max = center + newRange / 2;
        chart.update();
    }

    refreshData() {
        this.queryHistoricalLogs();
        this.loadStatistics();
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('errorToast');
        const messageElement = toast.querySelector('.toast-message');

        messageElement.textContent = message;
        toast.classList.add('show');

        // Auto-hide after 5 seconds
        setTimeout(() => this.hideToast(), 5000);
    }

    hideToast() {
        document.getElementById('errorToast').classList.remove('show');
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new LogDashboard();
});

// Make dashboard globally available for onclick handlers
window.dashboard = dashboard;
