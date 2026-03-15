import os
from utgen.generator import TestGeneratorCrew  # La teva lògica de CrewAI
from utgen.validator import validar_test_individual
from utgen.formatter import guardar_i_netejar_tests


class UtgenOrchestrator:
    def __init__(self, output_path="tests/generated/"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

    def run(self, source_code_path):
        print(f"Iniciant generació de tests per a: {source_code_path}")
        
        # 1. GENERACIÓ (CrewAI / RAG)
        # Suposem que el teu generator retorna (imports, cos_del_test)
        generator = TestGeneratorCrew()
        import_code, test_code = generator.kickoff(source_code_path)

        # 2. VALIDACIÓ
        intentos = 0
        max_intentos = 3
        test_es_valid = False

        while not test_es_valid and intentos < max_intentos:
            intentos += 1
            print(f"Validant test (Intent {intentos})...")
            
            # Aquí fem servir la funció amb tempfile que hem millorat
            test_es_valid, logs = validar_test_individual(import_code, test_code)

            if test_es_valid:
                print("El test ha passat la validació!")
                # 3. GUARDAR I NETEJAR
                nom_fitxer = f"test_{os.path.basename(source_code_path)}"
                desti = os.path.join(self.output_path, nom_fitxer)
                
                guardar_i_netejar_tests([(import_code, test_code)], desti)
            else:
                print("El test ha fallat. Re-generant amb feedback...")
                # Aquí podries passar 'logs' (l'error de pytest) a la Crew
                import_code, test_code = generator.fix_test(import_code, test_code, logs)

        if not test_es_valid:
            print("No s'ha pogut generat un test vàlid després de diversos intents.")
