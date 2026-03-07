#!/usr/bin/env bash
set -Eeuo pipefail

# =========================================================
# DIBS AI - Management Script
# =========================================================

APP_NAME="DIBS AI"
APP_VERSION="v2.3.0"

IP="94.100.26.128"
BACKEND_PORT="8081"
DOWNLOAD_PORT="9091"
MCP_PORT="8765"

BASE_DIR="${HOME}/dibs1"
FRONTEND_DIR="${BASE_DIR}/frontend"
BACKEND_DIR="${BASE_DIR}/backend"
DOWNLOAD_DIR="${BASE_DIR}/downloads"
MCP_DIR="${BASE_DIR}/mcp-server"
DATA_DIR="${BASE_DIR}/data"

LATEST_APK="${DOWNLOAD_DIR}/dibs1-latest.apk"

# =========================
# Colors
# =========================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# =========================
# Helpers
# =========================
log()    { echo -e "${BLUE}ℹ${NC} $*"; }
ok()     { echo -e "${GREEN}✅${NC} $*"; }
warn()   { echo -e "${YELLOW}⚠${NC} $*"; }
err()    { echo -e "${RED}❌${NC} $*" >&2; }

die() {
  err "$*"
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Command '$1' tidak ditemukan"
}

section() {
  echo
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}${CYAN}$1${NC}"
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_header() {
  echo
  echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${BLUE}║         ${APP_NAME} ${APP_VERSION} MANAGEMENT          ║${NC}"
  echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════╝${NC}"
}

on_error() {
  local exit_code=$?
  local line_no=$1
  err "Terjadi error di baris ${line_no} (exit code: ${exit_code})"
  exit "$exit_code"
}
trap 'on_error $LINENO' ERR

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti :"${port}" 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    warn "Port ${port} dipakai. Mematikan PID: ${pids}"
    kill -9 ${pids} 2>/dev/null || true
    sleep 1
  fi
}

is_running() {
  local port="$1"
  lsof -ti :"${port}" >/dev/null 2>&1
}

wait_for_backend() {
  local max_attempts=45
  local attempt=1

  log "Menunggu backend siap di http://localhost:${BACKEND_PORT}/health"
  while (( attempt <= max_attempts )); do
    if curl -fsS "http://localhost:${BACKEND_PORT}/health" >/dev/null 2>&1; then
      ok "Backend siap setelah ${attempt} detik"
      return 0
    fi
    printf "."
    sleep 1
    attempt=$((attempt + 1))
  done

  echo
  err "Backend tidak merespon setelah ${max_attempts} detik"
  return 1
}

ensure_dirs() {
  mkdir -p "${DOWNLOAD_DIR}" "${DATA_DIR}"
}

get_latest_apk_target() {
  if [[ -L "${LATEST_APK}" ]]; then
    readlink -f "${LATEST_APK}"
  elif [[ -f "${LATEST_APK}" ]]; then
    realpath "${LATEST_APK}"
  else
    echo ""
  fi
}

