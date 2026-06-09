"use client";
import React from 'react';
import MarketP2P from '@/components/MarketP2P';

interface MarketTabProps {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
}

export default function MarketTab({ userId, token, recargarSaldos }: MarketTabProps) {
  return (
    <div className="animate-in fade-in duration-300">
      <MarketP2P userId={userId} token={token} recargarSaldos={recargarSaldos} />
    </div>
  );
}
