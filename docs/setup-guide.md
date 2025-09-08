# Setup Guide

This guide will help you set up the GenAI Stack development environment on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Node.js** (v18+) and **npm** (v8+)
- **Python** (v3.9+) and **pip**
- **Git** (v2.30+)

### Optional but Recommended

- **VS Code** with Python and TypeScript extensions
- **Postman** or similar API testing tool
- **pgAdmin** for database management

### API Keys

You'll need API keys for external services:

1. **OpenAI API Key** (Required)
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key in your dashboard
   - Note: This requires a paid account with credits

2. **Google Gemini API Key** (Optional)
   - Visit [Google AI Studio](https://makersuite.google.com/)
   - Create a new API key

3. **SerpAPI Key** (Optional, for web search)
   - Sign up at [SerpAPI](https://serpapi.com/)
   - Get your API key from the dashboard

## Quick Start (Docker)

The fastest way to get started is using Docker Compose:

### 1. Clone the Repository

