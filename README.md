# AI Web Chatbot - FastAPI Environment

## Project Overview
This project is specifically designed for **FastAPI applications**, providing students with a **streamlined development environment** so they can focus on learning **FastAPI** without worrying about setup configurations.  
It includes the necessary **dependencies** and **services**, making the development process faster and more intuitive.

## Prerequisites
Ensure you have the following software installed:
- **Git**
- **Docker Desktop** or **Docker Engine**

## Project Structure
The project adopts a **modular structure**, with the following key components:
```
root/
│── requirements.txt   # Python dependencies for FastAPI
│── Dockerfile         # Docker image configuration for FastAPI application
│── docker-compose.yaml # Docker Compose setup
│── app/               # FastAPI application source code
│   ├── main.py        # Main FastAPI application
│   ├── routers/      
│   │   ├── chat.py        # Chat handling router
│   │   ├── session.py     # Session management router
│   │   ├── message.py     # Message management router
│   ├── services/      # Application service layer
│   │   ├── chat_service.py
│   │   ├── session_service.py
│   │   ├── message_service.py
│   ├── database/      # Data access layer (DAL)
│   │   ├── session_dal.py
│   │   ├── message_dal.py
```

## Setup & Execution
Follow these steps to set up and run the project:

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Start the application using Docker Compose**
   ```bash
   docker-compose up --build -d
   ```

3. **Build the Hello World FastAPI application**
   - Create `fastapi-env/app/main.py`
   - Add the following FastAPI base code:
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   async def root():
       return {"message": "Hello World"}
   ```
   - Start the FastAPI application and access it at:  
     **`http://localhost:8080`**

## Docker Configuration (Dockerfile)
The Dockerfile configures the **FastAPI environment**, including the following steps:
- Uses the official Python base image
- Sets the working directory
- Copies necessary files
- Installs Python dependencies
- Specifies the application startup command

## Docker Compose (docker-compose.yaml)
The `docker-compose.yaml` file defines **FastAPI services**, including:
- **FastAPI application service** (built from the Dockerfile)
- **Environment variables and port mapping**
- **PostgreSQL database service** and **PGAdmin4 management tool**

## API Routing Overview
This project provides an **Ollama API** to enable chatbot **message management**:
- **Session**
  - `POST /sessions/` ➝ Create a new session
  - `GET /sessions/?session_id=X` ➝ Retrieve specific session details
  - `PUT /sessions/{id}` ➝ Modify session title
  - `DELETE /sessions/{id}` ➝ Delete session
- **Message**
  - `POST /messages/` ➝ Add a message (requires valid session)
  - `GET /messages/?session_id=X` ➝ List all messages for the specified session
- **Chat**
  - `POST /chat/` ➝ Interact with the chatbot
  - `GET /chat/stream=True` ➝ Receive responses in streaming mode
