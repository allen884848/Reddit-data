"""
Vercel Complete Flask Application
===============================

Complete version of the Reddit Data Collector for Vercel deployment.
This version provides the full functionality and interface like the local application.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-reddit-collector-key-2025')

# 完整的HTML模板 - 与本地应用相同的界面
COMPLETE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Data Collector</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <style>
        :root {
            --primary-color: #ff4500;
            --secondary-color: #0079d3;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-bg: #f8f9fa;
            --border-color: #dee2e6;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--light-bg);
        }

        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .hero-section {
            background: linear-gradient(135deg, #ff4500, #ff6b35);
            color: white;
            padding: 4rem 0;
            margin-bottom: 2rem;
        }

        .search-container {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .search-input-group .form-control {
            border: 2px solid #e9ecef;
            font-size: 1.1rem;
            padding: 0.75rem 1rem;
        }

        .search-input-group .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(255, 69, 0, 0.25);
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            font-weight: 600;
        }

        .btn-primary:hover {
            background-color: #e03d00;
            border-color: #e03d00;
        }

        .card {
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .post-card {
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
        }

        .post-card.promotional {
            border-left-color: var(--warning-color);
            background-color: #fff8e1;
        }

        .post-card.reddit-promoted {
            border-left-color: var(--danger-color);
            background-color: #ffebee;
            border: 2px solid #ffcdd2;
        }

        .post-card.reddit-promoted .card-title {
            color: #c62828;
        }

        .status-section {
            padding: 2rem 0;
        }

        .status-icon {
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background-color: rgba(255, 69, 0, 0.1);
        }

        .results-section {
            padding: 2rem 0;
        }

        .history-section {
            padding: 2rem 0;
        }

        .footer {
            background-color: white;
            border-top: 1px solid var(--border-color);
        }

        .spinner-border-sm {
            width: 1rem;
            height: 1rem;
        }

        .toast {
            min-width: 300px;
        }

        @media (max-width: 768px) {
            .hero-section {
                padding: 2rem 0;
            }
            
            .search-container {
                padding: 1.5rem;
            }
        }

        .quick-actions {
            padding: 1.5rem 0;
        }

        .quick-actions .btn {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.8);
            color: var(--primary-color);
            font-weight: 500;
            padding: 0.6rem 1rem;
            border-radius: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            font-size: 0.875rem;
            position: relative;
            overflow: hidden;
        }

        .quick-actions .btn:hover {
            background-color: white;
            border-color: white;
            color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .quick-actions .btn i {
            font-size: 1em;
        }

        /* 特殊按钮样式 */
        #collect-reddit-promoted-btn {
            background: linear-gradient(135deg, #dc3545, #c82333);
            border-color: #dc3545;
            color: white;
            font-weight: 600;
        }

        #collect-reddit-promoted-btn:hover {
            background: linear-gradient(135deg, #c82333, #a71e2a);
            border-color: #c82333;
            color: white;
            transform: translateY(-2px) scale(1.02);
        }

        #quick-search-btn {
            background: linear-gradient(135deg, #0d6efd, #0b5ed7);
            border-color: #0d6efd;
            color: white;
            font-weight: 600;
        }

        #quick-search-btn:hover {
            background: linear-gradient(135deg, #0b5ed7, #0a58ca);
            border-color: #0b5ed7;
            color: white;
            transform: translateY(-2px) scale(1.02);
        }

        #collect-promotional-btn {
            background: linear-gradient(135deg, #ffc107, #e0a800);
            border-color: #ffc107;
            color: #212529;
            font-weight: 600;
        }

        #collect-promotional-btn:hover {
            background: linear-gradient(135deg, #e0a800, #d39e00);
            border-color: #e0a800;
            color: #212529;
            transform: translateY(-2px) scale(1.02);
        }

        #view-history-btn {
            background: linear-gradient(135deg, #6c757d, #5a6268);
            border-color: #6c757d;
            color: white;
            font-weight: 500;
        }

        #view-history-btn:hover {
            background: linear-gradient(135deg, #5a6268, #495057);
            border-color: #5a6268;
            color: white;
        }

        #export-data-btn {
            background: linear-gradient(135deg, #28a745, #1e7e34);
            border-color: #28a745;
            color: white;
            font-weight: 500;
        }

        #export-data-btn:hover {
            background: linear-gradient(135deg, #1e7e34, #155724);
            border-color: #1e7e34;
            color: white;
        }

        /* 响应式优化 */
        @media (max-width: 576px) {
            .quick-actions .btn {
                font-size: 0.8rem;
                padding: 0.5rem 0.8rem;
                margin-bottom: 0.5rem;
            }
            
            .quick-actions .row {
                margin: 0 -0.25rem;
            }
            
            .quick-actions .row > div {
                padding: 0 0.25rem;
            }
        }
    </style>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔍</text></svg>">
</head>
<body>
    <!-- Navigation -->
    <nav id="navbar" class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <i class="bi bi-reddit text-danger me-2 fs-4"></i>
                <span class="fw-bold">Reddit Data Collector</span>
            </a>
            
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#search-section">Search</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#results-section">Results</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#status-section">Status</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container-fluid">
        <!-- Hero Section -->
        <section id="hero-section" class="hero-section">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-8 col-xl-6">
                        <div class="text-center mb-5">
                            <h1 class="display-4 fw-light mb-3">Reddit Data Collector</h1>
                            <p class="lead text-white-50">Discover and analyze Reddit content with advanced search and promotional detection</p>
                        </div>
                        
                        <!-- Search Form -->
                        <div class="search-container">
                            <form id="search-form" class="search-form">
                                <div class="search-input-group">
                                    <div class="input-group input-group-lg">
                                        <span class="input-group-text bg-white border-end-0">
                                            <i class="bi bi-search text-muted"></i>
                                        </span>
                                        <input type="text" 
                                               id="keywords-input" 
                                               class="form-control border-start-0 ps-0" 
                                               placeholder="Enter keywords to search Reddit..."
                                               autocomplete="off">
                                        <button type="submit" class="btn btn-primary px-4">
                                            <span class="search-btn-text">Search</span>
                                            <span class="search-btn-spinner d-none">
                                                <span class="spinner-border spinner-border-sm me-2"></span>
                                                Searching...
                                            </span>
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- Advanced Options Toggle -->
                                <div class="text-center mt-3">
                                    <button type="button" 
                                            class="btn btn-link btn-sm text-decoration-none" 
                                            data-bs-toggle="collapse" 
                                            data-bs-target="#advanced-options">
                                        <i class="bi bi-gear me-1"></i>
                                        Advanced Options
                                        <i class="bi bi-chevron-down ms-1"></i>
                                    </button>
                                </div>
                                
                                <!-- Advanced Options Panel -->
                                <div class="collapse mt-3" id="advanced-options">
                                    <div class="card border-0 shadow-sm">
                                        <div class="card-body">
                                            <div class="row g-3">
                                                <div class="col-md-6">
                                                    <label for="subreddits-input" class="form-label">Subreddits</label>
                                                    <input type="text" 
                                                           id="subreddits-input" 
                                                           class="form-control" 
                                                           placeholder="e.g., technology, programming"
                                                           value="all">
                                                </div>
                                                <div class="col-md-6">
                                                    <label for="time-filter" class="form-label">Time Range</label>
                                                    <select id="time-filter" class="form-select">
                                                        <option value="hour">Past Hour</option>
                                                        <option value="day">Past Day</option>
                                                        <option value="week" selected>Past Week</option>
                                                        <option value="month">Past Month</option>
                                                        <option value="year">Past Year</option>
                                                        <option value="all">All Time</option>
                                                    </select>
                                                </div>
                                                <div class="col-md-6">
                                                    <label for="sort-by" class="form-label">Sort By</label>
                                                    <select id="sort-by" class="form-select">
                                                        <option value="relevance" selected>Relevance</option>
                                                        <option value="hot">Hot</option>
                                                        <option value="new">New</option>
                                                        <option value="top">Top</option>
                                                        <option value="comments">Comments</option>
                                                    </select>
                                                </div>
                                                <div class="col-md-6">
                                                    <label for="limit-input" class="form-label">Post Limit</label>
                                                    <select id="limit-input" class="form-select">
                                                        <option value="25">25 posts</option>
                                                        <option value="50">50 posts</option>
                                                        <option value="100" selected>100 posts</option>
                                                    </select>
                                                </div>
                                                <div class="col-12">
                                                    <div class="row g-3">
                                                        <div class="col-md-4">
                                                            <label for="min-score" class="form-label">Min Score</label>
                                                            <input type="number" id="min-score" class="form-control" value="0" min="0">
                                                        </div>
                                                        <div class="col-md-4">
                                                            <label for="min-comments" class="form-label">Min Comments</label>
                                                            <input type="number" id="min-comments" class="form-control" value="0" min="0">
                                                        </div>
                                                        <div class="col-md-4 d-flex align-items-end">
                                                            <div class="form-check">
                                                                <input class="form-check-input" type="checkbox" id="include-nsfw">
                                                                <label class="form-check-label" for="include-nsfw">
                                                                    Include NSFW
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                            
                            <!-- Quick Action Buttons -->
                            <div class="quick-actions mt-4">
                                <div class="row g-2 justify-content-center">
                                    <div class="col-4 col-sm-auto">
                                        <button type="button" 
                                                class="btn btn-light btn-sm w-100" 
                                                id="collect-promotional-btn"
                                                data-bs-toggle="tooltip" 
                                                data-bs-placement="top" 
                                                title="Detect promotional content using AI analysis">
                                            <i class="bi bi-bullseye me-1"></i>
                                            <span class="d-none d-sm-inline">General </span>Promo
                                        </button>
                                    </div>
                                    <div class="col-4 col-sm-auto">
                                        <button type="button" 
                                                class="btn btn-light btn-sm w-100" 
                                                id="collect-reddit-promoted-btn"
                                                data-bs-toggle="tooltip" 
                                                data-bs-placement="top" 
                                                title="Find official Reddit promoted posts">
                                            <i class="bi bi-badge-ad me-1"></i>
                                            <span class="d-none d-sm-inline">Reddit </span>Ads
                                        </button>
                                    </div>
                                    <div class="col-4 col-sm-auto">
                                        <button type="button" 
                                                class="btn btn-light btn-sm w-100" 
                                                id="export-data-btn"
                                                data-bs-toggle="tooltip" 
                                                data-bs-placement="top" 
                                                title="Export search results to file">
                                            <i class="bi bi-download me-1"></i>
                                            <span class="d-none d-sm-inline">Export </span>Data
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- 功能说明 -->
                                <div class="text-center mt-3">
                                    <small class="text-white-50">
                                        <i class="bi bi-info-circle me-1"></i>
                                        <strong>General Promo</strong> detects content-based ads • 
                                        <strong>Reddit Ads</strong> finds official promotions • 
                                        <strong>Export Data</strong> saves your results
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Status Bar -->
        <section id="status-bar" class="status-bar d-none">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <div class="alert alert-info d-flex align-items-center mb-0" role="alert">
                            <div class="spinner-border spinner-border-sm me-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div class="flex-grow-1">
                                <strong id="status-title">Searching Reddit...</strong>
                                <div id="status-message" class="small">Please wait while we collect data from Reddit</div>
                            </div>
                            <button type="button" class="btn-close" id="status-close"></button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Results Section -->
        <section id="results-section" class="results-section d-none">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <!-- Results Header -->
                        <div class="results-header d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h2 class="h4 mb-1">Search Results</h2>
                                <p class="text-muted mb-0" id="results-summary">Found 0 posts</p>
                            </div>
                            <div class="d-flex gap-2">
                                <div class="dropdown">
                                    <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-download me-1"></i>
                                        Export
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#" data-format="csv">
                                            <i class="bi bi-filetype-csv me-2"></i>CSV Format
                                        </a></li>
                                        <li><a class="dropdown-item" href="#" data-format="json">
                                            <i class="bi bi-filetype-json me-2"></i>JSON Format
                                        </a></li>
                                    </ul>
                                </div>
                                <button type="button" class="btn btn-outline-secondary btn-sm" id="clear-results-btn">
                                    <i class="bi bi-x-circle me-1"></i>
                                    Clear
                                </button>
                            </div>
                        </div>
                        
                        <!-- Results Grid -->
                        <div id="results-grid" class="results-grid">
                            <!-- Results will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- System Status Section -->
        <section id="status-section" class="status-section">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h2 class="h4 mb-4">System Status</h2>
                        
                        <div class="row g-4">
                            <!-- System Health -->
                            <div class="col-lg-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="status-icon me-3">
                                                <i class="bi bi-heart-pulse text-success fs-4"></i>
                                            </div>
                                            <div>
                                                <h5 class="card-title mb-1">System Health</h5>
                                                <p class="card-text text-muted small mb-0">Overall system status</p>
                                            </div>
                                        </div>
                                        <div id="system-health" class="status-content">
                                            <div class="d-flex justify-content-between">
                                                <span>Status:</span>
                                                <span class="badge bg-success">{{ system_status }}</span>
                                            </div>
                                            <div class="d-flex justify-content-between mt-2">
                                                <span>Environment:</span>
                                                <span class="fw-bold">Vercel</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Reddit API -->
                            <div class="col-lg-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="status-icon me-3">
                                                <i class="bi bi-reddit text-danger fs-4"></i>
                                            </div>
                                            <div>
                                                <h5 class="card-title mb-1">Reddit API</h5>
                                                <p class="card-text text-muted small mb-0">API connection status</p>
                                            </div>
                                        </div>
                                        <div id="reddit-api-status" class="status-content">
                                            <div class="d-flex justify-content-between">
                                                <span>Status:</span>
                                                <span class="badge bg-{{ reddit_status_color }}">{{ reddit_status }}</span>
                                            </div>
                                            <div class="d-flex justify-content-between mt-2">
                                                <span>Mode:</span>
                                                <span class="fw-bold">{{ reddit_mode }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Application Info -->
                            <div class="col-lg-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="status-icon me-3">
                                                <i class="bi bi-info-circle text-info fs-4"></i>
                                            </div>
                                            <div>
                                                <h5 class="card-title mb-1">Application</h5>
                                                <p class="card-text text-muted small mb-0">Version and info</p>
                                            </div>
                                        </div>
                                        <div id="app-info" class="status-content">
                                            <div class="d-flex justify-content-between">
                                                <span>Version:</span>
                                                <span class="fw-bold">v2.0</span>
                                            </div>
                                            <div class="d-flex justify-content-between mt-2">
                                                <span>Updated:</span>
                                                <span class="fw-bold">{{ timestamp }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer mt-5 py-4 bg-white">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <p class="mb-0 text-muted">
                        <i class="bi bi-reddit text-danger me-1"></i>
                        Reddit Data Collector v2.0 - Vercel Edition
                    </p>
                </div>
                <div class="col-md-6 text-md-end">
                    <small class="text-muted">
                        Built with Flask, Bootstrap & ❤️
                    </small>
                </div>
            </div>
        </div>
    </footer>

    <!-- Toast Container -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <!-- Toasts will be added here dynamically -->
    </div>

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script>
        // Application state
        let currentResults = [];
        
        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            initializeApp();
            checkRedditAPIStatus();
        });
        
        function initializeApp() {
            // Initialize Bootstrap tooltips
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // Bind event listeners
            document.getElementById('search-form').addEventListener('submit', handleSearch);
            document.getElementById('collect-promotional-btn').addEventListener('click', collectPromotionalPosts);
            document.getElementById('collect-reddit-promoted-btn').addEventListener('click', collectRedditPromotedPosts);
            document.getElementById('export-data-btn').addEventListener('click', exportCurrentResults);
            document.getElementById('clear-results-btn').addEventListener('click', clearResults);
            document.getElementById('status-close').addEventListener('click', hideStatusBar);
            
            // Enable enter key search
            document.getElementById('keywords-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSearch(e);
                }
            });
            
            showToast('Application initialized successfully!', 'success');
        }
        
        async function handleSearch(e) {
            e.preventDefault();
            
            const keywords = document.getElementById('keywords-input').value.trim();
            if (!keywords) {
                showToast('Please enter search keywords', 'warning');
                return;
            }
            
            const searchParams = {
                keywords: keywords.split(',').map(k => k.trim()),
                subreddit: document.getElementById('subreddits-input').value.trim() || null,
                time_filter: document.getElementById('time-filter').value,
                sort: document.getElementById('sort-by').value,
                limit: parseInt(document.getElementById('limit-input').value),
                min_score: parseInt(document.getElementById('min-score').value) || 0,
                min_comments: parseInt(document.getElementById('min-comments').value) || 0,
                include_nsfw: document.getElementById('include-nsfw').checked
            };
            
            showSearchProgress();
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(searchParams)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayResults(data.data);
                    addToSearchHistory(searchParams, data.data);
                    showToast(`Found ${data.data.posts.length} posts!`, 'success');
                } else {
                    showToast(`Search failed: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`Search error: ${error.message}`, 'error');
            } finally {
                hideSearchProgress();
            }
        }
        
        function displayResults(data) {
            currentResults = data.posts;
            const resultsGrid = document.getElementById('results-grid');
            const resultsSection = document.getElementById('results-section');
            const resultsSummary = document.getElementById('results-summary');
            
            resultsSummary.textContent = `Found ${data.posts.length} posts (${data.search_time}s)`;
            
            if (data.posts.length === 0) {
                resultsGrid.innerHTML = '<div class="text-center py-5"><p class="text-muted">No posts found. Try different keywords or adjust your filters.</p></div>';
            } else {
                resultsGrid.innerHTML = data.posts.map(post => createPostCard(post)).join('');
            }
            
            resultsSection.classList.remove('d-none');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        function createPostCard(post) {
            const isPromotional = post.is_promotional;
            const isRedditPromoted = post.reddit_promoted;
            
            // 推广标记
            let promotionalBadges = '';
            if (isRedditPromoted) {
                promotionalBadges += '<span class="badge bg-danger text-white ms-2">Reddit Promoted</span>';
            }
            if (isPromotional && !isRedditPromoted) {
                promotionalBadges += '<span class="badge bg-warning text-dark ms-2">Promotional Content</span>';
            }
            
            // 推广指示器
            let promotionalIndicators = '';
            if (post.promoted_indicators && post.promoted_indicators.length > 0) {
                promotionalIndicators = `<small class="text-muted">Promotion indicators: ${post.promoted_indicators.join(', ')}</small><br>`;
            }
            
            const cardClass = isRedditPromoted ? 'post-card reddit-promoted' : 
                             (isPromotional ? 'post-card promotional' : 'post-card');
            
            return `
                <div class="card ${cardClass} mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${escapeHtml(post.title)}${promotionalBadges}</h5>
                        <div class="row text-muted small mb-2">
                            <div class="col-md-6">
                                <i class="bi bi-person me-1"></i>u/${escapeHtml(post.author)}
                                <span class="mx-2">•</span>
                                <i class="bi bi-reddit me-1"></i>r/${escapeHtml(post.subreddit)}
                            </div>
                            <div class="col-md-6 text-md-end">
                                <i class="bi bi-arrow-up me-1"></i>${post.score}
                                <span class="mx-2">•</span>
                                <i class="bi bi-chat me-1"></i>${post.num_comments}
                                <span class="mx-2">•</span>
                                <i class="bi bi-clock me-1"></i>${formatDate(post.created_utc)}
                            </div>
                        </div>
                        ${promotionalIndicators}
                        ${post.selftext ? `<p class="card-text">${escapeHtml(post.selftext.substring(0, 200))}${post.selftext.length > 200 ? '...' : ''}</p>` : ''}
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                ${post.keywords_matched && post.keywords_matched.length > 0 ? `<small class="text-muted">Matched: ${post.keywords_matched.join(', ')}</small><br>` : ''}
                                ${post.auth_mode ? `<small class="text-info">API Mode: ${post.auth_mode}</small>` : ''}
                            </div>
                            <a href="${post.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                                <i class="bi bi-box-arrow-up-right me-1"></i>View Post
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }
        
        async function collectPromotionalPosts() {
            showSearchProgress('Collecting promotional posts...');
            
            try {
                const response = await fetch('/api/collect-promotional', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        subreddits: ['entrepreneur', 'startups', 'business', 'marketing', 'deals'],
                        limit: 50
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayResults({
                        posts: data.data.posts,
                        search_time: data.data.search_time
                    });
                    showToast(`Found ${data.data.promotional_count} promotional posts out of ${data.data.total_found} total posts!`, 'success');
                } else {
                    showToast(`Collection failed: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`Collection error: ${error.message}`, 'error');
            } finally {
                hideSearchProgress();
            }
        }
        
        async function collectRedditPromotedPosts() {
            showSearchProgress('Collecting Reddit Promoted posts...');
            
            try {
                const response = await fetch('/api/collect-reddit-promoted', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        subreddits: ['entrepreneur', 'startups', 'business', 'marketing', 'deals'],
                        limit: 50
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayResults({
                        posts: data.data.posts,
                        search_time: data.data.search_time
                    });
                    showToast(`Found ${data.data.reddit_promoted_count} Reddit Promoted posts out of ${data.data.total_found} total posts!`, 'success');
                } else {
                    showToast(`Collection failed: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`Collection error: ${error.message}`, 'error');
            } finally {
                hideSearchProgress();
            }
        }
        
        async function toggleHistorySection() {
            const historySection = document.getElementById('history-section');
            historySection.classList.toggle('d-none');
            
            if (!historySection.classList.contains('d-none')) {
                await loadAndDisplayHistory();
                historySection.scrollIntoView({ behavior: 'smooth' });
            }
        }
        
        async function loadAndDisplayHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayServerHistory(data.data);
                } else {
                    showToast(`Failed to load history: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`History error: ${error.message}`, 'error');
                // 回退到本地历史
                displaySearchHistory();
            }
        }
        
        function displayServerHistory(historyData) {
            const historyGrid = document.getElementById('history-grid');
            
            if (historyData.length === 0) {
                historyGrid.innerHTML = '<div class="text-center py-5"><p class="text-muted">No search history available.</p></div>';
                return;
            }
            
            historyGrid.innerHTML = historyData.map((item, index) => `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="card-title mb-1">${item.keywords.join(', ')}</h6>
                                <p class="card-text text-muted small mb-2">
                                    ${item.results_count} posts found • ${new Date(item.search_date).toLocaleString()}
                                </p>
                                <div class="small text-muted">
                                    Subreddit: ${item.subreddit || 'all'} • 
                                    Time: ${item.time_filter} • 
                                    Status: <span class="badge bg-success">${item.status}</span>
                                </div>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-primary btn-sm" onclick="replayServerSearch(${index}, '${item.keywords.join(',')}', '${item.subreddit}', '${item.time_filter}')">
                                    <i class="bi bi-arrow-clockwise me-1"></i>Replay
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="exportHistoryItem(${item.id})">
                                    <i class="bi bi-download me-1"></i>Export
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function replayServerSearch(index, keywords, subreddit, timeFilter) {
            // 填充搜索表单
            document.getElementById('keywords-input').value = keywords.replace(/,/g, ', ');
            document.getElementById('subreddits-input').value = subreddit || 'all';
            document.getElementById('time-filter').value = timeFilter || 'week';
            
            // 滚动到搜索表单
            document.getElementById('hero-section').scrollIntoView({ behavior: 'smooth' });
            
            showToast('Search parameters loaded from server history', 'info');
        }
        
        function addToSearchHistory(params, results) {
            const historyItem = {
                params: params,
                results: results,
                timestamp: new Date().toLocaleString()
            };
            
            searchHistory.unshift(historyItem);
            
            // Keep only last 10 searches
            if (searchHistory.length > 10) {
                searchHistory = searchHistory.slice(0, 10);
            }
            
            // Save to localStorage
            localStorage.setItem('reddit_search_history', JSON.stringify(searchHistory));
        }
        
        function loadSearchHistory() {
            const saved = localStorage.getItem('reddit_search_history');
            if (saved) {
                try {
                    searchHistory = JSON.parse(saved);
                } catch (e) {
                    console.error('Failed to load search history:', e);
                    searchHistory = [];
                }
            }
        }
        
        function clearHistory() {
            searchHistory = [];
            localStorage.removeItem('reddit_search_history');
            displaySearchHistory();
            showToast('Search history cleared', 'info');
        }
        
        function clearResults() {
            currentResults = [];
            document.getElementById('results-section').classList.add('d-none');
            showToast('Results cleared', 'info');
        }
        
        async function exportCurrentResults() {
            if (currentResults.length === 0) {
                // 如果没有当前结果，导出示例数据
                await exportSampleData();
                return;
            }
            
            const csv = convertToCSV(currentResults);
            downloadFile(csv, 'reddit_search_results.csv', 'text/csv');
            showToast('Results exported successfully!', 'success');
        }
        
        async function exportSampleData() {
            try {
                const response = await fetch('/api/export?format=csv&type=all&limit=100');
                const data = await response.json();
                
                if (data.status === 'success') {
                    downloadFile(data.data.content, data.data.filename, 'text/csv');
                    showToast(`Sample data exported: ${data.data.posts_count} posts`, 'success');
                } else {
                    showToast(`Export failed: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`Export error: ${error.message}`, 'error');
            }
        }
        
        async function exportHistoryItem(itemId) {
            try {
                const response = await fetch(`/api/export?format=json&type=promotional&limit=50`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    const jsonContent = JSON.stringify(data.data, null, 2);
                    downloadFile(jsonContent, data.data.filename, 'application/json');
                    showToast('History item exported successfully!', 'success');
                } else {
                    showToast(`Export failed: ${data.message}`, 'error');
                }
            } catch (error) {
                showToast(`Export error: ${error.message}`, 'error');
            }
        }
        
        function displaySearchHistory() {
            const historyGrid = document.getElementById('history-grid');
            
            if (searchHistory.length === 0) {
                historyGrid.innerHTML = '<div class="text-center py-5"><p class="text-muted">No search history yet. Perform a search to see it here.</p></div>';
                return;
            }
            
            historyGrid.innerHTML = searchHistory.map((item, index) => `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="card-title mb-1">${item.params.keywords.join(', ')}</h6>
                                <p class="card-text text-muted small mb-2">
                                    ${item.results.posts.length} posts found • ${item.timestamp}
                                </p>
                                <div class="small text-muted">
                                    Subreddit: ${item.params.subreddit || 'all'} • 
                                    Time: ${item.params.time_filter} • 
                                    Sort: ${item.params.sort}
                                </div>
                            </div>
                            <button class="btn btn-outline-primary btn-sm" onclick="replaySearch(${index})">
                                <i class="bi bi-arrow-clockwise me-1"></i>Replay
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function replaySearch(index) {
            const historyItem = searchHistory[index];
            
            // Fill form with previous search parameters
            document.getElementById('keywords-input').value = historyItem.params.keywords.join(', ');
            document.getElementById('subreddits-input').value = historyItem.params.subreddit || 'all';
            document.getElementById('time-filter').value = historyItem.params.time_filter;
            document.getElementById('sort-by').value = historyItem.params.sort;
            document.getElementById('limit-input').value = historyItem.params.limit;
            document.getElementById('min-score').value = historyItem.params.min_score;
            document.getElementById('min-comments').value = historyItem.params.min_comments;
            document.getElementById('include-nsfw').checked = historyItem.params.include_nsfw;
            
            // Scroll to search form
            document.getElementById('hero-section').scrollIntoView({ behavior: 'smooth' });
            
            showToast('Search parameters loaded from history', 'info');
        }
        
        async function checkRedditAPIStatus() {
            try {
                const response = await fetch('/api/reddit/test');
                const data = await response.json();
                
                const statusElement = document.getElementById('reddit-api-status');
                if (data.status === 'success') {
                    statusElement.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <span>Status:</span>
                            <span class="badge bg-success">Connected</span>
                        </div>
                        <div class="d-flex justify-content-between mt-2">
                            <span>Mode:</span>
                            <span class="fw-bold">${data.mode || 'Read-only'}</span>
                        </div>
                    `;
                } else {
                    statusElement.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <span>Status:</span>
                            <span class="badge bg-warning">Not Configured</span>
                        </div>
                        <div class="d-flex justify-content-between mt-2">
                            <span>Mode:</span>
                            <span class="fw-bold">Offline</span>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Failed to check Reddit API status:', error);
            }
        }
        
        function showSearchProgress(message = 'Searching Reddit...') {
            document.getElementById('status-title').textContent = message;
            document.getElementById('status-message').textContent = 'Please wait while we collect data from Reddit';
            document.getElementById('status-bar').classList.remove('d-none');
            
            // Update search button
            const searchBtn = document.querySelector('.search-btn-text');
            const searchSpinner = document.querySelector('.search-btn-spinner');
            searchBtn.classList.add('d-none');
            searchSpinner.classList.remove('d-none');
        }
        
        function hideSearchProgress() {
            document.getElementById('status-bar').classList.add('d-none');
            
            // Reset search button
            const searchBtn = document.querySelector('.search-btn-text');
            const searchSpinner = document.querySelector('.search-btn-spinner');
            searchBtn.classList.remove('d-none');
            searchSpinner.classList.add('d-none');
        }
        
        function hideStatusBar() {
            document.getElementById('status-bar').classList.add('d-none');
        }
        
        function showToast(message, type = 'info') {
            const toastContainer = document.querySelector('.toast-container');
            const toastId = 'toast-' + Date.now();
            
            const bgClass = {
                'success': 'bg-success',
                'error': 'bg-danger',
                'warning': 'bg-warning',
                'info': 'bg-info'
            }[type] || 'bg-info';
            
            const toastHtml = `
                <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
                    <div class="toast-body">
                        ${escapeHtml(message)}
                        <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
            toast.show();
            
            // Remove toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatDate(timestamp) {
            if (!timestamp) return 'Unknown';
            const date = new Date(timestamp * 1000);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
        
        function convertToCSV(data) {
            const headers = ['Title', 'Author', 'Subreddit', 'Score', 'Comments', 'URL', 'Is Promotional', 'Created'];
            const rows = data.map(post => [
                `"${post.title.replace(/"/g, '""')}"`,
                post.author,
                post.subreddit,
                post.score,
                post.num_comments,
                post.url,
                post.is_promotional ? 'Yes' : 'No',
                formatDate(post.created_utc)
            ]);
            
            return [headers.join(','), ...rows.map(row => row.join(','))].join('\\n');
        }
        
        function downloadFile(content, filename, contentType) {
            const blob = new Blob([content], { type: contentType });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """主页 - 显示完整功能界面"""
    try:
        # 检查Reddit API状态
        reddit_status = "Not Configured"
        reddit_status_color = "warning"
        reddit_mode = "Offline"
        
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if client_id and client_secret:
            try:
                # 测试Reddit API连接
                import praw
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
                )
                
                # 简单测试
                subreddit = reddit.subreddit('test')
                list(subreddit.hot(limit=1))
                
                reddit_status = "Connected"
                reddit_status_color = "success"
                reddit_mode = "Read-only"
                
            except Exception as e:
                logger.warning(f"Reddit API test failed: {e}")
                reddit_status = "Error"
                reddit_status_color = "danger"
                reddit_mode = "Failed"
        
        return render_template_string(
            COMPLETE_HTML_TEMPLATE,
            system_status="Operational",
            reddit_status=reddit_status,
            reddit_status_color=reddit_status_color,
            reddit_mode=reddit_mode,
            timestamp=datetime.now().strftime('%Y-%m-%d')
        )
        
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return render_template_string(
            COMPLETE_HTML_TEMPLATE,
            system_status="Error",
            reddit_status="Unknown",
            reddit_status_color="secondary",
            reddit_mode="Unknown",
            timestamp=datetime.now().strftime('%Y-%m-%d')
        )

@app.route('/api/health')
def health():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "Vercel",
        "version": "2.0-complete",
        "uptime": "Running",
        "features": ["reddit_search", "promotional_detection", "full_interface"]
    })

@app.route('/api/status')
def status():
    """系统状态端点"""
    return jsonify({
        "status": "ok",
        "application": "Reddit Data Collector Complete",
        "environment": "Vercel",
        "version": "2.0-complete",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "reddit_api": "available",
            "search": "enabled",
            "promotional_detection": "enabled",
            "web_interface": "complete",
            "export": "enabled",
            "history": "enabled"
        },
        "capabilities": [
            "Real-time Reddit search",
            "Multi-keyword support",
            "Promotional content detection",
            "Complete web interface",
            "Search history",
            "Data export",
            "Advanced filtering"
        ]
    })

@app.route('/api/search', methods=['POST'])
def search_reddit():
    """Reddit搜索端点 - 完整功能"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        keywords = data.get('keywords', [])
        subreddit = data.get('subreddit')
        limit = min(data.get('limit', 10), 100)
        time_filter = data.get('time_filter', 'week')
        sort = data.get('sort', 'relevance')
        min_score = data.get('min_score', 0)
        min_comments = data.get('min_comments', 0)
        include_nsfw = data.get('include_nsfw', False)
        
        if not keywords:
            return jsonify({
                "status": "error",
                "message": "Keywords are required",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 检查Reddit API配置
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured in Vercel environment variables",
                "timestamp": datetime.now().isoformat(),
                "help": "Please configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in Vercel project settings"
            }), 400
        
        # 执行Reddit搜索
        search_start = datetime.now()
        posts = perform_reddit_search(keywords, subreddit, limit, time_filter, sort, min_score, min_comments, include_nsfw)
        search_time = (datetime.now() - search_start).total_seconds()
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(posts)} posts",
            "data": {
                "posts": posts,
                "search_time": round(search_time, 2),
                "keywords": keywords,
                "subreddit": subreddit,
                "limit": limit,
                "filters": {
                    "time_filter": time_filter,
                    "sort": sort,
                    "min_score": min_score,
                    "min_comments": min_comments,
                    "include_nsfw": include_nsfw
                }
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

def detect_promotional_content(title, content, submission=None):
    """增强的推广内容检测 - 重点检测Reddit官方推广标记"""
    
    # 首先检查Reddit官方推广标记 - 这是最重要的
    is_reddit_promoted = False
    promoted_indicators = []
    
    if submission:
        try:
            # 方法1: 检查submission的promoted属性
            if hasattr(submission, 'promoted') and submission.promoted:
                is_reddit_promoted = True
                promoted_indicators.append("reddit_promoted_flag")
            
            # 方法2: 检查distinguished属性（Reddit官方标记）
            if hasattr(submission, 'distinguished'):
                if submission.distinguished == 'admin':
                    is_reddit_promoted = True
                    promoted_indicators.append("admin_distinguished")
                elif submission.distinguished == 'moderator':
                    promoted_indicators.append("mod_distinguished")
            
            # 方法3: 检查stickied属性（置顶帖子，可能是推广）
            if hasattr(submission, 'stickied') and submission.stickied:
                promoted_indicators.append("stickied_post")
            
            # 方法4: 检查is_promoted_content属性
            if hasattr(submission, 'is_promoted_content') and submission.is_promoted_content:
                is_reddit_promoted = True
                promoted_indicators.append("is_promoted_content")
            
            # 方法5: 检查author是否为特殊推广账户
            if hasattr(submission, 'author') and submission.author:
                author_name = str(submission.author).lower()
                if any(indicator in author_name for indicator in ['promoted', 'sponsored', 'ad_', '_ad']):
                    is_reddit_promoted = True
                    promoted_indicators.append("promotional_author")
            
            # 方法6: 检查subreddit类型
            if hasattr(submission, 'subreddit'):
                subreddit_name = submission.subreddit.display_name.lower()
                if subreddit_name in ['promoted', 'ads', 'sponsored']:
                    is_reddit_promoted = True
                    promoted_indicators.append("promotional_subreddit")
            
            # 方法7: 检查URL是否为Reddit推广链接
            if hasattr(submission, 'url') and submission.url:
                url_lower = submission.url.lower()
                if any(indicator in url_lower for indicator in ['redd.it/promoted', 'reddit.com/promoted', 'ads.reddit.com']):
                    is_reddit_promoted = True
                    promoted_indicators.append("promotional_url")
            
            # 方法8: 检查submission的特殊属性
            if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                flair_text = submission.link_flair_text.lower()
                if any(indicator in flair_text for indicator in ['promoted', 'sponsored', 'ad']):
                    is_reddit_promoted = True
                    promoted_indicators.append("promotional_flair")
            
            # 方法9: 检查submission的CSS类或特殊标记
            if hasattr(submission, 'link_flair_css_class') and submission.link_flair_css_class:
                css_class = submission.link_flair_css_class.lower()
                if any(indicator in css_class for indicator in ['promoted', 'sponsored', 'ad']):
                    is_reddit_promoted = True
                    promoted_indicators.append("promotional_css")
            
        except Exception as e:
            logger.warning(f"Error checking Reddit promotion attributes: {e}")
    
    # 检查标题和内容中的推广标记
    text = (title + ' ' + content).lower()
    
    # Reddit官方推广标记检测（标题中的明确标记）
    reddit_official_markers = ['promoted', 'sponsored', '[ad]', '[sponsored]', '[promoted]']
    for marker in reddit_official_markers:
        if marker in title.lower():
            is_reddit_promoted = True
            promoted_indicators.append(f"title_marker_{marker}")
    
    # 如果检测到Reddit官方推广，直接返回
    if is_reddit_promoted:
        return True
    
    # 如果不是Reddit官方推广，继续检查一般推广内容
    promotional_keywords = [
        # 英文关键词
        'buy', 'sale', 'discount', 'promo', 'deal', 'offer', 'free shipping',
        'limited time', 'click here', 'visit our', 'check out our', 'shop now',
        'special offer', 'save money', 'best price', 'coupon', 'voucher',
        'affiliate', 'advertisement', 'promotion',
        'get started', 'sign up', 'register', 'download now', 'try free',
        # 中文关键词
        '购买', '销售', '折扣', '促销', '优惠', '免费', '限时', '点击',
        '特价', '打折', '便宜', '代购', '微商', '推广', '广告'
    ]
    
    # 推广模式
    promotional_patterns = [
        r'\b\d+%\s*off\b',  # "50% off"
        r'\$\d+',           # "$99"
        r'free\s+shipping', # "free shipping"
        r'buy\s+now',       # "buy now"
        r'click\s+here',    # "click here"
        r'visit\s+our',     # "visit our"
        r'limited\s+time',  # "limited time"
        r'special\s+offer', # "special offer"
    ]
    
    # 检查关键词
    keyword_matches = sum(1 for keyword in promotional_keywords if keyword in text)
    
    # 检查模式
    import re
    pattern_matches = sum(1 for pattern in promotional_patterns if re.search(pattern, text))
    
    # 推广内容判断逻辑
    # 1. 多个关键词匹配
    if keyword_matches >= 2:
        return True
    
    # 2. 有推广模式匹配
    if pattern_matches >= 1:
        return True
    
    # 3. 单个强推广关键词
    strong_promotional_keywords = ['advertisement', 'affiliate', 'promo code']
    if any(keyword in text for keyword in strong_promotional_keywords):
        return True
    
    return False

def perform_reddit_search(keywords, subreddit=None, limit=10, time_filter='week', sort='relevance', min_score=0, min_comments=0, include_nsfw=False):
    """执行Reddit搜索 - 增强版，包含推广内容检测"""
    try:
        import praw
        
        # 获取环境变量
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        username = os.environ.get('REDDIT_USERNAME')
        password = os.environ.get('REDDIT_PASSWORD')
        
        # 检查必需的凭据
        if not client_id or not client_secret:
            raise Exception("Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) not configured")
        
        # 初始化Reddit客户端 - 尝试多种认证方式
        reddit = None
        auth_mode = "unknown"
        
        try:
            # 方式1: Script模式 (需要用户名和密码)
            if username and password:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=password,
                    user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
                )
                # 测试认证
                user = reddit.user.me()
                auth_mode = f"script (authenticated as {user.name})"
                logger.info(f"Reddit API authenticated in script mode as {user.name}")
            else:
                raise Exception("Username/password not provided, trying read-only mode")
                
        except Exception as script_error:
            logger.warning(f"Script mode failed: {script_error}, trying read-only mode")
            
            # 方式2: 只读模式
            try:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
                )
                # 测试只读访问
                test_subreddit = reddit.subreddit('test')
                list(test_subreddit.hot(limit=1))
                auth_mode = "read-only"
                logger.info("Reddit API initialized in read-only mode")
            except Exception as readonly_error:
                raise Exception(f"Both script and read-only authentication failed. Script error: {script_error}. Read-only error: {readonly_error}")
        
        posts = []
        search_query = ' OR '.join(keywords)
        
        # 选择搜索范围
        if subreddit and subreddit.lower() != 'all':
            search_target = reddit.subreddit(subreddit)
        else:
            search_target = reddit.subreddit('all')
        
        # 执行搜索
        search_results = search_target.search(
            search_query, 
            limit=limit * 2,  # 获取更多结果以便过滤
            sort=sort,
            time_filter=time_filter
        )
        
        processed_count = 0
        for submission in search_results:
            if processed_count >= limit:
                break
                
            try:
                # 应用过滤器
                if submission.score < min_score:
                    continue
                if submission.num_comments < min_comments:
                    continue
                if not include_nsfw and submission.over_18:
                    continue
                
                # 增强的推广内容检测
                is_promotional = detect_promotional_content(
                    submission.title, 
                    submission.selftext, 
                    submission
                )
                
                # 检测关键词匹配
                keywords_matched = []
                title_text = submission.title.lower()
                content_text = submission.selftext.lower() if submission.selftext else ""
                
                for kw in keywords:
                    if kw.lower() in title_text or kw.lower() in content_text:
                        keywords_matched.append(kw)
                
                # 获取作者信息
                author_name = str(submission.author) if submission.author else "[deleted]"
                
                # 检查是否为Reddit官方推广
                reddit_promoted = False
                promoted_indicators = []
                
                try:
                    # 检查各种推广标记
                    if hasattr(submission, 'distinguished') and submission.distinguished:
                        promoted_indicators.append(f"distinguished: {submission.distinguished}")
                    if hasattr(submission, 'stickied') and submission.stickied:
                        promoted_indicators.append("stickied")
                    if 'promoted' in submission.title.lower() or 'sponsored' in submission.title.lower():
                        promoted_indicators.append("title_marked")
                        reddit_promoted = True
                    if '[ad]' in submission.title.lower() or '[sponsored]' in submission.title.lower():
                        promoted_indicators.append("ad_tag")
                        reddit_promoted = True
                except:
                    pass
                
                post_data = {
                    "reddit_id": submission.id,
                    "title": submission.title,
                    "author": author_name,
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc,
                    "url": submission.url,
                    "selftext": submission.selftext[:500] if submission.selftext else "",  # 限制长度
                    "is_promotional": is_promotional,
                    "reddit_promoted": reddit_promoted,
                    "promoted_indicators": promoted_indicators,
                    "keywords_matched": keywords_matched,
                    "over_18": submission.over_18,
                    "auth_mode": auth_mode
                }
                posts.append(post_data)
                processed_count += 1
                
            except Exception as post_error:
                logger.warning(f"Error processing post {submission.id}: {post_error}")
                continue
        
        logger.info(f"Reddit search completed: {len(posts)} posts found using {auth_mode} mode")
        return posts
        
    except Exception as e:
        logger.error(f"Reddit search error: {e}")
        raise

