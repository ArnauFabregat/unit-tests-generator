import subprocess
import os

def validar_test_individual(import_code, test_code):
    """
    Prova un test en un fitxer temporal. 
    Retorna True si el test passa, False si no.
    """
    temp_filename = "temp_validation.py"
    full_code = f"{import_code}\n\n{test_code}"

    with open(temp_filename, "w") as f:
        f.write(full_code)
    
    # Executem pytest. -q per silenci, --tb=no per no embrutar la consola
    result = subprocess.run(["pytest", temp_filename, "-q", "--tb=no"], capture_output=True)
    
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        
    return result.returncode == 0

def guardar_i_netejar_tests(tests_valids, desti="../tests/test_generats_llm.py"):
    """
    tests_valids: Llista de tuples [(import, codi), ...]
    """
    if not tests_valids:
        print("No hi ha tests vàlids per guardar.")
        return

    os.makedirs(os.path.dirname(desti), exist_ok=True)

    # 1. SEPAREM EN DOS BLOCS
    bloc_imports = []
    bloc_tests = []
    
    for imp, code in tests_valids:
        bloc_imports.append(imp.strip())
        bloc_tests.append(code.strip())
    
    # 2. CONCATENEM: primer TOTS els imports, després els tests
    contingut_final = "\n".join(bloc_imports) + "\n\n" + "\n\n".join(bloc_tests)

    with open(desti, "w") as f:
        f.write(contingut_final)

    # 2. Passem Ruff per endreçar-ho tot
    print(f"Netejant {desti} amb Ruff...")
    
    # Ordenar imports i eliminar duplicats (isort)
    subprocess.run(["ruff", "check", "--select", "I", "--fix", desti], capture_output=True)
    # # Eliminar variables/imports no usats i altres errors comuns
    subprocess.run(["ruff", "check", "--fix", desti], capture_output=True)
    # # Formatar codi (estil Black)
    subprocess.run(["ruff", "format", desti], capture_output=True)
    
    print(f"✅ Procés finalitzat. Fitxer guardat a: {desti}")
