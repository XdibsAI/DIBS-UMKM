#!/bin/bash
set -e

# Konfigurasi
IP="94.100.26.128"
BACKEND_PORT="8081"
DOWNLOAD_PORT="9091"
MCP_PORT="8765"
BASE_DIR="$HOME/dibs1"
FRONTEND_DIR="$BASE_DIR/frontend"
BACKEND_DIR="$BASE_DIR/backend"
DOWNLOAD_DIR="$BASE_DIR/downloads"
MCP_DIR="$BASE_DIR/mcp-server"

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo -e "  ${YELLOW}➜ Port $port: mematikan PID $pid${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

is_running() {
    local port=$1
    lsof -ti:$port >/dev/null 2>&1
}

wait_for_backend() {
    local max_attempts=30
    local attempt=1
    echo -e "  ${YELLOW}⏳ Menunggu backend siap...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Backend siap setelah $attempt detik${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
        attempt=$((attempt + 1))
    done
    echo -e "\n  ${RED}❌ Backend tidak merespon setelah $max_attempts detik${NC}"
    return 1
}

status() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}        DIBS AI v2.3.0 STATUS           ${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"

    # MCP Server
    if is_running $MCP_PORT; then
        local mcp_pid=$(lsof -ti:$MCP_PORT)
        echo -e "  MCP Server    : ${GREEN}✅ RUNNING${NC} (port $MCP_PORT, PID: $mcp_pid)"
    else
        echo -e "  MCP Server    : ${RED}❌ STOPPED${NC}"
    fi

    # Backend (systemd)
    if systemctl is-active --quiet dibs-backend 2>/dev/null; then
        echo -e "  Backend       : ${GREEN}✅ RUNNING (systemd)${NC} (port $BACKEND_PORT)"
        local health=$(curl -s http://localhost:$BACKEND_PORT/health 2>/dev/null)
        if echo "$health" | grep -q "healthy"; then
            local version=$(echo $health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
            echo -e "  Health Check  : ${GREEN}✅ OK${NC} (v$version)"
            echo -e "  AI Provider   : ${BLUE}Nemotron 70B (primary)${NC}"
        else
            echo -e "  Health Check  : ${RED}❌ FAIL${NC}"
        fi
    else
        echo -e "  Backend       : ${RED}❌ STOPPED${NC}"
    fi

    # Download Server
    if is_running $DOWNLOAD_PORT; then
        local dl_pid=$(lsof -ti:$DOWNLOAD_PORT)
        echo -e "  Download      : ${GREEN}✅ RUNNING${NC} (port $DOWNLOAD_PORT, PID: $dl_pid)"
        if [ -f "$DOWNLOAD_DIR/dibs-ai-v2.3.0-STABLE.apk" ]; then
            local size=$(du -h "$DOWNLOAD_DIR/dibs-ai-v2.3.0-STABLE.apk" | cut -f1)
            local modified=$(date -r "$DOWNLOAD_DIR/dibs-ai-v2.3.0-STABLE.apk" "+%Y-%m-%d %H:%M")
            echo -e "  APK v2.3.0    : ${GREEN}✅ tersedia${NC} ($size, $modified)"
        fi
    else
        echo -e "  Download      : ${RED}❌ STOPPED${NC}"
    fi

    # Ollama
    if systemctl is-active --quiet ollama 2>/dev/null; then
        echo -e "  Ollama        : ${GREEN}✅ ACTIVE (systemd)${NC}"
    elif pgrep -f "ollama serve" >/dev/null; then
        echo -e "  Ollama        : ${GREEN}✅ RUNNING (manual)${NC}"
    else
        echo -e "  Ollama        : ${RED}❌ STOPPED${NC}"
    fi

    # Database
    if [ -f "$BASE_DIR/data/dibs.db" ]; then
        local db_size=$(du -h "$BASE_DIR/data/dibs.db" | cut -f1)
        local users=$(sqlite3 "$BASE_DIR/data/dibs.db" "SELECT COUNT(*) FROM users" 2>/dev/null || echo "?")
        echo -e "  Database      : ${GREEN}✅ OK${NC} ($db_size, $users users)"
    else
        echo -e "  Database      : ${RED}❌ NOT FOUND${NC}"
    fi

    if [ -f "$BACKEND_DIR/toko.db" ]; then
        local products=$(sqlite3 "$BACKEND_DIR/toko.db" "SELECT COUNT(*) FROM products" 2>/dev/null || echo "?")
        echo -e "  Toko DB       : ${GREEN}✅ OK${NC} ($products products)"
    fi

    echo -e "\n${BLUE}📊 RESOURCE USAGE${NC}"
    echo -e "  CPU Load      : $(uptime | awk -F'load average:' '{print $2}')"
    echo -e "  Memory Free   : $(free -h | awk '/^Mem:/ {print $4}') / $(free -h | awk '/^Mem:/ {print $2}')"

    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "📱 APK: http://$IP:$DOWNLOAD_PORT/dibs-ai-v2.3.0-STABLE.apk"
    echo -e "🤖 API: http://$IP:$BACKEND_PORT/api/docs"
    echo -e "💚 Health: http://$IP:$BACKEND_PORT/health"
    echo -e "🔧 MCP: http://localhost:$MCP_PORT"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

stop() {
    echo -e "\n${YELLOW}🛑 STOPPING SERVICES...${NC}\n"
    
    echo -e "🔸 MCP Server"
    kill_port $MCP_PORT
    sudo systemctl stop dibs-mcp 2>/dev/null || true
    
    echo -e "🔸 Backend"
    sudo systemctl stop dibs-backend 2>/dev/null || kill_port $BACKEND_PORT
    
    echo -e "🔸 Download Server"
    kill_port $DOWNLOAD_PORT
    
    echo -e "\n${GREEN}✅ Services stopped${NC}\n"
}

start() {
    echo -e "\n${GREEN}🚀 STARTING SERVICES...${NC}\n"

    # 1. MCP Server
    echo -e "🔸 MCP Server (port $MCP_PORT)"
    kill_port $MCP_PORT
    cd "$MCP_DIR"
    
    # Check venv
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -q fastapi uvicorn python-dotenv
    else
        source venv/bin/activate
    fi
    
    nohup python mcp_server_production.py > mcp.log 2>&1 &
    echo -e "  ${GREEN}✅ MCP Server started (PID: $!)${NC}"
    sleep 2

    # 2. Ollama
    echo -e "🔸 Ollama Service"
    if systemctl list-units --full -all | grep -q "ollama.service"; then
        sudo systemctl start ollama 2>/dev/null || true
        echo -e "  ${GREEN}✅ Ollama started (systemd)${NC}"
    else
        if ! pgrep -f "ollama serve" >/dev/null; then
            nohup ollama serve > /dev/null 2>&1 &
            echo -e "  ${GREEN}✅ Ollama started (manual)${NC}"
        else
            echo -e "  ${GREEN}✅ Ollama already running${NC}"
        fi
    fi
    sleep 2

    # 3. Backend (systemd)
    echo -e "🔸 Backend (systemd)"
    sudo systemctl start dibs-backend
    if wait_for_backend; then
        echo -e "  ${GREEN}✅ Backend ready${NC}"
    else
        echo -e "  ${RED}❌ Backend failed${NC}"
        echo -e "${YELLOW}Last 10 lines:${NC}"
        sudo journalctl -u dibs-backend -n 10 --no-pager
    fi

    # 4. Download Server
    echo -e "🔸 Download Server (port $DOWNLOAD_PORT)"
    kill_port $DOWNLOAD_PORT
    cd "$DOWNLOAD_DIR"
    
    if [ ! -f "index.html" ]; then
        cat > index.html << 'ENDHTML'
<!DOCTYPE html>
<html><head><title>DIBS AI v2.3.0</title></head>
<body style="font-family: Arial; padding: 40px; background: #0a0a0a; color: #0f0;">
<h1>🤖 DIBS AI v2.3.0 - Production Stable</h1>
<p>📱 Download APK: <a href="dibs-ai-v2.3.0-STABLE.apk" style="color: #0f0;">dibs-ai-v2.3.0-STABLE.apk</a></p>
<p>🚀 Features: Nemotron AI, Toko POS, Voice Scan, Mode Inklusif</p>
</body></html>
ENDHTML
    fi
    
    nohup python3 -m http.server $DOWNLOAD_PORT > http.log 2>&1 &
    echo -e "  ${GREEN}✅ Download Server started (PID: $!)${NC}"

    echo -e "\n${GREEN}✅ All services started!${NC}\n"
    status
}

restart() {
    echo -e "\n${BLUE}🔄 RESTARTING...${NC}\n"
    stop
    sleep 3
    start
}

build() {
    echo -e "\n${BLUE}📱 BUILDING APK v2.3.0...${NC}\n"
    cd "$FRONTEND_DIR"
    
    flutter clean
    flutter pub get
    
    echo -e "${YELLOW}⏳ Building with auth token support...${NC}"
    flutter build apk --release --dart-define=API_URL=http://$IP:$BACKEND_PORT/api/v1
    
    mkdir -p "$DOWNLOAD_DIR/archive"
    
    local timestamp=$(date +%Y%m%d-%H%M%S)
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/dibs-ai-v2.3.0-STABLE.apk"
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/archive/dibs-$timestamp.apk"
    
    local size=$(du -h "$DOWNLOAD_DIR/dibs-ai-v2.3.0-STABLE.apk" | cut -f1)
    echo -e "\n${GREEN}✅ APK Ready!${NC}"
    echo -e "  📦 Size: $size"
    echo -e "  📱 URL: http://$IP:$DOWNLOAD_PORT/dibs-ai-v2.3.0-STABLE.apk"
    echo -e "  💾 Backup: archive/dibs-$timestamp.apk\n"
}

logs() {
    case "$2" in
        backend)
            echo -e "${BLUE}📄 Backend logs (Ctrl+C to stop)${NC}\n"
            sudo journalctl -u dibs-backend -f
            ;;
        mcp)
            echo -e "${BLUE}📄 MCP logs (Ctrl+C to stop)${NC}\n"
            tail -f "$MCP_DIR/mcp.log" 2>/dev/null || echo "No log file"
            ;;
        download)
            echo -e "${BLUE}📄 Download server logs (Ctrl+C to stop)${NC}\n"
            tail -f "$DOWNLOAD_DIR/http.log" 2>/dev/null || echo "No log file"
            ;;
        all)
            echo -e "${BLUE}📄 All logs (Ctrl+C to stop)${NC}\n"
            tail -f "$DOWNLOAD_DIR/http.log" "$MCP_DIR/mcp.log" 2>/dev/null &
            sudo journalctl -u dibs-backend -f
            ;;
        *)
            echo "Usage: $0 logs {backend|mcp|download|all}"
            ;;
    esac
}

help() {
    echo -e "\n${BLUE}DIBS AI v2.3.0 MANAGEMENT SCRIPT${NC}"
    echo -e "${YELLOW}Commands:${NC}"
    echo "  ./manage.sh status   - Show all service status (detailed)"
    echo "  ./manage.sh start    - Start all services (MCP, Backend, Download)"
    echo "  ./manage.sh stop     - Stop all services"
    echo "  ./manage.sh restart  - Restart all services"
    echo "  ./manage.sh build    - Build new APK v2.3.0"
    echo "  ./manage.sh logs <service> - View logs (backend/mcp/download/all)"
    echo ""
}

case "$1" in
    status) status ;;
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    build) build ;;
    logs) logs $@ ;;
    *) help ;;
esac
