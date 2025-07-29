# 🚀 RAG App

A lightweight Retrieval-Augmented Generation (RAG) application built with FastAPI. This app supports semantic search, environment management with Miniconda, and easy deployment for development and experimentation.

---

## 🧰 Requirements

- Python 3.10 or later
- `libpq-dev`, `gcc`, `python3-dev` (for compilation of certain dependencies)

---

## 🐍 Python Environment Setup (Miniconda)

1. **Download & Install Miniconda**  
   Get Miniconda from the [official website](https://www.anaconda.com/docs/main#quick-command-line-install)

2. **Create a new environment**

   ```bash
   conda create -n mini-rag python=3.10
   ```

3. **Activate the environment**

   ```bash
   conda activate mini-rag
   ```

---

## 📦 System Package Installation (Ubuntu/Debian)

Make sure the following system-level dependencies are installed:

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

---

## 📥 Project Installation

1. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment variables**

   ```bash
   cp env.example .env
   ```

   Then edit the `.env` file and set your environment variables. For example:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

---

## 🚀 Run the FastAPI Server

Start the development server on port `5000`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

## 🧼 Optional: Make Terminal Prompt Cleaner

To make your terminal prompt cleaner and more readable:

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```