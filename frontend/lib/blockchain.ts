import { createPublicClient, http } from 'viem';
import { anvil, polygonAmoy } from 'viem/chains';

const RPC_URL = process.env.NEXT_PUBLIC_RPC_URL ?? 'http://127.0.0.1:8545';
const CHAIN_ID = Number(process.env.NEXT_PUBLIC_CHAIN_ID ?? 31337);

const chain = CHAIN_ID === 31337 ? anvil : polygonAmoy;

export const publicClient = createPublicClient({
  chain,
  transport: http(RPC_URL),
});

export const CONTRACT_ADDRESSES = {
  FRIJOLITO:      (process.env.NEXT_PUBLIC_GEMA_ALGA_ADDRESS       ?? '') as `0x${string}`,
  AXOFICHA:       (process.env.NEXT_PUBLIC_AXOGEMA_ADDRESS          ?? '') as `0x${string}`,
  WEBITOS:         (process.env.NEXT_PUBLIC_WEBITOS_ADDRESS          ?? '') as `0x${string}`,
  GAME_CONTROLLER: (process.env.NEXT_PUBLIC_GAME_CONTROLLER_ADDRESS  ?? '') as `0x${string}`,
} as const;
