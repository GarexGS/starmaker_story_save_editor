#!/usr/bin/env python3
"""
Starmaker Story Save Editor - CLI Tool
Permite ver y editar el estado de las misiones del juego.
"""
import json
import sys
import argparse
from pathlib import Path

# Mapeo conocido desde bishop_mario.json y strings del juego
KNOWN_QUESTS = {
    "c6215ae8-d47d-410e-8590-3aadd1cc5e20": {
        "name": "Bishop (Mario)",
        "tasks": {
            1813187919: "Help Mario compare files",
            -989935106: "Visit Mario once a week",
            1315981684: "Push Katarina past her limits",
            -1759660069: "Visit Mario",
            1410719678: "Corrupt Emma",
            1070760953: "Visit the sauna every week",
        },
    },
    # Nombres extraídos de los niveles del juego
    "287a5db7-6cf0-4542-bbc0-cdada612a928": {
        "name": "EmmaSaunaMario",
    },
    "197ca4c5-9149-4318-ad2f-060190f276f6": {
        "name": "AnnaCorruptKitchenSex",
    },
    "25f3557c-28fc-4c5b-86b4-2ad14c0af717": {
        "name": "EmmaKatarinaBeachVisit",
    },
    "07319a38-9acd-4454-b8f4-e76679115ca4": {
        "name": "EmmaSaunaDefault",
    },
    "07aa254d-4d5d-45ce-85a4-e599990cb961": {
        "name": "CharlottePhoenixQuestStart",
    },
    "52e14d1a-5267-4068-be12-b271d51f599d": {
        "name": "CharlottePhoenixQuestEnd",
    },
    "ec67744f-6a9b-49f4-99f4-2771d67ea870": {
        "name": "CharlotteAgentQuestStart",
    },
    "0fe57fbc-fa27-4ca4-913d-4258b975b82e": {
        "name": "CharlotteAgentQuestFinale",
    },
    "4d9f5182-032e-4177-afda-23da5753bcd8": {
        "name": "EmmaSaunaSex",
    },
    "338a697e-5ecc-40e3-bf9d-198f4fdeb921": {
        "name": "ChibiCorrupt",
    },
    "2c8ddbc6-00c2-42e7-bb71-533cd7c40036": {
        "name": "CharlottePhoenixQuest",
    },
    "48768267-101f-481d-bdfa-9d3d62a0c27f": {
        "name": "AnnaCorruptKitchenSex",
    },
    "871deedf-5b82-4b90-bc4b-cd8aca469c6f": {
        "name": "EmmaSaunaSex",
    },
    "a5adcac8-3228-4a59-9b8a-90e879f0d361": {
        "name": "EmmaSaunaDefault",
    },
    "fcce107d-4dfd-4319-9fe3-6cc0fd71f828": {
        "name": "AnnaCorruptKitchenSex",
    },
    "428e253b-9d44-45dc-a25d-c926409d81c8": {
        "name": "EmmaSaunaSex",
    },
    "a62918db-dbce-4701-842c-a6c1c2dc9a79": {
        "name": "AnnaCorruptKitchenSex",
    },
    "4c9f4cf6-6166-419e-8bff-764162da2a93": {
        "name": "EmmaSaunaSex",
    },
    "e62dceac-20c7-4061-9350-3054d6b61381": {
        "name": "AnnaCorruptKitchenSex",
    },
    "ac692a71-267a-4f09-8c2b-7c417eb26c68": {
        "name": "EmmaSaunaSex",
    },
    "795a919c-84c7-4038-975d-848386e69b36": {
        "name": "CharlottePhoenixQuestStart",
    },
    "dfcd1efd-c811-4538-9240-03a3bcb88c26": {
        "name": "CharlottePhoenixQuestStart",
    },
    "0145cd63-56c6-424c-94a6-0593a54fbead": {
        "name": "CharlottePhoenixQuestStart",
    },
    "cb45aa4f-fe2b-4cdf-bff0-57538ebf0a7d": {
        "name": "CharlottePhoenixQuestStart",
    },
    "33503a53-0933-40ce-93a7-d73cdb63ec97": {
        "name": "CharlottePhoenixQuestStart",
    },
    "882a24e7-cf0d-4896-a4da-24802c66ade5": {
        "name": "CharlottePhoenixQuest",
    },
    "daeb5091-71cd-46ef-af5b-1cb8b47d8c93": {
        "name": "CharlottePhoenixQuestStart",
    },
    "d5eeba4d-7942-402a-9cb7-03bcc7a0f689": {
        "name": "CharlottePhoenixQuestStart",
    },
    "b5187c70-d03d-42bb-97bb-1830655dba31": {
        "name": "CharlottePhoenixQuestStart",
    },
    "8efaa78a-ba3f-45fe-b133-585ac753cddc": {
        "name": "CharlottePhoenixQuestStart",
    },
    "c2cfbaab-c5bd-4bac-883b-301edaa44075": {
        "name": "CharlottePhoenixQuestStart",
    },
    "9a3d8fdb-417e-4ee6-94a4-52743dfe4cd6": {
        "name": "CharlottePhoenixQuestStart",
    },
    "eaeeb2f0-db4e-4e93-b9ef-39a228878dfd": {
        "name": "CharlottePhoenixQuestStart",
    },
}

