# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of EcoSort-AI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@your-org.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., SQL injection, XSS, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Resolution Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

## Security Best Practices

### For Contributors

1. **Never commit secrets** - Use environment variables
2. **Keep dependencies updated** - Run `safety check` regularly
3. **Use HTTPS** - All API calls must use HTTPS
4. **Validate inputs** - Sanitize all user inputs
5. **Follow least privilege** - Request minimum permissions

### For Users

1. **Protect API keys** - Store in Azure Key Vault in production
2. **Use OIDC authentication** - Avoid long-lived credentials
3. **Enable logging** - Monitor for suspicious activity
4. **Regular updates** - Keep dependencies current

## Security Tools

This project uses the following security tools:

- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner
- **GitHub Dependabot** - Automated dependency updates
- **CodeQL** - Semantic code analysis

## Acknowledgments

We thank the following individuals for responsibly disclosing vulnerabilities:

- *Your name could be here!*

---

Thank you for helping keep EcoSort-AI and our users safe! 🔒
