import ast
import os
import sys

def register(mcp):

    @mcp.tool()
    def dependency_resolver(project_path: str) -> str:
        """
        Scanne tous les fichiers Python d'un projet et génère requirements.txt.
        
        Détecte les imports externes (non stdlib) et les sauvegarde
        dans requirements.txt à la racine du projet.
        
        project_path doit être un chemin absolu sous /workspace
        """

        if not project_path.startswith("/workspace"):
            return "❌ Interdit : le chemin doit être sous /workspace"

        if not os.path.exists(project_path):
            return f"❌ Dossier introuvable : {project_path}"

        # Récupère tous les modules de la stdlib Python
        stdlib_modules = sys.stdlib_module_names

        imports = set()

        # Parcourt récursivement tous les fichiers .py du projet
        for root, dirs, files in os.walk(project_path):

            # Ignore les dossiers inutiles
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", "node_modules", ".git")]

            for file in files:
                if not file.endswith(".py"):
                    continue

                filepath = os.path.join(root, file)

                with open(filepath, "r", errors="ignore") as f:
                    source = f.read()

                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    continue  # Ignore les fichiers avec erreurs

                # Extrait les imports
                for node in ast.walk(tree):

                    # import fastapi
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Prend uniquement le nom de base (ex: "fastapi" de "fastapi.routing")
                            base = alias.name.split(".")[0]
                            imports.add(base)

                    # from fastapi import FastAPI
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            base = node.module.split(".")[0]
                            imports.add(base)

        # Filtre : garde uniquement les packages externes (pas stdlib, pas locaux)
        local_packages = _get_local_packages(project_path)
        
        external = sorted([
            pkg for pkg in imports
            if pkg not in stdlib_modules
            and pkg not in local_packages
            and not pkg.startswith("_")
        ])

        if not external:
            return "ℹ️ Aucune dépendance externe détectée"

        # Génère le requirements.txt
        content = "\n".join(external) + "\n"
        req_path = os.path.join(project_path, "requirements.txt")

        with open(req_path, "w") as f:
            f.write(content)

        return (
            f"✅ {len(external)} dépendance(s) détectée(s) et sauvegardées dans {req_path}\n\n"
            f"📦 Packages :\n" + "\n".join(f"  - {p}" for p in external)
        )


def _get_local_packages(project_path: str) -> set:
    """Retourne les noms des dossiers locaux du projet (modules internes)."""
    local = set()
    for item in os.listdir(project_path):
        if os.path.isdir(os.path.join(project_path, item)):
            local.add(item)
    return local