# 🌿 EcoSort-AI

> **AI-Powered Waste Classification for a Sustainable Future**

[![Azure Static Web Apps](https://img.shields.io/badge/Azure-Static%20Web%20Apps-0078D4?logo=microsoft-azure)](https://azure.microsoft.com/services/app-service/static/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

EcoSort-AI is a production-ready GenAI application that uses Google Gemini 2.5 Flash to classify waste items through image recognition, helping users make better recycling decisions.

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

- 📸 **Real-time Image Classification** - Upload or capture waste images for instant categorization
- 🤖 **Gemini 2.5 Flash Integration** - Leverages Google's latest multimodal AI model
- ♻️ **Smart Recycling Guidance** - Provides disposal recommendations based on local regulations
- 🌍 **Multi-language Support** - Accessible in multiple languages
- 📊 **Analytics Dashboard** - Track your recycling impact over time
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
| Frontend | Streamlit 1.40+ |
| AI/ML | Google Gemini 2.5 Flash |
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
   streamlit run app/main.py
   ```

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
