# Starmaker Story Save Editor

## Resumen
Proyecto para explorar y editar el save del juego **Starmaker Story** (Unity + GameCreator). Permite modificar el estado de la historia y buscar elementos ocultos sin reiniciar el juego.

## Hallazgos principales

### Formato del archivo
- El archivo original es un archivo **`.json`** extraído del `TokenJournal` (la cuarta entrada `m_Entries`).
- Contiene:
  - 34 **quests** (referenciados por hashes UUID, no por nombres legibles)
  - 176 **tasks** organizadas por `QuestHash` y `TaskId`
- Cada `task` tiene:
  - `m_State`: `0 = Inactiva`, `1 = Activa`, `2 = Completada`
  - `m_Value`: `0.0`, `3.0`, `5.0`, `54.0`, etc. — progreso de la historia

### Cómo funcionan las tareas
- La misión con Mario y Katarina está implementada como un conjunto de tareas.
- Las tareas se convierten en **"Activas"** (`m_State` = 1) cuando su `m_Value` es ≠ 0.0.
- Para marcar una misión como completada: `m_State` = 2 y `m_Value` = valor deseado.

## Scripts proporcionados

1. `parse_quests.py` → Muestra la estructura completa de quests del TokenJournal.
2. `list_active_tasks.py` → Lista todas las tareas actualmente activas (`m_State` = 1).
3. `filter_nonzero_active.py` → Muestra solo las tareas con `m_Value` ≠ 0.0 (partes *activas* clave).

Todas las tareas individuales se pueden ver con la salida del script (info completa sobre `QuestHash`, `TaskId` y `m_Value`).

## Cómo editar un save — Guía paso a paso

### 1. Editar el archivo JSON
1. Haz **copia de seguridad** del `doc_44b0013cfacf_SAVE` original.
2. Abre el JSON en VS Code/Notepad++/vim.
3. Si necesitas **agregar dinero** o una habilidad (ej. "Cash" = 250.0), busca el nombre legible:
   ```
   "m_Name": { "m_String": "Cash" }
   ```
   El `rid` referenciado (`"m_Value": { "rid": 2454 }`) lo enlaza con el bloque `ValueNumber`:
   ```
   "rid": 2454
   "m_Value": 250.0
   ```
4. Edita el `m_Value` deseado (copia la misma estructura si necesitas nuevos `rid`s, o reusa los existentes).
5. Guarda el JSON.

### 2. Comprimir el save
- Empaca el JSON editado en **`.gz`** (ej. usando `gzip -c doc_44b0013cfacf_SAVE > save.gz`).

### 3. Reemplazar el save
- En la carpeta AppData\LocalLow\Arvus Games\Starmaker Story\Saves, reemplaza el antiguo archivo con el nuevo.

### 4. Probar el cambio
- Abre el juego y verifica que el ajuste surtió efecto.

## Consejo de seguridad
- Siempre guarda el save original (`doc_44b0013cfacf_SAVE.backup`) antes de modificar.
- Los `rid`s pueden diferir entre versiones del juego; busca por el *nombre legible* ("Cash", "mario", "katarina") y compara si es posible.

## Archivo actual
- **Ruta**: `/home/jesusgs/proyects/starmaker/`
- Contiene scripts para **analizar el save actual**, encontrar tareas activas y extraer valores no nulos.
- Puedes editarlos y volver a ejecutarlos para verificar el estado de un save editado.

## Próximos pasos
1. Revisa los scripts (`parse_quests.py`, etc.).
2. Aplica la técnica `rid` de la guía anterior para modificar misiones, elementos o progreso en el archivo JSON.
3. Guarda el save como `.gz` y reemplázalo para probar los cambios.

## Licencia
Para uso personal del desarrollador. No redistribuir.

---
*Los hallazgos fueron hechos a partir del save `doc_44b0013cfacf_SAVE` encontrado en `~/.hermes/cache/documents/` (JSON extraído del TokenJournal del save).

Para más detalles sobre cómo editar variables específicas, revisa el archivo de código del script.