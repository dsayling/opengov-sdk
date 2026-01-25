#!/bin/bash
# Start Prism mock server for OpenAPI integration testing
#
# This script starts a Prism mock server that serves responses based on
# the OpenGov OpenAPI specification. The server runs on port 4010 by default.
#
# Prerequisites:
#   - Node.js/npm (for npx) OR Docker
#
# Usage:
#   ./scripts/start-mock-server.sh           # Start in foreground
#   ./scripts/start-mock-server.sh --daemon  # Start in background
#   ./scripts/start-mock-server.sh --stop    # Stop background server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# Use the original OpenAPI spec
OPENAPI_SPEC="$PROJECT_ROOT/docs/opengov-plc-api.json"
PORT="${MOCK_SERVER_PORT:-4010}"
PID_FILE="/tmp/prism-mock-server.pid"
LOG_FILE="/tmp/prism-mock-server.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_openapi_spec() {
    if [ ! -f "$OPENAPI_SPEC" ]; then
        log_error "OpenAPI spec not found at: $OPENAPI_SPEC"
        exit 1
    fi
}

check_prism_available() {
    if command -v npx &> /dev/null; then
        return 0
    elif command -v docker &> /dev/null; then
        return 0
    else
        log_error "Neither npx nor docker found. Please install Node.js or Docker."
        exit 1
    fi
}

wait_for_server() {
    local max_attempts=30
    local attempt=1

    log_info "Waiting for mock server to be ready on port $PORT..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
            log_info "Mock server is ready!"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    log_error "Mock server failed to start within ${max_attempts}s"
    return 1
}

start_server() {
    check_openapi_spec
    check_prism_available

    log_info "Starting Prism mock server on port $PORT..."
    log_info "OpenAPI spec: $OPENAPI_SPEC"

    if command -v npx &> /dev/null; then
        npx @stoplight/prism-cli mock \
            "$OPENAPI_SPEC" \
            --port "$PORT" \
            --host 0.0.0.0 \
            --errors
    else
        # Use Docker as fallback
        docker run --rm \
            -p "$PORT:4010" \
            -v "$OPENAPI_SPEC:/spec.json:ro" \
            stoplight/prism:latest mock \
            "/spec.json" \
            --host 0.0.0.0 \
            --errors
    fi
}

start_daemon() {
    check_openapi_spec
    check_prism_available

    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "Mock server already running (PID: $pid)"
            return 0
        fi
        rm -f "$PID_FILE"
    fi

    log_info "Starting Prism mock server in background on port $PORT..."

    if command -v npx &> /dev/null; then
        nohup npx @stoplight/prism-cli mock \
            "$OPENAPI_SPEC" \
            --port "$PORT" \
            --host 0.0.0.0 \
            --errors \
            > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
    else
        nohup docker run --rm \
            -p "$PORT:4010" \
            -v "$OPENAPI_SPEC:/spec.json:ro" \
            --name prism-mock-server \
            stoplight/prism:latest mock \
            "/spec.json" \
            --host 0.0.0.0 \
            --errors \
            > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
    fi

    wait_for_server
    log_info "Mock server started (PID: $(cat "$PID_FILE"))"
    log_info "Logs available at: $LOG_FILE"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Stopping mock server (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_FILE"
            log_info "Mock server stopped"
        else
            log_warn "Mock server not running"
            rm -f "$PID_FILE"
        fi
    else
        log_warn "No PID file found"
        # Try to kill docker container if running
        docker stop prism-mock-server 2>/dev/null || true
    fi
}

show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Mock server is running (PID: $pid)"
            if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
                log_info "Server is responding on port $PORT"
            else
                log_warn "Server process running but not responding"
            fi
        else
            log_warn "PID file exists but process not running"
        fi
    else
        log_warn "Mock server is not running"
    fi
}

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTION]

Start a Prism mock server for OpenAPI integration testing.

Options:
    --daemon    Start the server in the background
    --stop      Stop the background server
    --status    Show server status
    --help      Show this help message

Environment variables:
    MOCK_SERVER_PORT    Port to run the server on (default: 4010)

Examples:
    $(basename "$0")            # Start in foreground
    $(basename "$0") --daemon   # Start in background
    $(basename "$0") --stop     # Stop background server
EOF
}

# Main entry point
case "${1:-}" in
    --daemon)
        start_daemon
        ;;
    --stop)
        stop_daemon
        ;;
    --status)
        show_status
        ;;
    --help|-h)
        show_help
        ;;
    "")
        start_server
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
