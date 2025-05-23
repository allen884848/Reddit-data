/**
 * Reddit Data Collector - Frontend JavaScript Application
 * ======================================================
 * 
 * This file contains all the frontend functionality for the Reddit data collection website.
 * Features include search, results display, history management, data export, and real-time status updates.
 * 
 * Author: Reddit Data Collector Team
 * Version: 2.0
 * Last Updated: 2024
 */

// ===== APPLICATION STATE =====
const AppState = {
    currentResults: [],
    currentPage: 1,
    resultsPerPage: 10,
    isSearching: false,
    searchHistory: [],
    systemStatus: {},
    lastSearchId: null
};

// ===== API ENDPOINTS =====
const API = {
    search: '/api/search',
    posts: '/api/posts',
    history: '/api/history',
    export: '/api/export',
    status: '/api/status',
    health: '/api/health',
    statistics: '/api/statistics',
    collectPromotional: '/api/collect-promotional'
};

// ===== UTILITY FUNCTIONS =====

/**
 * Make HTTP requests with error handling
 */
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.querySelector('.toast-container');
    const toastId = `toast-${Date.now()}`;
    
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi bi-${getToastIcon(type)} text-${type} me-2"></i>
                <strong class="me-auto">${getToastTitle(type)}</strong>
                <small class="text-muted">now</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle-fill',
        error: 'exclamation-triangle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
    };
    return icons[type] || 'info-circle-fill';
}

function getToastTitle(type) {
    const titles = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Information'
    };
    return titles[type] || 'Notification';
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    if (typeof num !== 'number') return '0';
    return num.toLocaleString();
}

/**
 * Truncate text to specified length
 */
function truncateText(text, maxLength = 150) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Validate search form inputs
 */
