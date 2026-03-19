import os

def register(mcp):

    @mcp.tool()
    def generate_dockerfile(project_path: str) -> str:
        """
        Analyse un projet et génère Dockerfile + docker-compose.yml adaptés.
        
        Détecte automatiquement le type de projet :
        - requirements.txt → FastAPI
        - package.json     → React
        - les deux         → Fullstack
        
        project_path doit être un chemin absolu sous /workspace
        """

        if not project_path.startswith("/workspace"):
            return "❌ Interdit : le chemin doit être sous /workspace"

        if not os.path.exists(project_path):
            return f"❌ Dossier introuvable : {project_path}"

        # Détection du type de projet
        has_requirements = os.path.exists(f"{project_path}/requirements.txt")
        has_package_json = os.path.exists(f"{project_path}/package.json")
        has_backend      = os.path.exists(f"{project_path}/backend/requirements.txt")
        has_frontend     = os.path.exists(f"{project_path}/frontend/package.json")

        # Fullstack (backend/ + frontend/)
        if has_backend and has_frontend:
            return _generate_fullstack(project_path)

        # FastAPI seul
        elif has_requirements:
            return _generate_fastapi(project_path)

        # React seul
        elif has_package_json:
            return _generate_react(project_path)

        else:
            return "❌ Type de projet non détecté (requirements.txt ou package.json introuvable)"


def _generate_fastapi(path: str) -> str:
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    compose = """services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
"""

    _write(path, "Dockerfile", dockerfile)
    _write(path, "docker-compose.yml", compose)

    return (
        f"✅ Fichiers Docker générés pour FastAPI dans {path}\n"
        f"📄 Dockerfile\n"
        f"📄 docker-compose.yml"
    )


def _generate_react(path: str) -> str:
    dockerfile = """FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""

    compose = """services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
"""

    _write(path, "Dockerfile", dockerfile)
    _write(path, "docker-compose.yml", compose)

    return (
        f"✅ Fichiers Docker générés pour React dans {path}\n"
        f"📄 Dockerfile\n"
        f"📄 docker-compose.yml"
    )


def _generate_fullstack(path: str) -> str:
    # Dockerfile backend
    dockerfile_backend = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    # Dockerfile frontend
    dockerfile_frontend = """FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""

    # docker-compose global
    compose = """services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
"""

    _write(f"{path}/backend", "Dockerfile", dockerfile_backend)
    _write(f"{path}/frontend", "Dockerfile", dockerfile_frontend)
    _write(path, "docker-compose.yml", compose)

    return (
        f"✅ Fichiers Docker générés pour Fullstack dans {path}\n"
        f"📄 backend/Dockerfile\n"
        f"📄 frontend/Dockerfile\n"
        f"📄 docker-compose.yml"
    )


def _write(directory: str, filename: str, content: str):
    """Fonction utilitaire pour écrire un fichier."""
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), "w") as f:
        f.write(content)