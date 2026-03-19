import os

def register(mcp):

    @mcp.tool()
    def write_file_safe(filepath: str, content: str) -> str:
        """
        Écrit un fichier avec vérification de sécurité.
        
        - Crée les dossiers intermédiaires automatiquement
        - Détecte si le fichier existe déjà et retourne un diff
        - filepath doit être un chemin absolu sous /workspace
        
        Exemple: filepath="/workspace/my-app/app/main.py"
        """

        # Sécurité : on n'écrit que dans /workspace
        if not filepath.startswith("/workspace"):
            return "❌ Interdit : le chemin doit être sous /workspace"

        file_exists = os.path.exists(filepath)
        old_content = ""

        # Si le fichier existe, on lit l'ancien contenu pour le diff
        if file_exists:
            with open(filepath, "r") as f:
                old_content = f.read()

        # Création des dossiers intermédiaires si nécessaire
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Écriture du fichier
        with open(filepath, "w") as f:
            f.write(content)

        # Retour différent selon création ou modification
        if not file_exists:
            return f"✅ Fichier créé : {filepath}"
        
        if old_content == content:
            return f"ℹ️ Aucun changement : {filepath}"

        # Calcul simple du diff (lignes ajoutées/supprimées)
        old_lines = set(old_content.splitlines())
        new_lines = set(content.splitlines())
        added   = new_lines - old_lines
        removed = old_lines - new_lines

        return (
            f"✏️ Fichier modifié : {filepath}\n"
            f"+ {len(added)} lignes ajoutées\n"
            f"- {len(removed)} lignes supprimées"
        )