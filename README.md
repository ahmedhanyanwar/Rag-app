# 🚀 RAG App

A lightweight Retrieval-Augmented Generation (RAG) application built with FastAPI. This app supports semantic search, environment management with Miniconda, and easy deployment for development and experimentation.

---

## 🧰 Requirements

- Python 3.10 or later  
- `libpq-dev`, `gcc`, `python3-dev` (for building certain Python packages)

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

Install system-level dependencies:

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

   Then open the `.env` file and configure required variables, e.g.:

   ```env
   OPENAI_API_KEY=your_openai_key
   ```

---

## 🚀 Run the FastAPI Server

Start the development server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

## 🐳 Docker Setup (Optional)

Run the app with Docker (for local development)

1. **Install Docker Desktop**  
   - [Download Docker](https://www.docker.com/products/docker-desktop/) and ensure it's running.

2. **Navigate to the Docker setup folder**

   ```bash
   cd docker
   ```

3. **Copy and configure environment variables**

   ```bash
   cp env.example .env
   ```

   Then edit `.env` to set your Docker container values:

   ```env
   MONGO_INITDB_ROOT_USERNAME=your_username
   MONGO_INITDB_ROOT_PASSWORD=your_password
   ```

4. **Run Docker Compose**

   ```bash
   docker compose up --build
   ```

> 📌 Ensure ports in your Docker Compose file do not conflict with other services.

---

## 🧼 Optional: Clean Terminal Prompt

Make the terminal prompt more readable:

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```
