#!/bin/bash

# Reddit Data Collection Website - Enhanced Automatic Installation Script
# ========================================================================
# 
# This comprehensive script automatically sets up the Reddit data collection
# environment with full error handling, system checks, and user guidance.
#
# Features:
# - System requirements validation
# - Automatic dependency installation
# - Configuration setup assistance
# - Database initialization
# - Comprehensive testing
# - User-friendly progress reporting
#
# Author: Reddit Data Collector Team
# Version: 2.0
# Last Updated: 2024
#
# Usage: chmod +x install.sh && ./install.sh

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

PROJECT_NAME="Reddit Data Collection Website"
PROJECT_VERSION="2.0"
VENV_NAME="venv"
PYTHON_MIN_VERSION="3.7"
REQUIREMENTS_FILE="requirements.txt"
CONFIG_FILE="config.py"
DATABASE_FILE="reddit_data.db"
LOG_FILE="install.log"

# Required system commands
REQUIRED_COMMANDS=("curl" "git")

# Color codes for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Unicode symbols for better visual feedback
CHECK_MARK="✅"
CROSS_MARK="❌"
WARNING_SIGN="⚠️"
INFO_SIGN="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
DATABASE="💾"
GLOBE="🌐"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Function to print colored and formatted output
print_header() {
    echo ""
    echo -e "${PURPLE}${BOLD}================================${NC}"
    echo -e "${PURPLE}${BOLD} $1${NC}"
    echo -e "${PURPLE}${BOLD}================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}${BOLD}--- $1 ---${NC}"
}

print_status() {
    echo -e "${BLUE}${INFO_SIGN} ${NC}$1"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}${WARNING_SIGN} ${NC}$1"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} ${NC}$1"
}

print_step() {
    echo -e "${WHITE}${BOLD}Step $1:${NC} $2"
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get OS information
get_os_info() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "Windows"
    else
        echo "Unknown"
    fi
}

# Function to compare version numbers
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Function to prompt user for input
prompt_user() {
    local prompt="$1"
    local default="$2"
    local response
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " response
        echo "${response:-$default}"
    else
        read -p "$prompt: " response
        echo "$response"
    fi
}

# Function to confirm action
confirm_action() {
    local prompt="$1"
    local response
    
    while true; do
        read -p "$prompt (y/n): " response
        case $response in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

# =============================================================================
# SYSTEM CHECKS
# =============================================================================

# Function to display welcome message
show_welcome() {
    clear
    print_header "$PROJECT_NAME v$PROJECT_VERSION - Installer"
    
    echo -e "${CYAN}Welcome to the automated installation script!${NC}"
    echo ""
    echo "This script will:"
    echo "  ${CHECK_MARK} Check system requirements"
    echo "  ${CHECK_MARK} Set up Python virtual environment"
    echo "  ${CHECK_MARK} Install all dependencies"
    echo "  ${CHECK_MARK} Configure the application"
    echo "  ${CHECK_MARK} Initialize the database"
    echo "  ${CHECK_MARK} Run comprehensive tests"
    echo "  ${CHECK_MARK} Provide setup instructions"
    echo ""
    
    OS_INFO=$(get_os_info)
    print_status "Detected operating system: $OS_INFO"
    print_status "Installation log will be saved to: $LOG_FILE"
    echo ""
    
    if ! confirm_action "Do you want to continue with the installation?"; then
        echo "Installation cancelled by user."
        exit 0
    fi
    
    log_message "Installation started for $PROJECT_NAME v$PROJECT_VERSION on $OS_INFO"
}

# Function to check system requirements
check_system_requirements() {
    print_section "System Requirements Check"
    
    local all_good=true
    
    # Check required commands
    for cmd in "${REQUIRED_COMMANDS[@]}"; do
        if command_exists "$cmd"; then
            print_success "$cmd is available"
        else
            print_error "$cmd is not installed"
            all_good=false
        fi
    done
    
    # Check disk space (require at least 500MB)
    if command_exists df; then
        local available_space=$(df . | tail -1 | awk '{print $4}')
        local required_space=512000  # 500MB in KB
        
        if [ "$available_space" -gt "$required_space" ]; then
            print_success "Sufficient disk space available ($(($available_space / 1024))MB)"
        else
            print_error "Insufficient disk space. Required: 500MB, Available: $(($available_space / 1024))MB"
            all_good=false
        fi
    fi
    
    # Check internet connectivity
    print_status "Checking internet connectivity..."
    if curl -s --head --request GET https://www.google.com | grep "200 OK" > /dev/null; then
        print_success "Internet connection is working"
    else
        print_error "No internet connection detected"
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        print_error "System requirements check failed. Please resolve the issues above."
        exit 1
    fi
    
    print_success "All system requirements satisfied"
    log_message "System requirements check passed"
}

# Function to check Python installation and version
check_python_installation() {
    print_section "Python Installation Check"
    
    # Try to find Python
    if command_exists python3; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command_exists python; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        print_error "Python is not installed"
        echo ""
        echo "Please install Python $PYTHON_MIN_VERSION or higher:"
        echo "  • On Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        echo "  • On CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "  • On macOS: brew install python3"
        echo "  • On Windows: Download from https://python.org/downloads/"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_status "Found Python version: $PYTHON_VERSION"
    
    version_compare $PYTHON_VERSION $PYTHON_MIN_VERSION
    case $? in
        0) print_success "Python version meets requirements ($PYTHON_MIN_VERSION)" ;;
        1) print_success "Python version $PYTHON_VERSION exceeds requirements" ;;
        2) 
            print_error "Python version $PYTHON_VERSION is older than required $PYTHON_MIN_VERSION"
            echo "Please upgrade Python to version $PYTHON_MIN_VERSION or higher"
            exit 1
            ;;
    esac
    
    # Check pip
    if command_exists "$PIP_CMD"; then
        PIP_VERSION=$($PIP_CMD --version 2>&1 | cut -d' ' -f2)
        print_success "Found pip version: $PIP_VERSION"
    else
        print_error "pip is not installed"
        echo "Please install pip for Python package management"
        exit 1
    fi
    
    # Check venv module
    if $PYTHON_CMD -m venv --help > /dev/null 2>&1; then
        print_success "Python venv module is available"
    else
        print_error "Python venv module is not available"
        echo "Please install python3-venv package"
        exit 1
    fi
    
    log_message "Python check passed - Python $PYTHON_VERSION, pip $PIP_VERSION"
}

