import ast
import os
import json

def register(mcp):

    @mcp.tool()
    def extract_api_contract(filepath: str) -> str:
        """
        Analyse un fichier FastAPI et extrait toutes les routes HTTP.
        
        Retourne un contrat d'API JSON avec : méthode, route, paramètres.
        filepath doit être un chemin absolu sous /workspace
        
        Exemple: filepath="/workspace/my-app/app/main.py"
        """

        if not filepath.startswith("/workspace"):
            return "❌ Interdit : le chemin doit être sous /workspace"

        if not os.path.exists(filepath):
            return f"❌ Fichier introuvable : {filepath}"

        with open(filepath, "r") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return f"❌ Erreur de syntaxe dans le fichier : {e}"

        routes = []

        # Parcourt tous les noeuds de l'AST
        for node in ast.walk(tree):

            # On cherche les fonctions décorées
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            for decorator in node.decorator_list:

                # Détecte @app.get("/route") ou @router.post("/route")
                if not isinstance(decorator, ast.Call):
                    continue

                if not isinstance(decorator.func, ast.Attribute):
                    continue

                method = decorator.func.attr.upper()

                # On ne garde que les méthodes HTTP connues
                if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                    continue

                # Extrait le chemin de la route (premier argument)
                route = "unknown"
                if decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant):
                        route = arg.value

                # Extrait les paramètres de la fonction
                params = [
                    arg.arg for arg in node.args.args
                    if arg.arg != "self"
                ]

                routes.append({
                    "method": method,
                    "route": route,
                    "function": node.name,
                    "params": params
                })

        if not routes:
            return "ℹ️ Aucune route HTTP détectée dans ce fichier"

        contract = json.dumps(routes, indent=2)
        # Sauvegarde le contrat dans le même dossier que le fichier analysé
        contract_path = os.path.join(os.path.dirname(filepath), "api_contract.json")
        with open(contract_path, "w") as f:
            f.write(contract)

        return f"✅ {len(routes)} route(s) détectée(s) et sauvegardées dans {contract_path}:\n\n{contract}"