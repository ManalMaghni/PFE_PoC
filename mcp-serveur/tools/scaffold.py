import os

def register(mcp):

    @mcp.tool()
    def scaffold_project(project_name: str, project_type: str) -> str:
        """
        Génère une arborescence de projet vide avec fichiers de base.
        
        project_type accepte : 'fastapi' | 'react' | 'fullstack'
        Les fichiers sont créés dans /workspace/<project_name>
        """

        base = f"/workspace/{project_name}"

        # Structure selon le type de projet
        structures = {
            "fastapi": {
                "dirs": ["app/routers", "app/models", "app/schemas", "tests"],
                "files": {
                    "app/__init__.py": "",
                    "app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n",
                    "app/routers/__init__.py": "",
                    "app/models/__init__.py": "",
                    "app/schemas/__init__.py": "",
                    "tests/__init__.py": "",
                    "tests/test_main.py": "# Ajouter les tests ici\n",
                    "requirements.txt": "fastapi\nuvicorn\n",
                    "README.md": f"# {project_name}\n",
                }
            },
            "react": {
                "dirs": ["src/components", "src/pages", "src/hooks", "public"],
                "files": {
                    "src/App.jsx": "export default function App() {\n  return <div>Hello</div>\n}\n",
                    "src/main.jsx": "import React from 'react'\nimport App from './App'\n",
                    "public/index.html": "<!DOCTYPE html><html><body><div id='root'></div></body></html>\n",
                    "package.json": '{"name": "' + project_name + '", "version": "1.0.0"}\n',
                    "README.md": f"# {project_name}\n",
                }
            },
            "fullstack": {
                "dirs": [
                    "backend/app/routers", "backend/app/models",
                    "backend/tests",
                    "frontend/src/components", "frontend/src/pages",
                    "frontend/public"
                ],
                "files": {
                    "backend/app/__init__.py": "",
                    "backend/app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n",
                    "backend/requirements.txt": "fastapi\nuvicorn\n",
                    "frontend/public/index.html": "<!DOCTYPE html><html><body><div id='root'></div></body></html>\n",
                    "frontend/src/App.jsx": "export default function App() {\n  return <div>Hello</div>\n}\n",
                    "frontend/package.json": '{"name": "' + project_name + '-frontend", "version": "1.0.0"}\n',
                    "README.md": f"# {project_name}\n",
                    "docker-compose.yml": "services:\n  backend:\n  frontend:\n",
                }
            }
        }

        if project_type not in structures:
            return f"❌ Type inconnu : '{project_type}'. Choisir parmi : fastapi, react, fullstack"

        structure = structures[project_type]

        # Création des dossiers
        for d in structure["dirs"]:
            os.makedirs(os.path.join(base, d), exist_ok=True)

        # Création des fichiers
        created = []
        for filepath, content in structure["files"].items():
            full_path = os.path.join(base, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
            created.append(filepath)

        return (
            f"✅ Projet '{project_name}' ({project_type}) créé dans /workspace/{project_name}\n"
            f"📁 Dossiers : {len(structure['dirs'])}\n"
            f"📄 Fichiers : {', '.join(created)}"
        )