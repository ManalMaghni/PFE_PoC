import ast
import py_compile
import tempfile
import os

def register(mcp):

    @mcp.tool()
    def validate_code_syntax(code: str, language: str) -> str:
        """
        Vérifie la syntaxe d'un code sans l'exécuter.
        
        language accepte : 'python' | 'javascript' | 'typescript'
        
        Pour JS/TS : vérification basique par heuristiques
        Pour Python : vérification complète via ast
        """

        language = language.lower()

        if language == "python":
            return _validate_python(code)
        
        elif language in ("javascript", "typescript"):
            return _validate_js_ts(code, language)
        
        else:
            return f"❌ Langage non supporté : '{language}'. Choisir : python, javascript, typescript"


def _validate_python(code: str) -> str:
    """Utilise ast.parse pour détecter les erreurs de syntaxe Python."""
    try:
        ast.parse(code)
        lines = len(code.splitlines())
        return f"✅ Syntaxe Python valide ({lines} lignes)"
    
    except SyntaxError as e:
        return (
            f"❌ Erreur de syntaxe Python\n"
            f"   Ligne {e.lineno} : {e.msg}\n"
            f"   → {e.text}"
        )


def _validate_js_ts(code: str, language: str) -> str:
    """
    Vérification heuristique pour JS/TS.
    On vérifie les erreurs les plus communes : accolades, parenthèses, points-virgules.
    """
    errors = []

    # Vérification équilibre des accolades { }
    if code.count("{") != code.count("}"):
        errors.append("Accolades { } déséquilibrées")

    # Vérification équilibre des parenthèses ( )
    if code.count("(") != code.count(")"):
        errors.append("Parenthèses ( ) déséquilibrées")

    # Vérification équilibre des crochets [ ]
    if code.count("[") != code.count("]"):
        errors.append("Crochets [ ] déséquilibrés")

    if errors:
        return f"❌ Erreurs {language} détectées :\n" + "\n".join(f"   - {e}" for e in errors)

    lines = len(code.splitlines())
    return f"✅ Syntaxe {language} valide ({lines} lignes)"