render_download_page() {
  ensure_dirs

  local latest_size="Belum ada APK"
  local latest_time="-"

  if [[ -f "${LATEST_APK}" ]]; then
    latest_size="$(du -h "${LATEST_APK}" | awk '{print $1}')"
    latest_time="$(date -r "${LATEST_APK}" '+%Y-%m-%d %H:%M:%S')"
  fi

  cat > "${DOWNLOAD_DIR}/index.html" <<EOF
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${APP_NAME} ${APP_VERSION}</title>
  <style>
    :root{
      --bg:#0b1020;
      --card:#131a2a;
      --card2:#1a2338;
      --text:#e8eefc;
      --muted:#9db0d3;
      --accent:#4ade80;
      --accent2:#60a5fa;
      --border:rgba(255,255,255,.08);
      --shadow:0 20px 50px rgba(0,0,0,.35);
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
      background:linear-gradient(180deg,#0b1020 0%,#10172a 100%);
      color:var(--text);
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:24px;
    }
    .wrap{width:100%;max-width:860px}
    .card{
      background:linear-gradient(180deg,var(--card) 0%,var(--card2) 100%);
      border:1px solid var(--border);
      border-radius:24px;
      box-shadow:var(--shadow);
      padding:28px;
    }
    .badge{
      display:inline-block;
      padding:8px 14px;
      border-radius:999px;
      background:rgba(96,165,250,.12);
      color:#bfdbfe;
      font-size:13px;
      font-weight:700;
      letter-spacing:.3px;
      margin-bottom:14px;
    }
    h1{
      margin:0 0 10px;
      font-size:clamp(28px,4vw,44px);
      line-height:1.05;
    }
    p{
      color:var(--muted);
      font-size:16px;
      line-height:1.6;
      margin:0 0 18px;
    }
    .grid{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
      gap:14px;
      margin:22px 0;
    }
    .item{
      background:rgba(255,255,255,.03);
      border:1px solid var(--border);
      border-radius:18px;
      padding:16px;
    }
    .item .k{
      color:var(--muted);
      font-size:13px;
      margin-bottom:8px;
    }
    .item .v{
      font-size:15px;
      font-weight:700;
      word-break:break-word;
    }
    .actions{
      display:flex;
      flex-wrap:wrap;
      gap:12px;
      margin-top:22px;
    }
    .btn{
      text-decoration:none;
      border:none;
      cursor:pointer;
      padding:14px 18px;
      border-radius:16px;
      font-weight:800;
      font-size:15px;
      transition:.2s ease;
      display:inline-flex;
      align-items:center;
      gap:10px;
    }
    .btn.primary{
      background:linear-gradient(135deg,var(--accent) 0%,#22c55e 100%);
      color:#08110c;
    }
    .btn.secondary{
      background:rgba(96,165,250,.12);
      color:#dbeafe;
      border:1px solid rgba(96,165,250,.25);
    }
    .btn:hover{transform:translateY(-1px)}
    .footer{
      margin-top:18px;
      color:var(--muted);
      font-size:13px;
    }
    code{
      background:rgba(255,255,255,.06);
      padding:2px 8px;
      border-radius:10px;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="badge">🚀 Production Download Center</div>
      <h1>${APP_NAME} ${APP_VERSION}</h1>
      <p>
        Download APK terbaru langsung dari server. File <code>dibs1-latest.apk</code>
        selalu mengarah ke hasil build paling baru.
      </p>

      <div class="grid">
        <div class="item">
          <div class="k">APK terbaru</div>
          <div class="v">dibs1-latest.apk</div>
        </div>
        <div class="item">
          <div class="k">Ukuran</div>
          <div class="v">${latest_size}</div>
        </div>
        <div class="item">
          <div class="k">Last build</div>
          <div class="v">${latest_time}</div>
        </div>
        <div class="item">
          <div class="k">Backend API</div>
          <div class="v">http://${IP}:${BACKEND_PORT}/api/docs</div>
        </div>
      </div>

      <div class="actions">
        <a class="btn primary" href="dibs1-latest.apk">📱 Download APK Terbaru</a>
        <a class="btn secondary" href="http://${IP}:${BACKEND_PORT}/health">💚 Cek Health API</a>
        <a class="btn secondary" href="http://${IP}:${BACKEND_PORT}/api/docs">🤖 API Docs</a>
      </div>

      <div class="footer">
        Backup build lama tetap disimpan dengan format timestamp.
      </div>
    </div>
  </div>
</body>
</html>
EOF
}

show_links() {
  echo
  echo -e "${BOLD}${BLUE}LINKS${NC}"
  echo -e "📱 APK     : http://${IP}:${DOWNLOAD_PORT}/dibs1-latest.apk"
  echo -e "🌐 Page    : http://${IP}:${DOWNLOAD_PORT}/"
  echo -e "🤖 API     : http://${IP}:${BACKEND_PORT}/api/docs"
  echo -e "💚 Health  : http://${IP}:${BACKEND_PORT}/health"
  echo -e "🔧 MCP     : http://localhost:${MCP_PORT}"
  echo
}

status() {
  print_header
  section "STATUS SERVICE"

  # MCP
  if is_running "${MCP_PORT}"; then
    local mcp_pid
    mcp_pid="$(lsof -ti :"${MCP_PORT}" | tr '\n' ' ')"
    ok "MCP Server RUNNING  | port ${MCP_PORT} | PID: ${mcp_pid}"
  else
    err "MCP Server STOPPED"
  fi

  # Backend
  if systemctl is-active --quiet dibs-backend 2>/dev/null; then
    ok "Backend RUNNING     | systemd | port ${BACKEND_PORT}"
    local health version
    health="$(curl -fsS "http://localhost:${BACKEND_PORT}/health" 2>/dev/null || true)"
    if [[ -n "${health}" ]]; then
      version="$(echo "${health}" | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || true)"
      ok "Health Check OK     | version: ${version:-unknown}"
    else
      warn "Health Check belum bisa dibaca"
    fi
  else
    err "Backend STOPPED"
  fi

  # Download
  if is_running "${DOWNLOAD_PORT}"; then
    local dl_pid
    dl_pid="$(lsof -ti :"${DOWNLOAD_PORT}" | tr '\n' ' ')"
    ok "Download RUNNING    | port ${DOWNLOAD_PORT} | PID: ${dl_pid}"
  else
    err "Download STOPPED"
  fi

  # APK info
  section "APK INFO"
  if [[ -f "${LATEST_APK}" ]]; then
    local latest_real size modified
    latest_real="$(get_latest_apk_target)"
    size="$(du -h "${LATEST_APK}" | awk '{print $1}')"
    modified="$(date -r "${LATEST_APK}" '+%Y-%m-%d %H:%M:%S')"
    ok "Latest APK tersedia"
    echo -e "   ├─ File     : ${LATEST_APK}"
    echo -e "   ├─ Target   : ${latest_real}"
    echo -e "   ├─ Size     : ${size}"
    echo -e "   └─ Updated  : ${modified}"
  else
    warn "Belum ada dibs1-latest.apk"
  fi

  # Ollama
  section "DEPENDENCIES"
  if systemctl is-active --quiet ollama 2>/dev/null; then
    ok "Ollama ACTIVE (systemd)"
  elif pgrep -f "ollama serve" >/dev/null 2>&1; then
    ok "Ollama RUNNING (manual)"
  else
    warn "Ollama STOPPED"
  fi

  # DB
  section "DATABASE"
  if [[ -f "${DATA_DIR}/dibs.db" ]]; then
    local db_size users
    db_size="$(du -h "${DATA_DIR}/dibs.db" | awk '{print $1}')"
    users="$(sqlite3 "${DATA_DIR}/dibs.db" 'SELECT COUNT(*) FROM users;' 2>/dev/null || echo '?')"
    ok "Main DB OK | ${db_size} | users: ${users}"
  else
    warn "Main DB belum ada: ${DATA_DIR}/dibs.db"
  fi

  if [[ -f "${BACKEND_DIR}/toko.db" ]]; then
    local products
    products="$(sqlite3 "${BACKEND_DIR}/toko.db" 'SELECT COUNT(*) FROM products;' 2>/dev/null || echo '?')"
    ok "Toko DB OK | products: ${products}"
  else
    warn "Toko DB belum ada: ${BACKEND_DIR}/toko.db"
  fi

  section "RESOURCE"
  echo -e "CPU Load    : $(uptime | awk -F'load average:' '{print $2}' | xargs)"
  echo -e "Memory Free : $(free -h | awk '/^Mem:/ {print $4 " / " $2}')"

  show_links
}

stop() {
  print_header
  section "STOPPING SERVICES"

  log "Stopping MCP..."
  kill_port "${MCP_PORT}"
  sudo systemctl stop dibs-mcp 2>/dev/null || true

  log "Stopping Backend..."
  sudo systemctl stop dibs-backend 2>/dev/null || kill_port "${BACKEND_PORT}"

  log "Stopping Download Server..."
  kill_port "${DOWNLOAD_PORT}"

  ok "Semua service sudah dihentikan"
}

start_download_server() {
  ensure_dirs
  render_download_page

  kill_port "${DOWNLOAD_PORT}"
  cd "${DOWNLOAD_DIR}"
  nohup python3 -m http.server "${DOWNLOAD_PORT}" > http.log 2>&1 &
  sleep 1

  if is_running "${DOWNLOAD_PORT}"; then
    ok "Download Server started | port ${DOWNLOAD_PORT}"
  else
    die "Gagal menjalankan Download Server"
  fi
}

start_mcp() {
  log "Starting MCP Server..."
  kill_port "${MCP_PORT}"
  cd "${MCP_DIR}"

  if [[ ! -d "venv" ]]; then
    log "Membuat virtualenv MCP..."
    python3 -m venv venv
  fi

  # shellcheck disable=SC1091
  source "${MCP_DIR}/venv/bin/activate"
  pip install -q fastapi uvicorn python-dotenv
  nohup python mcp_server_production.py > mcp.log 2>&1 &
  sleep 2

  if is_running "${MCP_PORT}"; then
    ok "MCP Server started | port ${MCP_PORT}"
  else
    warn "MCP belum listen di port ${MCP_PORT}, cek log: ${MCP_DIR}/mcp.log"
  fi
}

start_ollama() {
  log "Starting Ollama..."
  if systemctl list-units --full -all | grep -q "ollama.service"; then
    sudo systemctl start ollama 2>/dev/null || true
    ok "Ollama via systemd"
  else
    if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
      nohup ollama serve >/dev/null 2>&1 &
      ok "Ollama manual mode"
    else
      ok "Ollama already running"
    fi
  fi
}

start_backend() {
  log "Starting Backend..."
  sudo systemctl start dibs-backend

  if wait_for_backend; then
    ok "Backend ready"
  else
    warn "Backend gagal ready, ini 20 log terakhir:"
    sudo journalctl -u dibs-backend -n 20 --no-pager || true
    return 1
  fi
}

start() {
  print_header
  section "STARTING SERVICES"

  require_cmd python3
  require_cmd curl
  require_cmd lsof

  start_mcp
  start_ollama
  start_backend
  start_download_server

  ok "Semua service berhasil dijalankan"
  status
}

restart() {
  print_header
  section "RESTART"
  stop
  sleep 2
  start
}

build() {
  print_header
  section "BUILD APK"

  require_cmd flutter
  require_cmd realpath
  ensure_dirs

  [[ -d "${FRONTEND_DIR}" ]] || die "Frontend directory tidak ditemukan: ${FRONTEND_DIR}"

  cd "${FRONTEND_DIR}"

  log "Validasi project Flutter..."
  [[ -f "pubspec.yaml" ]] || die "pubspec.yaml tidak ditemukan di ${FRONTEND_DIR}"

  log "Mengambil dependencies terbaru..."
  flutter pub get

  log "Membersihkan build lama..."
  flutter clean

  log "Build APK release dari source code yang sekarang..."
  flutter build apk --release

  local built_apk="build/app/outputs/flutter-apk/app-release.apk"
  [[ -f "${built_apk}" ]] || die "APK hasil build tidak ditemukan: ${built_apk}"

  local timestamp versioned_apk tmp_latest size
  timestamp="$(date '+%Y%m%d-%H%M%S')"
  versioned_apk="${DOWNLOAD_DIR}/dibs1-${timestamp}.apk"
  tmp_latest="${DOWNLOAD_DIR}/dibs1-latest.apk.tmp"

  log "Menyimpan backup APK versi timestamp..."
  cp -f "${built_apk}" "${versioned_apk}"

  log "Mengganti latest APK secara atomik..."
  cp -f "${built_apk}" "${tmp_latest}"
  mv -f "${tmp_latest}" "${LATEST_APK}"

  render_download_page

  if ! is_running "${DOWNLOAD_PORT}"; then
    log "Download server belum aktif, menjalankan sekarang..."
    start_download_server
  fi

  size="$(du -h "${LATEST_APK}" | awk '{print $1}')"

  ok "Build selesai"
  echo -e "   ├─ Latest APK : ${LATEST_APK}"
  echo -e "   ├─ Backup APK : ${versioned_apk}"
  echo -e "   ├─ Size       : ${size}"
  echo -e "   └─ URL        : http://${IP}:${DOWNLOAD_PORT}/dibs1-latest.apk"

  show_links
}

rebuild() {
  print_header
  section "REBUILD FULL FLOW"
  build
  restart
}

logs() {
  case "${2:-}" in
    backend)
      echo -e "${BLUE}📄 Backend logs (Ctrl+C untuk keluar)${NC}"
      sudo journalctl -u dibs-backend -f
      ;;
    mcp)
      echo -e "${BLUE}📄 MCP logs (Ctrl+C untuk keluar)${NC}"
      tail -f "${MCP_DIR}/mcp.log" 2>/dev/null || echo "No MCP log file"
      ;;
    download)
      echo -e "${BLUE}📄 Download logs (Ctrl+C untuk keluar)${NC}"
      tail -f "${DOWNLOAD_DIR}/http.log" 2>/dev/null || echo "No download log file"
      ;;
    all)
      echo -e "${BLUE}📄 All logs (Ctrl+C untuk keluar)${NC}"
      tail -f "${DOWNLOAD_DIR}/http.log" "${MCP_DIR}/mcp.log" 2>/dev/null &
      sudo journalctl -u dibs-backend -f
      ;;
    *)
      echo "Usage: $0 logs {backend|mcp|download|all}"
      ;;
  esac
}

help() {
  print_header
  echo -e "${YELLOW}Commands:${NC}"
  echo "  ./manage.sh status      - Lihat status semua service"
  echo "  ./manage.sh start       - Start semua service"
  echo "  ./manage.sh stop        - Stop semua service"
  echo "  ./manage.sh restart     - Restart semua service"
  echo "  ./manage.sh build       - Build APK terbaru dan update dibs1-latest.apk"
  echo "  ./manage.sh rebuild     - Build APK lalu restart semua service"
  echo "  ./manage.sh logs <svc>  - Lihat logs (backend|mcp|download|all)"
  echo
}

case "${1:-}" in
  status)  status ;;
  start)   start ;;
  stop)    stop ;;
  restart) restart ;;
  build)   build ;;
  rebuild) rebuild ;;
  logs)    logs "$@" ;;
  *)       help ;;
esac
