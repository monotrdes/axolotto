"use client";
import React, { useEffect, useState, useCallback, useRef } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import HoldButton from "@/components/ui/HoldButton";
import * as storeService from "@/services/storeService";
import type { StoreItem } from "@/types/store";
import { useToast } from "@/context/ToastContext";

interface Props {
  open: boolean;
  onClose: () => void;
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
}

const GREETINGS = [
  "¡Órale marchante! ¿Qué sobre te llevas hoy?",
  "¡Pásale, pásale! Cartas fresquecitas recién llegadas.",
  "¡Bienvenido! Tengo los mejores sobres del tianguis.",
  "¡Buenas! Echa un ojo a nuestros sobrecitos ✨",
  "¿Buscas cartas raras? ¡Hoy es tu día de suerte!",
];

function packTheme(theme: string) {
  switch (theme) {
    case "fiesta":
      return {
        border: "border-[#E4007C]/50",
        glow: "shadow-[0_0_20px_rgba(228,0,124,0.15)]",
        headerGrad: "from-[#E4007C]/15 via-purple-950/10 to-transparent",
        accent: "text-[#E4007C]",
        iconGrad: "from-[#E4007C] to-purple-900",
        badge: "bg-gradient-to-r from-pink-500 to-[#E4007C] text-white",
        badgeText: "FIESTA",
        bar: "bg-gradient-to-r from-pink-500 to-[#E4007C]",
      };
    case "nido":
      return {
        border: "border-emerald-500/50",
        glow: "shadow-[0_0_20px_rgba(16,185,129,0.12)]",
        headerGrad: "from-emerald-600/15 via-teal-950/10 to-transparent",
        accent: "text-emerald-400",
        iconGrad: "from-emerald-600 to-teal-900",
        badge: "bg-gradient-to-r from-emerald-500 to-teal-500 text-white",
        badgeText: "NIDO",
        bar: "bg-gradient-to-r from-emerald-500 to-teal-400",
      };
    case "cosmos":
      return {
        border: "border-indigo-500/50",
        glow: "shadow-[0_0_20px_rgba(99,102,241,0.12)]",
        headerGrad: "from-indigo-900/20 via-purple-950/10 to-transparent",
        accent: "text-indigo-400",
        iconGrad: "from-indigo-900 to-purple-950",
        badge: "bg-gradient-to-r from-indigo-500 to-purple-500 text-white",
        badgeText: "COSMOS",
        bar: "bg-gradient-to-r from-indigo-500 to-purple-500",
      };
    case "foil":
      return {
        border: "border-amber-400/60",
        glow: "shadow-[0_0_25px_rgba(245,158,11,0.2)]",
        headerGrad: "from-amber-400/15 via-fuchsia-950/10 to-transparent",
        accent: "text-amber-400",
        iconGrad: "from-amber-400 via-fuchsia-500 to-purple-700",
        badge: "bg-amber-400 text-slate-950",
        badgeText: "✨ FOIL",
        bar: "bg-gradient-to-r from-amber-400 via-fuchsia-500 to-purple-500",
      };
    default:
      return {
        border: "border-purple-500/40",
        glow: "shadow-[0_0_18px_rgba(168,85,247,0.10)]",
        headerGrad: "from-purple-900/15 via-indigo-950/10 to-transparent",
        accent: "text-purple-400",
        iconGrad: "from-purple-900 to-slate-900",
        badge: "bg-gradient-to-r from-purple-500 to-indigo-600 text-white",
        badgeText: "BÁSICO",
        bar: "bg-purple-500",
      };
  }
}

