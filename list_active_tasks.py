#!/usr/bin/env python3
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "/home/jesusgs/.hermes/cache/documents/doc_44b0013cfacf_SAVE"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for entry in data.get("m_Entries", []):
    val = entry.get("m_Value", "")
    if "TokenJournal" in val:
        inner = json.loads(val)
        refs = inner.get("references", {}).get("RefIds", [])
        for ref in refs:
            if ref.get("type", {}).get("class") == "TokenJournal":
                task_data = ref.get("data", {}).get("m_Tasks", {})
                task_keys = task_data.get("m_Keys", [])
                task_values = task_data.get("m_Values", [])
                print(f"Tasks activos ({sum(1 for v in task_values if v.get('m_State') == 1)}):")
                for i, (k, v) in enumerate(zip(task_keys, task_values)):
                    state = v.get("m_State", 0)
                    if state == 1:
                        qhash = k.get("m_QuestHash", 0)
                        task_id = k.get("m_TaskId", 0)
                        value = v.get("m_Value", 0.0)
                        print(f"  [{i}] QuestHash={qhash}, TaskId={task_id}, valor={value}")
                break
        break