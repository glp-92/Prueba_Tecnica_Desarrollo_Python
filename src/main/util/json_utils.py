import json, os

def load_json_file(json_file_path: str) -> dict:
    """
        Carga de fichero json a diccionario desde una ruta dada
    """
    json_file = None
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
                json_file = json.load(f)
    return json_file

def export_json_file(json_file_path: str, json_data: dict) -> bool:
    """
        Se exporta un diccionario a un fichero .json en la ruta dada por json_file_path
    """
    err = 0
    try:
        with open(json_file_path, 'w') as file:
            json.dump(json_data, file, indent=4)
    except:
        err = 1
    return err