#!/usr/bin/env python3
"""
Extractor de nombres de quests desde los assets del juego (Unity/GameCreator).
Usa strings de resources.assets y el ZIP del juego para encontrar nombres legibles.
"""
import re
import json
import zipfile
import sys
from pathlib import Path

# GUIDs conocidos del save (34 quests)
SAVE_GUIDS = [
    "287a5db7-6cf0-4542-bbc0-cdada612a928",
    "197ca4c5-9149-4318-ad2f-060190f276f6",
    "25f3557c-28fc-4c5b-86b4-2ad14c0af717",
    "c6215ae8-d47d-410e-8590-3aadd1cc5e20",  # Bishop (Mario) - YA CONOCIDO
    "07319a38-9acd-4454-b8f4-e76679115ca4",
    "07aa254d-4d5d-45ce-85a4-e599990cb961",
    "52e14d1a-5267-4068-be12-b271d51f599d",
    "ec67744f-6a9b-49f4-99f4-2771d67ea870",
    "0fe57fbc-fa27-4ca4-913d-4258b975b82e",
    "4d9f5182-032e-4177-afda-23da5753bcd8",
    "338a697e-5ecc-40e3-bf9d-198f4fdeb921",
    "2c8ddbc6-00c2-42e7-bb71-533cd7c40036",
    "48768267-101f-481d-bdfa-9d3d62a0c27f",
    "871deedf-5b82-4b90-bc4b-cd8aca469c6f",
    "a5adcac8-3228-4a59-9b8a-90e879f0d361",
    "fcce107d-4dfd-4319-9fe3-6cc0fd71f828",
    "428e253b-9d44-45dc-a25d-c926409d81c8",
    "a62918db-dbce-4701-842c-a6c1c2dc9a79",
    "4c9f4cf6-6166-419e-8bff-764162da2a93",
    "e62dceac-20c7-4061-9350-3054d6b61381",
    "ac692a71-267a-4f09-8c2b-7c417eb26c68",
    "795a919c-84c7-4038-975d-848386e69b36",
    "dfcd1efd-c811-4538-9240-03a3bcb88c26",
    "0145cd63-56c6-424c-94a6-0593a54fbead",
    "cb45aa4f-fe2b-4cdf-bff0-57538ebf0a7d",
    "33503a53-0933-40ce-93a7-d73cdb63ec97",
    "882a24e7-cf0d-4896-a4da-24802c66ade5",
    "daeb5091-71cd-46ef-af5b-1cb8b47d8c93",
    "d5eeba4d-7942-402a-9cb7-03bcc7a0f689",
    "b5187c70-d03d-42bb-97bb-1830655dba31",
    "8efaa78a-ba3f-45fe-b133-585ac753cddc",
    "c2cfbaab-c5bd-4bac-883b-301edaa44075",
    "9a3d8fdb-417e-4ee6-94a4-52743dfe4cd6",
    "eaeeb2f0-db4e-4e93-b9ef-39a228878dfd",
]

def extract_strings_from_zip(zip_path, output_file):
    """Extrae strings de los archivos .assets dentro del ZIP del juego."""
    print(f"📦 Leyendo ZIP: {zip_path}")
    strings_found = set()
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Buscar archivos .assets
        asset_files = [f for f in zf.namelist() if f.endswith('.assets')]
        print(f"   Encontrados {len(asset_files)} archivos .assets")
        
        for asset_name in asset_files:
            print(f"   Procesando: {asset_name}")
            try:
                data = zf.read(asset_name)
                # Extraer strings legibles (ASCII/UTF-8)
                text = data.decode('utf-8', errors='ignore')
                # Filtrar strings que parecen nombres de quests
                for match in re.finditer(r'[A-Za-z][A-Za-z0-9\s\-\'\.]{3,60}', text):
                    s = match.group().strip()
                    if len(s) >= 4 and any(c.isalpha() for c in s):
                        strings_found.add(s)
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
    
    # Guardar strings únicos
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in sorted(strings_found):
            f.write(s + '\n')
    
    print(f"✅ Strings extraídos: {len(strings_found)} guardados en {output_file}")
    return strings_found

def find_quest_names_in_strings(strings_set, known_guids):
    """Busca en los strings patrones que parezcan nombres de quests y los relaciona con GUIDs."""
    # Patrones típicos de nombres de quests en este juego
    quest_patterns = [
        r'[A-Z][a-z]+(?:\s+[A-Za-z]+)*\s*(?:mission|quest|task)?',
        r'(?:visit|push|help|corrupt|compare|meet|talk|go|find|get|collect|give|use)\s+[A-Za-z\s]+',
    ]
    
    # Filtrar strings que parecen quests
    potential_quests = []
    for s in strings_set:
        s_lower = s.lower()
        # Excluir cosas obvias que no son quests
        if any(skip in s_lower for skip in ['unity', 'shader', 'texture', 'material', 'mesh', 'animation', 
                                              'component', 'script', 'asset', 'prefab', 'scene',
                                              'gameobject', 'transform', 'rigidbody', 'collider',
                                              'audio', 'video', 'particle', 'light', 'camera',
                                              'input', 'ui', 'canvas', 'text', 'image', 'button',
                                              'slider', 'toggle', 'dropdown', 'inputfield']):
            continue
        if len(s) > 60 or len(s) < 4:
            continue
        if re.search(r'^[A-Za-z\s\-\'\.]{4,60}$', s):
            potential_quests.append(s)
    
    print(f"🔍 Posibles nombres de quest: {len(potential_quests)}")
    for q in sorted(potential_quests)[:50]:
        print(f"   - {q}")
    
    return potential_quests

def main():
    zip_path = "/home/jesusgs/proyects/starmaker/game/Starmaker_1_8E_FullGame.zip"
    output = "/home/jesusgs/proyects/starmaker/game_strings.txt"
    
    strings = extract_strings_from_zip(zip_path, output)
    quest_names = find_quest_names_in_strings(strings, SAVE_GUIDS)
    
    # Guardar lista candidata
    with open("/home/jesusgs/proyects/starmaker/candidate_quest_names.txt", 'w', encoding='utf-8') as f:
        for q in quest_names:
            f.write(q + '\n')
    
    print(f"\n📝 Candidatas guardadas en candidate_quest_names.txt")
    print("💡 Ahora revisa manualmente y mapea cada GUID a su nombre real")

if __name__ == "__main__":
    main()