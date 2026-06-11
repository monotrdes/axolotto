"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { usePrivy, useWallets } from '@privy-io/react-auth';
import { encodeFunctionData, parseUnits } from 'viem';
import axios from 'axios';
import { X, Copy, Check, ExternalLink, ChevronLeft, HelpCircle, ChevronDown, ChevronUp, CreditCard } from 'lucide-react';
import { useMoonPayWidget } from '@/hooks/useMoonPayWidget';
import BottomSheet from '@/components/ui/BottomSheet';
import HoldButton from '@/components/ui/HoldButton';

const API = `${API_BASE}`;

// ERC-20 transfer(address,uint256) ABI
const ERC20_TRANSFER_ABI = [{
  name: 'transfer',
  type: 'function' as const,
  stateMutability: 'nonpayable' as const,
  inputs: [{ name: 'to', type: 'address' }, { name: 'amount', type: 'uint256' }],
  outputs: [{ name: '', type: 'bool' }],
}];

// USDC contract address on Polygon Amoy (set via env, fallback empty)
const USDC_ADDRESS = (process.env.NEXT_PUBLIC_USDC_ADDRESS ?? '') as `0x${string}`;

interface Pack {
  id: string; label: string; emoji: string;
  usd: number; mxn: number;
  axf_base: number; axf_total: number;
  bonus_pct: number; badge: string | null;
  is_flash: boolean;
}

interface Order {
  order_id: string; pay_to: string;
  usdc_amount: number; axg_amount: number;
  bonus_pct: number; bonus_applied: string | null;
  expires_at: string; status: string;
  tx_hash_payment?: string | null;
}

type Screen = 'packs' | 'method' | 'paying' | 'confirming' | 'success';

