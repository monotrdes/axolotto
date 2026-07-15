"use client";
import React from 'react';
import { useStore } from '@/hooks/useStore';
import OfficialTab from '@/components/store/OfficialTab';
import MarketTab from '@/components/store/MarketTab';
import ReciclonPanel from '@/components/ReciclonPanel';
import UnboxingModal from '@/components/ui/UnboxingModal';
import UnboxingFlow from '@/components/store/UnboxingFlow';
import StoreHeader from '@/components/store/StoreHeader';
import StoreHelpModal from '@/components/store/StoreHelpModal';
import type { StoreProps } from '@/types/store';
import { PAPER_WORLD } from '@/lib/paperWorld';
import { useProductPolicy } from '@/hooks/useProductPolicy';

export default function AxolottoStore({
  userId,
  token,
  cambiarTab,
  recargarSaldos,
  initialSection,
  sectionNonce,
}: StoreProps) {
  const store = useStore({ userId, token, recargarSaldos, cambiarTab });
  const { capabilities } = useProductPolicy();

  // Mundo papel picado: el puesto tocado en el diorama abre su sección
  // (forja→reciclon, trajineras→market, puestos→official).
  React.useEffect(() => {
    if (initialSection) store.setStoreTab(initialSection);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialSection, sectionNonce]);

  if (store.cargando) {
    return (
      <div className="text-center text-[#E4007C] animate-pulse py-10 font-bold tracking-widest">
        CARGANDO EL CRIADERO...
      </div>
    );
  }

  const handleBack = () => {
    if (store.storeTab === 'market' || store.storeTab === 'reciclon') {
      store.setStoreTab('official');
    } else {
      cambiarTab('jugar');
    }
  };

  return (
    <div
      className={
        PAPER_WORLD
          ? 'w-full mt-6 papel-amate backdrop-blur-md text-white p-5 sm:p-8 relative'
          : 'w-full mt-6 bg-slate-950/80 backdrop-blur-md text-white rounded-[2rem] p-5 sm:p-8 border border-[#E4007C]/30 shadow-[0_0_40px_rgba(228,0,124,0.15)] relative'
      }
    >
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

      {store.storeTab === 'reciclon' && (
        <div className="animate-in fade-in duration-300">
          {capabilities.assets.reciclon ? (
            <ReciclonPanel
              userId={userId}
              token={token}
              recargarSaldos={recargarSaldos}
              onBack={() => store.setStoreTab('official')}
            />
          ) : (
            <UnavailableFeature
              title="El Reciclón está en pausa"
              description="Volverá cuando la custodia y el canje estén verificados en cadena."
              onBack={() => store.setStoreTab('official')}
            />
          )}
        </div>
      )}

      {store.storeTab === 'market' && (
        capabilities.commerce.player_marketplace ? (
          <MarketTab userId={userId} token={token} recargarSaldos={recargarSaldos} />
        ) : (
          <UnavailableFeature
            title="Marketplace aún no disponible"
            description="Se habilitará para adultos verificados cuando estén listos pagos, protección al comprador y retiros."
            onBack={() => store.setStoreTab('official')}
          />
        )
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

function UnavailableFeature({
  title,
  description,
  onBack,
}: {
  title: string;
  description: string;
  onBack: () => void;
}) {
  return (
    <div className="mx-auto max-w-xl rounded-3xl border border-white/10 bg-slate-950/70 p-8 text-center">
      <h3 className="text-xl font-black text-white">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-slate-400">{description}</p>
      <button
        type="button"
        onClick={onBack}
        className="mt-6 rounded-xl border border-white/15 px-5 py-2 text-sm font-bold text-white hover:bg-white/10"
      >
        Volver a la tienda
      </button>
    </div>
  );
}
