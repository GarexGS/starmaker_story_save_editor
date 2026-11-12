#!/usr/bin/env python3
"""
Starmaker Story Save Editor - Versión Extendida con Múltiples Secciones
Permite editar: Quests, Dinero, Autos, Items/Servicios, Variables Generales
"""
import customtkinter as ctk
import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import gzip
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuración de apariencia
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DEFAULT_SAVE = "./save.json"

# ============================================================
# CATEGORÍAS DE VARIABLES GLOBALES (organizadas por keywords)
# ============================================================

VARIABLE_CATEGORIES = {
    "💰 Economía": [
        "Cash", "Debt", "Cash-Before", "Daily-Income", "LastPayout-Purelyvisual",
        "2025newincome", "star-fans", "sub-dono-amount", "fan-dono-amount",
        "adrian-japan-money-needed", "adrian-japan-money-given",
        "2025starcon-totalvisits", "frank-count"
    ],
    "🚗 Vehículos": [
        "Selected-Car", "Car-Dirt", "D-car-key-event", "active-store",
        "carwash-service", "grocery-service", "maid-service"
    ],
    "📦 Items/Servicios": [
        "celeste-quest-done", "club-enabled", "wardrobe-scene",
        "take-this-wardrobe-key", "wine-gifted", "D-car-key-event"
    ],
    "📊 Estadísticas": [
        "Total-playtime", "DaysPassed", "Day", "Dayname", "year-day", "year-season",
        "Active-Level", "Upcoming-Level", "Lock-Game", "Start-Transfer",
        "church-visits", "park-visits", "movie-night", "photos-taken-today",
        "photos-taken-alltime", "Follower", "Subscriber"
    ],
    "🎭 Relaciones": [
        "happy-together", "anna-saved", "Rich", "Celebrity", "anna-liz-done",
        "ghost-girl", "android", "save-tristan", "collection",
        "ken-swimming", "matchmaker", "master", "heroic",
        "M", "D", "B", "Amelia", "Isabella", "Best-Friend"
    ],
    "⚙️ Configuración": [
        "Auto-Skip", "Auto-Skip-Very-Fast", "screenmode", "DialogueVariation",
        "2025dialoguespeed", "tutorialsdisabled", "tutorial-firststeps",
        "tutorial-worldmap", "tutorial-payout", "tutorial-newperk",
        "tutorial-annamood", "tutorial-annastatus", "carradio-enabled"
    ],
    "🎮 Gameplay/Estados": [
        "Auto-Skip", "Auto-Skip-Very-Fast", "Lock-Game", "Start-Transfer",
        "After-Talk-Transition", "talk-button", "stored-talk",
        "Characters-stay-on-screen", "important-decision", "active-menu",
        "random-1-of-10", "temp-stored-very-short-term", "Random-music",
        "end-of-the-week", "gamerestart", "Active-Ending"
    ]
}


