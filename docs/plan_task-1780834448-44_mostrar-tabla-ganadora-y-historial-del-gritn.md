# Plan: Mostrar tabla ganadora y historial del Gritón

> Generado por **antigravity** · tarea `task-1780834448-44` · 2026-06-07T12:14:08.867910+00:00

## Descripción
Mostrar la tabla ganadora y el patrón de victoria en la pantalla de win/lose. Mostrar el historial de cartas en orden de salida en el Gritón. Mostrar un Gritón simplificado en la pantalla win/lose destacando las cartas ganadoras.

## Archivos a crear/modificar
- `frontend/hooks/useCpuGame.ts`
- `frontend/components/CpuGameWrapper.tsx`
- `frontend/components/screens/GameScreen.tsx`

## Checklist de criterios de aceptación
- [ ] Visualizar la tabla ganadora en la pantalla de resultados (win/lose) con el estilo BoardCardGrid.
- [ ] Destacar el patrón de celdas ganadoras (winLine) en la tabla ganadora.
- [ ] Mostrar un historial horizontal auto-scrolleable de las cartas llamadas por el Gritón en orden de salida.
- [ ] Mostrar una versión simplificada del Gritón en la pantalla de resultados que destaque (resalte en oro y opaque el resto) las cartas que completaron el patrón de victoria.

## Notas de diseño
Alinear la detección de victoria en useCpuGame.ts con el winning_line del backend. Pasar playerWinLine, cpuWinLine y calledCardsHistory a GameScreen. Crear el componente MiniGriton y el diseño de burbuja de diálogo + historial filtrado en la pantalla de resultados.

## Guía de verificación
Iniciar partida CPU. Verificar que durante el juego aparece el historial de cartas. Al ganar o perder, verificar que la tabla ganadora aparece con sus celdas en oro, y el Gritón simplificado muestra la burbuja de lotería con las cartas ganadoras destacadas.