# =============================================================================
# INSTALLATION FUNCTIONS
# =============================================================================

# Function to create and setup virtual environment
setup_virtual_environment() {
    print_section "Virtual Environment Setup"
    
    # Remove existing virtual environment if it exists
    if [ -d "$VENV_NAME" ]; then
        print_warning "Existing virtual environment found"
        if confirm_action "Remove existing virtual environment and create a new one?"; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_NAME"
            print_success "Existing virtual environment removed"
        else
            print_status "Using existing virtual environment"
        fi
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_NAME" ]; then
        print_status "Creating Python virtual environment..."
        $PYTHON_CMD -m venv "$VENV_NAME"
        
        if [ $? -eq 0 ]; then
            print_success "Virtual environment created successfully"
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        print_success "Virtual environment activated (Unix/Linux/macOS)"
    elif [ -f "$VENV_NAME/Scripts/activate" ]; then
        source "$VENV_NAME/Scripts/activate"
        print_success "Virtual environment activated (Windows)"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
    
    # Upgrade pip in virtual environment
    print_status "Upgrading pip in virtual environment..."
    pip install --upgrade pip --quiet
    
    if [ $? -eq 0 ]; then
        print_success "pip upgraded successfully"
    else
        print_warning "Failed to upgrade pip, continuing with current version"
    fi
    
    log_message "Virtual environment setup completed"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_section "Python Dependencies Installation"
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    print_status "Installing Python packages from $REQUIREMENTS_FILE..."
    echo "This may take a few minutes depending on your internet connection..."
    
    # Install with progress indication
    pip install -r "$REQUIREMENTS_FILE" --progress-bar on
    
    if [ $? -eq 0 ]; then
        print_success "All Python dependencies installed successfully"
        
        # Show installed packages
        print_status "Installed packages:"
        pip list | grep -E "(flask|praw|pandas|requests|sqlite)" | while read line; do
            echo "  ${CHECK_MARK} $line"
        done
    else
        print_error "Failed to install some dependencies"
        echo "Please check the error messages above and try again"
        exit 1
    fi
    
    log_message "Python dependencies installation completed"
}

# Function to create necessary directories
create_directories() {
    print_section "Directory Structure Setup"
    
    local directories=("exports" "backups" "logs" "static/css" "static/js" "templates")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
    
    # Set appropriate permissions
    chmod 755 exports backups logs 2>/dev/null || true
    
    log_message "Directory structure setup completed"
}

# Function to initialize database
initialize_database() {
    print_section "Database Initialization"
    
    print_status "Initializing SQLite database..."
    
    # Initialize database using Python
    $PYTHON_CMD -c "
from database import get_database_manager
try:
    db = get_database_manager()
    db.create_tables()
    stats = db.get_database_stats()
    print('Database initialized successfully')
    print(f'Database file: $DATABASE_FILE')
    print(f'Tables created: {len(stats)} tables')
except Exception as e:
    print(f'Database initialization failed: {e}')
    exit(1)
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
        print_status "Database file: $DATABASE_FILE"
    else
        print_error "Database initialization failed"
        exit 1
    fi
    
    log_message "Database initialization completed"
}

