'use client';

import { useState, useEffect } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { API_BASE } from '@/lib/api';

interface CodeEntryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'join' | 'redeem';
  onRedeemSuccess?: (data: any) => void;
}

type PanelState = 'input' | 'submitting' | 'success' | 'error' | 'existing_redirect' | 'pending_tutorial';

export default function CodeEntryPanel({ isOpen, onClose, mode, onRedeemSuccess }: CodeEntryPanelProps) {
  const { ready, authenticated, login, getAccessToken, user } = usePrivy();
  const [code, setCode] = useState('');
  const [attempts, setAttempts] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');
  const [panelState, setPanelState] = useState<PanelState>('input');
  const [rewards, setRewards] = useState<{
    mensaje: string;
    frijolitos_rewarded: number;
    axofichas_rewarded: number;
    item_name: string;
  } | null>(null);

  // Pre-fill code from localStorage on mount
  useEffect(() => {
    if (isOpen) {
      const draft = localStorage.getItem('corcholata_code_draft') || '';
      setCode(draft.toUpperCase());
    }
  }, [isOpen]);

  // If user becomes authenticated while panel is open and code draft exists, auto-submit
  useEffect(() => {
    if (isOpen && ready && authenticated && panelState === 'input') {
      const draftCode = localStorage.getItem('corcholata_code_draft') || code;
      if (draftCode.trim()) {
        setCode(draftCode.toUpperCase());
        handleSubmitCode(draftCode);
      }
    }
  }, [ready, authenticated, isOpen]);

  if (!isOpen) return null;

  const handlePrivyLogin = () => {
    if (code.trim()) {
      localStorage.setItem('corcholata_code_draft', code.trim().toUpperCase());
    } else {
      localStorage.removeItem('corcholata_code_draft');
    }
    login();
  };

  const handleSubmitCode = async (codeToSubmit: string) => {
    if (!codeToSubmit.trim()) return;
    setPanelState('submitting');
    setErrorMsg('');

    try {
      const token = await getAccessToken();
      const email = user?.email?.address || (user?.google as any)?.email || '';
      
      const res = await fetch(`${API_BASE}/codes/redeem`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          code: codeToSubmit.trim().toUpperCase(),
          email,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Handle attempts remaining
        // Extract attempts remaining from server message if possible, or fall back to incrementing
        if (data.detail) {
          setErrorMsg(data.detail);
          if (data.detail.includes('Intentos restantes:')) {
            const match = data.detail.match(/Intentos restantes:\s*(\d+)/);
            if (match) {
              const rem = parseInt(match[1]);
              setAttempts(3 - rem);
            }
          } else if (res.status === 429) {
            setAttempts(3);
          }
        } else {
          setErrorMsg('Ocurrió un error al canjear el código.');
        }

        // If the user is an existing account (403 or already completed) or has already redeemed (409 without attempts)
        if (res.status === 403 || (res.status === 409 && !data.detail?.includes('Intentos restantes'))) {
          setPanelState('existing_redirect');
        } else {
          setPanelState('error');
        }
        localStorage.removeItem('corcholata_code_draft');
        return;
      }

      // Success — check if pending_tutorial (reward delayed until after tutorial)
      localStorage.removeItem('corcholata_code_draft');
      if (data.status === 'pending_tutorial') {
        setRewards(data);
        setPanelState('pending_tutorial');
        if (onRedeemSuccess) {
          onRedeemSuccess(data);
        }
        return;
      }

      setRewards(data);
      setPanelState('success');
      if (onRedeemSuccess) {
        onRedeemSuccess(data);
      }
    } catch (err) {
      setErrorMsg('Error de conexión. Intenta de nuevo.');
      setPanelState('error');
    }
  };

  const remainingAttempts = Math.max(0, 3 - attempts);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="relative z-10 w-full max-w-md overflow-hidden rounded-3xl border border-pink-500/20 bg-[#0d0d16] p-8 shadow-[0_0_50px_rgba(228,0,124,0.15)] text-white transform transition-all duration-300 scale-100">
        
        {/* Glow effect */}
        <div className="absolute -top-16 -left-16 w-32 h-32 bg-[#E4007C]/10 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute -bottom-16 -right-16 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />

        {/* Close Button */}
        {panelState !== 'success' && panelState !== 'existing_redirect' && (
          <button 
            className="absolute top-4 right-4 text-gray-400 hover:text-white text-xl p-2 transition-colors focus:outline-none"
            onClick={onClose}
          >
            ✕
          </button>
        )}

        {panelState === 'success' && rewards ? (
          /* SUCCESS SCREEN */
          <div className="text-center space-y-6 py-4 animate-fade-in">
            <div className="text-7xl animate-bounce">🎁</div>
            <h3 className="text-3xl font-black text-[#FF8DA1] drop-shadow-[0_0_15px_rgba(255,141,161,0.3)]">
              ¡Canje exitoso!
            </h3>
            <p className="text-gray-300 text-sm">
              Tu regalo de bienvenida ha sido añadido a tu inventario y billetera:
            </p>

            {/* Recompensas Grid */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 divide-y divide-white/10 text-left text-sm max-w-xs mx-auto">
              <div className="flex justify-between py-2">
                <span className="flex items-center gap-2">🪙 Axofichas (AXF)</span>
                <span className="font-bold text-pink-400">+{rewards.axofichas_rewarded} AXF</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="flex items-center gap-2">🌿 Frijolitos (FRJ)</span>
                <span className="font-bold text-[#E4007C]">+{rewards.frijolitos_rewarded} FRJ</span>
              </div>
              {rewards.item_name && (
                <div className="flex justify-between py-2">
                  <span className="flex items-center gap-2">🎁 {rewards.item_name}</span>
                  <span className="font-bold text-purple-400">1 unidad</span>
                </div>
              )}
            </div>

            <p className="text-xs text-gray-500 leading-tight">
              Tip: Empiezas con 139 AXF. Cada partida clásica cuesta 10 AXF. ¡Calcula bien tus rachas!
            </p>

            <button
              onClick={() => window.location.href = '/play'}
              className="w-full mt-4 py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95 text-white"
            >
              Comenzar a jugar →
            </button>
          </div>
        ) : panelState === 'pending_tutorial' && rewards ? (
          /* PENDING TUTORIAL — reward saved, revealed after tutorial */
          <div className="text-center space-y-6 py-4 animate-fade-in">
            <div className="text-7xl animate-bounce">🔒</div>
            <h3 className="text-2xl font-black text-yellow-400">¡Código Verificado!</h3>
            <p className="text-gray-300 text-sm">
              Tu Kit de Bienvenida está guardado. Se revelará al terminar el tutorial.
            </p>

            {/* Reward preview */}
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-xs text-yellow-300 space-y-1 text-left max-w-xs mx-auto">
              <div className="flex justify-between py-1">
                <span>🪙 Axofichas (AXF)</span>
                <span className="font-bold text-yellow-400">+{rewards.axofichas_rewarded} AXF</span>
              </div>
              <div className="flex justify-between py-1">
                <span>🌿 Frijolitos (FRJ)</span>
                <span className="font-bold text-yellow-400">+{rewards.frijolitos_rewarded} FRJ</span>
              </div>
              {rewards.item_name && (
                <div className="flex justify-between py-1">
                  <span>🎁 {rewards.item_name}</span>
                  <span className="font-bold text-yellow-400">1 unidad</span>
                </div>
              )}
            </div>

            <button
              onClick={() => window.location.href = '/play'}
              className="w-full mt-4 py-4 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 rounded-full font-black text-lg text-black shadow-[0_0_30px_rgba(234,179,8,0.5)] transition-all transform hover:scale-105 active:scale-95"
            >
              Comenzar Tutorial →
            </button>
          </div>
        ) : panelState === 'existing_redirect' ? (
          /* EXISTING USER REDIRECT */
          <div className="text-center space-y-6 py-6">
            <div className="text-5xl">🦎</div>
            <h3 className="text-2xl font-black text-white">¡Bienvenido de vuelta!</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              {errorMsg || 'Esta cuenta ya está registrada o ya has canjeado un código promocional. Te redirigimos al juego principal.'}
            </p>
            <button
              onClick={() => window.location.href = '/play'}
              className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95 text-white"
            >
              Ir al juego →
            </button>
          </div>
        ) : (
          /* CODE ENTRY FORM */
          <div className="space-y-6">
            <div className="text-center">
              <span className="text-4xl">🎁</span>
              <h2 className="text-2xl font-black mt-2">
                {mode === 'redeem' ? 'Canjear mi Corcholata' : 'Únete a Axolotto'}
              </h2>
              <p className="text-gray-400 text-xs mt-1">
                {mode === 'redeem' 
                  ? 'Ingresa el código único de tu corcholata física.' 
                  : 'Regístrate y opcionalmente añade tu código de corcholata para recibir un kit premium.'}
              </p>
            </div>

            {/* Input field */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">
                Código de Corcholata {mode === 'join' && '(Opcional)'}
              </label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                placeholder="AXOL-K7M3"
                maxLength={12}
                disabled={panelState === 'submitting'}
                className="w-full bg-white/5 border border-white/10 focus:border-pink-500 rounded-xl px-4 py-3 text-white text-center font-mono text-xl tracking-widest placeholder-white/10 focus:outline-none transition-all duration-200"
              />
            </div>

            {/* Attempts indicator if error exists */}
            {attempts > 0 && panelState === 'error' && (
              <div className="text-center space-y-1">
                <p className="text-xs text-gray-400">Intentos de validación:</p>
                <div className="flex justify-center space-x-2">
                  {[...Array(3)].map((_, i) => (
                    <span
                      key={i}
                      className={`h-3 w-3 rounded-full transition-all duration-300 ${
                        i < remainingAttempts ? 'bg-pink-500 shadow-[0_0_8px_#ec4899]' : 'bg-gray-700'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Inline Error Message */}
            {panelState === 'error' && errorMsg && (
              <p className="text-center text-sm font-semibold text-red-400 leading-snug">
                {errorMsg}
              </p>
            )}

            {/* Submit Action */}
            <div className="space-y-3 pt-2">
              {!authenticated ? (
                /* Unauthenticated Flow */
                <button
                  onClick={handlePrivyLogin}
                  disabled={panelState === 'submitting'}
                  className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 text-white"
                >
                  {panelState === 'submitting' 
                    ? 'Procesando...' 
                    : code.trim() 
                      ? 'Iniciar sesión para canjear' 
                      : 'Iniciar sesión con Privy'}
                </button>
              ) : (
                /* Authenticated Flow */
                <button
                  onClick={() => handleSubmitCode(code)}
                  disabled={panelState === 'submitting' || (mode === 'redeem' && !code.trim())}
                  className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 text-white"
                >
                  {panelState === 'submitting' 
                    ? 'Validando...' 
                    : code.trim() 
                      ? 'Validar código corcholata' 
                      : 'Continuar al juego'}
                </button>
              )}

              {/* Subtitle notes */}
              <p className="text-center text-gray-500 text-[10px]">
                {!authenticated 
                  ? 'Privy permite acceso rápido mediante Google, Apple o tu Correo Electrónico.' 
                  : 'Ya has iniciado sesión con éxito. Haz clic arriba para proceder.'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
