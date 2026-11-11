#!/usr/bin/env python3
"""
Extrae nombres de misiones y sus datos desde resources.assets del juego.
Para usar como base del mapeo QuestHash -> Nombre de misión.
"""
import re
import json
import sys

# Archivo generado previamente por strings
STRINGS_PATH = "/tmp/strings_out.txt"

def extract_quest_names(strings_path):
    """Extrae nombres de misiones relacionadas con personajes principales."""
    quest_names = set()
    character_keywords = ["mario", "katarina", "emma", "sofia", "josef", "quest", "task"]
    
    with open(strings_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line_lower = line.lower()
        # Filtrar nombres que parezcan identificadores de misiones
        if any(kw in line_lower for kw in character_keywords):
            # Evitar strings muy largos o JSON/código
            if len(line) > 0 and len(line) < 100:
                quest_names.add(line)
    
    return sorted(quest_names)

def save_mapping(names, output_path):
    """Guarda un mapeo inicial vacío que el usuario puede completar."""
    mapping = {}
    for name in names:
        mapping[name] = {
            "quest_hash": None,
            "task_ids": [],
            "description": name
        }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    names = extract_quest_names(STRINGS_PATH)
    print(f"Se encontraron {len(names)} nombres de misiones/caracteres:")
    for n in names[:30]:
        print(f"  - {n}")
    if len(names) > 30:
        print(f"  ... y {len(names) - 30} más")
    
    output_path = sys.argv[1] if len(sys.argv) > 1 else "/home/jesusgs/proyects/starmaker/quests_mapping.json"
    save_mapping(names, output_path)
    print(f"\nMapeo guardado en: {output_path}")