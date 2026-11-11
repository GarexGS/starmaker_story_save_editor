#!/usr/bin/env python3
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "/home/jesusgs/.hermes/cache/documents/doc_44b0013cfacf_SAVE"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Buscar la entrada que contiene TokenJournal
for entry in data.get("m_Entries", []):
    val = entry.get("m_Value", "")
    if "TokenJournal" in val:
        print(f"Entrada encontrada: {entry.get('m_Key')}")
        inner = json.loads(val)
        tokens = inner.get("m_Tokens", [])
        for token in tokens:
            refs = inner.get("references", {}).get("RefIds", [])
            # Buscar el TokenJournal en refs
            for ref in refs:
                if ref.get("type", {}).get("class") == "TokenJournal":
                    quest_data = ref.get("data", {}).get("m_Quests", {})
                    task_data = ref.get("data", {}).get("m_Tasks", {})
                    
                    keys = quest_data.get("m_Keys", [])
                    values = quest_data.get("m_Values", [])
                    print(f"\n=== Quests ({len(keys)}) ===")
                    for i, (k, v) in enumerate(zip(keys, values)):
                        state = v.get("m_State", 0)
                        tracking = v.get("m_IsTracking", False)
                        state_name = {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(state, f"Desconocido({state})")
                        print(f"  [{i}] {k} -> {state_name} (tracking={tracking})")
                    
                    task_keys = task_data.get("m_Keys", [])
                    task_values = task_data.get("m_Values", [])
                    print(f"\n=== Tasks ({len(task_keys)}) ===")
                    for i, (k, v) in enumerate(zip(task_keys, task_values)):
                        qhash = k.get("m_QuestHash", 0)
                        task_id = k.get("m_TaskId", 0)
                        state = v.get("m_State", 0)
                        value = v.get("m_Value", 0.0)
                        state_name = {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(state, f"Desconocido({state})")
                        print(f"  [{i}] QuestHash={qhash} TaskId={task_id} -> {state_name} (valor={value})")
                    break
        break