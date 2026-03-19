import subprocess
import os

def register(mcp):

    @mcp.tool()
    def run_tests_in_sandbox(test_path: str) -> str:
        """
        Exécute un fichier de tests pytest dans un subprocess isolé.
        
        Retourne le rapport complet : tests passés, échoués, erreurs.
        test_path doit être un chemin absolu sous /workspace
        
        Exemple: test_path="/workspace/my-app/tests/test_main.py"
        """

        if not test_path.startswith("/workspace"):
            return "❌ Interdit : le chemin doit être sous /workspace"

        if not os.path.exists(test_path):
            return f"❌ Fichier introuvable : {test_path}"

        if not test_path.endswith(".py"):
            return "❌ Le fichier doit être un fichier Python (.py)"

        try:
            # Lance pytest dans un subprocess isolé
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
                capture_output=True,   # capture stdout et stderr
                text=True,             # retourne du texte, pas des bytes
                timeout=30,            # timeout 30 secondes max
                cwd=os.path.dirname(test_path)  # exécute depuis le dossier du fichier
            )

            # Combine stdout et stderr
            output = result.stdout + result.stderr

            # Résultat selon le code de retour pytest
            # 0 = tous passent, 1 = certains échouent, 2+ = erreur
            if result.returncode == 0:
                return f"✅ Tous les tests passent !\n\n{output}"
            
            elif result.returncode == 1:
                return f"❌ Certains tests échouent :\n\n{output}"
            
            else:
                return f"⚠️ Erreur d'exécution pytest :\n\n{output}"

        except subprocess.TimeoutExpired:
            return "⏱️ Timeout : les tests ont pris plus de 30 secondes"
        
        except Exception as e:
            return f"❌ Erreur inattendue : {str(e)}"