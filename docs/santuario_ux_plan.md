Restricciones de Layout (UI/UX Móvil Vertical)
Relación de Aspecto: 9:16 / Vertical nativo para móviles.

Regla de Oro de Programación: CERO SCROLL VERTICAL u HORIZONTAL. Toda la pantalla es un diorama estático unificado en un solo plano de cámara (Chinampa Estática). Todo el Core Loop se debe gestionar en esta vista única mediante estados visuales dinámicos.

El espacio en pantalla se divide estrictamente en Tres Zonas Fijas:

+---------------------------------------+
|  [HUD: Recursos / AXF / FRJ / Ticket] |
|---------------------------------------|
|  ZONA SUPERIOR: Crianza y Estados     |
|  - 7 Slots Fijos de Nidos (Webitos)   |
|---------------------------------------|
|  ZONA CENTRAL: El Diorama del Cenote  |
|  - Mesa de Lotería Central            |
|  - Anclaje Host (1) + Visitantes (4)  |
|  - Anclajes de Adorno Fijos (Slots)   |
+---------------------------------------+
|  ZONA INFERIOR: UI Social Compacta    |
|  - Lista Fija Amigos Activos          |
|  - Menú Navegación Global (Iconos)    |
+---------------------------------------+

Categorías del Inventario de Adornos del Santuario:
Mantel de Mesa (Runner Overlay):

Tipo: Capa que se dibuja directamente sobre la superficie de la mesa de papel.

Ítems de ejemplo: Papel Picado 'Catrina', Mantel Bordado Tenango, Estilo Zenote Minimalista.

Adornos Fijos (Table Slots):

Tipo: 4 posiciones o coordenadas fijas (2 a la izquierda de la mesa, 2 a la derecha) en el suelo de piedra recortada del cenote.

Ítems de ejemplo: Maceta Loto de Papel, Jarrón de Obsidiana Calada, Mini-Altar de Velas, Incensario Copal.

Iluminación (Lighting Layer):

Tipo: Capa superior y ambiental que modifica los tintes de color y añade objetos colgantes.

Ítems de ejemplo: Guirnalda Fuego Fatuo (tira de faroles de papel picado colgando de las raíces), Lámparas de Jade, Antorchas Chinampa.

Entorno Skin (Cenote Background Skin):

Tipo: Swap completo del sprite/textura de fondo de las capas de papel que forman la cueva y el agua.

Ítems de ejemplo: Cueva de Coral de Papel, Templo Maya en Ruinas, Fondo de Día de Muertos (Calaveras Caladas).