#!/usr/bin/env python3
"""
Starmaker Story Save Editor - Interfaz Gráfica (GUI)
Permite ver y editar el estado de las misiones mediante una interfaz visual.
"""
import customtkinter as ctk
import json
import sys
from pathlib import Path
import tkinter.messagebox
import os

# Configuración de apariencia moderna
ctk.set_appearance_mode("System")  # Modo: System (Claro/Oscuro)
ctk.set_default_color_theme("blue")  # Temas: blue, dark-blue, green

# Mapeo de quests (importado desde save_editor.py)
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

DEFAULT_SAVE = "/home/jesusgs/.hermes/cache/documents/doc_44b0013cfacf_SAVE"


class QuestTask:
    """Representa una tarea individual dentro de una quest."""
    
    def __init__(self, task_id, name, state=1, value=0.0):
        self.task_id = task_id
        self.name = name
        self.state = state  # 0=Inactiva, 1=Activa, 2=Completada
        self.value = value
    
    def get_state_name(self):
        return {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(self.state, f"Desconocido({self.state})")


class SaveEditorGUI:
    """Interfaz gráfica principal del editor de saves."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Starmaker Story Save Editor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variable para el save path
        self.save_path = ctk.StringVar(value=DEFAULT_SAVE)
        self.save_backup_path = ""
        
        # Cargar datos
        self.quests_data = []
        self.tasks_data = {}
        
        # Configurar interfaz
        self._setup_styles()
        self._create_widgets()
        self._load_data()
    
    def _setup_styles(self):
        """Configurar estilos personalizados."""
        style = ctk.CTkThemeManager(root=self.root)
        style.set_scaling(1.0)
    
    def _create_widgets(self):
        """Crear los widgets de la interfaz."""
        # Frame principal con diseño en grid
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel superior - Información del save
        self._create_save_panel()
        
        # Panel central - Lista de quests
        self._create_quests_panel()
        
        # Panel inferior - Acciones
        self._create_actions_panel()
    
    def _create_save_panel(self):
        """Crear panel de información del save."""
        save_frame = ctk.CTkFrame(self.main_frame)
        save_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        save_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(save_frame, text="📁 Archivo Save:", anchor="w").grid(row=0, column=0, padx=5, pady=5)
        
        ctk.CTkEntry(save_frame, textvariable=self.save_path, width=400).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(save_frame, text="Examinar", command=self._browse_save).grid(row=0, column=2, padx=5, pady=5)
        
        # Información del save
        self.save_info_label = ctk.CTkLabel(save_frame, text="", anchor="w")
        self.save_info_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")
    
    def _browse_save(self):
        """Abrir diálogo para seleccionar archivo save."""
        filepath = ctk.filedialog.askopenfilename(
            title="Seleccionar archivo de save",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.save_path.set(filepath)
            self._update_save_info()
    
    def _update_save_info(self):
        """Actualizar información del save."""
        try:
            path = self.save_path.get()
            if os.path.exists(path):
                size = os.path.getsize(path) / 1024  # KB
                self.save_info_label.configure(text=f"📄 {os.path.basename(path)} ({size:.1f} KB) - Listo para editar")
            else:
                self.save_info_label.configure(text="⚠ Archivo no encontrado - Se creará uno nuevo al guardar")
        except Exception as e:
            self.save_info_label.configure(text=f"❌ Error: {str(e)[:50]}")
    
    def _create_quests_panel(self):
        """Crear panel de quests."""
        # Frame con scroll
        self.quests_canvas = ctk.CTkScrollableFrame(self.main_frame, height=500)
        self.quests_canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.quests_canvas.grid_columnconfigure(0, weight=1)
        
        # Frame para los quests (se agregará dinámicamente)
        self.quests_frame = ctk.CTkFrame(self.quests_canvas)
        self.quests_canvas._frame = self.quests_frame
        
        # Configurar grid weight
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def _create_actions_panel(self):
        """Crear panel de acciones inferiores."""
        actions_frame = ctk.CTkFrame(self.main_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Botón guardar
        self.btn_save = ctk.CTkButton(
            actions_frame,
            text="💾 Guardar Cambios",
            command=self._save_changes,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_save.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        # Botón restablecer
        self.btn_reset = ctk.CTkButton(
            actions_frame,
            text="↩️ Restablecer a Default",
            command=self._reset_changes,
            height=35,
            fg_color="orange",
            hover_color="red"
        )
        self.btn_reset.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Label de estado
        self.status_label = ctk.CTkLabel(actions_frame, text="", anchor="w")
        self.status_label.grid(row=0, column=2, padx=(20, 0), pady=5, sticky="w")
    
    def _load_data(self):
        """Cargar datos del save y poblar la interfaz."""
        try:
            data = self._load_save(self.save_path.get())
            if data:
                self.quests_data, self.tasks_data = self._parse_save(data)
                self._populate_quests()
                self._update_save_info()
                self.status_label.configure(text="✅ Datos cargados exitosamente")
            else:
                self.status_label.configure(text="❌ Error cargando el save")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error al cargar el save:\n{str(e)}")
            self.status_label.configure(text="❌ Error al cargar datos")
    
    def _load_save(self, save_path):
        """Cargar archivo save JSON."""
        with open(save_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _parse_save(self, save_data):
        """Parsear los datos del save para extraer quests y tareas."""
        # Extraer quests del TokenJournal
        quests = []
        tasks = {}
        
        for entry in save_data.get("m_Entries", []):
            if "TokenJournal" in entry.get("m_Value", ""):
                inner = json.loads(entry["m_Value"])
                refs = inner.get("references", {}).get("RefIds", [])
                
                for ref in refs:
                    t = ref.get("type", {}).get("class")
                    if t == "TokenJournal":
                        data = ref.get("data", {})
                        
                        # Parsear m_Quests
                        m_quests = data.get("m_Quests", {})
                        if isinstance(m_quests, dict) and "m_Keys" in m_quests:
                            for i, k in enumerate(m_quests["m_Keys"]):
                                guid = k.get("m_String", "")
                                state = m_quests["m_Values"][i].get("m_State", 0) if i < len(m_quests["m_Values"]) else 0
                                quests.append({"guid": guid, "state": state})
                        
                        # Parsear m_Tasks
                        m_tasks = data.get("m_Tasks", {})
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
        """Poblar la interfaz con las quests encontradas."""
        # Limpiar frame actual
        for widget in self.quests_frame.winfo_children():
            widget.destroy()
        
        # Agrupar quests por nombre conocido
        quest_groups = {}
        for q in self.quests_data:
            guid = q["guid"]
            known = KNOWN_QUESTS.get(guid, {"name": f"Quest {guid[:8]}..."})
            name = known["name"]
            if name not in quest_groups:
                quest_groups[name] = []
            quest_groups[name].append(q)
        
        # Crear widgets para cada quest
        row = 0
        col = 0
        
        for quest_name, quests in quest_groups.items():
            # Frame de la quest
            quest_frame = ctk.CTkFrame(self.quests_frame)
            quest_frame.grid(row=row, column=col, sticky="ew", padx=(5, 2), pady=5, columnspan=2)
            quest_frame.grid_columnconfigure(1, weight=1)
            
            # Nombre de la quest
            name_label = ctk.CTkLabel(quest_frame, text=f"📋 {quest_name}", 
                                       font=ctk.CTkFont(size=13, weight="bold"))
            name_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="w")
            
            # Estado de la quest
            if quests:
                quest_state = quests[0]["state"]
                state_name = {0: "🔴 Inactiva", 1: "🟢 Activa", 2: "🟡 Completada"}.get(quest_state, "⚪ Desconocida")
                state_label = ctk.CTkLabel(quest_frame, text=f"Estado: {state_name}", 
                                           font=ctk.CTkFont(size=11))
                state_label.grid(row=1, column=0, columnspan=2, padx=10, pady=2, sticky="w")
            
            # Tareas de la quest
            task_row = 2
            for q in quests:
                guid = q["guid"]
                known = KNOWN_QUESTS.get(guid, {"name": "Unknown", "tasks": {}})
                tasks = known.get("tasks", {})
                
                # Nombre de la quest para referencia
                quest_display_name = known["name"]
                
                # Frame de tarea
                task_inner = ctk.CTkFrame(quest_frame)
                task_inner.grid(row=task_row, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
                task_inner.grid_columnconfigure(1, weight=1)
                task_inner.grid_columnconfigure(3, weight=0)
                
                # Nombre de la tarea
                task_name = tasks.get(q["task_id"], "Desconocida") if hasattr(q, 'task_id') else "Desconocida"
                
                # State combobox
                state_var = ctk.StringVar(value=self._get_state_name_str(q["state"]))
                
                # Usamos un dict para guardar referencias a los combobox
                if not hasattr(self, 'task_vars'):
                    self.task_vars = {}
                
                self.task_vars[q["task_id"]] = state_var
                
                task_name_label = ctk.CTkLabel(task_inner, text=f"  {task_name}:", 
                                               width=150, anchor="w")
                task_name_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
                
                state_combo = ctk.CTkComboBox(task_inner, values=["Inactiva", "Activa", "Completada"],
                                              variable=state_var, width=120)
                state_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
                
                # Vincar evento de cambio
                state_var.trace_add("write", lambda *args, tid=q["task_id"], cv=state_var: 
                                   self._on_task_state_change(tid, cv.get()))
                
                task_row += 1
            
            row += 1
        
        # Configurar que el frame se expanda
        self.quests_frame.update_idletasks()
    
    def _get_state_name_str(self, state):
        """Convertir estado numérico a string."""
        return {0: "Inactiva", 1: "Activa", 2: "Completada"}.get(state, "Activa")
    
    def _on_task_state_change(self, task_id, new_state_str):
        """Manejar cambio de estado de tarea."""
        # Mapear string a número
        state_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
        new_state = state_map.get(new_state_str, 1)
        
        # Guardar cambio (pendiente de guardar)
        # Podríamos guardar inmediatamente o al hacer click en "Guardar"
        # Por ahora, solo actualizamos la interfaz
        self.status_label.configure(text=f"📝 Tarea {task_id} cambiada a {new_state_str}")
    
    def _save_changes(self):
        """Guardar los cambios realizados en el save."""
        try:
            # Cargar save actual
            data = self._load_save(self.save_path.get())
            
            if not data:
                tkinter.messagebox.showerror("Error", "No se pudo cargar el save actual")
                return
            
            # Aplicar cambios a las tareas
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
                                task_id = k.get("m_TaskId")
                                if task_id in self.task_vars:
                                    # Nuevo estado
                                    state_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
                                    new_state = state_map.get(self.task_vars[task_id].get(), 1)
                                    
                                    # Actualizar m_State
                                    if i < len(values):
                                        values[i]["m_State"] = new_state
                                        modified = True
                            
                            # Reconstruir m_Tasks
                            m_tasks["m_Keys"] = keys
                            m_tasks["m_Values"] = values
                            entry["m_Value"] = json.dumps(inner)
                            
                            if modified:
                                break
            
            if modified:
                # Crear backup
                backup_path = self.save_path.get() + ".backup"
                import shutil
                shutil.copy2(self.save_path.get(), backup_path)
                
                # Guardar nuevo save
                with open(self.save_path.get(), "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Cre save comprimido .gz
                import gzip
                gz_path = self.save_path.get().replace(".json", ".gz")
                with open(self.save_path.get(), "rb") as f_in:
                    with gzip.open(gz_path, "wb") as f_out:
                        f_out.write(f_in.read())
                
                self.status_label.configure(text="✅ Save guardado exitosamente con backup!")
                tkinter.messagebox.showinfo("Éxito", 
                    f"Save guardado correctamente!\n\n"
                    f"📁 Archivo original: {self.save_path.get()}\n"
                    f"💾 Backup creado: {backup_path}\n"
                    f"📦 Save comprimido: {gz_path}")
            else:
                tkinter.showinfo("Información", "No se detectaron cambios para guardar")
                
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error al guardar el save:\n{str(e)}")
            self.status_label.configure(text="❌ Error al guardar cambios")
    
    def _reset_changes(self):
        """Restablecer todos los cambios."""
        if tkinter.messagebox.askyesno("Confirmar", 
                                        "¿Estás seguro de restablecer todos los cambios?\n"
                                        "Esto revertirá el save a su estado original."):
            # Restaurar backup si existe
            backup = self.save_path.get() + ".backup"
            if os.path.exists(backup):
                import shutil
                shutil.copy2(backup, self.save_path.get())
                self.status_label.configure(text="♻️ Cambios restablecidos desde backup")
                tkinter.messagebox.showinfo("Éxito", "Los cambios han sido restablecidos desde el backup")
            else:
                tkinter.messagebox.showwarning("Advertencia", 
                    "No se encontró el archivo de backup.\n"
                    "Los cambios actuales se mantendrán.")
            self._load_data()


def main():
    """Punto de entrada principal."""
    root = ctk.CTk()
    app = SaveEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()