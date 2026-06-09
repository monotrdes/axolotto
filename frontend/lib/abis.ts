// Minimal event ABI fragments — extracted from /contracts/out/*.json
// Only event definitions needed for watchContractEvent

export const FRIJOLITO_EVENTS = [
  {
    type: 'event',
    name: 'Transfer',
    inputs: [
      { name: 'from',  type: 'address', indexed: true },
      { name: 'to',    type: 'address', indexed: true },
      { name: 'value', type: 'uint256', indexed: false },
    ],
  },
] as const;

export const GAME_CONTROLLER_EVENTS = [
  {
    type: 'event',
    name: 'PartidaJugada',
    inputs: [
      { name: 'jugador',     type: 'address', indexed: true },
      { name: 'axolotitoId', type: 'uint256', indexed: true },
      { name: 'tablaId',     type: 'uint256', indexed: false },
      { name: 'gano',        type: 'bool',    indexed: false },
      { name: 'premio',      type: 'uint256', indexed: false },
    ],
  },
  {
    type: 'event',
    name: 'TiendaCompra',
    inputs: [
      { name: 'jugador',  type: 'address', indexed: true },
      { name: 'itemType', type: 'string',  indexed: false },
      { name: 'itemId',   type: 'uint256', indexed: false },
      { name: 'precio',   type: 'uint256', indexed: false },
      { name: 'moneda',   type: 'string',  indexed: false },
    ],
  },
  {
    type: 'event',
    name: 'AxolotitoNutrido',
    inputs: [
      { name: 'jugador',      type: 'address', indexed: true },
      { name: 'axolotitoId',  type: 'uint256', indexed: false },
      { name: 'consumableId', type: 'uint256', indexed: false },
    ],
  },
] as const;

export const WEBITOS_EVENTS = [
  {
    type: 'event',
    name: 'WebitoMinted',
    inputs: [
      { name: 'tokenId', type: 'uint256', indexed: true },
      { name: 'to',      type: 'address', indexed: true },
      { name: 'fase',    type: 'uint8',   indexed: false },
    ],
  },
] as const;
