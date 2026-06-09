"use client";
import React from 'react';
import { useStore } from '@/hooks/useStore';
import OfficialTab from '@/components/store/OfficialTab';
import MarketTab from '@/components/store/MarketTab';
import CardMelter from '@/components/CardMelter';
import UnboxingModal from '@/components/ui/UnboxingModal';
import UnboxingFlow from '@/components/store/UnboxingFlow';
import StoreHeader from '@/components/store/StoreHeader';
import StoreHelpModal from '@/components/store/StoreHelpModal';
import type { StoreProps } from '@/types/store';

export default function AxolottoStore({
  userId,
  balances,
  token,
  cambiarTab,
  recargarSaldos,
}: StoreProps) {
  const store = useStore({ userId, token, recargarSaldos, cambiarTab });

  if (store.cargando) {
    return (
      <div className="text-center text-[#E4007C] animate-pulse py-10 font-bold tracking-widest">
        CARGANDO EL CRIADERO...
      </div>
    );
  }

  const handleBack = () => {
    if (store.storeTab === 'market' || store.storeTab === 'melter') {
      store.setStoreTab('official');
    } else {
      cambiarTab('jugar');
    }
  };

  return (
    <div className="w-full mt-6 bg-slate-950/80 backdrop-blur-md text-white rounded-[2rem] p-5 sm:p-8 border border-[#E4007C]/30 shadow-[0_0_40px_rgba(228,0,124,0.15)] relative">
      <StoreHeader storeTab={store.storeTab} onBack={handleBack} onHelp={() => store.setHelpOpen(true)} />

      {store.storeTab === 'official' && (
        <OfficialTab
          items={store.items}
          userId={userId}
          token={token}
          recargarSaldos={recargarSaldos}
          cambiarTab={cambiarTab}
          setStoreTab={store.setStoreTab}
          setSobresDrawerAbierto={store.setSobresDrawerAbierto}
          sobresDrawerAbierto={store.sobresDrawerAbierto}
          setWebitosDrawerAbierto={store.setWebitosDrawerAbierto}
          webitosDrawerAbierto={store.webitosDrawerAbierto}
          setCryptoCheckoutOpen={store.setCryptoCheckoutOpen}
          cryptoCheckoutOpen={store.cryptoCheckoutOpen}
          comprarItem={store.comprarItem}
          maxNidos={store.maxNidos}
          totalEggsInInventory={store.totalEggsInInventory}
          totalAxolotitosHatched={store.totalAxolotitosHatched}
          nextCaveLevel={store.nextCaveLevel}
        />
      )}

      {store.storeTab === 'melter' && (
        <div className="animate-in fade-in duration-300">
          <CardMelter
            userId={userId}
            token={token}
            recargarSaldos={recargarSaldos}
            balances={balances}
            onBack={() => store.setStoreTab('official')}
            onNavigateToMarket={() => store.setStoreTab('market')}
          />
        </div>
      )}

      {store.storeTab === 'market' && (
        <MarketTab userId={userId} token={token} recargarSaldos={recargarSaldos} />
      )}

      <UnboxingModal
        open={store.modalAbierto}
        onClose={store.cerrarModalUnboxing}
        pack={store.currentOpeningPack}
        cards={store.cartasObtenidasObjects}
        txHash={store.txHash}
        ownedCardIds={store.ownedCardIds}
      />

      <UnboxingFlow
        open={store.modalAdopcionAbierto}
        itemComprado={store.itemComprado}
        mensajeAdopcion={store.mensajeAdopcion}
        txHash={store.txHash}
        abrirAhoraLoading={store.abrirAhoraLoading}
        adopcionParticles={store.adopcionParticles}
        onAbrirAhora={store.abrirSobreDesdeModal}
        onCerrar={() => store.setModalAdopcionAbierto(false)}
        onIrAlInventario={() => {
          store.setModalAdopcionAbierto(false);
          cambiarTab('inventario');
        }}
        onIrAlCriadero={() => {
          store.setModalAdopcionAbierto(false);
          cambiarTab('criadero');
        }}
        onIrATablas={() => {
          store.setModalAdopcionAbierto(false);
          cambiarTab('tablas');
        }}
        onSeguirComprando={() => store.setModalAdopcionAbierto(false)}
      />

      <StoreHelpModal open={store.helpOpen} onClose={() => store.setHelpOpen(false)} />
    </div>
  );
}
