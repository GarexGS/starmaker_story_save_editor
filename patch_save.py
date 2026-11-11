#!/usr/bin/env python3
import json, sys

def patch_save(save_path, task_ids_to_complete):
    """Marca tareas específicas como completadas (State=2)."""
    import gzip
    with open(save_path, "rb") as f:
        magic = f.read(2)
    if magic == b"\x1f\x8b":
        with gzip.open(save_path, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
    else:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    # Encontrar TokenJournal
    for entry in data.get("m_Entries", []):
        if "TokenJournal" in entry.get("m_Value", ""):
            inner = json.loads(entry["m_Value"])
            refs = inner.get("references", {}).get("RefIds", [])
            for ref in refs:
                if ref.get("type", {}).get("class") == "TokenJournal":
                    tj = ref.get("data", {})
                    tasks = tj.get("m_Tasks", {})
                    keys = tasks.get("m_Keys", [])
                    values = tasks.get("m_Values", [])
                    
                    # Parchear cada tarea solicitada
                    for target_id in task_ids_to_complete:
                        for i, k in enumerate(keys):
                            if k.get("m_TaskId") == target_id:
                                v = values[i]
                                v["m_State"] = 2  # Completada
                                v["m_Value"] = 0.0
                                print(f"Parcheado: TaskId={target_id} -> State=2, Value=0.0")
                    
                    # Reconstruir m_Tasks
                    tasks["m_Keys"] = keys
                    tasks["m_Values"] = values
                    entry["m_Value"] = json.dumps(inner)
                    print(f"Save parcheado exitosamente: {save_path}")
                    break
            break
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ Parcheo completado. Ahora puedes comprimir a .gz y reemplazar el save.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 patch_save.py <ruta_save> <task_id1> [task_id2] ...")
        print("Ejemplo: python3 patch_save.py doc_44b0013cfacf_SAVE 1070760953 -1759660069")
        sys.exit(1)
    
    save_path = sys.argv[1]
    task_ids = [int(x) for x in sys.argv[2:]]
    patch_save(save_path, task_ids)