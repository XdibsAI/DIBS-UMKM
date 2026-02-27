# 🤖 DIBS AI - Digital Intelligent Business System

**Smart AI Assistant for Indonesian UMKM**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/XdibsAI/DIBS-UMKM/releases)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com)

---

## 🌟 Features

### 🤖 **Dual AI Engine**
- **Nemotron 30B** (NVIDIA) - 1.8s response time
- **Ollama Llama 3.2** - Local fallback for offline use
- Auto-switching for 99.9% uptime

### 💬 **Intelligent Chat**
- Multilingual support (Indonesian, Javanese, Sundanese)
- Context-aware conversations (6-message history)
- Natural language understanding
- DIBS brand identity consistency

### 🏪 **Voice-Enabled POS System**
- Voice scan kasir (Indonesian + numbers)
- Real-time inventory management
- Transaction history & analytics
- Low stock alerts

### 📊 **Knowledge Management**
- Auto-categorization (finance, work, health)
- Instant recall (<0.2s)
- PDF report generation (daily/weekly/monthly)
- Export to PDF with analytics

### 🖼️ **Image & Document Analysis**
- OCR text extraction (Tesseract)
- Product image analysis
- PDF/DOC/CSV document processing
- Multi-format support

### 🎬 **AI Video Generation**
- Script generation
- TTS audio synthesis (gTTS)
- Video rendering (MoviePy)
- MP4 export & download

---

## 🚀 Quick Start

### Prerequisites
- **Backend:** Python 3.12+, Ubuntu 24
- **Frontend:** Flutter 3.x, Dart 3.x
- **AI:** Ollama (local) or NVIDIA API key

### Installation

```bash
# 1. Clone repository
git clone https://github.com/XdibsAI/DIBS-UMKM.git
cd DIBS-UMKM

# 2. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 4. Initialize database
python3 -c "from database.manager import DatabaseManager; import asyncio; asyncio.run(DatabaseManager('/path/to/dibs.db').initialize())"

# 5. Start backend
python3 main.py

# 6. Frontend setup (new terminal)
cd ../frontend
flutter pub get
flutter run

# 7. Build APK (optional)
flutter build apk --release
```

---

## 📱 Architecture

```
DIBS-UMKM/
├── backend/          # FastAPI modular backend
│   ├── auth/         # JWT authentication
│   ├── chat/         # Dual AI provider (Nemotron/Ollama)
│   ├── knowledge/    # Knowledge management
│   ├── video/        # Video generation
│   ├── toko/         # POS system
│   └── main.py       # App entry point
├── frontend/         # Flutter mobile app
│   ├── lib/
│   │   ├── providers/    # State management
│   │   ├── screens/      # UI screens
│   │   └── services/     # API client
│   └── pubspec.yaml
├── manage.sh         # Management script
└── README.md
```

---

## 🔧 Configuration

### Backend (.env)
```env
# AI Provider
USE_NVIDIA=true
NVIDIA_API_KEY=your-key-here
OLLAMA_URL=http://localhost:11434

# Database
DB_PATH=~/dibs1/dibs1.db

# Security
JWT_SECRET_KEY=your-secret-key
```

### Frontend (API endpoint)
Update `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://your-server:8081/api/v1';
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| AI Response Time (Nemotron) | 1.8s |
| AI Response Time (Ollama) | 30-60s |
| Knowledge Recall | <0.2s |
| Video Generation | 30-60s |
| Uptime | 99.9% |
| APK Size | 54MB |

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (async web framework)
- SQLite + aiosqlite (database)
- OpenAI SDK (NVIDIA API client)
- Ollama (local AI)
- PyTesseract (OCR)
- MoviePy (video generation)

**Frontend:**
- Flutter 3.x (cross-platform)
- Provider (state management)
- HTTP client
- file_picker (document upload)

**Infrastructure:**
- Ubuntu 24 LTS
- systemd (service management)
- fail2ban (security)

---

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Documentation](docs/API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPLv3).

- ✅ Free for personal, educational, and non-profit use
- ⚠️ If you use DIBS AI as a service (SaaS), you must:
  - Open-source your modifications (AGPLv3 requirement)
  - OR obtain a commercial license

See [LICENSE](LICENSE) for details.

### Commercial Licensing
For commercial use without open-sourcing requirements:
📧 Email: dibsardiant@gmail.com

---

## 🌐 Links

- **Website:** Coming soon
- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/XdibsAI/DIBS-UMKM/issues)
- **Discussions:** [GitHub Discussions](https://github.com/XdibsAI/DIBS-UMKM/discussions)

---

## 💰 Support & Sponsorship

DIBS AI is open source and free to use. If you find it helpful:

- ⭐ Star this repository
- 🐛 Report bugs
- 💡 Suggest features
- 🔀 Contribute code
- ☕ [Buy me a coffee](https://paypal.me/yourusername)

---

## 🙏 Acknowledgments

- **NVIDIA** - Nemotron 30B API access
- **Ollama** - Local AI runtime
- **Flutter Team** - Cross-platform framework
- **FastAPI** - Modern Python web framework
- **Community Contributors**

---

## 📞 Contact

**DIBS AI Team**
- Email: dibsardiant@gmail.com
- GitHub: [@XdibsAI](https://github.com/XdibsAI)

---

**Built with ❤️ for Indonesian UMKM**

*Empowering small businesses with AI technology*