export default function SobrecitosStallPanel({ open, onClose, userId, token, recargarSaldos }: Props) {
  const { toast } = useToast();
  const [items, setItems] = useState<StoreItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [buying, setBuying] = useState<number | null>(null);
  const [greeting] = useState(() => GREETINGS[Math.floor(Math.random() * GREETINGS.length)]);
  const [greetingVisible, setGreetingVisible] = useState(false);
  const [mounted, setMounted] = useState(false);
  // Phantom-click guard: el pointerup que abre el panel genera un click sintético
  // que llegaría al backdrop antes de que el usuario pudiera verlo. Lo ignoramos
  // durante los primeros 350ms tras abrir.
  const backdropReadyRef = useRef(false);
  const backdropTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    if (backdropTimerRef.current) clearTimeout(backdropTimerRef.current);
    if (open) {
      backdropReadyRef.current = false;
      backdropTimerRef.current = setTimeout(() => {
        backdropReadyRef.current = true;
      }, 350);
    } else {
      backdropReadyRef.current = false;
    }
    return () => {
      if (backdropTimerRef.current) clearTimeout(backdropTimerRef.current);
    };
  }, [open]);

  useEffect(() => {
    if (!open || !userId) return;
    setLoading(true);
    setGreetingVisible(false);
    storeService
      .fetchShopItems(userId)
      .then((data: StoreItem[]) => {
        setItems(data.filter((i: StoreItem) => i.item_type?.toLowerCase() === "booster"));
        setTimeout(() => setGreetingVisible(true), 350);
      })
      .catch(() => toast.error("Error cargando la tienda"))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, userId]);

  const comprar = useCallback(
    async (itemId: number, moneda: string) => {
      if (buying !== null) return;
      setBuying(itemId);
      try {
        await storeService.buyItem(userId, itemId, moneda, token);
        toast.ok("¡Sobrecito comprado! Revisa tu mochila 📦");
        recargarSaldos();
        const data = await storeService.fetchShopItems(userId);
        setItems(data.filter((i: StoreItem) => i.item_type?.toLowerCase() === "booster"));
      } catch (e: any) {
        toast.error(e?.response?.data?.detail || "Error al comprar");
      } finally {
        setBuying(null);
      }
    },
    [buying, userId, token, recargarSaldos, toast],
  );

  if (!mounted) return null;

  const content = (
    <div
      className={`fixed inset-0 z-[200] flex flex-col justify-end transition-opacity duration-300 ${
        open ? "opacity-100" : "opacity-0 pointer-events-none"
      }`}
    >
      {/* Dim overlay — phantom-click guard: ignora el primer click hasta 350ms */}
      <div
        className="absolute inset-0 bg-black/55 backdrop-blur-[3px]"
        onClick={() => { if (backdropReadyRef.current) onClose(); }}
      />

      {/* Bottom sheet */}
      <div
        className={`relative z-10 bg-gradient-to-b from-[#10101f] via-[#0a0a18] to-[#060610] rounded-t-[2rem] flex flex-col border-t border-l border-r border-purple-500/20 shadow-[0_-8px_60px_rgba(100,0,255,0.22)] transition-transform duration-500 ease-out max-h-[88vh] ${
          open ? "translate-y-0" : "translate-y-full"
        }`}
      >
        {/* Drag handle */}
        <div className="flex justify-center pt-3 pb-1 shrink-0">
          <div className="w-10 h-1 rounded-full bg-white/15" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-1 pb-3 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-gradient-to-br from-purple-500 to-indigo-700 rounded-[14px] flex items-center justify-center text-2xl shadow-lg shadow-purple-500/25">
              📦
            </div>
            <div>
              <h2 className="text-[15px] font-black text-white uppercase tracking-tight leading-none">
                Venta de Sobrecitos
              </h2>
              <p className="text-[10px] text-slate-500 font-medium mt-0.5">El Tianguis · Puesto de Cartas</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-90"
            aria-label="Cerrar"
          >
            <X size={15} />
          </button>
        </div>

        {/* Greeting bubble */}
        <div
          className={`mx-5 mb-4 bg-gradient-to-r from-purple-950/70 to-indigo-950/60 border border-purple-500/25 rounded-2xl p-3.5 flex items-start gap-3 shrink-0 transition-all duration-500 ${
            greetingVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
          }`}
        >
          <div className="w-9 h-9 shrink-0 bg-gradient-to-br from-purple-700 to-indigo-900 rounded-xl flex items-center justify-center text-xl border border-purple-400/20 shadow-md">
            🦎
          </div>
          <div>
            <p className="text-[9px] text-purple-400 font-black uppercase tracking-widest mb-0.5">
              Marchanta del Tianguis
            </p>
            <p className="text-[13px] text-slate-200 leading-snug">{greeting}</p>
          </div>
        </div>

        {/* Scrollable items */}
        <div className="overflow-y-auto flex-1 px-5 pb-10 space-y-3 overscroll-contain">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-3xl animate-pulse">
                📦
              </div>
              <p className="text-slate-500 text-sm">Cargando sobrecitos...</p>
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-16 text-slate-500 text-sm">
              Sin sobrecitos disponibles por ahora.
            </div>
          ) : (
            items.map((booster) => {
              const vendidos = booster.total_sold || 0;
              const maxSupply = booster.max_supply ?? 0;
              const restantes = Math.max(0, maxSupply - vendidos);
              const porcentaje = maxSupply > 0 ? (restantes / maxSupply) * 100 : 100;
              const theme = (booster.item_metadata?.pack_theme as string) || "pure";
              const isFoil = theme === "foil";
              const t = packTheme(theme);
              const isBuying = buying === booster.id;
              const agotado = restantes <= 0;

              return (
                <div
                  key={booster.id}
                  className={`rounded-2xl overflow-hidden border transition-all duration-200 ${t.border} ${t.glow} ${
                    isFoil ? "border-2" : ""
                  } ${agotado ? "opacity-50" : ""}`}
                >
                  {/* Card top: icon + name + description */}
                  <div className={`bg-gradient-to-r ${t.headerGrad} px-4 pt-4 pb-3 flex items-start gap-3`}>
                    {/* Icon */}
                    <div
                      className={`w-[60px] h-[60px] shrink-0 bg-gradient-to-br ${t.iconGrad} rounded-xl flex items-center justify-center text-[2rem] shadow-md relative overflow-hidden`}
                    >
                      {isFoil && (
                        <>
                          <span className="absolute top-0.5 right-0.5 text-[9px] animate-bounce select-none">✨</span>
                          <span className="absolute bottom-0 left-0 right-0 bg-amber-400 text-slate-950 text-[7px] font-black text-center py-[2px]">
                            FOIL
                          </span>
                        </>
                      )}
                      📦
                    </div>

                    {/* Name + desc */}
                    <div className="flex-1 min-w-0 pt-0.5">
                      <div className="flex items-center gap-1.5 flex-wrap mb-1">
                        <span
                          className={`font-black text-[15px] leading-tight ${
                            isFoil
                              ? "text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-fuchsia-300 to-purple-200"
                              : "text-white"
                          }`}
                        >
                          {booster.name}
                        </span>
                        <span className={`${t.badge} text-[8px] font-black px-2 py-[2px] rounded-full uppercase tracking-wider`}>
                          {t.badgeText}
                        </span>
                        {isFoil && (
                          <span className="bg-amber-400/20 border border-amber-400/40 text-amber-300 text-[7px] font-black px-1.5 py-[2px] rounded-full uppercase tracking-wider animate-pulse">
                            100/mes
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">
                        {booster.description}
                      </p>
                    </div>
                  </div>

                  {/* Stock bar */}
                  <div className="px-4 pb-2">
                    <div className="flex items-center justify-between text-[9px] text-slate-500 mb-1.5 font-semibold">
                      <span>
                        Quedan{" "}
                        <span className={`font-black ${t.accent}`}>{restantes}</span>{" "}
                        de {maxSupply}
                      </span>
                      {agotado && (
                        <span className="text-red-400 font-black uppercase tracking-wider">AGOTADO</span>
                      )}
                    </div>
                    <div className="h-[3px] bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${t.bar}`}
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                  </div>

                  {/* Buy buttons */}
                  <div className="px-4 pb-4 pt-1 flex gap-2">
                    <HoldButton
                      variant="primary"
                      label={agotado ? "Agotado" : `💎 ${booster.price_axg} AXF`}
                      sublabel={agotado ? "" : isBuying ? "Procesando..." : "Mantén para confirmar"}
                      className="flex-1"
                      disabled={isBuying || agotado}
                      onConfirm={() => comprar(booster.id, "axoficha")}
                    />
                    {booster.price_gal != null && booster.price_gal > 0 && (
                      <HoldButton
                        variant="amber"
                        label={agotado ? "Agotado" : `🪙 ${booster.price_gal} FRJ`}
                        sublabel={agotado ? "" : isBuying ? "Procesando..." : "Mantén para confirmar"}
                        className="flex-1"
                        disabled={isBuying || agotado}
                        onConfirm={() => comprar(booster.id, "frijolito")}
                      />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}