# Function to setup configuration
setup_configuration() {
    print_section "Configuration Setup"
    
    if [ -f "$CONFIG_FILE" ]; then
        print_status "Configuration file already exists: $CONFIG_FILE"
        
        # Check if Reddit API is configured
        if grep -q "your_client_id_here" "$CONFIG_FILE"; then
            print_warning "Reddit API credentials are not configured"
            setup_reddit_api_config
        else
            print_success "Reddit API credentials appear to be configured"
        fi
    else
        print_error "Configuration file not found: $CONFIG_FILE"
        echo "Please ensure the config.py file exists in the project directory"
        exit 1
    fi
    
    log_message "Configuration setup completed"
}

# Function to setup Reddit API configuration
setup_reddit_api_config() {
    echo ""
    echo -e "${YELLOW}${BOLD}Reddit API Configuration Required${NC}"
    echo ""
    echo "To use this application, you need Reddit API credentials."
    echo "Here's how to get them:"
    echo ""
    echo "1. Go to: https://www.reddit.com/prefs/apps"
    echo "2. Click 'Create App' or 'Create Another App'"
    echo "3. Fill out the form:"
    echo "   - Name: Reddit Data Collector"
    echo "   - App type: script"
    echo "   - Description: Data collection for research"
    echo "   - Redirect URI: http://localhost:8080"
    echo "4. Note your Client ID (under app name) and Client Secret"
    echo ""
    
    if confirm_action "Do you have Reddit API credentials ready?"; then
        echo ""
        CLIENT_ID=$(prompt_user "Enter your Reddit Client ID")
        CLIENT_SECRET=$(prompt_user "Enter your Reddit Client Secret")
        USER_AGENT=$(prompt_user "Enter your Reddit username for user agent" "RedditDataCollector")
        
        if [ -n "$CLIENT_ID" ] && [ -n "$CLIENT_SECRET" ]; then
            # Update configuration file
            sed -i.bak "s/your_client_id_here/$CLIENT_ID/g" "$CONFIG_FILE"
            sed -i.bak "s/your_client_secret_here/$CLIENT_SECRET/g" "$CONFIG_FILE"
            sed -i.bak "s/RedditDataCollector\/1.0/RedditDataCollector\/2.0 by $USER_AGENT/g" "$CONFIG_FILE"
            
            print_success "Reddit API credentials configured successfully"
            
            # Test API connection
            print_status "Testing Reddit API connection..."
            $PYTHON_CMD -c "
from reddit_scraper import RedditScraper
try:
    scraper = RedditScraper()
    print('Reddit API connection successful!')
except Exception as e:
    print(f'Reddit API connection failed: {e}')
    print('Please check your credentials and try again')
" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                print_success "Reddit API connection test passed"
            else
                print_warning "Reddit API connection test failed"
                print_warning "You can configure this later by editing $CONFIG_FILE"
            fi
        else
            print_warning "Reddit API credentials not provided"
            print_warning "You can configure this later by editing $CONFIG_FILE"
        fi
    else
        print_warning "Reddit API configuration skipped"
        echo "You can configure this later by:"
        echo "1. Getting credentials from https://www.reddit.com/prefs/apps"
        echo "2. Editing the $CONFIG_FILE file"
        echo "3. Replacing 'your_client_id_here' and 'your_client_secret_here'"
    fi
}

# =============================================================================
# TESTING AND VALIDATION
# =============================================================================

# Function to run comprehensive tests
run_system_tests() {
    print_section "System Testing"
    
    print_status "Running comprehensive system tests..."
    
    # Test database functionality
    print_status "Testing database functionality..."
    $PYTHON_CMD -c "
from database import get_database_manager
db = get_database_manager()
stats = db.get_database_stats()
print(f'Database test passed - {stats[\"total_posts\"]} posts in database')
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Database test passed"
    else
        print_error "Database test failed"
    fi
    
    # Test Flask application
    print_status "Testing Flask application..."
    timeout 10 $PYTHON_CMD -c "
from app import app
with app.test_client() as client:
    response = client.get('/api/health')
    if response.status_code == 200:
        print('Flask application test passed')
    else:
        print('Flask application test failed')
        exit(1)
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Flask application test passed"
    else
        print_warning "Flask application test skipped (may require Reddit API)"
    fi
    
    # Test frontend files
    print_status "Testing frontend files..."
    if [ -f "templates/index.html" ] && [ -f "static/css/style.css" ] && [ -f "static/js/app.js" ]; then
        print_success "Frontend files test passed"
    else
        print_error "Frontend files test failed - missing required files"
    fi
    
    # Run full test suite if available
    if [ -f "test_system.py" ]; then
        print_status "Running full test suite..."
        $PYTHON_CMD test_system.py --quiet 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Full test suite passed"
        else
            print_warning "Some tests failed - check test_system.py for details"
        fi
    fi
    
    log_message "System testing completed"
}

