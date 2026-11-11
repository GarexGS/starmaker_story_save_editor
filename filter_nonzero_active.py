#!/usr/bin/env python3
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "./save.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for entry in data.get("m_Entries", []):
    val = entry.get("m_Value", "")
    if "TokenJournal" in val:
        inner = json.loads(val)
        task_data = inner.get("references", {}).get("RefIds", [])
        for ref in task_data:
            if ref.get("type", {}).get("class") == "TokenJournal":
                tasks_dict = ref.get("data", {}).get("m_Tasks", {})
                keys = tasks_dict.get("m_Keys", [])
                values = tasks_dict.get("m_Values", [])
                print("=== Tasks con valor != 0.0 (activo) ===")
                for i, (k, v) in enumerate(zip(keys, values)):
                    state = v.get("m_State", 0)
                    qhash = k.get("m_QuestHash", 0)
                    task_id = k.get("m_TaskId", 0)
                    val = v.get("m_Value", 0.0)
                    if val != 0.0:
                        print(f"  [{i}] QuestHash={qhash}, TaskId={task_id}, valor={val}")
                print("=== Activos solo (state=1) ===")
                for i, (k, v) in enumerate(zip(keys, values)):
                    state = v.get("m_State", 0)
                    if state == 1:
                        qhash = k.get("m_QuestHash", 0)
                        task_id = k.get("m_TaskId", 0)
                        val = v.get("m_Value", 0.0)
                        print(f"  [{i}] QuestHash={qhash}, TaskId={task_id}, valor={val}")
                break
        break