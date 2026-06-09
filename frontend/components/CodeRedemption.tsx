'use client';

import { useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { API_BASE } from "@/lib/api";

type State = 'idle' | 'submitting' | 'success' | 'error';

interface RedeemResult {
  mensaje: string;
  item_name: string;
}

interface Props {
  initialCode?: string;
}

export default function CodeRedemption({ initialCode = '' }: Props) {
  const { ready, authenticated, user, login, getAccessToken } = usePrivy();
  const [code, setCode] = useState(initialCode);
  const [state, setState] = useState<State>('idle');
  const [result, setResult] = useState<RedeemResult | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const email =
    user?.email?.address ||
    (user?.google as any)?.email ||
    '';

  async function handleRedeem() {
    if (!code.trim()) return;
    setState('submitting');
    setErrorMsg('');
    try {
      const token = await getAccessToken();
      const res = await fetch(`${API_BASE}/codes/redeem`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code: code.trim().toUpperCase(), email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(
          res.status === 404
            ? 'Código no válido. Revisa que lo escribiste bien.'
            : res.status === 409 && data.detail?.includes('persona')
            ? 'Ya canjeaste una corcholata. ¡Solo una por persona!'
            : res.status === 409
            ? 'Este código ya fue canjeado por otra persona.'
            : 'Algo salió mal. Intenta de nuevo.'
        );
        setState('error');
        return;
      }
      setResult(data);
      setState('success');
    } catch {
      setErrorMsg('Algo salió mal. Intenta de nuevo.');
      setState('error');
    }
  }

  if (!ready) return null;

  if (state === 'success' && result) {
    return (
      <div className="text-center space-y-6 py-8">
        <div className="text-7xl animate-bounce">🎁</div>
        <h3 className="text-2xl font-black text-white">{result.mensaje}</h3>
        <p className="text-gray-400">
          Tu <span className="text-[#E4007C] font-bold">{result.item_name}</span> ya está en tu inventario.
        </p>
        <a
          href="https://play.axolot.to/"
          className="inline-block mt-4 px-10 py-3 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105"
        >
          Ir al juego →
        </a>
      </div>
    );
  }

  if (!authenticated) {
    return (
      <div className="space-y-4">
        {initialCode && (
          <div className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Tu código</p>
            <p className="font-mono text-xl font-bold text-[#E4007C] tracking-widest">{initialCode}</p>
          </div>
        )}
        <p className="text-gray-400 text-sm text-center">
          Inicia sesión para canjear tu corcholata y recibir tu booster gratis.
        </p>
        <button
          onClick={login}
          className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95"
        >
          Iniciar sesión para canjear
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-2">Código de tu corcholata</label>
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="AXL-XXXX"
          maxLength={8}
          className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3 text-white font-mono text-lg tracking-widest placeholder-white/20 focus:outline-none focus:border-[#E4007C] transition-colors"
          disabled={state === 'submitting'}
        />
      </div>

      {state === 'error' && (
        <p className="text-red-400 text-sm">{errorMsg}</p>
      )}

      <button
        onClick={handleRedeem}
        disabled={state === 'submitting' || !code.trim()}
        className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] disabled:opacity-50 disabled:cursor-not-allowed rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95"
      >
        {state === 'submitting' ? 'Canjeando...' : 'Canjear mi corcholata'}
      </button>
    </div>
  );
}