def load_save(save_path):
    """Carga el archivo save JSON."""
    with open(save_path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_token_journal(save_data):
    """Encuentra la entrada TokenJournal en el save."""
    for entry in save_data.get("m_Entries", []):
        if "TokenJournal" in entry.get("m_Value", ""):
            return json.loads(entry["m_Value"])
    return None

def get_quests_and_tasks(token_journal):
    """Extrae quests y tasks del TokenJournal."""
    refs = token_journal.get("references", {}).get("RefIds", [])
    quests = []
    tasks = {}
    
    for ref in refs:
        t = ref.get("type", {}).get("class")
        if t == "TokenJournal":
            data = ref.get("data", {})
            # m_Quests - estructura: {m_Keys: [{m_String: "guid"}, ...], m_Values: [{m_State: 2, m_IsTracking: false}, ...]}
            m_quests = data.get("m_Quests", {})
            if isinstance(m_quests, dict) and "m_Keys" in m_quests:
                for i, k in enumerate(m_quests.get("m_Keys", [])):
                    guid = k.get("m_String", "")
                    state = m_quests["m_Values"][i].get("m_State", 0) if i < len(m_quests["m_Values"]) else 0
                    quests.append({"guid": guid, "state": state, "is_tracking": m_quests["m_Values"][i].get("m_IsTracking", False) if i < len(m_quests["m_Values"]) else False})
            else:
                # fallback: lista simple
                for q in data.get("m_Quests", []):
                    if isinstance(q, dict):
                        quests.append({"guid": q.get("m_String", str(q)), "state": 0})
                    else:
                        quests.append({"guid": str(q), "state": 0})
            
            # m_Tasks
            m_tasks = data.get("m_Tasks", {})
            keys = m_tasks.get("m_Keys", [])
            values = m_tasks.get("m_Values", [])
            for k, v in zip(keys, values):
                tasks[k.get("m_TaskId")] = {
                    "quest_hash": k.get("m_QuestHash"),
                    "state": v.get("m_State"),
                    "value": v.get("m_Value"),
                }
    return quests, tasks

def state_name(state):
    return {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(state, f"Desconocido({state})")

def list_quests(save_path):
    """Lista todas las quests y sus tareas con estado actual."""
    data = load_save(save_path)
    tj = find_token_journal(data)
    if not tj:
        print("❌ No se encontró TokenJournal en el save")
        return
    
    quests, tasks = get_quests_and_tasks(tj)
    
    print(f"\n{'='*80}")
    print(f"QUESTS ENCONTRADAS: {len(quests)}")
    print(f"{'='*80}")
    
    for i, q in enumerate(quests):
        q_guid = q.get("guid", "")
        state = q.get("state", 0)
        print(f"\n[{i}] Quest GUID: {q_guid} | Estado: {state_name(state)}")
        known = KNOWN_QUESTS.get(q_guid)
        if known:
            print(f"    Nombre: {known['name']}")
            if "tasks" in known:
                print(f"    Tareas:")
                for task_id, task_name in known["tasks"].items():
                    t = tasks.get(task_id, {})
                    print(f"      {task_id:12} ({state_name(t.get('state', 0)):10}) | {task_name}")
        else:
            print(f"    Nombre: [DESCONOCIDO - buscar en assets]")

def edit_task(save_path, task_id, new_state, new_value=None):
    """Edita el estado de una tarea específica."""
    data = load_save(save_path)
    modified = False
    
    for entry in data.get("m_Entries", []):
        if "TokenJournal" in entry.get("m_Value", ""):
            inner = json.loads(entry["m_Value"])
            refs = inner.get("references", {}).get("RefIds", [])
            for ref in refs:
                if ref.get("type", {}).get("class") == "TokenJournal":
                    tj = ref.get("data", {})
                    m_tasks = tj.get("m_Tasks", {})
                    keys = m_tasks.get("m_Keys", [])
                    values = m_tasks.get("m_Values", [])
                    
                    for i, k in enumerate(keys):
                        if k.get("m_TaskId") == task_id:
                            values[i]["m_State"] = new_state
                            if new_value is not None:
                                values[i]["m_Value"] = new_value
                            print(f"✅ TaskId {task_id} -> State={new_state} ({state_name(new_state)})")
                            modified = True
                    
                    if modified:
                        m_tasks["m_Keys"] = keys
                        m_tasks["m_Values"] = values
                        entry["m_Value"] = json.dumps(inner)
                        break
            break
    
    if modified:
        backup = save_path + ".backup"
        Path(save_path).rename(backup)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Save guardado. Backup en: {backup}")
    else:
        print(f"❌ TaskId {task_id} no encontrado")

DEFAULT_SAVE = "/home/jesusgs/.hermes/cache/documents/doc_44b0013cfacf_SAVE"

def main():
    parser = argparse.ArgumentParser(description="Starmaker Story Save Editor")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    subparsers.add_parser("list", help="Lista quests y tareas")
    
    edit_parser = subparsers.add_parser("edit", help="Edita estado de una tarea")
    edit_parser.add_argument("task_id", type=int, help="TaskId a editar")
    edit_parser.add_argument("state", type=int, choices=[0, 1, 2], 
                           help="Nuevo estado: 0=Inactiva, 1=Activa, 2=Completada")
    edit_parser.add_argument("--value", type=float, help="Nuevo m_Value (opcional)")
    edit_parser.add_argument("--save", type=str, default=DEFAULT_SAVE, help="Ruta al save (opcional)")
    
    args = parser.parse_args()
    
    if args.cmd == "list":
        list_quests(DEFAULT_SAVE)
    elif args.cmd == "edit":
        edit_task(args.save, args.task_id, args.state, args.value)

if __name__ == "__main__":
    main()