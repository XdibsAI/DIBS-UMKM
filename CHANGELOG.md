# 📝 DIBS AI - Changelog

## v2.0.0 - Modular Architecture with Nemotron 30B (2026-02-25)

### 🎯 Major Changes

**Architecture:**
- ✅ Migrated from monolith (3,353 lines) to modular structure
- ✅ Separated concerns: auth, chat, knowledge, video, config, database
- ✅ Clean imports, independent testing, easier maintenance

**AI Provider:**
- ✅ **Nemotron 30B via NVIDIA API** (1.8s response time!)
- ✅ Auto-fallback to Ollama llama3.2:3b (local, offline)
- ✅ Dual provider with smart switching
- ✅ OpenAI SDK integration for stability

**Performance:**
- ⚡ Response time: **1.8s** (NVIDIA) vs 30-60s (Ollama)
- ✅ DIBS identity preserved across providers
- ✅ Context-aware conversation (6 message history)
- ✅ Bahasa Indonesia native responses

**Features:**
- ✅ Settings screen: AI provider toggle
- ✅ Model selection: Nemotron / Llama 3.2 3B/1B / DIBS Pro
- ✅ Knowledge management with instant recall
- ✅ PDF report generation
- ✅ Video generation (script → audio → MP4)
- ✅ Timezone sync (UTC → Local)

**Security:**
- ✅ fail2ban integration (auto-ban scanners)
- ✅ JWT token authentication
- ✅ bcrypt password hashing
- ✅ SQL injection protection

### 🐛 Bug Fixes
- Fixed database schema (chat_messages created_at column)
- Fixed token persistence (SharedPreferences)
- Fixed password reset functionality
- Fixed video project deletion
- Fixed timezone display in chat

### 📊 Stats
- **Backend:** 15 modules, 200 lines main.py
- **API Endpoints:** 16 total (4 auth, 5 chat, 3 knowledge, 4 video)
- **Response Time:** 1.8s average (Nemotron)
- **APK Size:** 54.2MB
- **Architecture:** Production-ready modular

### 🔧 Tech Stack
- **Backend:** FastAPI, SQLite, NVIDIA API, Ollama
- **AI Models:** Nemotron 30B (primary), Llama 3.2 (fallback)
- **Frontend:** Flutter, Provider, HTTP
- **Infrastructure:** Ubuntu 24, systemd, fail2ban

---

## v1.1.0 - Video Generation & Multilingual (2026-02-19)

### Features
- Video generation pipeline (MoviePy, gTTS)
- Multilingual understanding (Jawa, Sunda, Melayu, Betawi)
- Knowledge auto-categorization
- PDF reports

---

## v1.0.0 - Initial Release (2026-02-16)

### Features
- Chat with Ollama llama3.2:3b
- Basic authentication
- Session management
- Knowledge storage

---

**Built with ❤️ for Indonesian UMKM**