# =============================================================================
# COMPLETION AND INSTRUCTIONS
# =============================================================================

# Function to show completion message and next steps
show_completion_message() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}${BOLD}🎉 Congratulations! The Reddit Data Collection Website has been successfully installed.${NC}"
    echo ""
    
    print_section "What's Been Set Up"
    echo "  ${CHECK_MARK} Python virtual environment with all dependencies"
    echo "  ${CHECK_MARK} SQLite database initialized and ready"
    echo "  ${CHECK_MARK} Modern web interface with Google-style design"
    echo "  ${CHECK_MARK} Complete RESTful API with 10+ endpoints"
    echo "  ${CHECK_MARK} Advanced promotional content detection system"
    echo "  ${CHECK_MARK} Data export capabilities (CSV, JSON)"
    echo "  ${CHECK_MARK} Comprehensive error handling and logging"
    echo ""
    
    print_section "Next Steps"
    echo ""
    echo -e "${BOLD}1. Start the Application:${NC}"
    echo "   source $VENV_NAME/bin/activate  # Activate virtual environment"
    echo "   python app.py                   # Start the web server"
    echo ""
    echo -e "${BOLD}2. Access the Web Interface:${NC}"
    echo "   Open your browser and go to: ${CYAN}http://localhost:5000${NC}"
    echo ""
    echo -e "${BOLD}3. Configure Reddit API (if not done already):${NC}"
    echo "   • Visit: https://www.reddit.com/prefs/apps"
    echo "   • Create a new 'script' application"
    echo "   • Edit $CONFIG_FILE with your credentials"
    echo ""
    echo -e "${BOLD}4. Start Collecting Data:${NC}"
    echo "   • Enter keywords in the search box"
    echo "   • Use advanced options for filtering"
    echo "   • Export results in CSV or JSON format"
    echo ""
    
    print_section "Useful Commands"
    echo "  ${GEAR} Start application:     python app.py"
    echo "  ${DATABASE} Run tests:            python test_system.py"
    echo "  ${GLOBE} Check API status:     curl http://localhost:5000/api/health"
    echo "  ${INFO_SIGN} View logs:            tail -f app.log"
    echo ""
    
    print_section "Documentation"
    echo "  📖 Complete guide:       README.md"
    echo "  🎨 Frontend guide:       FRONTEND_GUIDE.md"
    echo "  🚀 Quick start:          QUICK_START.md"
    echo ""
    
    print_section "Support"
    echo "  🐛 Report issues:        Create GitHub issue"
    echo "  💬 Get help:             Check troubleshooting section in README.md"
    echo "  📧 Contact:              See README.md for contact information"
    echo ""
    
    echo -e "${CYAN}${BOLD}Thank you for using the Reddit Data Collection Website!${NC}"
    echo -e "${CYAN}Happy data collecting! 🔍📊${NC}"
    echo ""
    
    log_message "Installation completed successfully"
}

# Function to handle installation errors
handle_error() {
    print_error "Installation failed at step: $1"
    echo ""
    echo "Error details have been logged to: $LOG_FILE"
    echo ""
    echo "Common solutions:"
    echo "  • Check your internet connection"
    echo "  • Ensure you have sufficient permissions"
    echo "  • Verify Python and pip are properly installed"
    echo "  • Try running the installer again"
    echo ""
    echo "For more help, check the troubleshooting section in README.md"
    
    log_message "Installation failed at step: $1"
    exit 1
}

# =============================================================================
# MAIN INSTALLATION FLOW
# =============================================================================

main() {
    # Initialize log file
    echo "Installation started at $(date)" > "$LOG_FILE"
    
    # Set up error handling
    trap 'handle_error "Unknown error"' ERR
    
    # Main installation steps
    show_welcome
    
    print_step "1/8" "Checking system requirements"
    check_system_requirements
    
    print_step "2/8" "Verifying Python installation"
    check_python_installation
    
    print_step "3/8" "Setting up virtual environment"
    setup_virtual_environment
    
    print_step "4/8" "Installing Python dependencies"
    install_python_dependencies
    
    print_step "5/8" "Creating directory structure"
    create_directories
    
    print_step "6/8" "Initializing database"
    initialize_database
    
    print_step "7/8" "Configuring application"
    setup_configuration
    
    print_step "8/8" "Running system tests"
    run_system_tests
    
    # Show completion message
    show_completion_message
}

# Run main installation if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 