function validateSearchForm() {
    const keywords = document.getElementById('keywords-input').value.trim();
    
    if (!keywords) {
        showToast('Please enter at least one keyword to search', 'warning');
        return false;
    }
    
    if (keywords.length < 2) {
        showToast('Keywords must be at least 2 characters long', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Get search parameters from form
 */
function getSearchParameters() {
    const keywords = document.getElementById('keywords-input').value.trim().split(',').map(k => k.trim()).filter(k => k);
    const subreddits = document.getElementById('subreddits-input').value.trim();
    const timeFilter = document.getElementById('time-filter').value;
    const sortBy = document.getElementById('sort-by').value;
    const limit = parseInt(document.getElementById('limit-input').value);
    const minScore = parseInt(document.getElementById('min-score').value) || 0;
    const minComments = parseInt(document.getElementById('min-comments').value) || 0;
    const includeNsfw = document.getElementById('include-nsfw').checked;
    
    const subredditList = subreddits === 'all' || !subreddits ? ['all'] : 
                         subreddits.split(',').map(s => s.trim()).filter(s => s);
    
    return {
        keywords,
        subreddits: subredditList,
        time_filter: timeFilter,
        sort: sortBy,
        limit,
        min_score: minScore,
        min_comments: minComments,
        include_nsfw: includeNsfw
    };
}

// ===== SEARCH FUNCTIONALITY =====

/**
 * Perform Reddit search
 */
async function performSearch() {
    if (!validateSearchForm()) return;
    
    if (AppState.isSearching) {
        showToast('Search already in progress', 'warning');
        return;
    }
    
    const searchParams = getSearchParameters();
    
    try {
        setSearchingState(true);
        showStatusBar('Searching Reddit...', 'Please wait while we collect data from Reddit');
        
        const response = await makeRequest(API.search, {
            method: 'POST',
            body: JSON.stringify(searchParams)
        });
        
        if (response.status === 'success') {
            AppState.currentResults = response.results.posts;
            AppState.lastSearchId = response.search_id;
            AppState.currentPage = 1;
            
            displayResults(AppState.currentResults);
            updateResultsSummary(response.results);
            showResultsSection();
            
            showToast(
                `Found ${response.results.total_processed} posts (${response.results.promotional_count} promotional)`,
                'success'
            );
            
            // Refresh search history
            loadSearchHistory();
        } else {
            throw new Error(response.message || 'Search failed');
        }
        
    } catch (error) {
        console.error('Search failed:', error);
        showToast(`Search failed: ${error.message}`, 'error');
    } finally {
        setSearchingState(false);
        hideStatusBar();
    }
}

/**
 * Collect promotional posts
 */
async function collectPromotionalPosts() {
    if (AppState.isSearching) {
        showToast('Search already in progress', 'warning');
        return;
    }
    
    try {
        setSearchingState(true);
        showStatusBar('Collecting Promotional Posts...', 'Searching for promotional and advertising content');
        
        const subreddits = document.getElementById('subreddits-input').value.trim();
        const subredditList = subreddits === 'all' || !subreddits ? ['all'] : 
                             subreddits.split(',').map(s => s.trim()).filter(s => s);
        
        const response = await makeRequest(API.collectPromotional, {
            method: 'POST',
            body: JSON.stringify({
                subreddits: subredditList,
                limit: 100
            })
        });
        
        if (response.status === 'success') {
            AppState.currentResults = response.results.posts;
            AppState.lastSearchId = response.search_id;
            AppState.currentPage = 1;
            
            displayResults(AppState.currentResults);
            updateResultsSummary(response.results);
            showResultsSection();
            
            showToast(
                `Found ${response.results.promotional_count} promotional posts out of ${response.results.total_processed} total`,
                'success'
            );
            
            loadSearchHistory();
        } else {
            throw new Error(response.message || 'Promotional collection failed');
        }
        
    } catch (error) {
        console.error('Promotional collection failed:', error);
        showToast(`Promotional collection failed: ${error.message}`, 'error');
    } finally {
        setSearchingState(false);
        hideStatusBar();
    }
}

/**
 * Set searching state UI
 */
function setSearchingState(isSearching) {
    AppState.isSearching = isSearching;
    
    const searchBtn = document.querySelector('#search-form button[type="submit"]');
    const searchBtnText = searchBtn.querySelector('.search-btn-text');
    const searchBtnSpinner = searchBtn.querySelector('.search-btn-spinner');
    const collectBtn = document.getElementById('collect-promotional-btn');
    
    if (isSearching) {
        searchBtn.disabled = true;
        collectBtn.disabled = true;
        searchBtnText.classList.add('d-none');
        searchBtnSpinner.classList.remove('d-none');
    } else {
        searchBtn.disabled = false;
        collectBtn.disabled = false;
        searchBtnText.classList.remove('d-none');
        searchBtnSpinner.classList.add('d-none');
    }
}

// ===== STATUS BAR FUNCTIONALITY =====

/**
 * Show status bar
 */
function showStatusBar(title, message) {
    const statusBar = document.getElementById('status-bar');
    const statusTitle = document.getElementById('status-title');
    const statusMessage = document.getElementById('status-message');
    
    statusTitle.textContent = title;
    statusMessage.textContent = message;
    statusBar.classList.remove('d-none');
}

/**
 * Hide status bar
 */
function hideStatusBar() {
    const statusBar = document.getElementById('status-bar');
    statusBar.classList.add('d-none');
}

// ===== RESULTS DISPLAY =====

/**
 * Display search results
 */
function displayResults(results) {
    const resultsGrid = document.getElementById('results-grid');
    
    if (!results || results.length === 0) {
        resultsGrid.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-search fs-1 text-muted mb-3"></i>
                <h3 class="h5 text-muted">No results found</h3>
                <p class="text-muted">Try adjusting your search criteria or keywords</p>
            </div>
        `;
        return;
    }
    
    const startIndex = (AppState.currentPage - 1) * AppState.resultsPerPage;
    const endIndex = startIndex + AppState.resultsPerPage;
    const pageResults = results.slice(startIndex, endIndex);
    
    resultsGrid.innerHTML = pageResults.map(post => createResultItem(post)).join('');
    
    // Update pagination
    updatePagination(results.length);
}

/**
 * Create result item HTML
 */
function createResultItem(post) {
    const isPromotional = post.is_promotional;
    const promotionalClass = isPromotional ? 'promotional' : '';
    
    return `
        <div class="result-item ${promotionalClass}" data-post-id="${post.reddit_id}">
            <div class="result-title">${escapeHtml(post.title)}</div>
            <div class="result-meta">
                <span class="badge">/r/${escapeHtml(post.subreddit)}</span>
                <span><i class="bi bi-person"></i> ${escapeHtml(post.author)}</span>
                <span><i class="bi bi-clock"></i> ${formatDate(post.created_utc)}</span>
            </div>
            ${post.content ? `<div class="result-content">${escapeHtml(truncateText(post.content))}</div>` : ''}
            <div class="result-stats">
                <span><i class="bi bi-arrow-up"></i> ${formatNumber(post.score)}</span>
                <span><i class="bi bi-chat"></i> ${formatNumber(post.num_comments)}</span>
                ${post.url && post.url !== post.reddit_id ? `<a href="${escapeHtml(post.url)}" target="_blank" class="text-decoration-none"><i class="bi bi-link-45deg"></i> Link</a>` : ''}
            </div>
        </div>
    `;
}

/**
 * Update results summary
 */
function updateResultsSummary(results) {
    const summary = document.getElementById('results-summary');
    const promotionalText = results.promotional_count > 0 ? 
        ` (${results.promotional_count} promotional)` : '';
    
    summary.textContent = `Found ${formatNumber(results.total_processed)} posts${promotionalText} in ${results.execution_time.toFixed(2)}s`;
}

/**
 * Show results section
 */
function showResultsSection() {
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('d-none');
    
    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Update pagination
 */
function updatePagination(totalResults) {
    const pagination = document.getElementById('results-pagination');
    const totalPages = Math.ceil(totalResults / AppState.resultsPerPage);
    
    if (totalPages <= 1) {
        pagination.classList.add('d-none');
        return;
    }
    
    pagination.classList.remove('d-none');
    const paginationList = pagination.querySelector('.pagination');
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${AppState.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${AppState.currentPage - 1}">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, AppState.currentPage - 2);
    const endPage = Math.min(totalPages, AppState.currentPage + 2);
    
    if (startPage > 1) {
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (startPage > 2) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === AppState.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${AppState.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${AppState.currentPage + 1}">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationList.innerHTML = paginationHTML;
}

/**
 * Handle pagination click
 */
function handlePaginationClick(event) {
    event.preventDefault();
    
    if (event.target.closest('.page-item.disabled') || event.target.closest('.page-item.active')) {
        return;
    }
    
    const pageLink = event.target.closest('[data-page]');
    if (pageLink) {
        const newPage = parseInt(pageLink.dataset.page);
        if (newPage !== AppState.currentPage) {
            AppState.currentPage = newPage;
            displayResults(AppState.currentResults);
            
            // Scroll to top of results
            document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

// ===== SEARCH HISTORY =====

/**
 * Load search history
 */
async function loadSearchHistory() {
    try {
        const response = await makeRequest(`${API.history}?limit=10`);
        
        if (response.status === 'success') {
            AppState.searchHistory = response.data;
            displaySearchHistory(AppState.searchHistory);
        }
    } catch (error) {
        console.error('Failed to load search history:', error);
    }
}

/**
 * Display search history
 */
function displaySearchHistory(history) {
    const historyGrid = document.getElementById('history-grid');
    
    if (!history || history.length === 0) {
        historyGrid.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-clock-history fs-1 text-muted mb-3"></i>
                <h3 class="h6 text-muted">No search history</h3>
                <p class="text-muted small">Your search history will appear here</p>
            </div>
        `;
        return;
    }
    
    historyGrid.innerHTML = history.map(item => createHistoryItem(item)).join('');
}

/**
 * Create history item HTML
 */
function createHistoryItem(item) {
    const statusBadge = getStatusBadge(item.status);
    
    return `
        <div class="history-item" data-search-id="${item.id}">
            <div class="history-keywords">${escapeHtml(item.keywords)}</div>
            <div class="history-meta">
                <span><i class="bi bi-clock"></i> ${formatDate(item.search_date)}</span>
                ${item.subreddits ? `<span><i class="bi bi-reddit"></i> ${escapeHtml(item.subreddits)}</span>` : ''}
                <span><i class="bi bi-collection"></i> ${formatNumber(item.results_count || 0)} posts</span>
                <span class="badge ${statusBadge.class}">${statusBadge.text}</span>
            </div>
        </div>
    `;
}

/**
 * Get status badge for history item
 */
function getStatusBadge(status) {
    const badges = {
        completed: { class: 'bg-success', text: 'Completed' },
        in_progress: { class: 'bg-warning', text: 'In Progress' },
        failed: { class: 'bg-danger', text: 'Failed' }
    };
    return badges[status] || { class: 'bg-secondary', text: 'Unknown' };
}

/**
 * Show search history section
 */
function showHistorySection() {
    const historySection = document.getElementById('history-section');
    historySection.classList.remove('d-none');
    
    // Load history if not already loaded
    if (AppState.searchHistory.length === 0) {
        loadSearchHistory();
    }
    
    // Smooth scroll to history
    setTimeout(() => {
        historySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// ===== DATA EXPORT =====

/**
 * Show export modal
 */
function showExportModal() {
    const modal = new bootstrap.Modal(document.getElementById('exportModal'));
    modal.show();
}

/**
 * Perform data export
 */
async function performExport() {
    const format = document.getElementById('export-format').value;
    const filter = document.getElementById('export-filter').value;
    const limit = document.getElementById('export-limit').value;
    
    try {
        // Build export URL with parameters
        const params = new URLSearchParams({
            format: format,
            limit: limit === 'all' ? '10000' : limit
        });
        
        if (filter === 'promotional') {
            params.append('is_promotional', 'true');
        } else if (filter === 'non-promotional') {
            params.append('is_promotional', 'false');
        }
        
        const exportUrl = `${API.export}?${params.toString()}`;
        
        // Show loading state
        const exportBtn = document.getElementById('confirm-export-btn');
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Exporting...';
        exportBtn.disabled = true;
        
        const response = await makeRequest(exportUrl);
        
        if (response.status === 'success') {
            // Download the file
            const downloadUrl = response.export_info.download_url;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = response.export_info.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast(`Data exported successfully as ${response.export_info.filename}`, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
            modal.hide();
        } else {
            throw new Error(response.message || 'Export failed');
        }
        
    } catch (error) {
        console.error('Export failed:', error);
        showToast(`Export failed: ${error.message}`, 'error');
    } finally {
        // Restore button state
        const exportBtn = document.getElementById('confirm-export-btn');
        exportBtn.innerHTML = originalText;
        exportBtn.disabled = false;
    }
}

// ===== SYSTEM STATUS =====

/**
 * Load system status
 */
async function loadSystemStatus() {
    try {
        const response = await makeRequest(API.status);
        
        if (response.status === 'success') {
            AppState.systemStatus = response;
            updateSystemStatusDisplay(response);
        }
    } catch (error) {
        console.error('Failed to load system status:', error);
        updateSystemStatusDisplay({ status: 'error', message: 'Failed to load status' });
    }
}

/**
 * Update system status display
 */
function updateSystemStatusDisplay(status) {
    // Update system health
    const systemHealth = document.getElementById('system-health');
    const healthStatus = status.configuration?.reddit_api_configured ? 'Operational' : 'Limited';
    const healthClass = status.configuration?.reddit_api_configured ? 'bg-success' : 'bg-warning';
    
    systemHealth.innerHTML = `
        <div class="d-flex justify-content-between">
            <span>Status:</span>
            <span class="badge ${healthClass}">${healthStatus}</span>
        </div>
    `;
    
    // Update database stats
    const databaseStats = document.getElementById('database-stats');
    const dbStats = status.statistics?.database || {};
    
    databaseStats.innerHTML = `
        <div class="d-flex justify-content-between mb-2">
            <span>Total Posts:</span>
            <span class="fw-bold">${formatNumber(dbStats.total_posts || 0)}</span>
        </div>
        <div class="d-flex justify-content-between">
            <span>Promotional:</span>
            <span class="fw-bold">${formatNumber(dbStats.promotional_posts || 0)}</span>
        </div>
    `;
    
    // Update API stats
    const apiStats = document.getElementById('api-stats');
    const appStats = status.statistics?.application || {};
    
    const successRate = appStats.successful_searches && appStats.failed_searches ? 
        ((appStats.successful_searches / (appStats.successful_searches + appStats.failed_searches)) * 100).toFixed(1) : 
        '100';
    
    apiStats.innerHTML = `
        <div class="d-flex justify-content-between mb-2">
            <span>Total Calls:</span>
            <span class="fw-bold">${formatNumber(appStats.total_api_calls || 0)}</span>
        </div>
        <div class="d-flex justify-content-between">
            <span>Success Rate:</span>
            <span class="fw-bold">${successRate}%</span>
        </div>
    `;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Clear search results
 */
function clearResults() {
    AppState.currentResults = [];
    AppState.currentPage = 1;
    
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.add('d-none');
    
    showToast('Results cleared', 'info');
}

/**
 * Clear search history
 */
async function clearHistory() {
    if (!confirm('Are you sure you want to clear the search history?')) {
        return;
    }
    
    // For now, just clear the display
    // In a real implementation, you'd call an API endpoint to clear server-side history
    AppState.searchHistory = [];
    displaySearchHistory([]);
    
    showToast('Search history cleared', 'info');
}

// ===== EVENT LISTENERS =====

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Search form submission
    document.getElementById('search-form').addEventListener('submit', (e) => {
        e.preventDefault();
        performSearch();
    });
    
    // Quick action buttons
    document.getElementById('collect-promotional-btn').addEventListener('click', collectPromotionalPosts);
    document.getElementById('view-history-btn').addEventListener('click', showHistorySection);
    document.getElementById('export-data-btn').addEventListener('click', showExportModal);
    
    // Results section buttons
    document.getElementById('clear-results-btn').addEventListener('click', clearResults);
    
    // History section buttons
    document.getElementById('clear-history-btn').addEventListener('click', clearHistory);
    
    // Export modal buttons
    document.getElementById('confirm-export-btn').addEventListener('click', performExport);
    
    // Status bar close button
    document.getElementById('status-close').addEventListener('click', hideStatusBar);
    
    // Pagination clicks
    document.getElementById('results-pagination').addEventListener('click', handlePaginationClick);
    
    // Export dropdown clicks
    document.querySelectorAll('.dropdown-item[data-format]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const format = e.target.dataset.format;
            
            // Quick export without modal
            const params = new URLSearchParams({
                format: format,
                limit: '100'
            });
            
            const exportUrl = `${API.export}?${params.toString()}`;
            window.open(exportUrl, '_blank');
        });
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Advanced options toggle icon rotation
    const advancedToggle = document.querySelector('[data-bs-target="#advanced-options"]');
    const advancedOptions = document.getElementById('advanced-options');
    
    advancedOptions.addEventListener('show.bs.collapse', () => {
        const icon = advancedToggle.querySelector('.bi-chevron-down');
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    });
    
    advancedOptions.addEventListener('hide.bs.collapse', () => {
        const icon = advancedToggle.querySelector('.bi-chevron-up');
        if (icon) {
            icon.classList.remove('bi-chevron-up');
            icon.classList.add('bi-chevron-down');
        }
    });
    
    // Auto-refresh system status every 30 seconds
    setInterval(loadSystemStatus, 30000);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to search
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!AppState.isSearching) {
                performSearch();
            }
        }
        
        // Escape to close status bar
        if (e.key === 'Escape') {
            hideStatusBar();
        }
    });
}

// ===== APPLICATION INITIALIZATION =====

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 Reddit Data Collector - Frontend Application Starting...');
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial data
    loadSystemStatus();
    loadSearchHistory();
    
    // Focus on search input
    document.getElementById('keywords-input').focus();
    
    // Show welcome message
    setTimeout(() => {
        showToast('Welcome to Reddit Data Collector! Enter keywords to start searching.', 'info', 3000);
    }, 1000);
    
    console.log('✅ Application initialized successfully');
}

// ===== APPLICATION STARTUP =====

// Wait for DOM to be fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export functions for global access (if needed)
window.RedditDataCollector = {
    performSearch,
    collectPromotionalPosts,
    showExportModal,
    loadSystemStatus,
    showToast
}; 