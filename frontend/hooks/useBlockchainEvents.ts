'use client';

import { useEffect, useRef } from 'react';
import { formatUnits } from 'viem';
import { publicClient, CONTRACT_ADDRESSES } from '@/lib/blockchain';
import { FRIJOLITO_EVENTS, GAME_CONTROLLER_EVENTS, WEBITOS_EVENTS } from '@/lib/abis';
import { useRealtime } from '@/context/RealtimeContext';

type Callbacks = {
  onBalanceChange: (diffGal: number) => void;
  onGameEvent: () => void;
  onShopEvent: () => void;
};

export function useBlockchainEvents(
  walletAddress: string | undefined,
  callbacks: Callbacks
) {
  // Always reference latest callbacks without recreating watchers
  const cbRef = useRef(callbacks);
  cbRef.current = callbacks;

  const { enablePolling } = useRealtime();

  useEffect(() => {
    if (!walletAddress || !CONTRACT_ADDRESSES.FRIJOLITO || !enablePolling) return;

    const addr = walletAddress.toLowerCase() as `0x${string}`;

    // COR received (minted or transferred to us)
    const unwatchGalIn = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.FRIJOLITO,
      abi: FRIJOLITO_EVENTS,
      eventName: 'Transfer',
      args: { to: addr },
      poll: true,
      pollingInterval: 5_000,
      onLogs: (logs) => {
        const total = logs.reduce(
          (sum, l) => sum + Number(formatUnits((l.args.value as bigint) ?? BigInt(0), 18)),
          0
        );
        if (total > 0) cbRef.current.onBalanceChange(total);
      },
    });

    // COR spent (burned or transferred from us)
    const unwatchGalOut = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.FRIJOLITO,
      abi: FRIJOLITO_EVENTS,
      eventName: 'Transfer',
      args: { from: addr },
      poll: true,
      pollingInterval: 5_000,
      onLogs: (logs) => {
        const total = logs.reduce(
          (sum, l) => sum + Number(formatUnits((l.args.value as bigint) ?? BigInt(0), 18)),
          0
        );
        if (total > 0) cbRef.current.onBalanceChange(-total);
      },
    });

    // Individual game played
    const unwatchPartida = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.GAME_CONTROLLER,
      abi: GAME_CONTROLLER_EVENTS,
      eventName: 'PartidaJugada',
      args: { jugador: addr },
      poll: true,
      pollingInterval: 10_000,
      onLogs: () => cbRef.current.onGameEvent(),
    });

    // Axolotito fed
    const unwatchNutrido = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.GAME_CONTROLLER,
      abi: GAME_CONTROLLER_EVENTS,
      eventName: 'AxolotitoNutrido',
      args: { jugador: addr },
      poll: true,
      pollingInterval: 10_000,
      onLogs: () => cbRef.current.onGameEvent(),
    });

    // Shop purchase
    const unwatchCompra = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.GAME_CONTROLLER,
      abi: GAME_CONTROLLER_EVENTS,
      eventName: 'TiendaCompra',
      args: { jugador: addr },
      poll: true,
      pollingInterval: 15_000,
      onLogs: () => cbRef.current.onShopEvent(),
    });

    // Webito adopted
    const unwatchWebito = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.WEBITOS,
      abi: WEBITOS_EVENTS,
      eventName: 'WebitoMinted',
      args: { to: addr },
      poll: true,
      pollingInterval: 15_000,
      onLogs: () => cbRef.current.onShopEvent(),
    });

    return () => {
      unwatchGalIn();
      unwatchGalOut();
      unwatchPartida();
      unwatchNutrido();
      unwatchCompra();
      unwatchWebito();
    };
  }, [walletAddress, enablePolling]);
}
