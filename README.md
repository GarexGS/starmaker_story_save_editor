# 🎮 Starmaker Story Save Editor

A modern tool to analyze, view, and edit the save file of **Starmaker Story** (Unity + GameCreator).

[![License](https://img.shields.io/github/license/your-username/starmaker-save-editor?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](LICENSE)
[![Last Updated](https://img.shields.io/github/last-modified-version/your-username/starmaker-save-editor?style=flat-square)](https://github.com/your-username/starmaker-save-editor/commits/main)

## 📖 Description

**Starmaker Story** is a game built in Unity using GameCreator's narrative system. The save file (`TokenJournal`) contains:

- **34 quests** tracked by UUID hashes (not human-readable)
- **176 tasks** with `m_State` (0=Inactive, 1=Active, 2=Completed) and `m_Value` (progress)

This project allows you to:

- 🔍 **Visualize** all quests and their current states
- ✏️ **Edit** task states via a graphical interface (recommended)
- ⚡ **Edit** via CLI scripts for automation
- 💾 **Save** with automatic backup and compression

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install customtkinter
```

### 2. Run the GUI Editor

```bash
python3 ./gui_editor_fixed.py
```

### 3. Or Use the CLI Editor

```bash
python3 ./save_editor.py list
python3 ./save_editor.py edit <task_id> <state>
```

---

## 🖥️ GUI Features

| Feature | Status |
|---------|--------|
| View all quests | ✅ Done |
| Edit task states | ✅ Done |
| Save with backup | ✅ Done |
| View save path | ✅ Done |
| Reset from backup | ✅ Done |

The GUI displays:
- All 34 quests found in the save
- Current state for each quest (Inactive/Active/Completed)
- Task names and states
- Save path information

---

## ⚙️ CLI Features

```bash
# List all quests and tasks
python3 ./save_editor.py list

# Edit task state (0=Inactive, 1=Active, 2=Completed)
python3 ./save_editor.py edit <task_id> <state>
```

---

## 📊 Task Mapping

Key tasks for the "Bishop (Mario)" quest:

| Task ID | Name | State |
|---------|------|-------|
| `-1759660069` | Visit Mario | 🟢 Activa |
| `1315981684` | Push Katarina past her limits | 🟢 Activa |
| `1070760953` | Visit the sauna every week | 🟢 Activa |
| `1410719678` | Corrupt Emma | 🔴 Completada |
| `1813187919` | Help Mario compare files | 🔴 Completada |
| `1070760953` | Visit the sauna every week | 🟢 Activa |

---

## 📁 Project Structure

```
starmaker/
├── gui_editor_fixed.py      # Main GUI editor
├── save_editor.py           # CLI editor
├── launch_gui.py            # Quick launch script
├── quest_mapping.json       # Quest GUID → name mappings
├── README.md                # This file
└── game/                    # Extracted game files (1.9GB)
```

---

## 📌 Important Notes

- The save file is located at: `./save.json` (or `save_original.json` for backup)
- The game save directory: `C:\Users\%USERPROFILE%\AppData\LocalLow\Arvus Games\Starmaker Story\Saves`
- Always keep a backup before editing
- Task states: `0=Inactive`, `1=Active`, `2=Completed`
- Task IDs are visible in the GUI and CLI tools

---

## 📌 License

Personal use only.

---

*Project built with Python, CustomTkinter, and deep dive into Unity GameCreator saves.*