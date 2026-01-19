# 🌿 EcoSort-AI

> **AI-Powered Waste Classification for a Sustainable Future**

[![Azure Static Web Apps](https://img.shields.io/badge/Azure-Static%20Web%20Apps-0078D4?logo=microsoft-azure)](https://azure.microsoft.com/services/app-service/static/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.0%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

EcoSort-AI is a production-ready GenAI application that uses Google Gemini 2.0 Flash to classify waste items through image recognition and **live webcam detection**, helping users make better recycling decisions.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

---

## ✨ Features

- 📸 **Image Upload Classification** - Upload waste images for instant AI-powered categorization
- 📹 **Live Webcam Detection** - Real-time object detection with bounding boxes via WebRTC
- 🤖 **Gemini 2.0 Flash Integration** - Leverages Google's multimodal AI model for accurate detection
- 🎯 **Bounding Box Visualization** - Color-coded boxes showing detected items and categories
- ♻️ **Smart Recycling Guidance** - Provides disposal recommendations for each detected item
- ⚙️ **Adjustable Detection Speed** - Configurable detection interval (1-10 seconds)
- 🔒 **Enterprise Security** - Azure Key Vault integration for secrets management

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              User Interface                              │
│                         (Streamlit Frontend)                            │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Azure Static Web App                            │
│                    (Hosting & Global Distribution)                      │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│     AI Engine Module      │   │    Azure Key Vault        │
│  (Gemini 2.5 Flash API)   │   │   (Secrets Management)    │
└───────────────────────────┘   └───────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit 1.53+ |
| Live Video | streamlit-webrtc, WebRTC |
| Image Processing | OpenCV, Pillow |
| AI/ML | Google Gemini 2.0 Flash |
| Cloud Platform | Microsoft Azure |
| Infrastructure | Azure Bicep (IaC) |
| CI/CD | GitHub Actions |
| Secrets | Azure Key Vault |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure CLI (for deployment)
- Google Cloud account with Gemini API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/EcoSort-AI.git
   cd EcoSort-AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run app/main.py --server.port 8509
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8509`
   - Use **Upload Image** tab for static image classification
   - Use **Live Camera** tab for real-time webcam detection with bounding boxes

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ |
| `AZURE_KEY_VAULT_URL` | Azure Key Vault URL | ❌ |
| `APP_ENV` | Environment (dev/staging/prod) | ❌ |

See [.env.example](.env.example) for all configuration options.

---

## 🚢 Deployment

### Azure Deployment

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Deploy infrastructure**
   ```bash
   az deployment group create \
     --resource-group rg-ecosort-ai \
     --template-file infra/main.bicep \
     --parameters infra/params.json
   ```

3. **Deploy application** via GitHub Actions (automatic on push to `main`)

---

## 📚 API Reference

See [PROMPTS.md](PROMPTS.md) for detailed AI prompt documentation.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

## 🔒 Security

For security concerns, please see our [Security Policy](SECURITY.md).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with 💚 for a sustainable future
</p>