interface CryptoCheckoutProps {
  userId: string;
  token: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

// ── Countdown hook ─────────────────────────────────────────────────────────────
function useCountdown(expiresAt: string | null): string {
  const [text, setText] = useState('');
  useEffect(() => {
    if (!expiresAt) { setText(''); return; }
    const tick = () => {
      const diff = new Date(expiresAt).getTime() - Date.now();
      if (diff <= 0) { setText('Expirada'); return; }
      const m = Math.floor(diff / 60_000);
      const s = Math.floor((diff % 60_000) / 1000);
      setText(`${m}:${s.toString().padStart(2, '0')}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);
  return text;
}

// ── Copy button ────────────────────────────────────────────────────────────────
function CopyButton({ text, label }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button
      onClick={copy}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-white/10 text-[10px] font-black uppercase tracking-wide transition-all active:scale-95 text-slate-300 hover:text-white shrink-0"
    >
      {copied ? <Check size={12} className="text-teal-400" /> : <Copy size={12} />}
      {copied ? '¡Copiado!' : (label ?? 'Copiar')}
    </button>
  );
}

// ── Pack card ──────────────────────────────────────────────────────────────────
function PackCard({ pack, selected, onClick }: { pack: Pack; selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`relative flex flex-col items-center gap-1.5 p-3 rounded-2xl border-2 transition-all active:scale-95 text-left w-full ${
        selected
          ? 'border-purple-500 bg-purple-950/40 shadow-[0_0_18px_rgba(168,85,247,0.25)]'
          : 'border-white/8 bg-slate-900/40 hover:border-white/20'
      } ${pack.is_flash ? 'ring-1 ring-yellow-500/50' : ''}`}
    >
      {pack.is_flash && (
        <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-yellow-500 text-slate-950 text-[7px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest whitespace-nowrap animate-pulse">
          ⚡ OFERTA FLASH
        </span>
      )}
      {pack.badge && !pack.is_flash && (
        <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-[#E4007C] text-white text-[7px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest whitespace-nowrap">
          {pack.badge}
        </span>
      )}
      <span className="text-2xl leading-none mt-1">{pack.emoji}</span>
      <span className="text-[10px] font-black text-white uppercase tracking-wide">{pack.label}</span>
      <span className="text-sm font-black text-purple-300">{pack.axf_total.toLocaleString()} AXF</span>
      {pack.bonus_pct > 0 && (
        <span className="text-[8px] text-teal-400 font-bold">+{pack.bonus_pct}% bonus</span>
      )}
      <span className="mt-1 w-full text-center bg-black/40 rounded-xl py-1 text-[10px] font-black text-yellow-400">
        ${pack.usd} USD · ~${pack.mxn.toFixed(0)} MXN
      </span>
    </button>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function CryptoCheckout({ userId, token, onClose, onSuccess }: CryptoCheckoutProps) {
  const { user } = usePrivy();
  const { wallets } = useWallets();
  const { openWidget: openMoonPay, isConfigured: moonPayReady } = useMoonPayWidget();

  const [screen, setScreen]           = useState<Screen>('packs');
  const [packs, setPacks]             = useState<Pack[]>([]);
  const [selectedPack, setSelected]   = useState<Pack | null>(null);
  const [order, setOrder]             = useState<Order | null>(null);
  const [error, setError]             = useState<string | null>(null);
  const [loading, setLoading]         = useState(false);
  const [manualHash, setManualHash]     = useState('');
  const [completedAxg, setCompleted]    = useState(0);
  const [newBalance, setNewBalance]     = useState<number | null>(null);
  const [binanceHelpOpen, setBinanceHelpOpen] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const countdown = useCountdown(order?.expires_at ?? null);

  // Load packs
  useEffect(() => {
    axios.get(`${API}/bank/checkout/packs`)
      .then(r => setPacks(r.data.packs || []))
      .catch(() => setError('No se pudieron cargar los packs.'));
  }, []);

  // Poll order status when confirming
  const startPolling = useCallback((orderId: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const r = await axios.get(`${API}/bank/checkout/crypto/${orderId}`, { headers });
        if (r.data.status === 'completed') {
          clearInterval(pollRef.current!);
          setCompleted(r.data.axg_amount);
          setScreen('success');
          onSuccess();
        } else if (r.data.status === 'failed') {
          clearInterval(pollRef.current!);
          setError('El pago no pudo verificarse. Revisa el monto y la dirección enviada.');
          setScreen('paying');
        }
      } catch { /* ignorar errores de red durante polling */ }
    }, 4000);
  }, [token]);

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  const handleCreateOrder = async () => {
    if (!selectedPack) return;
    setLoading(true); setError(null);
    try {
      const r = await axios.post(`${API}/bank/checkout/crypto`, { pack_id: selectedPack.id }, { headers });
      setOrder(r.data);
      setScreen('paying');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al crear la orden.');
    } finally { setLoading(false); }
  };

  const handleConfirm = async (txHash: string) => {
    if (!order || !txHash.trim()) return;
    setLoading(true); setError(null);
    try {
      await axios.post(`${API}/bank/checkout/crypto/${order.order_id}/confirm`, { tx_hash: txHash.trim() }, { headers });
      setScreen('confirming');
      startPolling(order.order_id);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al confirmar el pago.');
    } finally { setLoading(false); }
  };

  const handlePrivyPay = async () => {
    if (!order) return;
    setError(null);
    try {
      if (!USDC_ADDRESS) {
        throw new Error('La dirección del contrato USDC no está configurada (NEXT_PUBLIC_USDC_ADDRESS).');
      }
      const embeddedWallet = wallets.find(w => w.walletClientType === 'privy');
      if (!embeddedWallet) throw new Error('No se encontró tu wallet de Privy.');

      const provider = await embeddedWallet.getEthereumProvider();
      const from = embeddedWallet.address;

      // Encode ERC-20 transfer(to, amount) — USDC tiene 6 decimales
      const data = encodeFunctionData({
        abi: ERC20_TRANSFER_ABI,
        functionName: 'transfer',
        args: [order.pay_to as `0x${string}`, parseUnits(order.usdc_amount.toFixed(6), 6)],
      });

      const txHash = await provider.request({
        method: 'eth_sendTransaction',
        params: [{ from, to: USDC_ADDRESS, data, value: '0x0' }],
      });

      if (txHash) await handleConfirm(txHash as string);
    } catch (e: any) {
      const msg = e?.message || 'Error al enviar desde tu wallet.';
      if (!msg.toLowerCase().includes('reject') && !msg.toLowerCase().includes('cancel')) {
        setError(msg);
      }
    }
  };

  // ── Screens ────────────────────────────────────────────────────────────────

  const renderPacks = () => (
    <div className="flex flex-col gap-4">
      <div className="text-center">
        <h2 className="text-xl font-black text-white uppercase tracking-tight">💎 Recargar AXF</h2>
        <p className="text-[10px] text-slate-500 mt-0.5">Paga con USDC · Recibe Axofichas al instante</p>
      </div>

      {packs.length === 0 ? (
        <div className="text-center text-slate-600 text-sm py-8">Cargando packs…</div>
      ) : (
        <div className="grid grid-cols-2 gap-3 mt-1">
          {packs.map(p => (
            <PackCard key={p.id} pack={p} selected={selectedPack?.id === p.id} onClick={() => setSelected(p)} />
          ))}
        </div>
      )}

      {/* Primera compra bonus notice */}
      {user && (
        <div className="bg-teal-950/30 border border-teal-500/20 rounded-2xl px-4 py-2.5 flex items-center gap-2.5">
          <span className="text-lg">🎁</span>
          <div>
            <div className="text-[10px] font-black text-teal-400 uppercase tracking-wide">+10% en tu primera compra</div>
            <div className="text-[9px] text-slate-500">Se aplica automáticamente si es tu primer recarga</div>
          </div>
        </div>
      )}

      <button
        onClick={() => setScreen('method')}
        disabled={!selectedPack}
        className="w-full py-3.5 rounded-2xl font-black uppercase tracking-widest text-sm transition-all active:scale-95 disabled:opacity-30"
        style={{
          background: selectedPack ? 'linear-gradient(135deg, #7C3AED, #E4007C)' : 'rgba(30,30,50,0.6)',
          color: selectedPack ? 'white' : '#475569',
          boxShadow: selectedPack ? '0 0 24px rgba(168,85,247,0.3)' : undefined,
        }}
      >
        Continuar →
      </button>
    </div>
  );

  const renderMethod = () => (
    <div className="flex flex-col gap-4">
      <button onClick={() => setScreen('packs')} className="flex items-center gap-1 text-slate-500 hover:text-slate-300 text-[11px] font-bold self-start">
        <ChevronLeft size={14} /> Volver
      </button>
      <div className="text-center">
        <h2 className="text-lg font-black text-white uppercase tracking-tight">Método de pago</h2>
        <p className="text-[10px] text-slate-500 mt-0.5">
          {selectedPack?.emoji} {selectedPack?.label} · {selectedPack?.axf_total?.toLocaleString()} AXF
        </p>
      </div>

      <div className="bg-slate-900/50 border-2 border-purple-500/50 rounded-2xl p-4 flex items-center gap-3">
        <span className="text-2xl">🪙</span>
        <div className="flex-1">
          <div className="text-[11px] font-black text-white uppercase">USDC en Polygon</div>
          <div className="text-[9px] text-slate-500">Rápido · Sin gas para el usuario</div>
        </div>
        <div className="w-5 h-5 rounded-full border-2 border-purple-500 bg-purple-500 flex items-center justify-center">
          <div className="w-2 h-2 rounded-full bg-white" />
        </div>
      </div>

      <div className="bg-slate-900/30 border border-white/5 rounded-2xl p-4 space-y-2">
        <div className="flex justify-between text-[11px]">
          <span className="text-slate-400">Pack</span>
          <span className="font-bold text-white">{selectedPack?.label}</span>
        </div>
        <div className="flex justify-between text-[11px]">
          <span className="text-slate-400">AXF a recibir</span>
          <span className="font-black text-purple-300">{selectedPack?.axf_total?.toLocaleString()} AXF</span>
        </div>
        {(selectedPack?.bonus_pct ?? 0) > 0 && (
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Bonus incluido</span>
            <span className="font-bold text-teal-400">+{selectedPack?.bonus_pct}%</span>
          </div>
        )}
        <div className="border-t border-white/5 pt-2 flex justify-between text-[12px]">
          <span className="text-slate-300 font-bold">Total a pagar</span>
          <span className="font-black text-yellow-400">${selectedPack?.usd} USD</span>
        </div>
      </div>

      {/* MoonPay — cargar wallet con tarjeta/SPEI antes de pagar */}
      {moonPayReady && (
        <>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-white/8" />
            <span className="text-[9px] text-slate-600 uppercase font-bold tracking-widest">¿no tienes USDC?</span>
            <div className="flex-1 h-px bg-white/8" />
          </div>
          <button
            onClick={() => openMoonPay({ amountUsd: selectedPack?.usd })}
            className="w-full py-3 rounded-2xl border border-blue-500/30 bg-blue-950/20 flex items-center gap-3 px-4 transition-all hover:bg-blue-950/40 active:scale-95"
          >
            <CreditCard size={16} className="text-blue-400 shrink-0" />
            <div className="text-left flex-1">
              <div className="text-[11px] font-black text-blue-300 uppercase tracking-wide">Comprar con tarjeta / SPEI</div>
              <div className="text-[9px] text-slate-500">MoonPay deposita USDC en tu wallet · Luego vuelve aquí</div>
            </div>
            <span className="text-blue-400 text-xs shrink-0">→</span>
          </button>
        </>
      )}

      <HoldButton
        onConfirm={handleCreateOrder}
        disabled={loading}
        duration={1000}
        variant="primary"
        className="w-full"
        style={{
          width: '100%',
          background: 'linear-gradient(135deg, #7C3AED, #E4007C)',
          color: 'white',
          boxShadow: '0 0 24px rgba(168,85,247,0.3)',
          borderRadius: '1rem',
          padding: '14px',
          fontSize: '14px',
          letterSpacing: '0.1em',
          fontWeight: '900',
          textTransform: 'uppercase',
        }}
        label={loading ? '⏳ Creando orden…' : 'Ya tengo USDC → Pagar →'}
      />
    </div>
  );

  const renderBinanceHelp = () => {
    const embeddedWallet = wallets.find(w => w.walletClientType === 'privy');
    const privyAddr = embeddedWallet?.address ?? '(tu wallet de Privy)';
    const steps = [
      { icon: '1️⃣', text: 'Abre Binance → toca "Portafolio" → "Retirar"' },
      { icon: '2️⃣', text: 'Selecciona la moneda: USDC o USDT' },
      { icon: '3️⃣', text: <>Elige la red: <strong className="text-yellow-400">Polygon</strong> — comisión ≈ $0.01 USD</> },
      { icon: '4️⃣', text: <span>Pega tu dirección de Privy como destino:<br /><span className="font-mono text-teal-400 text-[9px] break-all">{privyAddr}</span></span> },
      { icon: '5️⃣', text: 'Ingresa el monto y confirma el retiro (puede pedir 2FA)' },
      { icon: '6️⃣', text: 'Espera la confirmación (1–2 min) y vuelve aquí' },
      { icon: '7️⃣', text: <>Haz clic en <strong className="text-purple-300">Pagar con mi wallet (Privy)</strong> — listo 🎉</> },
    ];
    return (
      <div className="mt-1 bg-slate-900/70 border border-white/8 rounded-2xl overflow-hidden">
        <button
          onClick={() => setBinanceHelpOpen(v => !v)}
          className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/3 transition-colors"
        >
          <div className="flex items-center gap-2">
            <HelpCircle size={13} className="text-yellow-400 shrink-0" />
            <span className="text-[10px] font-black text-yellow-400 uppercase tracking-wide">¿Cómo pago desde Binance?</span>
          </div>
          {binanceHelpOpen ? <ChevronUp size={13} className="text-slate-500" /> : <ChevronDown size={13} className="text-slate-500" />}
        </button>

        {binanceHelpOpen && (
          <div className="px-4 pb-4 space-y-3 border-t border-white/6 pt-3">
            <p className="text-[9px] text-slate-500 leading-relaxed">
              Binance soporta retiros USDC/USDT a la red <strong className="text-yellow-400">Polygon</strong> con comisiones bajísimas.
              Primero carga tu wallet de Privy, luego paga con un clic.
            </p>
            <ol className="space-y-2.5">
              {steps.map((s, i) => (
                <li key={i} className="flex gap-2.5 items-start">
                  <span className="text-sm leading-none shrink-0 mt-0.5">{s.icon}</span>
                  <span className="text-[10px] text-slate-300 leading-relaxed">{s.text}</span>
                </li>
              ))}
            </ol>
            <div className="bg-yellow-950/40 border border-yellow-500/20 rounded-xl p-3 flex gap-2">
              <span className="text-sm shrink-0">⚠️</span>
              <p className="text-[9px] text-yellow-300/80 leading-relaxed">
                Retira a tu wallet de Privy (no directamente a la dirección del treasury).
                Una vez que recibas los fondos, el botón de Privy procesará el pago automáticamente.
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPaying = () => {
    if (!order) return null;
    const shortAddr = `${order.pay_to.slice(0, 6)}…${order.pay_to.slice(-4)}`;

    return (
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <button onClick={() => setScreen('method')} className="flex items-center gap-1 text-slate-500 hover:text-slate-300 text-[11px] font-bold">
            <ChevronLeft size={14} /> Volver
          </button>
          <span className="text-[10px] font-black text-amber-400 tabular-nums">⏳ {countdown}</span>
        </div>

        <div className="text-center">
          <h2 className="text-lg font-black text-white uppercase">Realiza tu pago</h2>
          <p className="text-[10px] text-slate-500 mt-0.5">Envía exactamente esta cantidad a la dirección de abajo</p>
        </div>

        {/* Amount */}
        <div className="bg-purple-950/30 border border-purple-500/30 rounded-2xl p-4 text-center">
          <div className="text-3xl font-black text-white tabular-nums">{order.usdc_amount.toFixed(2)}</div>
          <div className="text-[10px] font-black text-purple-400 uppercase tracking-widest mt-0.5">USDC en Polygon</div>
          <div className="text-[9px] text-slate-500 mt-1">≈ ${(order.usdc_amount).toFixed(2)} USD</div>
        </div>

        {/* Address */}
        <div className="bg-slate-900/50 border border-white/8 rounded-2xl p-4 space-y-2">
          <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Dirección Treasury</div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] text-white break-all flex-1">{order.pay_to}</span>
            <CopyButton text={order.pay_to} />
          </div>
        </div>

        {/* Privy 1-tap pay */}
        <HoldButton
          onConfirm={handlePrivyPay}
          disabled={loading || !USDC_ADDRESS}
          duration={1000}
          variant="danger"
          className="w-full"
          style={{
            width: '100%',
            background: !USDC_ADDRESS ? 'rgba(30,30,50,0.6)' : 'linear-gradient(135deg, #6D28D9, #7C3AED)',
            color: !USDC_ADDRESS ? '#475569' : 'white',
            boxShadow: !USDC_ADDRESS ? undefined : '0 0 20px rgba(109,40,217,0.35)',
            borderRadius: '1rem',
            padding: '14px',
            fontSize: '12px',
            letterSpacing: '0.05em',
            fontWeight: '900',
            textTransform: 'uppercase',
          }}
          label={
            <>
              <span className="text-lg">💜</span>
              {!USDC_ADDRESS ? 'Error: USDC no configurado' : (loading ? 'Enviando…' : 'Pagar con mi wallet (Privy)')}
            </>
          }
        />

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-white/8" />
          <span className="text-[9px] text-slate-600 font-bold uppercase">¿Ya pagaste desde otra app?</span>
          <div className="flex-1 h-px bg-white/8" />
        </div>

        {/* Manual hash */}
        <div className="flex gap-2">
          <input
            value={manualHash}
            onChange={e => setManualHash(e.target.value)}
            placeholder="0x hash de tu transacción…"
            className="flex-1 bg-slate-900/60 border border-white/10 rounded-xl px-3 py-2.5 text-[11px] text-white placeholder-slate-600 font-mono outline-none focus:border-purple-500/50"
          />
          <button
            onClick={() => handleConfirm(manualHash)}
            disabled={!manualHash.trim() || loading}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-white/10 rounded-xl text-[10px] font-black uppercase text-slate-300 hover:text-white transition-all disabled:opacity-30 active:scale-95"
          >
            Verificar
          </button>
        </div>

        {renderBinanceHelp()}
      </div>
    );
  };

  const renderConfirming = () => (
    <div className="flex flex-col items-center gap-5 py-6 text-center">
      <div className="relative">
        <div className="w-20 h-20 rounded-full border-4 border-purple-500/30 border-t-purple-500 animate-spin" />
        <span className="absolute inset-0 flex items-center justify-center text-2xl">⛓️</span>
      </div>
      <div>
        <h2 className="text-lg font-black text-white uppercase">Confirmando pago…</h2>
        <p className="text-[10px] text-slate-500 mt-1">Verificando tu transacción on-chain. Puede tomar 15–60 segundos.</p>
      </div>
      {order?.tx_hash_payment && (
        <a
          href={`https://amoy.polygonscan.com/tx/${order.tx_hash_payment}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-[10px] text-purple-400 hover:text-purple-300 font-bold underline"
        >
          Ver en explorador <ExternalLink size={10} />
        </a>
      )}
    </div>
  );

  const renderSuccess = () => (
    <div className="flex flex-col items-center gap-5 py-4 text-center">
      <style>{`
        @keyframes checkout-glow { 0%,100%{box-shadow:0 0 30px rgba(168,85,247,0.4)} 50%{box-shadow:0 0 60px rgba(228,0,124,0.5)} }
      `}</style>
      <div
        className="w-24 h-24 rounded-full flex items-center justify-center text-4xl"
        style={{ background: 'linear-gradient(135deg,#7C3AED,#E4007C)', animation: 'checkout-glow 2s infinite' }}
      >
        ✅
      </div>
      <div>
        <h2 className="text-2xl font-black text-white uppercase tracking-tight">¡Listo!</h2>
        <p className="text-[11px] text-slate-400 mt-1">Tu recarga fue procesada exitosamente</p>
      </div>
      <div className="bg-purple-950/40 border border-purple-500/30 rounded-2xl px-6 py-4">
        <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
          +{completedAxg.toLocaleString()} AXF
        </div>
        <div className="text-[9px] text-slate-500 uppercase tracking-widest mt-1">Axofichas acreditadas</div>
      </div>
      <button
        onClick={onClose}
        className="w-full py-3.5 rounded-2xl font-black uppercase tracking-widest text-sm transition-all active:scale-95"
        style={{ background: 'linear-gradient(135deg,#7C3AED,#E4007C)', color: 'white', boxShadow: '0 0 24px rgba(168,85,247,0.3)' }}
      >
        ¡A jugar! 🎰
      </button>
    </div>
  );

  // ── Shell ──────────────────────────────────────────────────────────────────
  return (
    <BottomSheet
      open={true}
      onClose={onClose}
      accent="#818CF8"
    >
      <div className="p-5 pb-8 relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all"
        >
          <X size={14} />
        </button>

        {/* Config Error Chip */}
        {!USDC_ADDRESS && (
          <div className="mb-4 bg-red-950/80 border-2 border-red-500 rounded-2xl px-4 py-3 text-red-200 text-[11px] font-black flex items-start gap-2">
            <span>🚨</span>
            <span className="flex-1">
              Error de configuración: La dirección del contrato USDC no está definida en el cliente (NEXT_PUBLIC_USDC_ADDRESS). Las transacciones de pago están deshabilitadas.
            </span>
          </div>
        )}

        {/* Error chip */}
        {error && (
          <div className="mb-4 bg-red-950/50 border border-red-500/30 rounded-2xl px-4 py-3 text-red-200 text-[11px] font-bold flex items-start gap-2">
            <span>⚠️</span>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="shrink-0 text-red-500"><X size={12} /></button>
          </div>
        )}

        {screen === 'packs'      && renderPacks()}
        {screen === 'method'     && renderMethod()}
        {screen === 'paying'     && renderPaying()}
        {screen === 'confirming' && renderConfirming()}
        {screen === 'success'    && renderSuccess()}
      </div>
    </BottomSheet>
  );
}
