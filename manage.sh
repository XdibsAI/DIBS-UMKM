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

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Fungsi mematikan proses di port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo -e "  ${YELLOW}➜ Port $port: mematikan PID $pid${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Fungsi cek service hidup
is_running() {
    local port=$1
    if lsof -ti:$port >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Fungsi wait for backend ready
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

# Status semua service (dengan detail)
status() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}        DIBS1 SERVICE STATUS             ${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"

    # MCP Server
    if is_running $MCP_PORT; then
        local mcp_pid=$(lsof -ti:$MCP_PORT)
        echo -e "  MCP Server    : ${GREEN}✅ RUNNING${NC} (port $MCP_PORT, PID: $mcp_pid)"
    else
        echo -e "  MCP Server    : ${RED}❌ STOPPED${NC}"
    fi

    # Backend dengan detail
    if is_running $BACKEND_PORT; then
        local backend_pid=$(lsof -ti:$BACKEND_PORT)
        echo -e "  Backend       : ${GREEN}✅ RUNNING${NC} (port $BACKEND_PORT, PID: $backend_pid)"
        
        # Health check detail
        local health=$(curl -s http://localhost:$BACKEND_PORT/health 2>/dev/null)
        if echo "$health" | grep -q "healthy"; then
            local version=$(echo $health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
            local arch=$(echo $health | grep -o '"architecture":"[^"]*"' | cut -d'"' -f4)
            echo -e "  Health Check   : ${GREEN}✅ OK${NC}"
            echo -e "  Version        : ${BLUE}v$version${NC} ($arch)"
        else
            echo -e "  Health Check   : ${RED}❌ FAIL${NC}"
            echo -e "  Response       : $health"
        fi
    else
        echo -e "  Backend       : ${RED}❌ STOPPED${NC}"
    fi

    # Download Server
    if is_running $DOWNLOAD_PORT; then
        local dl_pid=$(lsof -ti:$DOWNLOAD_PORT)
        echo -e "  Download      : ${GREEN}✅ RUNNING${NC} (port $DOWNLOAD_PORT, PID: $dl_pid)"
        
        # Cek file APK
        if [ -f "$DOWNLOAD_DIR/dibs1-latest.apk" ]; then
            local size=$(du -h "$DOWNLOAD_DIR/dibs1-latest.apk" | cut -f1)
            local modified=$(date -r "$DOWNLOAD_DIR/dibs1-latest.apk" "+%Y-%m-%d %H:%M")
            echo -e "  APK Info       : ${GREEN}✅ tersedia${NC} ($size, $modified)"
        else
            echo -e "  APK Info       : ${RED}❌ file tidak ditemukan${NC}"
        fi
    else
        echo -e "  Download      : ${RED}❌ STOPPED${NC}"
    fi

    # Ollama
    if systemctl is-active --quiet ollama 2>/dev/null; then
        echo -e "  Ollama        : ${GREEN}✅ ACTIVE (systemd)${NC}"
    elif pgrep -f "ollama serve" >/dev/null; then
        local ollama_pid=$(pgrep -f "ollama serve")
        echo -e "  Ollama        : ${GREEN}✅ RUNNING (manual)${NC} (PID: $ollama_pid)"
    else
        echo -e "  Ollama        : ${RED}❌ STOPPED${NC}"
    fi

    # MCP Model
    if ollama list 2>/dev/null | grep -q "dibs-ai-pro"; then
        local model_info=$(ollama list | grep "dibs-ai-pro")
        echo -e "  AI Model      : ${GREEN}✅ dibs-ai-pro${NC}"
        echo -e "  Model Info    : $model_info"
    else
        echo -e "  AI Model      : ${RED}❌ NOT FOUND${NC}"
    fi

    # Resource usage
    echo -e "\n${BLUE}📊 RESOURCE USAGE${NC}"
    echo -e "  CPU Load      : $(uptime | awk -F'load average:' '{print $2}')"
    echo -e "  Memory Free   : $(free -h | awk '/^Mem:/ {print $4}') / $(free -h | awk '/^Mem:/ {print $2}')"
    
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "📱 APK: http://$IP:$DOWNLOAD_PORT/dibs1-latest.apk"
    echo -e "🤖 API: http://$IP:$BACKEND_PORT/health"
    echo -e "🔧 MCP: http://localhost:$MCP_PORT"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

# Stop semua service (dengan verifikasi)
stop() {
    echo -e "\n${YELLOW}🛑 STOPPING ALL SERVICES...${NC}\n"

    echo -e "🔸 MCP Server (port $MCP_PORT)"
    kill_port $MCP_PORT
    sudo systemctl stop dibs-mcp 2>/dev/null || true
    sleep 1

    echo -e "🔸 Backend (port $BACKEND_PORT)"
    kill_port $BACKEND_PORT
    pkill -f "python main.py" 2>/dev/null || true
    sleep 1

    echo -e "🔸 Download Server (port $DOWNLOAD_PORT)"
    kill_port $DOWNLOAD_PORT
    sleep 1

    # Verifikasi semua mati
    echo -e "\n${YELLOW}🔍 Verifikasi...${NC}"
    local masih_jalan=false
    for port in $MCP_PORT $BACKEND_PORT $DOWNLOAD_PORT; do
        if is_running $port; then
            echo -e "  ${RED}❌ Port $port masih berjalan${NC}"
            masih_jalan=true
        fi
    done
    
    if [ "$masih_jalan" = false ]; then
        echo -e "\n${GREEN}✅ Semua service berhasil dihentikan${NC}\n"
    else
        echo -e "\n${RED}⚠️  Beberapa service masih berjalan, coba lagi${NC}\n"
    fi
}

# Start semua service (dengan logging detail)
start() {
    echo -e "\n${GREEN}🚀 STARTING ALL SERVICES...${NC}\n"

    # 1. MCP Server
    echo -e "🔸 MCP Server (port $MCP_PORT)"
    kill_port $MCP_PORT
    cd "$MCP_DIR"
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -q fastapi uvicorn
    nohup python mcp_server_production.py > mcp.log 2>&1 &
    echo -e "  ${GREEN}✅ MCP Server started (PID: $!)${NC}"
    sleep 2

    # 2. Ollama
    echo -e "🔸 Ollama Service"
    if systemctl list-units --full -all | grep -q "ollama.service"; then
        sudo systemctl restart ollama
        echo -e "  ${GREEN}✅ Ollama restarted (systemd)${NC}"
    else
        pkill -f ollama 2>/dev/null || true
        nohup ollama serve > /dev/null 2>&1 &
        echo -e "  ${GREEN}✅ Ollama started (manual, PID: $!)${NC}"
    fi
    sleep 3

    # 3. Backend
    echo -e "🔸 Backend (port $BACKEND_PORT)"
    kill_port $BACKEND_PORT
    cd "$BACKEND_DIR"
    
    # Hapus log lama
    > backend.log
    
    source venv/bin/activate
    nohup python main.py > backend.log 2>&1 &
    local backend_pid=$!
    echo -e "  ${GREEN}✅ Backend started (PID: $backend_pid)${NC}"
    
    # Tunggu backend siap
    if wait_for_backend; then
        echo -e "  ${GREEN}✅ Backend ready${NC}"
    else
        echo -e "  ${RED}❌ Backend failed to start${NC}"
        echo -e "  ${YELLOW}📄 Last 10 lines of backend.log:${NC}"
        tail -10 "$BACKEND_DIR/backend.log"
    fi

    # 4. Download Server
    echo -e "🔸 Download Server (port $DOWNLOAD_PORT)"
    kill_port $DOWNLOAD_PORT
    cd "$DOWNLOAD_DIR"
    
    # Buat index.html jika belum ada
    if [ ! -f "index.html" ]; then
        echo "<h1>DIBS1 Download Server</h1><p>APK: <a href='dibs1-latest.apk'>dibs1-latest.apk</a></p>" > index.html
    fi
    
    > http.log
    nohup python3 -m http.server $DOWNLOAD_PORT > http.log 2>&1 &
    echo -e "  ${GREEN}✅ Download Server started (PID: $!)${NC}"

    echo -e "\n${GREEN}✅ Semua service berjalan!${NC}\n"
    
    # Tampilkan status setelah start
    status
}

# Restart (dengan verifikasi)
restart() {
    echo -e "\n${BLUE}🔄 RESTARTING ALL SERVICES...${NC}\n"
    stop
    sleep 3
    start
}

# Build APK
build() {
    echo -e "
${BLUE}📱 BUILDING APK...${NC}
"

    cd "$FRONTEND_DIR"

    # Bersihkan
    flutter clean > /dev/null 2>&1
    rm -rf pubspec.lock

    # Install dependencies
    flutter pub get > /dev/null 2>&1

    # Build dengan logging
    echo -e "${YELLOW}⏳ Building APK, mohon tunggu...${NC}"
    flutter build apk --release

    # Copy ke download folder
    mkdir -p "$DOWNLOAD_DIR"
    
    # Hapus symlink/file lama
    rm -f "$DOWNLOAD_DIR/dibs1-latest.apk"
    
    # Copy file baru
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/dibs1-latest.apk"
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/dibs1-$(date +%Y%m%d-%H%M).apk"

    local size=$(du -h "$DOWNLOAD_DIR/dibs1-latest.apk" | cut -f1)
    echo -e "
${GREEN}✅ APK siap!${NC}"
    echo -e "  📦 Ukuran: $size"
    echo -e "  📱 URL: http://$IP:$DOWNLOAD_PORT/dibs1-latest.apk"
    echo -e "  💾 Backup: dibs1-$(date +%Y%m%d-%H%M).apk
"
}

# Logs dengan lebih detail
logs() {
    case "$2" in
        backend)
            echo -e "${BLUE}📄 Showing backend logs (Ctrl+C to stop)${NC}\n"
            if [ -f "$BACKEND_DIR/backend.log" ]; then
                tail -f "$BACKEND_DIR/backend.log"
            else
                echo -e "${RED}❌ File log tidak ditemukan${NC}"
            fi
            ;;
        mcp)
            echo -e "${BLUE}📄 Showing MCP logs (Ctrl+C to stop)${NC}\n"
            if [ -f "$MCP_DIR/mcp.log" ]; then
                tail -f "$MCP_DIR/mcp.log"
            else
                echo -e "${RED}❌ File log tidak ditemukan${NC}"
            fi
            ;;
        download)
            echo -e "${BLUE}📄 Showing download server logs (Ctrl+C to stop)${NC}\n"
            if [ -f "$DOWNLOAD_DIR/http.log" ]; then
                tail -f "$DOWNLOAD_DIR/http.log"
            else
                echo -e "${RED}❌ File log tidak ditemukan${NC}"
            fi
            ;;
        all)
            echo -e "${BLUE}📄 Showing all logs (Ctrl+C to stop)${NC}\n"
            tail -f "$BACKEND_DIR/backend.log" "$MCP_DIR/mcp.log" "$DOWNLOAD_DIR/http.log" 2>/dev/null
            ;;
        *)
            echo -e "Usage: $0 logs {backend|mcp|download|all}"
            ;;
    esac
}

# Help
help() {
    echo -e "\n${BLUE}DIBS1 MANAGEMENT SCRIPT${NC}"
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./manage.sh status        - Tampilkan status semua service (detail)"
    echo "  ./manage.sh start         - Start semua service"
    echo "  ./manage.sh stop          - Stop semua service"
    echo "  ./manage.sh restart       - Restart semua service"
    echo "  ./manage.sh build         - Build APK baru"
    echo "  ./manage.sh logs <service> - Lihat logs (backend/mcp/download/all)"
    echo "  ./manage.sh help          - Tampilkan help ini"
    echo ""
}

# Main
case "$1" in
    status)
        status
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    build)
        build
        ;;
    logs)
        logs $@
        ;;
    *)
        help
        ;;
esac
