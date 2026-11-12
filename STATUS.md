# Starmaker Story — Estado de extracción de assets

## Estado actual
- .NET 11.0.100 instalado en /home/jesusgs/.dotnet
- AssetRipper compilado correctamente
- Extracción C# (Extractor.cs) lista para construir
- Bloqueo: AssetRipper.Primitives.dll 3.2.0.0 no está en el directorio de salida del extractor

## Rutas
- Proyecto: /home/jesusgs/proyectos/starmaker/
- Datos del juego: /home/jesusgs/proyectos/starmaker/game/Starmaker 1.8E/Starmaker Story_Data/
- AssetRipper: /home/jesusgs/proyectos/AssetRipper/
- Extractor: /home/jesusgs/proyectos/starmaker/AssetRipperExtractor/
- Salida: /home/jesusgs/proyectos/starmaker/extracted_assets/

## Pasos para ejecutar
1. export PATH="$HOME/.dotnet:$PATH"
2. cd /home/jesusgs/proyectos/starmaker/AssetRipperExtractor
3. cp /home/jesusgs/proyectos/AssetRipper/Source/0Bins/AssetRipper.GUI.Free/Release/AssetRipper.Primitives.dll bin/Release/net11.0/
4. dotnet build Extractor.csproj -c Release
5. dotnet run --project Extractor.csproj -c Release

## Assets reales confirmados
- globalgamemanagers (binario, 1.5 MB)
- globalgamemanagers.assets
- globalgamemanagers.resources
- level0, level1, level2
- resources.assets, resources.resource
- sharedassets0.assets, sharedassets0.resource
- sharedassets1.assets, sharedassets1.resource
- sharedassets2.assets, sharedassets2.resource
- app.info

## Próximos pasos
- Extraer assets y cruzar con quest_mapping_final.json
- Completar las quests faltantes (34 quests, 176 tasks)
- Actualizar gui_editor_fixed.py con los nombres de las misiones