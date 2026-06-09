'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import CodeEntryPanel from '@/components/CodeEntryPanel';
import TutorialResetButton from '@/components/dev/TutorialResetButton';

const CARDS = [
  { name: 'El Axolotito', emoji: '🦎', rarity: 'Legendario', color: 'from-yellow-500/20 to-orange-500/10 border-yellow-500/30' },
  { name: 'La Luna', emoji: '🌙', rarity: 'Épico', color: 'from-purple-500/20 to-blue-500/10 border-purple-500/30' },
  { name: 'El Sol', emoji: '☀️', rarity: 'Raro', color: 'from-orange-500/20 to-red-500/10 border-orange-500/30' },
  { name: 'La Rosa', emoji: '🌹', rarity: 'Común', color: 'from-pink-500/20 to-red-500/10 border-pink-500/30' },
];

function JoinPageInner() {
  const searchParams = useSearchParams();
  const codeFromUrl = searchParams.get('code') ?? '';
  const showRewardFromUrl = searchParams.get('show_reward') ?? '';
  const router = useRouter();
  const { ready, authenticated, login } = usePrivy();
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [panelMode, setPanelMode] = useState<'join' | 'redeem'>('join');
  const [showRewardPreview, setShowRewardPreview] = useState(false);

  // Si hay código en draft pendiente y ya está autenticado, abrir el panel de redeem
  useEffect(() => {
    if (ready && authenticated) {
      const draft = localStorage.getItem('corcholata_code_draft');
      if (draft) {
        setIsPanelOpen(true);
        setPanelMode('redeem');
      }
    }
  }, [ready, authenticated]);

  // Si viene de un reset de tutorial con premio dev, mostrar preview del premio
  useEffect(() => {
    if (ready && authenticated && showRewardFromUrl === '1') {
      localStorage.removeItem('dev_show_reward');
      setShowRewardPreview(true);
    }
  }, [ready, authenticated, showRewardFromUrl]);

  const handleOpenPanel = (mode: 'join' | 'redeem') => {
    setPanelMode(mode);
    setIsPanelOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">

      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-40 bg-[#0a0a0f]/80 backdrop-blur-md border-b border-white/5 px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-black text-[#FF8DA1] tracking-tighter">AXOLOTTO</h1>
        <button 
          onClick={() => {
            if (ready && authenticated) {
              router.push('/play');
            } else {
              login();
            }
          }}
          className="px-6 py-2 border border-white/20 hover:border-white/40 hover:bg-white/5 rounded-full text-sm font-bold transition-all"
        >
          {ready && authenticated ? 'Ir al juego →' : 'Iniciar sesión'}
        </button>
      </header>

      {/* Hero */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden pt-20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(228,0,124,0.15)_0%,transparent_70%)] pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-[#E4007C]/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 text-center space-y-6 max-w-2xl">

          {/* ── Reward Preview (dev reset flow) ─────────────────────────────── */}
          {showRewardPreview ? (
            <>
              <div className="text-7xl animate-bounce">🔒</div>
              <div className="inline-block px-4 py-1 bg-yellow-500/20 border border-yellow-500/40 rounded-full text-yellow-400 text-sm font-bold tracking-wider mb-2">
                DEV — PREMIO DE PRUEBA
              </div>
              <h2 className="text-4xl sm:text-5xl font-black text-yellow-400 drop-shadow-[0_0_30px_rgba(234,179,8,0.4)]">
                ¡Premio Listo!
              </h2>
              <p className="text-gray-300 text-lg">
                Tu Kit de Bienvenida está guardado. Se revelará al terminar el tutorial.
              </p>

              {/* Reward amounts */}
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-5 space-y-3 max-w-xs mx-auto text-left">
                <div className="flex justify-between items-center py-1">
                  <span className="flex items-center gap-2 text-sm text-yellow-200">🪙 Axofichas</span>
                  <span className="font-black text-lg text-yellow-400">+10,000 AXF</span>
                </div>
                <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
                  <span className="flex items-center gap-2 text-sm text-yellow-200">🌿 Frijolitos</span>
                  <span className="font-black text-lg text-yellow-400">+100,000 FRJ</span>
                </div>
                <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
                  <span className="flex items-center gap-2 text-sm text-yellow-200">🎁 Ítem exclusivo</span>
                  <span className="font-black text-lg text-purple-400">1 und</span>
                </div>
              </div>

              <button
                onClick={() => router.push('/play')}
                className="inline-block mt-4 px-10 py-4 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 rounded-full font-black text-xl text-black shadow-[0_0_40px_rgba(234,179,8,0.5)] transition-all transform hover:scale-105 active:scale-95"
              >
                Comenzar Tutorial →
              </button>
            </>
          ) : (
            <>
              <div className="inline-block px-4 py-1 bg-[#E4007C]/20 border border-[#E4007C]/40 rounded-full text-[#E4007C] text-sm font-bold tracking-wider mb-2">
                FASE 1 — ACCESO ANTICIPADO
              </div>

              <h1 className="text-7xl sm:text-9xl font-black text-[#FF8DA1] drop-shadow-[0_0_40px_rgba(255,141,161,0.4)] tracking-tighter">
                AXOLOTTO
              </h1>

              {codeFromUrl ? (
                <div className="space-y-2">
                  <p className="text-xl text-gray-300">Tu corcholata te está esperando 🎉</p>
                  <div className="inline-block font-mono text-2xl font-black text-[#E4007C] bg-[#E4007C]/10 border border-[#E4007C]/30 px-6 py-2 rounded-xl tracking-widest">
                    {codeFromUrl}
                  </div>
                </div>
              ) : (
                <p className="text-xl text-gray-400">La lotería del futuro ya llegó</p>
              )}

              <button
                onClick={() => handleOpenPanel(codeFromUrl ? 'redeem' : 'join')}
                className="inline-block mt-2 px-10 py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-xl shadow-[0_0_40px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95 text-white animate-fade-in"
              >
                {codeFromUrl ? 'Canjear mi regalo →' : 'Únete ahora →'}
              </button>
            </>
          )}
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-600 animate-bounce text-2xl">↓</div>
      </section>

      {/* Qué es Axolotto */}
      <section className="py-24 px-6 max-w-5xl mx-auto">
        <h2 className="text-4xl sm:text-5xl font-black text-center mb-4">¿Qué es Axolotto?</h2>
        <p className="text-gray-400 text-center text-lg mb-16 max-w-2xl mx-auto">
          Un juego de lotería mexicana con Axolotitos NFT que puedes coleccionar, criar y usar para ganar premios reales en la blockchain.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            {
              icon: '🦎',
              title: 'Colecciona Axolotitos',
              desc: 'Cada Axolotito es único. Críalos, personalízalos y consigue los más raros para dominar el juego.',
            },
            {
              icon: '🃏',
              title: 'Juega Lotería On-Chain',
              desc: 'Partidas multijugador con jackpots reales. La emoción de la lotería tradicional potenciada por blockchain.',
            },
            {
              icon: '🏆',
              title: 'Gana Premios Reales',
              desc: 'Los mejores jugadores ganan tokens AXF y FRJ canjeables. Rankings globales, temporadas, torneos.',
            },
          ].map((item) => (
            <div
              key={item.title}
              className="bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-[#E4007C]/40 transition-colors"
            >
              <div className="text-5xl mb-4">{item.icon}</div>
              <h3 className="font-black text-xl mb-2">{item.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Colecciones Preview */}
      <section className="py-16 px-6 bg-gradient-to-b from-transparent via-[#E4007C]/5 to-transparent">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl sm:text-5xl font-black text-center mb-4">Colecciona cosas chidas</h2>
          <p className="text-gray-400 text-center mb-12">
            Cartas de lotería en distintas rarezas. Primeras ediciones. Versiones holográficas. El coleccionismo de verdad.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {CARDS.map((card) => (
              <div
                key={card.name}
                className={`bg-gradient-to-br ${card.color} border rounded-2xl p-6 text-center hover:scale-105 transition-transform cursor-default`}
              >
                <div className="text-5xl mb-3">{card.emoji}</div>
                <p className="font-black">{card.name}</p>
                <p className="text-xs text-gray-400 mt-1">{card.rarity}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-500 text-sm mt-8">
            54 cartas oficiales · Versiones Foil · Axolotitos únicos generados on-chain
          </p>
        </div>
      </section>

      {/* LOGIN CTA */}
      <section className="py-16 px-6 max-w-md mx-auto text-center">
        <div className="bg-gradient-to-br from-[#E4007C]/10 to-purple-900/10 border border-[#E4007C]/30 rounded-3xl p-8">
          <div className="text-6xl mb-4">🦎</div>
          <h2 className="text-3xl font-black mb-2">¿Listo para jugar?</h2>
          <p className="text-gray-400 text-sm mb-6">
            Entra con tu cuenta y te asignamos un Webito. El tutorial es gratis — solo pagas cuando quieras jugar de verdad.
          </p>
          <button
            onClick={() => handleOpenPanel('join')}
            disabled={!ready}
            className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_40px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed text-white"
          >
            {ready ? '¡Jugar gratis! →' : 'Cargando...'}
          </button>
          <p className="text-gray-600 text-xs mt-4">
            Google · Apple · Email — sin wallet requerida
          </p>
        </div>
      </section>

      {/* Code Redemption CTA */}
      <section id="canjear" className="py-24 px-6">
        <div className="max-w-md mx-auto">
          <div className="bg-white/5 border border-white/10 rounded-3xl p-8 sm:p-10 text-center">
            <div className="mb-6">
              <div className="text-5xl mb-3">🎁</div>
              <h2 className="text-3xl font-black mb-2">Tu regalo de bienvenida</h2>
              <p className="text-gray-400 text-sm">
                {codeFromUrl
                  ? 'Inicia sesión y canjea tu corcholata para recibir un booster pack gratis.'
                  : 'Si tienes una corcholata de Axolotto, ingresa tu código aquí para recibir un booster pack gratis.'}
              </p>
            </div>

            <button
              onClick={() => handleOpenPanel('redeem')}
              className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95 text-white"
            >
              Ingresar código de corcholata
            </button>

            {!codeFromUrl && (
              <p className="text-center text-gray-600 text-xs mt-6">
                ¿No tienes corcholata? Encuéntranos en ferias y eventos de maker/tech.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/5 text-center">
        <h2 className="text-2xl font-black text-[#FF8DA1] mb-2">AXOLOTTO</h2>
        <p className="text-gray-600 text-sm">axolot.to · La lotería del futuro</p>
      </footer>

      {/* Modal CodeEntryPanel */}
      <CodeEntryPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        mode={panelMode}
      />

      {/* Dev tools */}
      <TutorialResetButton />
    </div>
  );
}

export default function JoinPage() {
  return (
    <Suspense>
      <JoinPageInner />
    </Suspense>
  );
}
