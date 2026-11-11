#!/usr/bin/env python3
"""
Starmaker Story Save Editor - Interfaz Gráfica (GUI) - Versión Corregida
"""
import customtkinter as ctk
import json
import os
import tkinter as tk
from tkinter import messagebox
import shutil
import gzip

# Configuración de apariencia
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DEFAULT_SAVE = "./save.json"

# Mapeo de quests
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
}


class SaveEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Starmaker Story Save Editor")
        self.root.geometry("1200x800")
        
        self.save_path = ""
        self.save_path_var = ctk.StringVar(value="")
        self.save_backup_path = ""
        self.quests_data = []
        self.tasks_data = {}
        self.task_widgets = {}  # task_id -> (label, combobox)
        
        # Crear widgets
        self._setup_widgets()
        # No cargar datos al inicio - esperar a que el usuario seleccione archivo
        self.root.mainloop()
    
    def _setup_widgets(self):
        """Crear layout de widgets."""
        # Frame principal
        self.main_frame = ctk.CTkFrame(master=self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame superior - info del save
        self.top_frame = ctk.CTkFrame(master=self.main_frame)
        self.top_frame.pack(fill="x", pady=(0, 10))
        self.top_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(self.top_frame, text="📁 Save:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.save_entry = ctk.CTkEntry(self.top_frame, textvariable=self.save_path_var, width=400)
        self.save_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.top_frame, text="Examinar", command=self._browse_save).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame central - lista de quests
        self.center_frame = ctk.CTkFrame(master=self.main_frame)
        self.center_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        # Frame scrollable para quests
        self.scroll_frame = ctk.CTkScrollableFrame(master=self.center_frame, orientation="vertical")
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Frame de acciones
        self.actions_frame = ctk.CTkFrame(master=self.main_frame)
        self.actions_frame.pack(fill="x", pady=(10, 0))
        self.actions_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(self.actions_frame, text="💾 Guardar Cambios", command=self._save_changes).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(self.actions_frame, text="↩️ Restablecer", command=self._reset_changes).grid(row=0, column=1, padx=10, pady=10)
        self.status_label = ctk.CTkLabel(self.actions_frame, text="", anchor="w")
        self.status_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Variables
        self.tasks_vars = {}
        self.task_widgets_map = {}
    
    def _browse_save(self):
        filepath = ctk.filedialog.askopenfilename(
            title="Seleccionar archivo de save",
            filetypes=[
                ("JSON files", "*.json"),
                ("GZIP files", "*.gz"),
                ("Todos los archivos", "*.*")
            ]
        )
        if filepath:
            self.save_path = filepath
            self.save_path_var.set(filepath)
            self._load_data()
    
    def _load_data(self):
        if not self.save_path:
            messagebox.showwarning("Info", "Selecciona un archivo con Examinar")
            return
        try:
            save_data = self._load_save(self.save_path)
            
            quests, tasks = self._parse_save(save_data)
            self.quests_data = quests
            self.tasks_data = tasks
            self._populate_quests()
            self.status_label.configure(text="✅ Datos cargados")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar save:\n{str(e)}")
            self.status_label.configure(text="❌ Error al cargar")
    
    def _parse_save(self, save_data):
        quests = []
        tasks = {}
        for entry in save_data.get("m_Entries", []):
            if "TokenJournal" in entry.get("m_Value", ""):
                inner = json.loads(entry["m_Value"])
                refs = inner.get("references", {}).get("RefIds", [])
                for ref in refs:
                    if ref.get("type", {}).get("class") == "TokenJournal":
                        tj = ref.get("data", {})
                        m_quests = tj.get("m_Quests", {})
                        if isinstance(m_quests, dict) and "m_Keys" in m_quests:
                            for i, k in enumerate(m_quests["m_Keys"]):
                                guid = k.get("m_String", "")
                                state = m_quests["m_Values"][i].get("m_State", 0) if i < len(m_quests["m_Values"]) else 0
                                quests.append({"guid": guid, "state": state})
                        m_tasks = tj.get("m_Tasks", {})
                        if isinstance(m_tasks, dict):
                            keys = m_tasks.get("m_Keys", [])
                            values = m_tasks.get("m_Values", [])
                            for k, v in zip(keys, values):
                                task_id = k.get("m_TaskId")
                                if task_id is not None:
                                    tasks[task_id] = {
                                        "quest_hash": k.get("m_QuestHash"),
                                        "state": v.get("m_State"),
                                        "value": v.get("m_Value"),
                                    }
        return quests, tasks
    
    def _populate_quests(self):
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.quest_frames = {}
        
        for q in self.quests_data:
            guid = q["guid"]
            known = KNOWN_QUESTS.get(guid, {"name": f"Quest {guid[:8]}..."})
            quest_name = known["name"]
            quest_state = q["state"]
            quest_state_str = {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(quest_state, "Activa")
            
            # Crear frame de quest
            quest_frame = ctk.CTkFrame(master=self.scroll_frame, fg_color="transparent")
            quest_frame.pack(fill="x", pady=(5, 0))
            
            ctk.CTkLabel(quest_frame, text=f"📋 {quest_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            
            # Crear frame para tareas
            task_frame = ctk.CTkFrame(master=quest_frame, fg_color="transparent")
            task_frame.pack(fill="x", pady=(5, 0))
            
            # Agregar tareas de esta quest
            tasks_for_quest = self._get_tasks_for_quest(guid)
            task_state_var = {}
            
            for task_id, task_name in tasks_for_quest.items():
                task_frame_inner = ctk.CTkFrame(master=task_frame, fg_color="transparent")
                task_frame_inner.pack(fill="x", pady=(3, 0))
                
                # Label con nombre
                task_label = ctk.CTkLabel(task_frame_inner, text=f"  {task_name}", width=300, anchor="w")
                task_label.pack(side="left", fill="x", expand=True)
                
                # State combobox
                state_var = tk.StringVar(value={0: "Inactiva", 1: "Activa", 2: "Completada"}.get(self.tasks_data.get(task_id, {}).get("state", 1), "Activa"))
                task_combobox = ctk.CTkComboBox(task_frame_inner, values=["Inactiva", "Activa", "Completada"], variable=state_var, width=120)
                task_combobox.pack(side="right")
                
                # Vincular cambio
                task_combobox.bind("<<ComboboxSelected>>", lambda e, tid=task_id, sv=state_var: self._on_task_change(tid, sv))
                task_state_var[task_id] = state_var
            
            # Guardar frame con el estado de la quest
            self.quest_frames[quest_name] = {
                "frame": quest_frame,
                "state_var": tk.StringVar(value=quest_state_str),
                "task_frames": task_frame,
                "task_vars": task_state_var,
            }
    
    def _get_tasks_for_quest(self, guid):
        """Obtener tareas de una quest."""
        if guid in KNOWN_QUESTS and "tasks" in KNOWN_QUESTS[guid]:
            return KNOWN_QUESTS[guid]["tasks"]
        return {}
    
    def _on_task_change(self, task_id, var):
        """Manejador de cambio de estado."""
        state_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
        new_state = state_map.get(var.get(), 1)
        self.status_label.configure(text=f"📝 Tarea {task_id} → {var.get()}")
    
    def _save_changes(self):
        """Guardar cambios."""
        try:
            data = self._load_save(self.save_path)
            if not data:
                messagebox.showerror("Error", "No se pudo cargar el save")
                return
            
            task_combos = {}
            for quest_name, qdata in self.quest_frames.items():
                task_vars = qdata["task_vars"]
                for task_id, var in task_vars.items():
                    task_combos[task_id] = var
            
            modified = False
            task_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
            
            for entry in data.get("m_Entries", []):
                if "TokenJournal" in entry.get("m_Value", ""):
                    inner = json.loads(entry["m_Value"])
                    refs = inner.get("references", {}).get("RefIds", [])
                    for ref in refs:
                        if ref.get("type", {}).get("class") == "TokenJournal":
                            tj = ref.get("data", {})
                            m_tasks = tj.get("m_Tasks", {})
                            if isinstance(m_tasks, dict):
                                keys = m_tasks.get("m_Keys", [])
                                values = m_tasks.get("m_Values", [])
                                for i, k in enumerate(keys):
                                    task_id = k.get("m_TaskId")
                                    if task_id in task_combos:
                                        # Nuevo estado
                                        new_state_str = task_combos[task_id].get()
                                        new_state = task_map.get(new_state_str, 1)
                                        if i < len(values):
                                            values[i]["m_State"] = new_state
                                            modified = True
                                m_tasks["m_Keys"] = keys
                                m_tasks["m_Values"] = values
                                entry["m_Value"] = json.dumps(inner)
            
            if not modified:
                messagebox.showinfo("Info", "No se detectaron cambios")
                return
            
            # Backup del archivo original
            backup_path = self.save_path + ".backup"
            shutil.copy2(self.save_path, backup_path)
            
            # Preparar el nombre base sin extensión para el .gz del juego
            from pathlib import Path
            p = Path(self.save_path)
            if p.suffix:
                base_name = str(p.with_suffix(""))  # quita .json/.gz/.GZ
            else:
                base_name = str(p)
            
            # 1. Guardar versión editada en JSON plano (para inspección)
            edited_path = base_name + ".edited.json"
            with open(edited_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 2. Crear SAVE.gz con un miembro interno llamado "SAVE" (sin extensión)
            gz_path = base_name + ".gz"
            import gzip, io
            json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
            with open(gz_path, "wb") as f_out:
                info = gzip.GzipFile(filename="SAVE", mode="wb", fileobj=f_out)
                info.write(json_bytes)
                info.close()
            
            # 3. Sobrescribir el archivo fuente con los cambios (persistencia)
            #    Detectamos si el original era gzip para preservar formato.
            with open(self.save_path, "rb") as f:
                magic = f.read(2)
            if magic == b"\x1f\x8b":
                with open(self.save_path, "wb") as f_out:
                    info = gzip.GzipFile(filename="SAVE", mode="wb", fileobj=f_out)
                    info.write(json_bytes)
                    info.close()
            else:
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"Save guardado!\nBackup: {backup_path}\nEditado: {edited_path}\nGz (miembro 'SAVE'): {gz_path}")
            self.status_label.configure(text="✅ Guardado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            self.status_label.configure(text="❌ Error al guardar")
    
    def _reset_changes(self):
        pass  # Implementar
    
    def _load_save(self, path):
        """Cargar save detectando si es gzip o plain JSON."""
        import gzip
        
        # Detectar gzip por los primeros bytes (magic: 1f 8b)
        with open(path, "rb") as f:
            magic = f.read(2)
        
        if magic == b"\x1f\x8b":
            with gzip.open(path, "rb") as f:
                content = f.read()
                return json.loads(content.decode("utf-8"))
        # Si no, leer normal
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def main():
    root = ctk.CTk()
    app = SaveEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
