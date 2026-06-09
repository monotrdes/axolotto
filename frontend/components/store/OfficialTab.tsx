"use client";
import React from 'react';
import { X, ChevronRight } from 'lucide-react';
import HoldButton from '@/components/ui/HoldButton';
import BottomSheet from '@/components/ui/BottomSheet';
import CryptoCheckout from '@/components/CryptoCheckout';
import type { StoreItem } from '@/types/store';

interface OfficialTabProps {
  items: StoreItem[];
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
  cambiarTab: (tab: string) => void;
  setStoreTab: (tab: 'official' | 'market' | 'melter') => void;
  setSobresDrawerAbierto: (v: boolean) => void;
  sobresDrawerAbierto: boolean;
  setWebitosDrawerAbierto: (v: boolean) => void;
  webitosDrawerAbierto: boolean;
  setCryptoCheckoutOpen: (v: boolean) => void;
  cryptoCheckoutOpen: boolean;

  /** Called when a booster/egg is bought */
  comprarItem: (itemId: number, moneda: string) => Promise<void>;

  maxNidos?: number;
  totalEggsInInventory?: number;
  totalAxolotitosHatched?: number;
  nextCaveLevel?: any;
}

export default function OfficialTab({
  items,
  userId,
  token,
  recargarSaldos,
  cambiarTab,
  setStoreTab,
  setSobresDrawerAbierto,
  sobresDrawerAbierto,
  setWebitosDrawerAbierto,
  webitosDrawerAbierto,
  setCryptoCheckoutOpen,
  cryptoCheckoutOpen,
  comprarItem,
  maxNidos,
  totalEggsInInventory,
  totalAxolotitosHatched,
  nextCaveLevel,
}: OfficialTabProps) {
  const ocupadosTotal = (totalEggsInInventory ?? 0) + (totalAxolotitosHatched ?? 0);
  const sinNidosGlobal =
    maxNidos !== undefined &&
    totalEggsInInventory !== undefined &&
    totalAxolotitosHatched !== undefined &&
    ocupadosTotal >= maxNidos;

  return (
    <div className="max-w-xl mx-auto flex flex-col">
      {/* === PAPEL PICADO === */}
      <div className="flex justify-between w-full gap-1 mb-6 overflow-hidden select-none h-6">
        {['#0ea5e9', '#10b981', '#f97316', '#ec4899', '#ef4444', '#3b82f6', '#f59e0b', '#14b8a6'].map(
          (color, i) => (
            <div
              key={i}
              className="flex-1 h-5 flex items-center justify-center text-[8px] font-black text-black/60 relative"
              style={{
                backgroundColor: color,
                clipPath: 'polygon(0% 0%, 100% 0%, 100% 85%, 50% 100%, 0% 85%)',
              }}
            >
              ☺
            </div>
          ),
        )}
      </div>

      {/* === CARD GOLDEN: EL BANCO === */}
      <div className="bg-gradient-to-br from-slate-950 via-[#272710]/20 to-slate-950 border border-yellow-500/40 rounded-[2rem] p-6 mb-6 shadow-[0_0_30px_rgba(234,179,8,0.08)] relative overflow-hidden group">
        <div className="absolute top-0 right-0 text-[120px] opacity-5 select-none pointer-events-none leading-none">
          💎
        </div>

        <div className="flex items-start gap-4 mb-5">
          <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-amber-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-yellow-500/20 group-hover:scale-105 transition-transform duration-300">
            💎
          </div>
          <div>
            <h3 className="text-xl font-black text-yellow-400 tracking-tight uppercase">
              El Banco
            </h3>
            <p className="text-xs text-slate-450">Compra AXF aquí, gana FRJ jugando</p>
          </div>
        </div>

        {/* Recargar AXF con cripto — único botón en El Banco */}
        <button
          onClick={() => setCryptoCheckoutOpen(true)}
          className="w-full flex items-center justify-between bg-gradient-to-r from-purple-950/40 via-[#1a0a2e]/60 to-purple-950/40 hover:via-purple-950/50 border border-purple-500/25 hover:border-purple-500/50 rounded-2xl p-3.5 transition-all duration-300 group active:scale-[0.98]"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center text-xl shadow-md shadow-purple-500/20 group-hover:scale-105 transition-transform shrink-0">
              💎
            </div>
            <div className="text-left">
              <div className="text-[11px] font-black text-white uppercase tracking-wide">
                Recargar AXF con cripto
              </div>
              <div className="text-[9px] text-slate-500">
                Paga USDC · Recibe Axofichas al instante
              </div>
            </div>
          </div>
          <div className="w-7 h-7 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-all shrink-0">
            <ChevronRight size={14} />
          </div>
        </button>

        {/* Los FRJ ya no se compran — se ganan jugando */}
        <div className="mt-3 rounded-xl bg-amber-950/20 border border-amber-500/20 p-3">
          <p className="text-[10px] text-amber-300/80 font-bold leading-relaxed text-center">
            🪙 Los Frijolitos (FRJ) ya no están a la venta.
            Gánalos participando en partidas, reclamando tu recompensa diaria
            o mediante el staking de tus Axolotitos en el Cenote.
          </p>
        </div>
      </div>

      {/* === FILAS DE CATEGORÍAS (STACK VERTICAL) === */}
      <div className="flex flex-col gap-4">
        {/* ROW 1: LOS SOBRES */}
        <button
          onClick={() => setSobresDrawerAbierto(true)}
          className="w-full text-left bg-gradient-to-r from-slate-950 via-purple-950/20 to-slate-950 hover:via-purple-950/40 border border-purple-500/20 hover:border-purple-500/50 rounded-3xl p-4 flex items-center justify-between transition-all duration-300 group shadow-[0_0_20px_rgba(0,0,0,0.4)] active:scale-[0.98] cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              📦
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-lg sm:text-xl font-black italic uppercase text-white tracking-tight leading-none mb-1">
                  Los Sobres
                </h4>
                <span className="bg-gradient-to-r from-pink-500 to-[#E4007C] text-white font-black text-[8px] tracking-wider px-2 py-0.5 rounded-full shadow-md uppercase">
                  OFERTA
                </span>
              </div>
              <p className="text-xs text-slate-400">Booster packs de cartas</p>
            </div>
          </div>
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-all">
            <ChevronRight size={16} />
          </div>
        </button>

        {/* ROW 2: LOS WEBITOS */}
        <button
          onClick={() => setWebitosDrawerAbierto(true)}
          className={`w-full text-left bg-gradient-to-r from-slate-950 to-slate-950 rounded-3xl p-4 flex items-center justify-between transition-all duration-300 group shadow-[0_0_20px_rgba(0,0,0,0.4)] active:scale-[0.98] cursor-pointer ${
            sinNidosGlobal
              ? 'via-red-950/20 hover:via-red-950/30 border border-red-500/25 hover:border-red-500/40'
              : 'via-pink-950/20 hover:via-pink-950/40 border border-pink-500/20 hover:border-pink-500/50'
          }`}
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-pink-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              🥚
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-lg sm:text-xl font-black italic uppercase text-white tracking-tight leading-none">
                  Los Webitos
                </h4>
                {sinNidosGlobal && (
                  <span className="bg-red-500/20 border border-red-500/40 text-red-400 font-black text-[7px] px-2 py-0.5 rounded-full uppercase tracking-wider animate-pulse">
                    🔒 Sin nidos
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-440">Adopta un axolotito</p>
            </div>
          </div>
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all ${
            sinNidosGlobal
              ? 'bg-red-500/10 border border-red-500/20 text-red-400 group-hover:bg-red-500 group-hover:text-white'
              : 'bg-pink-500/10 border border-pink-500/20 text-pink-450 group-hover:bg-pink-500 group-hover:text-white'
          }`}>
            <ChevronRight size={16} />
          </div>
        </button>

        {/* ROW 3: EL CENOTE MÍSTICO */}
        <button
          onClick={() => setStoreTab('melter')}
          className="w-full text-left bg-gradient-to-r from-slate-950 via-purple-950/20 to-slate-950 hover:via-purple-950/40 border border-purple-500/20 hover:border-purple-500/50 rounded-3xl p-4 flex items-center justify-between transition-all duration-300 group shadow-[0_0_20px_rgba(0,0,0,0.4)] active:scale-[0.98] cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              🌊
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-lg sm:text-xl font-black italic uppercase text-white tracking-tight leading-none mb-1">
                  El Cenote Místico
                </h4>
                <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-black text-[8px] tracking-wider px-2 py-0.5 rounded-full shadow-md uppercase">
                  NUEVO
                </span>
              </div>
              <p className="text-xs text-slate-400">Funde duplicados y forja cartas</p>
            </div>
          </div>
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-all">
            <ChevronRight size={16} />
          </div>
        </button>

        {/* ROW 4: EL TRUEQUE */}
        <button
          onClick={() => setStoreTab('market')}
          className="w-full text-left bg-gradient-to-r from-slate-950 via-orange-950/20 to-slate-950 hover:via-orange-950/40 border border-orange-500/20 hover:border-orange-500/50 rounded-3xl p-4 flex items-center justify-between transition-all duration-300 group shadow-[0_0_20px_rgba(0,0,0,0.4)] active:scale-[0.98] cursor-pointer relative overflow-hidden"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-orange-400 to-amber-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-orange-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              🤝
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-lg sm:text-xl font-black italic uppercase text-white tracking-tight leading-none mb-1">
                  El Trueque
                </h4>
                <span className="bg-gradient-to-r from-orange-500 to-amber-500 text-white font-black text-[7px] tracking-wider px-2 py-0.5 rounded-full shadow-md uppercase">
                  P2P · ENTRE MARCHANTES
                </span>
              </div>
              <p className="text-xs text-slate-400 text-ellipsis overflow-hidden whitespace-nowrap max-w-[240px] sm:max-w-xs">
                ¿Buscas comprar o cambalachear con otros marchantes? Acá tienes tablas, axolotitos, cartas sueltas y skins.
              </p>
            </div>
          </div>
          <div className="w-8 h-8 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400 group-hover:bg-orange-500 group-hover:text-white transition-all">
            <ChevronRight size={16} />
          </div>
        </button>
      </div>

      {/* === BOTTOM SHEET: SOBRES === */}
      <BottomSheet open={sobresDrawerAbierto} onClose={() => setSobresDrawerAbierto(false)} accent="#818CF8">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl sm:text-2xl font-black text-purple-400 tracking-tight uppercase flex items-center gap-2">
              <span>📦</span> Tienda de Sobres
            </h3>
            <button
              onClick={() => setSobresDrawerAbierto(false)}
              className="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 cursor-pointer"
            >
              <X size={20} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {items
              .filter((i) => i.item_type?.toLowerCase() === 'booster')
              .map((booster) => {
                const vendidos = booster.total_sold || 0;
                const maxSupply = booster.max_supply ?? 0;
                const porcentaje = maxSupply > 0 ? (vendidos / maxSupply) * 100 : 0;
                const theme = booster.item_metadata?.pack_theme || 'pure';
                const isFoil = theme === 'foil';

                let themeBorder = 'border-slate-800 hover:border-slate-700';
                let themeGlow = 'from-slate-800 to-slate-950';
                if (theme === 'fiesta') {
                  themeBorder = 'border-[#E4007C]/40 hover:border-[#E4007C]';
                  themeGlow = 'from-[#E4007C] to-purple-950';
                } else if (theme === 'nido') {
                  themeBorder = 'border-emerald-500/40 hover:border-emerald-500';
                  themeGlow = 'from-emerald-600 to-slate-950';
                } else if (theme === 'cosmos') {
                  themeBorder = 'border-[#818CF8]/40 hover:border-[#818CF8]';
                  themeGlow = 'from-indigo-900 to-purple-950';
                } else if (theme === 'foil') {
                  themeBorder = 'border-amber-400/50 hover:border-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.2)]';
                  themeGlow = 'from-amber-400 via-fuchsia-500 to-purple-600';
                } else {
                  themeBorder = 'border-purple-500/40 hover:border-purple-500';
                  themeGlow = 'from-purple-900 to-slate-950';
                }

                return (
                  <div
                    key={booster.id}
                    className={`bg-slate-950/80 border p-4 rounded-3xl relative overflow-hidden group transition-all duration-300 ${themeBorder} ${
                      isFoil
                        ? 'bg-gradient-to-b from-purple-950/35 via-slate-950 to-slate-950 shadow-[0_0_30px_rgba(245,158,11,0.18)] border-2 border-amber-400/80'
                        : ''
                    }`}
                  >
                    {isFoil && (
                      <div className="absolute top-2.5 right-2.5 bg-amber-400 text-slate-950 font-black text-[7px] px-1.5 py-0.5 rounded uppercase tracking-widest border border-amber-250 z-10 animate-pulse">
                        ¡100 al Mes!
                      </div>
                    )}

                    <div className="flex items-start gap-4">
                      <div
                        className={`w-16 h-16 shrink-0 bg-gradient-to-br ${themeGlow} rounded-2xl flex items-center justify-center text-3xl shadow-md group-hover:scale-105 transition-transform relative overflow-hidden`}
                      >
                        {isFoil && (
                          <>
                            <span className="absolute top-0.5 right-0.5 text-[8px] animate-bounce">
                              ✨
                            </span>
                            <span className="absolute bottom-0.5 bg-amber-400 text-slate-950 text-[6px] font-black px-1 rounded-full uppercase tracking-wider scale-90 border border-amber-200">
                              FOIL
                            </span>
                          </>
                        )}
                        📦
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4
                          className={`font-bold text-md leading-tight mb-1 truncate ${
                            isFoil
                              ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-fuchsia-300 to-purple-300 font-extrabold'
                              : 'text-white'
                          }`}
                        >
                          {booster.name}
                        </h4>
                        <p className="text-[10px] text-slate-400 leading-tight mb-2 line-clamp-2 h-7">
                          {booster.description}
                        </p>

                        <div className="mb-3">
                          <div className="flex justify-between text-[8px] mb-1 text-slate-400 font-semibold">
                            <span>
                              Quedan: {maxSupply - vendidos} / {maxSupply}
                            </span>
                          </div>
                          <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                isFoil
                                  ? 'bg-gradient-to-r from-amber-400 via-fuchsia-500 to-purple-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]'
                                  : 'bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.8)]'
                              }`}
                              style={{ width: `${100 - porcentaje}%` }}
                            ></div>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <HoldButton
                            variant="primary"
                            label={`💎 ${booster.price_axg} AXF`}
                            sublabel="Mantén para confirmar"
                            className="flex-1"
                            onConfirm={() => {
                              setSobresDrawerAbierto(false);
                              comprarItem(booster.id, 'axoficha');
                            }}
                          />
                          {booster.price_gal && (
                            <HoldButton
                              variant="amber"
                              label={`🪙 ${booster.price_gal} FRJ`}
                              sublabel="Mantén para confirmar"
                              className="flex-1"
                              onConfirm={() => {
                                setSobresDrawerAbierto(false);
                                comprarItem(booster.id, 'frijolito');
                              }}
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </BottomSheet>

      {/* === BOTTOM SHEET: WEBITOS === */}
      <BottomSheet open={webitosDrawerAbierto} onClose={() => setWebitosDrawerAbierto(false)} accent="#E4007C">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl sm:text-2xl font-black text-[#E4007C] tracking-tight uppercase flex items-center gap-2">
              <span>🥚</span> Adopta tu Webito
            </h3>
            <button
              onClick={() => setWebitosDrawerAbierto(false)}
              className="text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 cursor-pointer"
            >
              <X size={20} />
            </button>
          </div>

          <div className="flex flex-col gap-4">
            {sinNidosGlobal && (
              <div className="rounded-3xl bg-gradient-to-b from-red-950/50 via-slate-950 to-slate-950 border border-red-500/30 p-6 text-center shadow-[0_0_30px_rgba(239,68,68,0.07)]">
                <div className="w-20 h-20 mx-auto mb-4 rounded-3xl bg-gradient-to-br from-red-900/50 to-slate-900 border border-red-500/25 flex items-center justify-center text-5xl">
                  🔒
                </div>
                <h4 className="text-white font-black text-lg uppercase tracking-tight mb-2">
                  Sin nidos disponibles
                </h4>
                <p className="text-sm text-slate-400 leading-relaxed mb-2 max-w-sm mx-auto">
                  Tu cenote tiene{' '}
                  <span className="text-white font-bold">
                    {ocupadosTotal} / {maxNidos ?? 1}
                  </span>{' '}
                  espacios ocupados
                  {(totalAxolotitosHatched ?? 0) > 0 && (
                    <span className="text-slate-500">
                      {' '}({totalAxolotitosHatched} dormitorio{(totalAxolotitosHatched ?? 0) !== 1 ? 's' : ''} + {totalEggsInInventory ?? 0} nido{(totalEggsInInventory ?? 0) !== 1 ? 's' : ''})
                    </span>
                  )}
                  . Eclosiona un webito o expande tu Cenote para liberar espacio.
                </p>
                <p className="text-[10px] text-red-400/70 mb-4 font-semibold uppercase tracking-wide animate-pulse">
                  No puedes adoptar más webitos hasta liberar un nido
                </p>

                {/* Bloque de compra: expandir Cenote */}
                {nextCaveLevel && (
                  <div className="w-full bg-emerald-950/30 border border-emerald-500/25 rounded-2xl p-4 mb-4 text-left">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-base">🏔️</span>
                      <span className="text-xs font-black text-emerald-400 uppercase tracking-wide">
                        Expande tu Cenote
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                      Desbloquea{' '}
                      <span className="text-white font-bold">{nextCaveLevel.name}</span>{' '}
                      y obtén{' '}
                      <span className="text-emerald-300 font-bold">{nextCaveLevel.spots} nidos</span>.
                    </p>
                    {nextCaveLevel.paths?.find((p: any) => p.type === 'pago') ? (
                      <div className="flex items-center justify-between">
                        <span className="text-yellow-400 font-black text-sm">
                          💎 {nextCaveLevel.paths.find((p: any) => p.type === 'pago').cost_axg} AXF
                        </span>
                        <button
                          onClick={() => {
                            setWebitosDrawerAbierto(false);
                            cambiarTab('santuario');
                          }}
                          className="py-2 px-4 bg-gradient-to-r from-emerald-700 to-teal-700 hover:from-emerald-600 hover:to-teal-600 text-white font-black text-[10px] uppercase tracking-wider rounded-xl transition-all shadow-md shadow-emerald-900/30 active:scale-[0.98]"
                        >
                          Comprar nido
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setWebitosDrawerAbierto(false);
                          cambiarTab('santuario');
                        }}
                        className="w-full py-2.5 bg-gradient-to-r from-emerald-700 to-teal-700 hover:from-emerald-600 hover:to-teal-600 text-white font-black text-[10px] uppercase tracking-wider rounded-xl transition-all shadow-md shadow-emerald-900/30 active:scale-[0.98]"
                      >
                        Ver cómo desbloquear
                      </button>
                    )}
                  </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => {
                      setWebitosDrawerAbierto(false);
                      cambiarTab('santuario');
                    }}
                    className="flex-1 py-3.5 bg-gradient-to-r from-emerald-700 to-teal-700 hover:from-emerald-600 hover:to-teal-600 text-white font-black text-xs uppercase tracking-wider rounded-2xl transition-all shadow-lg shadow-emerald-900/30 active:scale-[0.98]"
                  >
                    🥚 Ir al Nido
                  </button>
                  <button
                    onClick={() => setWebitosDrawerAbierto(false)}
                    className="flex-1 py-3.5 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 text-slate-300 font-black text-xs uppercase tracking-wider rounded-2xl transition-all active:scale-[0.98]"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            )}
            {items
              .filter((i) => i.item_type?.toLowerCase() === 'egg')
              .map((egg) => {
                const adoptados = egg.total_sold || 0;
                const limiteUsuario = egg.user_owned || 0;
                const maxSupply = egg.max_supply ?? 0;
                const porcentaje = maxSupply > 0 ? (adoptados / maxSupply) * 100 : 0;
                const limiteAlcanzado = limiteUsuario >= 7;
                const isAstral = egg.item_metadata?.is_astral;
                const totalNidosMax = maxNidos ?? 1;
                const totalHuevos = totalEggsInInventory ?? 0;
                const ocupadosCard = totalHuevos + (totalAxolotitosHatched ?? 0);
                const sinNidos = ocupadosCard >= totalNidosMax;

                const cardBg = isAstral
                  ? 'bg-gradient-to-b from-indigo-950/60 via-slate-950 to-slate-950 border-2 border-amber-400/80 shadow-[0_0_30px_rgba(245,158,11,0.25)]'
                  : 'bg-slate-950/80 border border-[#E4007C]/40';

                const headerGrad = isAstral
                  ? 'bg-gradient-to-b from-amber-400/20 to-transparent'
                  : 'bg-gradient-to-b from-[#E4007C]/10 to-transparent';

                const iconBg = isAstral
                  ? 'bg-gradient-to-br from-amber-400 via-fuchsia-500 to-indigo-600 shadow-amber-500/40 border border-amber-300/30'
                  : 'bg-gradient-to-br from-[#E4007C] to-purple-800 shadow-[#E4007C]/25';

                const nameColor = isAstral
                  ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-fuchsia-300 to-cyan-200 font-extrabold'
                  : 'text-white font-extrabold';

                const progressBg = isAstral
                  ? 'bg-gradient-to-r from-amber-400 via-fuchsia-500 to-indigo-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]'
                  : 'bg-[#E4007C] shadow-[0_0_10px_rgba(228,0,124,0.8)]';

                const limitColor = isAstral ? 'text-amber-400' : 'text-[#FF8DA1]';

                return (
                  <div
                    key={egg.id}
                    className={`p-5 rounded-3xl relative overflow-hidden group flex flex-col items-center text-center animate-in fade-in ${cardBg}`}
                  >
                    <div
                      className={`absolute inset-x-0 top-0 h-24 pointer-events-none ${headerGrad}`}
                    ></div>

                    {isAstral && (
                      <div className="absolute top-3 left-3 bg-amber-400 text-slate-950 font-black text-[9px] px-2 py-0.5 rounded-full tracking-widest uppercase shadow-md border border-amber-200 z-10">
                        ★ Astral ★
                      </div>
                    )}

                    <div
                      className={`w-24 h-24 rounded-3xl flex items-center justify-center text-5xl shadow-lg mb-4 group-hover:scale-105 transition-transform animate-pulse relative ${iconBg}`}
                    >
                      {isAstral && (
                        <>
                          <span className="absolute top-1 right-1 text-sm select-none z-10 filter drop-shadow-[0_2px_4px_rgba(0,0,0,0.5)] animate-bounce">
                            👑
                          </span>
                          <span
                            className="absolute text-amber-200 animate-spin"
                            style={{ top: '8%', left: '8%', fontSize: 14 }}
                          >
                            ✦
                          </span>
                          <span className="absolute bottom-1 bg-amber-400 text-slate-950 text-[8px] font-black px-1.5 py-0.5 rounded-full tracking-widest uppercase shadow-md border border-amber-200">
                            VIP
                          </span>
                        </>
                      )}
                      🥚
                    </div>

                    <h4 className={`text-lg mb-1 ${nameColor}`}>{egg.name}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed mb-4 max-w-xs">
                      {egg.description}
                    </p>

                    <div className="w-full mb-5 max-w-xs bg-slate-900/60 p-3 rounded-2xl border border-slate-800/85">
                      <div className="flex justify-between text-[10px] mb-1.5 text-slate-300 font-bold">
                        <span>
                          Adoptados:{' '}
                          <span className="text-white">
                            {adoptados} / {maxSupply}
                          </span>
                        </span>
                        <span className={limitColor}>Límite: {limiteUsuario}/7</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${progressBg}`}
                          style={{ width: `${porcentaje}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-[10px] mt-2.5 text-slate-300 font-bold border-t border-slate-800/50 pt-2">
                        <span>
                          Cenote:{' '}
                          <span className="text-white">
                            {ocupadosCard} / {totalNidosMax}
                          </span>
                          {(totalAxolotitosHatched ?? 0) > 0 && (
                            <span className="text-slate-500 font-normal ml-1">
                              ({totalAxolotitosHatched} dorm.)
                            </span>
                          )}
                        </span>
                        {sinNidos ? (
                          <span className="text-red-400 font-black uppercase tracking-wider animate-pulse text-[9px]">
                            ⚠️ Lleno
                          </span>
                        ) : (
                          <span className="text-emerald-400 font-bold">
                            ✓ Nido libre
                          </span>
                        )}
                      </div>
                    </div>

                    {limiteAlcanzado ? (
                      <button
                        disabled
                        className="w-full max-w-xs py-3.5 text-white font-black rounded-xl uppercase tracking-widest text-xs bg-slate-850 border border-slate-800 text-slate-500 cursor-not-allowed shadow-none"
                      >
                        Límite alcanzado (Máx 7)
                      </button>
                    ) : sinNidos ? (
                      <button
                        disabled
                        className="w-full max-w-xs py-3.5 text-red-400/80 font-black rounded-xl uppercase tracking-widest text-xs bg-red-950/20 border border-red-900/30 cursor-not-allowed shadow-[0_0_15px_rgba(239,68,68,0.05)]"
                      >
                        Sin nidos libres
                      </button>
                    ) : (
                      <HoldButton
                        variant={isAstral ? 'amber' : 'primary'}
                        label={`Adoptar por ${egg.price_axg} AXF`}
                        sublabel="Mantén para confirmar"
                        className="w-full max-w-xs"
                        onConfirm={() => {
                          setWebitosDrawerAbierto(false);
                          comprarItem(egg.id, 'axoficha');
                        }}
                      />
                    )}
                  </div>
                );
              })}
          </div>
        </div>
      </BottomSheet>

      {/* CryptoCheckout */}
      {cryptoCheckoutOpen && (
        <CryptoCheckout
          userId={userId}
          token={token}
          onClose={() => setCryptoCheckoutOpen(false)}
          onSuccess={() => {
            recargarSaldos();
            setCryptoCheckoutOpen(false);
          }}
        />
      )}
    </div>
  );
}
