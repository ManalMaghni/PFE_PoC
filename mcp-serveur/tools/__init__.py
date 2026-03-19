# Ce fichier importe et enregistre tous les outils sur l'instance mcp
# Tu décommentes chaque import au fur et à mesure que tu ajoutes les fichiers

def register_all_tools(mcp):
    from .scaffold         import register as register_scaffold
    from .file_writer      import register as register_file_writer
    from .syntax_validator import register as register_syntax_validator
    from .dockerfile_gen   import register as register_dockerfile_gen
    from .test_runner      import register as register_test_runner
    from .api_extractor    import register as register_api_extractor
    from .dep_resolver     import register as register_dep_resolver

    register_scaffold(mcp)
    register_file_writer(mcp)
    register_syntax_validator(mcp)
    register_dockerfile_gen(mcp)
    register_test_runner(mcp)
    register_api_extractor(mcp) 
    register_dep_resolver(mcp)  
    