class EnhancedSaveEditor:
    """Editor principal con múltiples secciones/pestañas."""

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Starmaker Story Save Editor - Enhanced")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)

        # Estado del save
        self.save_path = ""
        self.save_data = None
        self.backup_path = ""

        # Datos parseados
        self.quests_data = []           # Lista de {guid, state, tracking}
        self.tasks_data = {}            # Dict task_id -> {quest_hash, state, value}
        self.global_variables = {}      # Dict name -> {type, value, name_rid, value_rid, value_type}
        self.token_journal_entry = None # Referencia a la entrada TokenJournal

        # Variables de GUI
        self.save_path_var = ctk.StringVar(value="")
        self.section_frames = {}
        self.section_widgets = {}

        # Crear interfaz
        self._setup_ui()
        self.root.mainloop()

    # ============================================================
    # UI SETUP
    # ============================================================

    def _setup_ui(self):
        """Configurar interfaz principal."""
        # Frame principal
        self.main_frame = ctk.CTkFrame(master=self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel superior - Archivo
        self._create_file_panel()

        # Panel central - Notebook con pestañas
        self._create_notebook()

        # Panel inferior - Acciones
        self._create_actions_panel()

    def _create_file_panel(self):
        """Panel superior para seleccionar archivo save."""
        file_frame = ctk.CTkFrame(master=self.main_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(file_frame, text="📁 Save:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.save_entry = ctk.CTkEntry(file_frame, textvariable=self.save_path_var, width=500)
        self.save_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(file_frame, text="Examinar", command=self._browse_save, width=100).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(file_frame, text="Recargar", command=self._reload_save, width=100).grid(row=0, column=3, padx=5, pady=5)

        self.save_info_label = ctk.CTkLabel(file_frame, text="", anchor="w")
        self.save_info_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    def _create_notebook(self):
        """Crear notebook con pestañas para cada sección."""
        self.notebook = ctk.CTkTabview(master=self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Añadir pestañas
        tabs = [
            ("🎯 Quests", self._create_quests_tab),
            ("💰 Economía", lambda: self._create_category_tab("💰 Economía")),
            ("🚗 Vehículos", lambda: self._create_category_tab("🚗 Vehículos")),
            ("📦 Items/Servicios", lambda: self._create_category_tab("📦 Items/Servicios")),
            ("📊 Estadísticas", lambda: self._create_category_tab("📊 Estadísticas")),
            ("🎭 Relaciones", lambda: self._create_category_tab("🎭 Relaciones")),
            ("⚙️ Configuración", lambda: self._create_category_tab("⚙️ Configuración")),
            ("🔍 Todas las Variables", self._create_all_variables_tab),
        ]

        for tab_name, creator in tabs:
            tab = self.notebook.add(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            creator()

    def _create_quests_tab(self):
        """Pestaña de Quests (existente mejorada)."""
        tab = self.notebook.tab("🎯 Quests")
        
        # Frame scrollable
        self.quests_scroll = ctk.CTkScrollableFrame(tab, orientation="vertical")
        self.quests_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.quests_scroll.grid_columnconfigure(0, weight=1)

    def _create_category_tab(self, category_name):
        """Crear pestaña para una categoría de variables."""
        tab = self.notebook.tab(category_name)
        
        # Frame scrollable
        scroll = ctk.CTkScrollableFrame(tab, orientation="vertical")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        scroll.grid_columnconfigure(0, weight=1)
        
        self.section_frames[category_name] = scroll

    def _create_all_variables_tab(self):
        """Pestaña con búsqueda de todas las variables."""
        tab = self.notebook.tab("🔍 Todas las Variables")
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="🔍 Buscar:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=400)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_var.trace_add("write", self._on_search_change)

        ctk.CTkLabel(search_frame, text="Tipo:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_type_var = ctk.StringVar(value="Todos")
        self.filter_type_combo = ctk.CTkComboBox(
            search_frame,
            values=["Todos", "ValueNumber", "ValueBool", "ValueString", "NameVariable"],
            variable=self.filter_type_var,
            width=120,
            command=self._on_filter_change
        )
        self.filter_type_combo.grid(row=0, column=3, padx=5, pady=5)

        # Frame scrollable para resultados
        self.all_vars_scroll = ctk.CTkScrollableFrame(tab, orientation="vertical")
        self.all_vars_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.all_vars_scroll.grid_columnconfigure(0, weight=1)

    def _on_search_change(self, var_name, index, mode):
        """Debounced search handler."""
        import time
        current_time = time.time()
        if not hasattr(self, '_last_search_time'):
            self._last_search_time = 0
        if current_time - self._last_search_time > 300:
            self._last_search_time = current_time
            self._filter_all_variables()

    def _on_filter_change(self, event=None):
        """Filter change handler with debouncing."""
        import time
        current_time = time.time()
        if not hasattr(self, '_last_filter_time'):
            self._last_filter_time = 0
        if current_time - self._last_filter_time > 300:
            self._last_filter_time = current_time
            self._filter_all_variables()

    def _create_actions_panel(self):
        """Panel inferior con botones de acción."""
        actions_frame = ctk.CTkFrame(master=self.main_frame)
        actions_frame.pack(fill="x", pady=(10, 0))
        actions_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            actions_frame, 
            text="💾 Guardar Cambios", 
            command=self._save_changes,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(
            actions_frame, 
            text="↩️ Restablecer Backup", 
            command=self._reset_backup,
            height=40,
            fg_color="orange",
            hover_color="red"
        ).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(actions_frame, text="", anchor="w")
        self.status_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")

    # ============================================================
    # CARGA Y PARSEO DEL SAVE
    # ============================================================

    def _browse_save(self):
        """Abrir diálogo para seleccionar archivo save."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de save",
            filetypes=[
                ("Archivos JSON", "*.json"),
                ("Archivos GZIP", "*.gz"),
                ("Todos los archivos", "*.*")
            ]
        )
        if filepath:
            self.save_path = filepath
            self.save_path_var.set(filepath)
            self._load_save()

    def _reload_save(self):
        """Recargar el save actual."""
        if self.save_path:
            self._load_save()

    def _load_save(self):
        """Cargar y parsear el archivo save."""
        try:
            self.save_data = self._load_save_file(self.save_path)
            if not self.save_data:
                raise ValueError("No se pudo cargar el save")

            # Parsear todas las secciones
            self._parse_token_journal()
            self._parse_global_variables()

            # Poblar UI
            self._populate_quests_tab()
            self._populate_category_tabs()
            self._populate_all_variables_tab()

            # Info del archivo
            size = os.path.getsize(self.save_path) / 1024
            self.save_info_label.configure(
                text=f"✅ {os.path.basename(self.save_path)} ({size:.1f} KB) - "
                     f"{len(self.quests_data)} quests, {len(self.tasks_data)} tasks, "
                     f"{len(self.global_variables)} variables globales"
            )
            self.status_label.configure(text="✅ Datos cargados exitosamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar save:\n{str(e)}")
            self.status_label.configure(text=f"❌ Error: {str(e)[:80]}")

    def _load_save_file(self, path):
        """Cargar archivo detectando si es gzip o JSON plano."""
        with open(path, "rb") as f:
            magic = f.read(2)
        
        if magic == b"\x1f\x8b":
            with gzip.open(path, "rb") as f:
                content = f.read()
                return json.loads(content.decode("utf-8"))
        else:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _parse_token_journal(self):
        """Extraer quests y tasks del TokenJournal."""
        self.quests_data = []
        self.tasks_data = {}
        self.token_journal_entry = None

        for entry in self.save_data.get("m_Entries", []):
            val = entry.get("m_Value", "")
            if "TokenJournal" in val:
                self.token_journal_entry = entry
                inner = json.loads(val)
                refs = inner.get("references", {}).get("RefIds", [])
                
                for ref in refs:
                    if ref.get("type", {}).get("class") == "TokenJournal":
                        tj = ref.get("data", {})
                        
                        # Parsear m_Quests
                        m_quests = tj.get("m_Quests", {})
                        if isinstance(m_quests, dict) and "m_Keys" in m_quests:
                            for i, k in enumerate(m_quests["m_Keys"]):
                                guid = k.get("m_String", "")
                                state = m_quests["m_Values"][i].get("m_State", 0) if i < len(m_quests["m_Values"]) else 0
                                tracking = m_quests["m_Values"][i].get("m_IsTracking", False)
                                self.quests_data.append({
                                    "guid": guid, 
                                    "state": state,
                                    "tracking": tracking
                                })
                        
                        # Parsear m_Tasks
                        m_tasks = tj.get("m_Tasks", {})
                        if isinstance(m_tasks, dict):
                            keys = m_tasks.get("m_Keys", [])
                            values = m_tasks.get("m_Values", [])
                            for k, v in zip(keys, values):
                                task_id = k.get("m_TaskId")
                                if task_id is not None:
                                    self.tasks_data[task_id] = {
                                        "quest_hash": k.get("m_QuestHash"),
                                        "state": v.get("m_State"),
                                        "value": v.get("m_Value"),
                                    }
                break

    def _parse_global_variables(self):
        """Extraer todas las variables globales (NameVariable + Value*)."""
        self.global_variables = {}
        name_vars = {}
        value_vars = {}

        for entry in self.save_data.get("m_Entries", []):
            key = entry.get("m_Key", "")
            if "global-name-variables" in key:
                val = entry.get("m_Value", "")
                inner = json.loads(val)
                refs = inner.get("references", {}).get("RefIds", [])

                for ref in refs:
                    rtype = ref.get("type", {}).get("class", "")
                    rid = ref.get("rid")

                    if rtype == "NameVariable":
                        data = ref.get("data", {})
                        # m_Name puede ser dict o string directo
                        m_name = data.get("m_Name", {})
                        if isinstance(m_name, dict):
                            name = m_name.get("m_String", "")
                        else:
                            name = str(m_name)
                        # m_Value puede ser dict o string directo
                        m_value = data.get("m_Value", {})
                        if isinstance(m_value, dict):
                            value_rid = m_value.get("rid")
                        else:
                            value_rid = None
                        if name:
                            name_vars[name] = {"rid": rid, "value_rid": value_rid}

                    elif rtype in ("ValueBool", "ValueNumber", "ValueString", "ValueVector2", "ValueVector3", "ValueGameObject"):
                        data = ref.get("data", {})
                        value = data.get("m_Value")
                        value_vars[rid] = {"type": rtype, "value": value}

                # Combinar: name -> {type, value, name_rid, value_rid}
                for name, nv in name_vars.items():
                    vv = value_vars.get(nv["value_rid"], {})
                    self.global_variables[name] = {
                        "type": vv.get("type", "Unknown"),
                        "value": vv.get("value"),
                        "name_rid": nv["rid"],
                        "value_rid": nv["value_rid"],
                        "value_type": vv.get("type", "Unknown")
                    }
                break

    # ============================================================
    # POBLAR TABS
    # ============================================================

    def _populate_quests_tab(self):
        """Poblar pestaña de quests con caché para evitar destrucción completa."""
        current_quests = [(q["guid"], q["state"], q.get("tracking", False)) for q in self.quests_data]
        if current_quests == getattr(self, '_last_quests_data', None):
            return  # Sin cambios, no reconstruir

        # Limpiar
        for widget in self.quests_scroll.winfo_children():
            widget.destroy()

        # Mapeo de nombres conocidos (del quest_mapping_final.json)
        known_quests = self._load_known_quests()

        for q in self.quests_data:
            guid = q["guid"]
            known = known_quests.get(guid, {"name": f"Quest {guid[:8]}..."})
            quest_name = known["name"]
            quest_state = q["state"]
            tracking = q.get("tracking", False)
            
            state_names = {0: "Inactiva", 1: "Activa", 2: "Completada"}
            state_str = state_names.get(quest_state, f"Desconocido({quest_state})")

            # Frame de quest
            qframe = ctk.CTkFrame(self.quests_scroll)
            qframe.pack(fill="x", pady=(5, 0), padx=5)
            qframe.grid_columnconfigure(1, weight=1)

            # Nombre
            name_label = ctk.CTkLabel(
                qframe, 
                text=f"📋 {quest_name}", 
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            name_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

            # Estado
            state_var = ctk.StringVar(value=state_str)
            state_combo = ctk.CTkComboBox(
                qframe, 
                values=["Inactiva", "Activa", "Completada"],
                variable=state_var,
                width=130,
                command=lambda v, g=guid: self._on_quest_state_change(g, v)
            )
            state_combo.grid(row=0, column=1, padx=10, pady=8, sticky="e")

            # Tracking
            track_var = ctk.BooleanVar(value=tracking)
            track_check = ctk.CTkCheckBox(
                qframe,
                text="📍 Rastrear",
                variable=track_var,
                command=lambda g=guid, v=track_var: self._on_quest_track_change(g, v.get())
            )
            track_check.grid(row=0, column=2, padx=10, pady=8)

            # GUID (pequeño)
            guid_label = ctk.CTkLabel(qframe, text=guid[:8] + "...", font=ctk.CTkFont(size=9), text_color="gray")
            guid_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

            # Mostrar tasks vinculados (si los hay)
            quest_tasks = self._get_tasks_for_quest(guid)
            if quest_tasks:
                for i, (task_id, task_info) in enumerate(quest_tasks.items(), 1):
                    task_state = task_info.get("state", 0)
                    task_state_names = {0: "Inactiva", 1: "Activa", 2: "Completada", 3: "Fallada"}
                    task_state_str = task_state_names.get(task_state, f"Desconocido({task_state})")
                    task_label = ctk.CTkLabel(
                        qframe,
                        text=f"   🔹 Task {task_id[:8]}... — {task_state_str}",
                        font=ctk.CTkFont(size=10),
                        text_color="gray",
                        anchor="w"
                    )
                    task_label.grid(row=2 + i, column=0, columnspan=3, padx=10, pady=(2, 0), sticky="w")

            # Guardar referencias para guardar después
            self.section_widgets[f"quest_{guid}"] = {
                "state_var": state_var,
                "track_var": track_var,
                "guid": guid
            }

        # Guardar estado para caché
        self._last_quests_data = current_quests

    def _populate_category_tabs(self):
            """Poblar pestañas de categorías con caching para evitar recreación completa."""
            import time

            current_time = time.time()
            if not hasattr(self, '_last_category_update'):
                self._last_category_update = 0
                self._last_category_vars = {}

            for category_name, var_names in VARIABLE_CATEGORIES.items():
                if category_name not in self.section_frames:
                    continue

                frame = self.section_frames[category_name]

                # Filtrar variables que existen en el save
                found_vars = []
                for name in var_names:
                    if name in self.global_variables:
                        found_vars.append((name, self.global_variables[name]))

                # Si no hay cambios en esta categoría y no ha pasado tiempo suficiente, saltar
                cached_vars = self._last_category_vars.get(category_name)
                if (cached_vars == found_vars and current_time - self._last_category_update < 5):
                    continue

                if not found_vars:
                    ctk.CTkLabel(frame, text=f"⚠️ No se encontraron variables para '{category_name}'",
                               text_color="gray").pack(pady=20)
                    continue

                # Limpiar
                for widget in frame.winfo_children():
                    widget.destroy()

                # Crear widgets para cada variable
                for name, var_info in found_vars:
                    self._create_variable_widget(frame, name, var_info, category_name)

                # Guardar estado para caché
                self._last_category_vars[category_name] = found_vars
                self._last_category_update = current_time

    def _create_variable_widget(self, parent, name, var_info, category):
        """Crear widget para una variable individual."""
        vtype = var_info["type"]
        value = var_info["value"]
        value_rid = var_info["value_rid"]

        # Frame de la variable
        vframe = ctk.CTkFrame(parent)
        vframe.pack(fill="x", pady=3, padx=5)
        vframe.grid_columnconfigure(1, weight=1)

        # Nombre
        display_name = name.replace("-", " ").replace("_", " ").title()
        name_label = ctk.CTkLabel(vframe, text=f"🔧 {display_name}", anchor="w", width=250)
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Widget según tipo
        if vtype == "ValueBool":
            var = ctk.BooleanVar(value=bool(value))
            widget = ctk.CTkSwitch(vframe, text="", variable=var, width=60)
            widget.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            self.section_widgets[f"var_{category}_{name}"] = {
                "var": var, "name": name, "value_rid": value_rid, "type": vtype
            }

        elif vtype == "ValueNumber":
            var = ctk.StringVar(value=str(value))
            entry = ctk.CTkEntry(vframe, textvariable=var, width=120, placeholder_text="0.0")
            entry.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            self.section_widgets[f"var_{category}_{name}"] = {
                "var": var, "name": name, "value_rid": value_rid, "type": vtype
            }

        elif vtype == "ValueString":
            var = ctk.StringVar(value=str(value) if value else "")
            entry = ctk.CTkEntry(vframe, textvariable=var, width=200, placeholder_text="texto")
            entry.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            self.section_widgets[f"var_{category}_{name}"] = {
                "var": var, "name": name, "value_rid": value_rid, "type": vtype
            }

        else:
            # Tipo desconocido - solo mostrar
            ctk.CTkLabel(vframe, text=f"[{vtype}] {value}", text_color="gray").grid(
                row=0, column=1, padx=10, pady=5, sticky="e"
            )

        # RID info (pequeño)
        rid_label = ctk.CTkLabel(vframe, text=f"rid:{value_rid}", font=ctk.CTkFont(size=8), text_color="gray")
        rid_label.grid(row=0, column=2, padx=5, pady=5)

    def _populate_all_variables_tab(self):
        """Poblar pestaña con todas las variables (filtrada por búsqueda)."""
        self._filter_all_variables()

    def _filter_all_variables(self, *args):
        """Filtrar y mostrar variables según búsqueda."""
        search = self.search_var.get().lower()
        filter_type = self.filter_type_var.get()

        # Limpiar
        for widget in self.all_vars_scroll.winfo_children():
            widget.destroy()

        count = 0
        for name, var_info in sorted(self.global_variables.items()):
            if search and search not in name.lower():
                continue
            if filter_type != "Todos" and var_info["type"] != filter_type:
                continue

            self._create_variable_widget(self.all_vars_scroll, name, var_info, "all")
            count += 1

        # Mostrar contador
        if count == 0:
            ctk.CTkLabel(self.all_vars_scroll, text="No hay variables que coincidan", text_color="gray").pack(pady=20)

    # ============================================================
    # MANEJADORES DE CAMBIOS
    # ============================================================

    def _on_quest_state_change(self, guid, new_state_str):
        """Cambio de estado de quest."""
        state_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
        new_state = state_map.get(new_state_str, 1)
        self.status_label.configure(text=f"📋 Quest {guid[:8]}... → {new_state_str}")

    def _on_quest_track_change(self, guid, new_tracking):
        """Cambio de tracking de quest."""
        self.status_label.configure(text=f"📍 Quest {guid[:8]}... tracking={'on' if new_tracking else 'off'}")

    # ============================================================
    # GUARDAR CAMBIOS
    # ============================================================

    def _save_changes(self):
        """Guardar todos los cambios en el save."""
        try:
            if not self.save_data or not self.token_journal_entry:
                raise ValueError("No hay datos cargados")

            modified = False
            inner = json.loads(self.token_journal_entry["m_Value"])
            refs = inner.get("references", {}).get("RefIds", [])

            # 1. Guardar cambios de QUESTS
            for ref in refs:
                if ref.get("type", {}).get("class") == "TokenJournal":
                    tj = ref.get("data", {})
                    
                    # m_Quests
                    m_quests = tj.get("m_Quests", {})
                    if isinstance(m_quests, dict) and "m_Keys" in m_quests:
                        for i, k in enumerate(m_quests["m_Keys"]):
                            guid = k.get("m_String", "")
                            widget_key = f"quest_{guid}"
                            if widget_key in self.section_widgets:
                                w = self.section_widgets[widget_key]
                                state_map = {"Inactiva": 0, "Activa": 1, "Completada": 2}
                                new_state = state_map.get(w["state_var"].get(), 1)
                                new_tracking = w["track_var"].get()
                                
                                if i < len(m_quests["m_Values"]):
                                    if m_quests["m_Values"][i].get("m_State") != new_state:
                                        m_quests["m_Values"][i]["m_State"] = new_state
                                        modified = True
                                    if m_quests["m_Values"][i].get("m_IsTracking") != new_tracking:
                                        m_quests["m_Values"][i]["m_IsTracking"] = new_tracking
                                        modified = True
                    
                    # m_Tasks - por ahora solo quests, se puede extender
                    break

            # 2. Guardar cambios de VARIABLES GLOBALES
            # Necesitamos modificar las referencias Value* en global-name-variables
            for entry in self.save_data.get("m_Entries", []):
                key = entry.get("m_Key", "")
                if "global-name-variables" in key:
                    inner2 = json.loads(entry["m_Value"])
                    refs2 = inner2.get("references", {}).get("RefIds", [])
                    
                    for ref in refs2:
                        rid = ref.get("rid")
                        rtype = ref.get("type", {}).get("class", "")
                        
                        # Buscar si este rid corresponde a un value_rid modificado
                        for widget_key, w in self.section_widgets.items():
                            if widget_key.startswith("var_") and w.get("value_rid") == rid:
                                new_value = self._parse_widget_value(w)
                                if ref.get("data", {}).get("m_Value") != new_value:
                                    ref["data"]["m_Value"] = new_value
                                    modified = True
                    
                    if modified:
                        entry["m_Value"] = json.dumps(inner2)
                    break

            if not modified:
                messagebox.showinfo("Info", "No se detectaron cambios para guardar")
                return

            # Backup
            self.backup_path = self.save_path + ".backup"
            shutil.copy2(self.save_path, self.backup_path)

            # Guardar
            self._write_save_file(self.save_path, self.save_data)
            
            # También crear .edited.json y .gz
            base = Path(self.save_path).with_suffix("")
            edited_path = str(base) + ".edited.json"
            with open(edited_path, "w", encoding="utf-8") as f:
                json.dump(self.save_data, f, indent=2, ensure_ascii=False)

            gz_path = str(base) + ".gz"
            json_bytes = json.dumps(self.save_data, indent=2, ensure_ascii=False).encode("utf-8")
            with open(gz_path, "wb") as f_out:
                with gzip.GzipFile(filename="SAVE", mode="wb", fileobj=f_out) as gz:
                    gz.write(json_bytes)

            self.status_label.configure(text="✅ Save guardado exitosamente")
            messagebox.showinfo(
                "Éxito", 
                f"Save guardado correctamente!\n\n"
                f"📁 Original: {self.save_path}\n"
                f"💾 Backup: {self.backup_path}\n"
                f"📝 Editado: {edited_path}\n"
                f"📦 GZ (miembro 'SAVE'): {gz_path}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            self.status_label.configure(text=f"❌ Error al guardar: {str(e)[:80]}")

    def _parse_widget_value(self, widget_info):
        """Convertir valor de widget al tipo correcto para el save."""
        var = widget_info["var"]
        vtype = widget_info["type"]
        
        raw = var.get()
        
        if vtype == "ValueBool":
            return raw if isinstance(raw, bool) else raw.lower() in ("true", "1", "yes", "on")
        
        elif vtype == "ValueNumber":
            try:
                return float(raw)
            except ValueError:
                return 0.0
        
        elif vtype == "ValueString":
            return raw if isinstance(raw, str) else str(raw)
        
        return raw

    def _write_save_file(self, path, data):
        """Escribir save preservando formato original (gzip o JSON)."""
        with open(path, "rb") as f:
            magic = f.read(2)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if magic == b"\x1f\x8b":
            with open(path, "wb") as f_out:
                with gzip.GzipFile(filename="SAVE", mode="wb", fileobj=f_out) as gz:
                    gz.write(json_str.encode("utf-8"))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)

    def _reset_backup(self):
        """Restaurar desde backup."""
        if not self.backup_path or not os.path.exists(self.backup_path):
            messagebox.showwarning("Advertencia", "No se encontró archivo de backup")
            return
        
        if messagebox.askyesno("Confirmar", "¿Restaurar save desde backup? Se perderán cambios actuales."):
            shutil.copy2(self.backup_path, self.save_path)
            self._load_save()
            self.status_label.configure(text="♻️ Restaurado desde backup")

    # ============================================================
    # HELPERS
    # ============================================================

    def _load_known_quests(self):
        """Cargar nombres de quests conocidos desde quest_mapping_final.json.
        Busca en múltiples rutas: Linux, Windows y rel. al exe."""
        import os
        possible_paths = [
            "/home/jesusgs/proyectos/starmaker/quest_mapping_final.json",
            "/home/jesusgs/proyectos/starmaker/quest_mapping.json",
            "quest_mapping_final.json",
            "quest_mapping.json",
        ]
        # Si estamos en Windows, añadir paths comunes
        if os.name == "nt":  # Windows
            possible_paths.extend([
                os.path.expanduser("~/quest_mapping_final.json"),
                "C:/Starmaker/quest_mapping_final.json",
                os.path.join(os.getcwd(), "quest_mapping_final.json"),
            ])
        # Añadir path del directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(script_dir, "quest_mapping_final.json"))
        possible_paths.append(os.path.join(script_dir, "quest_mapping.json"))
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    continue
        return {}

    def _get_tasks_for_quest(self, quest_guid):
        """Obtener los tasks (sub-objetivos) vinculados a una quest por su GUID."""
        if not hasattr(self, 'tasks_data'):
            return {}
        tasks = self.tasks_data
        quest_tasks = {}
        for task_id, task_info in tasks.items():
            quest_hash = task_info.get("quest_hash")
            if quest_hash == quest_guid:
                quest_tasks[task_id] = task_info
        return quest_tasks


def main():
    root = ctk.CTk()
    app = EnhancedSaveEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()