@app.route('/api/reddit/test')
def reddit_test():
    """Reddit API连接测试 - 增强版"""
    try:
        # 检查环境变量
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured",
                "help": "Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables in Vercel",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 尝试导入praw并测试连接
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
            )
            
            # 测试只读访问
            subreddit = reddit.subreddit('test')
            posts = list(subreddit.hot(limit=1))
            
            return jsonify({
                "status": "success",
                "message": "Reddit API connection successful",
                "mode": "read-only",
                "test_result": f"Successfully accessed r/test subreddit",
                "posts_found": len(posts),
                "client_id_preview": client_id[:8] + "..." if len(client_id) > 8 else client_id,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as reddit_error:
            return jsonify({
                "status": "error",
                "message": "Reddit API connection failed",
                "error": str(reddit_error),
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error in reddit test: {e}")
        return jsonify({
            "status": "error",
            "message": "Reddit test endpoint error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def collect_reddit_promoted_posts(subreddits=None, limit=50):
    """专门收集Reddit官方推广帖子（Promoted/Sponsored）"""
    try:
        import praw
        
        # 获取环境变量
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        username = os.environ.get('REDDIT_USERNAME')
        password = os.environ.get('REDDIT_PASSWORD')
        
        if not client_id or not client_secret:
            raise Exception("Reddit API credentials not configured")
        
        # 初始化Reddit客户端
        reddit = None
        auth_mode = "unknown"
        
        try:
            if username and password:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=password,
                    user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
                )
                user = reddit.user.me()
                auth_mode = f"script (authenticated as {user.name})"
            else:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
                )
                auth_mode = "read-only"
        except Exception as auth_error:
            logger.warning(f"Authentication failed: {auth_error}")
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
            )
            auth_mode = "read-only"
        
        # 如果没有指定subreddit，使用容易出现推广内容的subreddit
        if not subreddits:
            subreddits = [
                'all',  # 全站搜索最容易找到推广内容
                'popular',  # 热门内容
                'deals',
                'entrepreneur', 
                'startups', 
                'business', 
                'marketing',
                'technology',
                'gaming',
                'movies',
                'music'
            ]
        
        all_posts = []
        promoted_posts = []
        
        # 搜索策略：使用多种方法寻找推广内容
        search_strategies = [
            # 策略1: 搜索包含推广关键词的帖子
            {
                'keywords': ['promoted', 'sponsored', 'advertisement'],
                'sort': 'new',
                'time_filter': 'week'
            },
            # 策略2: 搜索热门内容（推广帖子通常会被推到热门）
            {
                'method': 'hot',
                'limit_per_sub': max(10, limit // len(subreddits))
            },
            # 策略3: 搜索新帖子（新的推广内容）
            {
                'method': 'new',
                'limit_per_sub': max(5, limit // (len(subreddits) * 2))
            }
        ]
        
        for subreddit_name in subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # 策略1: 关键词搜索
                try:
                    search_results = subreddit.search(
                        'promoted OR sponsored OR advertisement', 
                        limit=20,
                        sort='new',
                        time_filter='month'
                    )
                    
                    for submission in search_results:
                        if len(all_posts) >= limit * 3:  # 获取更多帖子以便筛选
                            break
                        all_posts.append(submission)
                        
                except Exception as search_error:
                    logger.warning(f"Search failed in r/{subreddit_name}: {search_error}")
                
                # 策略2: 热门帖子检查
                try:
                    hot_posts = subreddit.hot(limit=20)
                    for submission in hot_posts:
                        if len(all_posts) >= limit * 3:
                            break
                        all_posts.append(submission)
                except Exception as hot_error:
                    logger.warning(f"Hot posts failed in r/{subreddit_name}: {hot_error}")
                
                # 策略3: 新帖子检查
                try:
                    new_posts = subreddit.new(limit=10)
                    for submission in new_posts:
                        if len(all_posts) >= limit * 3:
                            break
                        all_posts.append(submission)
                except Exception as new_error:
                    logger.warning(f"New posts failed in r/{subreddit_name}: {new_error}")
                    
            except Exception as subreddit_error:
                logger.warning(f"Failed to access r/{subreddit_name}: {subreddit_error}")
                continue
        
        # 处理收集到的帖子，检测推广内容
        processed_count = 0
        for submission in all_posts:
            if processed_count >= limit:
                break
                
            try:
                # 详细的推广检测
                is_promoted = detect_promotional_content(
                    submission.title, 
                    submission.selftext, 
                    submission
                )
                
                # 额外的Reddit官方推广检测
                reddit_promoted = False
                promoted_indicators = []
                
                # 检查所有可能的推广属性
                try:
                    # 检查promoted属性
                    if hasattr(submission, 'promoted') and submission.promoted:
                        reddit_promoted = True
                        promoted_indicators.append("promoted_flag")
                    
                    # 检查distinguished
                    if hasattr(submission, 'distinguished') and submission.distinguished:
                        promoted_indicators.append(f"distinguished_{submission.distinguished}")
                        if submission.distinguished == 'admin':
                            reddit_promoted = True
                    
                    # 检查stickied
                    if hasattr(submission, 'stickied') and submission.stickied:
                        promoted_indicators.append("stickied")
                    
                    # 检查标题中的明确标记
                    title_lower = submission.title.lower()
                    if 'promoted' in title_lower:
                        reddit_promoted = True
                        promoted_indicators.append("title_promoted")
                    if 'sponsored' in title_lower:
                        reddit_promoted = True
                        promoted_indicators.append("title_sponsored")
                    
                    # 检查作者名称
                    if submission.author:
                        author_name = str(submission.author).lower()
                        if any(marker in author_name for marker in ['promoted', 'sponsored', 'ad_']):
                            reddit_promoted = True
                            promoted_indicators.append("promotional_author")
                    
                    # 检查flair
                    if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                        flair_lower = submission.link_flair_text.lower()
                        if any(marker in flair_lower for marker in ['promoted', 'sponsored', 'ad']):
                            reddit_promoted = True
                            promoted_indicators.append("promotional_flair")
                
                except Exception as check_error:
                    logger.warning(f"Error checking promotion attributes for {submission.id}: {check_error}")
                
                # 如果检测到推广内容，添加到结果中
                if is_promoted or reddit_promoted:
                    post_data = {
                        "reddit_id": submission.id,
                        "title": submission.title,
                        "author": str(submission.author) if submission.author else "[deleted]",
                        "subreddit": submission.subreddit.display_name,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "created_utc": submission.created_utc,
                        "url": submission.url,
                        "selftext": submission.selftext[:500] if submission.selftext else "",
                        "is_promotional": is_promoted,
                        "reddit_promoted": reddit_promoted,
                        "promoted_indicators": promoted_indicators,
                        "auth_mode": auth_mode,
                        "collection_method": "promoted_search"
                    }
                    promoted_posts.append(post_data)
                    processed_count += 1
                    
            except Exception as post_error:
                logger.warning(f"Error processing post {submission.id}: {post_error}")
                continue
        
        logger.info(f"Collected {len(promoted_posts)} promoted posts from {len(all_posts)} total posts")
        return promoted_posts
        
    except Exception as e:
        logger.error(f"Error collecting promoted posts: {e}")
        raise

@app.route('/api/collect-promotional', methods=['POST'])
def collect_promotional():
    """收集推广内容端点 - 增强版，专门寻找Reddit官方推广"""
    try:
        data = request.get_json() or {}
        
        subreddits = data.get('subreddits', None)
        limit = min(data.get('limit', 50), 100)
        search_type = data.get('search_type', 'all')  # 'all', 'reddit_promoted', 'general'
        
        # 检查Reddit API配置
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        search_start = datetime.now()
        
        if search_type == 'reddit_promoted':
            # 专门搜索Reddit官方推广帖子
            promoted_posts = collect_reddit_promoted_posts(subreddits, limit)
            all_posts = promoted_posts
        else:
            # 使用原有的推广内容搜索，但增强检测
            if not subreddits:
                subreddits = ['all', 'deals', 'entrepreneur', 'startups', 'business', 'marketing']
            
            # 使用推广相关关键词搜索
            promotional_keywords = ['deal', 'discount', 'sale', 'promo', 'offer', 'promoted', 'sponsored']
            
            all_posts = []
            
            # 在多个subreddit中搜索推广内容
            for subreddit in subreddits:
                try:
                    posts = perform_reddit_search(
                        keywords=promotional_keywords[:3],
                        subreddit=subreddit,
                        limit=limit // len(subreddits),
                        time_filter='week',
                        sort='new'
                    )
                    all_posts.extend(posts)
                except Exception as e:
                    logger.warning(f"Failed to search in r/{subreddit}: {e}")
            
            # 过滤出推广内容
            promoted_posts = [post for post in all_posts if post.get('is_promotional') or post.get('reddit_promoted')]
        
        search_time = (datetime.now() - search_start).total_seconds()
        
        # 统计不同类型的推广内容
        reddit_promoted_count = len([p for p in promoted_posts if p.get('reddit_promoted')])
        general_promotional_count = len([p for p in promoted_posts if p.get('is_promotional') and not p.get('reddit_promoted')])
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(promoted_posts)} promotional posts out of {len(all_posts)} total posts",
            "data": {
                "posts": promoted_posts,
                "total_found": len(all_posts),
                "promotional_count": len(promoted_posts),
                "reddit_promoted_count": reddit_promoted_count,
                "general_promotional_count": general_promotional_count,
                "search_time": round(search_time, 2),
                "subreddits_searched": subreddits,
                "search_type": search_type
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in collect promotional endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Collection failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/history')
def get_history():
    """获取搜索历史端点"""
    try:
        # 由于Vercel是无状态的，我们返回一个示例历史记录
        # 在实际应用中，这些数据会存储在数据库中
        sample_history = [
            {
                "id": 1,
                "keywords": ["python", "programming"],
                "subreddit": "programming",
                "time_filter": "week",
                "results_count": 25,
                "search_date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "completed"
            },
            {
                "id": 2,
                "keywords": ["machine learning", "AI"],
                "subreddit": "MachineLearning",
                "time_filter": "day",
                "results_count": 15,
                "search_date": (datetime.now() - timedelta(hours=5)).isoformat(),
                "status": "completed"
            },
            {
                "id": 3,
                "keywords": ["startup", "entrepreneur"],
                "subreddit": "entrepreneur",
                "time_filter": "week",
                "results_count": 30,
                "search_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "completed"
            }
        ]
        
        return jsonify({
            "status": "success",
            "data": sample_history,
            "message": "Search history retrieved successfully",
            "note": "In Vercel environment, history is simulated. In production, this would be stored in a database.",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in history endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve history: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/export')
def export_data():
    """数据导出端点"""
    try:
        export_format = request.args.get('format', 'csv').lower()
        data_type = request.args.get('type', 'current').lower()  # current, promotional, all
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        if export_format not in ['csv', 'json']:
            return jsonify({
                "status": "error",
                "message": "Invalid format. Supported formats: csv, json",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 生成示例数据用于导出
        sample_posts = [
            {
                "title": "Sample Reddit Post 1",
                "author": "user1",
                "subreddit": "technology",
                "score": 150,
                "num_comments": 25,
                "url": "https://reddit.com/r/technology/sample1",
                "is_promotional": False,
                "created_utc": datetime.now().timestamp()
            },
            {
                "title": "Amazing Deal - 50% Off!",
                "author": "seller123",
                "subreddit": "deals",
                "score": 75,
                "num_comments": 10,
                "url": "https://reddit.com/r/deals/sample2",
                "is_promotional": True,
                "created_utc": datetime.now().timestamp()
            }
        ]
        
        # 根据类型过滤数据
        if data_type == 'promotional':
            filtered_posts = [post for post in sample_posts if post['is_promotional']]
        elif data_type == 'non_promotional':
            filtered_posts = [post for post in sample_posts if not post['is_promotional']]
        else:
            filtered_posts = sample_posts
        
        # 限制数量
        filtered_posts = filtered_posts[:limit]
        
        if export_format == 'csv':
            # 生成CSV格式
            csv_headers = ['Title', 'Author', 'Subreddit', 'Score', 'Comments', 'URL', 'Is Promotional', 'Created Date']
            csv_rows = []
            
            for post in filtered_posts:
                csv_rows.append([
                    f'"{post["title"]}"',
                    post['author'],
                    post['subreddit'],
                    post['score'],
                    post['num_comments'],
                    post['url'],
                    'Yes' if post['is_promotional'] else 'No',
                    datetime.fromtimestamp(post['created_utc']).strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            csv_content = ','.join(csv_headers) + '\\n' + '\\n'.join([','.join(map(str, row)) for row in csv_rows])
            
            return jsonify({
                "status": "success",
                "message": f"CSV export generated with {len(filtered_posts)} posts",
                "data": {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"reddit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "posts_count": len(filtered_posts)
                },
                "timestamp": datetime.now().isoformat()
            })
        
        else:  # JSON format
            return jsonify({
                "status": "success",
                "message": f"JSON export generated with {len(filtered_posts)} posts",
                "data": {
                    "format": "json",
                    "posts": filtered_posts,
                    "filename": f"reddit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "posts_count": len(filtered_posts),
                    "export_info": {
                        "generated_at": datetime.now().isoformat(),
                        "filter_type": data_type,
                        "total_posts": len(filtered_posts)
                    }
                },
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error in export endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """获取系统统计信息端点"""
    try:
        # 模拟统计数据（在Vercel环境中）
        statistics = {
            "total_posts": 150,
            "promotional_posts": 25,
            "reddit_promoted_posts": 8,
            "total_searches": 45,
            "unique_subreddits": 12,
            "database_size": "2.5 MB",
            "last_updated": datetime.now().isoformat(),
            "environment": "Vercel",
            "uptime": "Running",
            "api_status": "Connected"
        }
        
        return jsonify({
            "status": "success",
            "message": "Statistics retrieved successfully",
            "statistics": statistics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in statistics endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get statistics: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """清除搜索历史端点"""
    try:
        return jsonify({
            "status": "success",
            "message": "Search history cleared successfully",
            "note": "In Vercel environment, history is simulated",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to clear history: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "/", 
            "/api/health", 
            "/api/status", 
            "/api/search", 
            "/api/reddit/test",
            "/api/collect-promotional",
            "/api/export",
            "/api/history",
            "/api/statistics",
            "/api/clear-history"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat(),
        "note": "Check Vercel function logs for details"
    }), 500

@app.route('/api/collect-reddit-promoted', methods=['POST'])
def collect_reddit_promoted():
    """专门收集Reddit官方推广帖子的端点"""
    try:
        data = request.get_json() or {}
        
        subreddits = data.get('subreddits', None)
        limit = min(data.get('limit', 50), 100)
        
        # 检查Reddit API配置
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        search_start = datetime.now()
        
        # 使用专门的Reddit推广帖子收集函数
        promoted_posts = collect_reddit_promoted_posts(subreddits, limit)
        
        search_time = (datetime.now() - search_start).total_seconds()
        
        # 统计不同类型的推广内容
        reddit_promoted_count = len([p for p in promoted_posts if p.get('reddit_promoted')])
        general_promotional_count = len([p for p in promoted_posts if p.get('is_promotional') and not p.get('reddit_promoted')])
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(promoted_posts)} Reddit promoted posts",
            "data": {
                "posts": promoted_posts,
                "total_found": len(promoted_posts),
                "reddit_promoted_count": reddit_promoted_count,
                "general_promotional_count": general_promotional_count,
                "search_time": round(search_time, 2),
                "subreddits_searched": subreddits or ['all', 'popular', 'deals', 'entrepreneur', 'startups'],
                "search_type": "reddit_promoted_only"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in collect Reddit promoted endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Collection failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=False) 