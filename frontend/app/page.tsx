'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import CodeEntryPanel from '@/components/CodeEntryPanel';
import LoteriaCard from '@/components/ui/LoteriaCard';
import { 
  Coins, 
  Flame, 
  Sparkles, 
  Trophy, 
  Egg, 
  Layers, 
  ArrowRight, 
  Users, 
  Zap, 
  Heart,
  Gift
} from 'lucide-react';

const CARDS = [
  {
    name: 'El Axolotl',
    item_metadata: { numero_loteria: 1 },
    dynamic_rarity: 'Legendaria',
    is_shiny: true,
  },
  {
    name: 'La Luna',
    item_metadata: { numero_loteria: 23 },
    dynamic_rarity: 'Épica',
    is_shiny: false,
  },
  {
    name: 'El Sol',
    item_metadata: { numero_loteria: 46 },
    dynamic_rarity: 'Rara',
    is_shiny: false,
  },
  {
    name: 'La Rosa',
    item_metadata: { numero_loteria: 41 },
    dynamic_rarity: 'Común',
    is_shiny: false,
  },
];

function JoinPageInner() {
  const searchParams = useSearchParams();
  const codeFromUrl = searchParams.get('code') ?? '';
  const showStarterKitFromUrl = searchParams.get('show_reward') ?? '';
  const router = useRouter();
  const { ready, authenticated, login } = usePrivy();
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [panelMode, setPanelMode] = useState<'join' | 'redeem'>('join');
  const [showStarterKitPreview, setShowStarterKitPreview] = useState(false);

  // Si hay código en draft pendiente y ya está autenticado, abrir el panel de redeem
  useEffect(() => {
    if (!ready || !authenticated) return;

    const draft = localStorage.getItem('corcholata_code_draft');
    if (!draft) return;

    const timer = window.setTimeout(() => {
      setPanelMode('redeem');
      setIsPanelOpen(true);
    }, 0);

    return () => window.clearTimeout(timer);
  }, [ready, authenticated]);

  // Si viene de un reset de tutorial, mostrar el kit interno de prueba
  useEffect(() => {
    if (!ready || !authenticated || showStarterKitFromUrl !== '1') return;

    localStorage.removeItem('dev_show_reward');
    const timer = window.setTimeout(() => {
      setShowStarterKitPreview(true);
    }, 0);

    return () => window.clearTimeout(timer);
  }, [ready, authenticated, showStarterKitFromUrl]);

  const handleOpenPanel = (mode: 'join' | 'redeem') => {
    setPanelMode(mode);
    setIsPanelOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#07070c] text-white selection:bg-[#E4007C] selection:text-white font-sans overflow-x-hidden">
      
      {/* Glowes de fondo decorativos */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[#E4007C]/10 rounded-full blur-[120px] pointer-events-none z-0" />
      <div className="absolute top-[20%] right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[140px] pointer-events-none z-0" />
      <div className="absolute top-[50%] left-10 w-[450px] h-[450px] bg-[#FF8DA1]/5 rounded-full blur-[110px] pointer-events-none z-0" />
      <div className="absolute bottom-[10%] right-10 w-[550px] h-[550px] bg-indigo-600/10 rounded-full blur-[130px] pointer-events-none z-0" />

      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-50 bg-[#07070c]/85 backdrop-blur-lg border-b border-white/5 px-6 py-4 flex justify-between items-center transition-all duration-300">
        <div className="flex items-center gap-2 group cursor-pointer" onClick={() => router.push('/')}>
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#E4007C] to-[#B30062] flex items-center justify-center font-black text-white shadow-[0_0_15px_rgba(228,0,124,0.5)] transform group-hover:scale-110 transition-transform">
            L
          </div>
          <span className="text-2xl font-black text-[#FF8DA1] tracking-tighter uppercase">AXOLOTTO</span>
        </div>
        <button 
          onClick={() => {
            if (ready && authenticated) {
              router.push('/play');
            } else {
              login();
            }
          }}
          className="px-6 py-2.5 bg-gradient-to-r from-[#E4007C]/10 to-purple-600/10 border border-[#E4007C]/30 hover:border-[#E4007C]/60 hover:bg-[#E4007C]/20 rounded-full text-sm font-bold transition-all shadow-[0_0_15px_rgba(228,0,124,0.15)] hover:shadow-[0_0_20px_rgba(228,0,124,0.3)] hover:scale-105"
        >
          {ready && authenticated ? 'Ir al juego →' : 'Iniciar sesión'}
        </button>
      </header>

      {/* Hero */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden pt-24 pb-16 z-10">
        <div className="relative text-center space-y-8 max-w-3xl">

          {/* ── Starter kit preview (dev reset flow) ───────────────────────── */}
          {showStarterKitPreview ? (
            <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-3xl p-8 sm:p-12 space-y-6 max-w-lg mx-auto shadow-[0_0_50px_rgba(234,179,8,0.1)] backdrop-blur-md">
              <div className="text-7xl animate-bounce">🔒</div>
              <div className="inline-block px-4 py-1 bg-yellow-500/20 border border-yellow-500/40 rounded-full text-yellow-400 text-xs font-black tracking-wider uppercase">
                ADMIN — KIT INTERNO DE PRUEBA
              </div>
              <h2 className="text-4xl sm:text-5xl font-black text-yellow-400 drop-shadow-[0_0_20px_rgba(234,179,8,0.3)]">
                ¡Kit de prueba listo!
              </h2>
              <p className="text-gray-300 text-base leading-relaxed">
                Tu kit de bienvenida se mostrará en el inventario al terminar el tutorial. Su contenido sirve únicamente dentro del entorno de prueba.
              </p>

              {/* Internal test credits */}
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-5 space-y-3 text-left">
                <div className="flex justify-between items-center py-1">
                  <span className="flex items-center gap-2 text-sm text-yellow-200 font-bold">🪙 Axofichas</span>
                  <span className="font-black text-lg text-yellow-400">+10,000 AXF</span>
                </div>
                <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
                  <span className="flex items-center gap-2 text-sm text-yellow-200 font-bold">🌿 Frijolitos</span>
                  <span className="font-black text-lg text-yellow-400">+100,000 FRJ</span>
                </div>
                <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
                  <span className="flex items-center gap-2 text-sm text-yellow-200 font-bold">🎁 Ítem exclusivo</span>
                  <span className="font-black text-lg text-purple-400">1 und</span>
                </div>
                <p className="border-t border-yellow-500/10 pt-3 text-[10px] leading-relaxed text-yellow-200/70">
                  AXF y FRJ son créditos internos de prueba: no son dinero, no se retiran y no tienen valor garantizado fuera del juego.
                </p>
              </div>

              <button
                onClick={() => router.push('/play')}
                className="w-full mt-4 px-10 py-4 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 rounded-full font-black text-lg text-black shadow-[0_0_40px_rgba(234,179,8,0.4)] transition-all transform hover:scale-105 active:scale-95"
              >
                Comenzar Tutorial de Prueba →
              </button>
            </div>
          ) : (
            <>
              <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[#E4007C]/15 border border-[#E4007C]/30 rounded-full text-[#FF8DA1] text-xs font-bold tracking-wider uppercase animate-pulse">
                <Sparkles size={14} /> FASE 1 — ACCESO ANTICIPADO COMPLETO
              </div>

              <h1 className="text-6xl sm:text-8xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#FF8DA1] via-[#E4007C] to-purple-400 drop-shadow-[0_0_50px_rgba(228,0,124,0.3)] tracking-tighter uppercase leading-[0.95]">
                AXOLOTTO
              </h1>

              <p className="text-lg sm:text-xl md:text-2xl text-gray-300 font-medium max-w-2xl mx-auto leading-relaxed">
                El clásico juego de la <span className="text-[#FF8DA1] font-bold">lotería mexicana</span> convertido en una experiencia social gratuita. Colecciona Axolotitos, personaliza tus tableros y juega con tu comunidad sin pagar por entrar.
              </p>

              {codeFromUrl && (
                <div className="max-w-md mx-auto bg-[#E4007C]/10 border border-[#E4007C]/30 p-4 rounded-2xl backdrop-blur-md animate-fade-in">
                  <p className="text-sm text-gray-300 font-bold mb-1.5">🎉 ¡Código de Corcholata Detectado!</p>
                  <div className="font-mono text-xl font-black text-[#FF8DA1] tracking-widest uppercase">
                    {codeFromUrl}
                  </div>
                </div>
              )}

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                <button
                  onClick={() => handleOpenPanel(codeFromUrl ? 'redeem' : 'join')}
                  className="w-full sm:w-auto px-10 py-4.5 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_40px_rgba(228,0,124,0.4)] hover:shadow-[0_0_50px_rgba(228,0,124,0.6)] transition-all transform hover:scale-105 active:scale-95 text-white flex items-center justify-center gap-2"
                >
                  {codeFromUrl ? 'Canjear mi Regalo →' : 'Comenzar a Jugar →'}
                </button>
                <button
                  onClick={() => {
                    const el = document.getElementById('explicacion');
                    el?.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="w-full sm:w-auto px-8 py-4.5 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 rounded-full font-bold text-lg text-gray-300 hover:text-white transition-all"
                >
                  Conocer más ↓
                </button>
              </div>
            </>
          )}
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-600 animate-bounce text-2xl cursor-pointer" onClick={() => {
          const el = document.getElementById('explicacion');
          el?.scrollIntoView({ behavior: 'smooth' });
        }}>↓</div>
      </section>

      {/* Qué es Axolotto */}
      <section id="explicacion" className="py-24 px-6 max-w-6xl mx-auto scroll-mt-20 relative z-10">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl sm:text-5xl font-black tracking-tight">¿Cómo funciona Axolotto?</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Axolotto combina colección digital, cuidado de mascotas y partidas gratuitas de lotería mexicana.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: <Egg className="w-8 h-8 text-[#FF8DA1]" />,
              title: '1. Cría Axolotitos',
              desc: 'Empieza con un Webito, cuídalo durante su incubación y descubre un Axolotito con apariencia y personalidad propias. El tutorial incluye una forma gratuita de comenzar.',
              glow: 'shadow-[0_0_20px_rgba(255,141,161,0.15)] border-[#FF8DA1]/20'
            },
            {
              icon: <Layers className="w-8 h-8 text-[#E4007C]" />,
              title: '2. Arma tus Tableros',
              desc: 'Colecciona cartas y crea tableros de 16 posiciones. Combina estilos, variantes visuales y decoraciones para construir una identidad propia.',
              glow: 'shadow-[0_0_20px_rgba(228,0,124,0.15)] border-[#E4007C]/20'
            },
            {
              icon: <Trophy className="w-8 h-8 text-purple-400" />,
              title: '3. Juega y Progresa',
                desc: 'Juega gratis contra la CPU, completa patrones de lotería y avanza en misiones, niveles y colecciones. Los resultados no otorgan dinero ni saldos retirables.',
              glow: 'shadow-[0_0_20px_rgba(168,85,247,0.15)] border-purple-500/20'
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className={`bg-white/[0.02] border backdrop-blur-sm rounded-3xl p-8 hover:bg-white/[0.05] hover:border-white/20 transition-all duration-300 hover:-translate-y-1.5 ${item.glow}`}
            >
              <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mb-6 shadow-inner">
                {item.icon}
              </div>
              <h3 className="font-black text-xl mb-3 text-white">{item.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Créditos internos */}
      <section className="py-20 px-6 bg-gradient-to-b from-transparent via-[#E4007C]/5 to-transparent border-y border-white/5 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl sm:text-5xl font-black">Créditos y catálogo transparentes</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              AXF y FRJ son créditos de uso interno: no son dinero, inversión ni saldo retirable. Jugar no requiere comprarlos.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* AXF Box */}
            <div className="bg-gradient-to-br from-amber-500/5 to-orange-500/[0.02] border border-amber-500/25 rounded-3xl p-8 backdrop-blur-md shadow-[0_0_30px_rgba(245,158,11,0.05)] hover:border-amber-500/40 transition-colors">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
                  <Coins className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-black text-2xl text-amber-400 tracking-tight">AXF</h3>
                  <p className="text-xs text-amber-300/80 font-bold uppercase tracking-wider">Axofichas — Crédito interno de catálogo</p>
                </div>
              </div>
              
              <ul className="space-y-4 text-sm text-gray-300">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0" />
                  <span><strong>Contenido opcional:</strong> Se usa para artículos digitales y cosméticos; las partidas principales siguen siendo gratuitas.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0" />
                  <span><strong>Precio claro:</strong> Cada artículo mostrará su contenido completo y precio fijo antes de cualquier confirmación.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0" />
                  <span><strong>Sin azar comprado:</strong> No se venderán resultados aleatorios ni ventajas basadas en una compra incierta.</span>
                </li>
              </ul>
            </div>

            {/* FRJ Box */}
            <div className="bg-gradient-to-br from-emerald-500/5 to-teal-500/[0.02] border border-emerald-500/25 rounded-3xl p-8 backdrop-blur-md shadow-[0_0_30px_rgba(16,185,129,0.05)] hover:border-emerald-500/40 transition-colors">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                  <Flame className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-black text-2xl text-emerald-400 tracking-tight">FRJ</h3>
                  <p className="text-xs text-emerald-300/80 font-bold uppercase tracking-wider">Frijolitos — Crédito interno de progresión</p>
                </div>
              </div>
              
              <ul className="space-y-4 text-sm text-gray-300">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span><strong>Partidas gratuitas:</strong> Las salas principales no cobran cuota de entrada ni exigen arriesgar créditos.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span><strong>Personalización y crafteo:</strong> Se usan dentro del juego para cuidados, recetas y transformación de duplicados.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span><strong>Uso cerrado:</strong> Forman parte de la progresión interna; no se cambian por efectivo, no se retiran y no prometen valor futuro.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Colecciones Preview */}
      <section className="py-24 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl sm:text-5xl font-black">Colecciona y personaliza tu estilo</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Cada carta es una pieza visual para jugar y crear tableros. Las rarezas describen su estilo y disponibilidad, no una rentabilidad financiera.
            </p>
          </div>

          {/* Cards Render with LoteriaCard component */}
          <div className="flex flex-wrap justify-center gap-6 md:gap-8 mb-12">
            {CARDS.map((card) => (
              <div 
                key={card.name} 
                className="flex flex-col items-center space-y-4 p-5 bg-white/[0.02] border border-white/10 rounded-2xl hover:border-[#E4007C]/40 hover:bg-white/[0.05] transition-all duration-300 transform hover:-translate-y-2 shadow-[0_10px_20px_rgba(0,0,0,0.5)] group"
              >
                <div className="relative transform group-hover:scale-105 transition-transform duration-300">
                  <LoteriaCard 
                    card={card} 
                    size={135} 
                    interactive={true} 
                    showQty={false} 
                    isFirstEdition={card.is_shiny} 
                  />
                </div>
                <div className="text-center w-full">
                  <p className="font-black text-base tracking-tight text-white">{card.name}</p>
                  <span className={`inline-block mt-1 px-3 py-0.5 text-[10px] font-bold rounded-full border tracking-wide uppercase ${
                    card.dynamic_rarity === 'Legendaria' ? 'bg-amber-500/10 border-amber-500/30 text-amber-300' :
                    card.dynamic_rarity === 'Épica' ? 'bg-purple-500/10 border-purple-500/30 text-purple-300' :
                    card.dynamic_rarity === 'Rara' ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300' :
                    'bg-slate-500/10 border-slate-500/30 text-slate-300'
                  }`}>
                    {card.dynamic_rarity} {card.is_shiny && '★ Shiny'}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center text-sm mt-12 bg-white/[0.02] border border-white/5 rounded-3xl p-8 backdrop-blur-sm">
            <div className="space-y-1.5">
              <div className="text-[#FF8DA1] font-black text-xl flex items-center justify-center gap-1.5"><Sparkles size={18} /> Variantes visuales</div>
              <p className="text-gray-400 text-xs">Las cartas Shiny aportan acabados holográficos y opciones de personalización, sin promesas de valor económico.</p>
            </div>
            <div className="space-y-1.5 border-y md:border-y-0 md:border-x border-white/5 py-4 md:py-0 md:px-4">
              <div className="text-[#FF8DA1] font-black text-xl flex items-center justify-center gap-1.5"><Layers size={18} /> Tableros personales</div>
              <p className="text-gray-400 text-xs">Ordena tus cartas, guarda composiciones y cambia la presentación de cada tablero para distintos eventos.</p>
            </div>
            <div className="space-y-1.5">
              <div className="text-[#FF8DA1] font-black text-xl flex items-center justify-center gap-1.5"><Users size={18} /> Creadores en el futuro</div>
              <p className="text-gray-400 text-xs">Se estudia un mercado curado para creadores adultos verificados. Todavía no está disponible.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Los Axolotitos (Mascotas y Stats) */}
      <section className="py-24 px-6 bg-[#E4007C]/[0.02] border-y border-white/5 relative z-10">
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/25 rounded-full text-purple-300 text-xs font-bold uppercase tracking-wider">
              <Zap size={12} /> Genética y personalización
            </div>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight leading-tight">Axolotitos digitales únicos</h2>
            <p className="text-gray-300 text-base leading-relaxed">
              Cada Axolotito cuenta con un <span className="text-[#FF8DA1] font-bold">DNA digital</span> que determina su color, tipo de branquias, cola y rasgos de juego. La cadena puede registrar estos datos para hacerlos verificables, sin convertirlos en una inversión.
            </p>
            
            <div className="space-y-4 text-sm">
              <div className="flex gap-3">
                <span className="text-xl">🎯</span>
                <div>
                  <strong className="text-white block font-black">Concentración (Focus)</strong>
                  <span className="text-gray-400">Reduce la posibilidad de que el Axolotito pierda de vista o ignore una carta cantada durante la partida.</span>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-xl">🍀</span>
                <div>
                  <strong className="text-white block font-black">Suerte (Luck)</strong>
                  <span className="text-gray-400">Aporta variedad a reacciones y descubrimientos cosméticos; nunca representa una probabilidad de obtener dinero.</span>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-xl">🔋</span>
                <div>
                  <strong className="text-white block font-black">Estamina y Sueño</strong>
                  <span className="text-gray-400">Determina la energía disponible. Al agotarse, el Axolotito descansa y muestra un resumen de actividad y progreso.</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-6 bg-gradient-to-br from-purple-500/5 via-[#E4007C]/5 to-transparent border border-white/10 rounded-3xl p-8 relative overflow-hidden backdrop-blur-md shadow-[0_0_50px_rgba(228,0,124,0.1)]">
            <div className="absolute top-0 right-0 w-28 h-28 bg-[#E4007C]/20 rounded-full blur-2xl pointer-events-none" />
            <h3 className="font-black text-xl mb-4 text-[#FF8DA1] flex items-center gap-2">🦎 Resumen de actividad</h3>
            <p className="text-xs text-gray-400 mb-6">Ejemplo de progreso después de una sesión gratuita:</p>
            
            <div className="space-y-3 bg-[#07070c]/60 border border-white/5 rounded-2xl p-5 font-mono text-xs">
              <div className="flex justify-between border-b border-white/5 pb-2 text-gray-500">
                <span>AXOLOTITO_ID:</span>
                <span className="text-gray-300">#4728 (Nature: Suertudo)</span>
              </div>
              <div className="flex justify-between py-1 text-gray-400">
                <span>Rondas completadas:</span>
                <span className="text-white">18 de 20</span>
              </div>
              <div className="flex justify-between py-1 text-gray-400">
                <span>Patrones completados:</span>
                <span className="text-emerald-400">3 Lín. / 1 Tab. Llena</span>
              </div>
              <div className="flex justify-between py-1 text-gray-400">
                <span>Experiencia de compañero:</span>
                <span className="text-cyan-300">+180 XP</span>
              </div>
              <div className="flex justify-between py-1 text-gray-400">
                <span>Fragmentos cosméticos:</span>
                <span className="text-purple-300">4 descubiertos</span>
              </div>
              <div className="flex justify-between border-t border-white/5 pt-2.5 font-bold text-sm">
                <span className="text-gray-300">Nivel de vínculo:</span>
                <span className="text-[#FF8DA1]">7 · Amistoso</span>
              </div>
            </div>
            
            <div className="mt-6 flex flex-col gap-2">
              <div className="w-full py-3 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 rounded-xl text-center font-black text-xs text-emerald-300 flex items-center justify-center gap-1.5 cursor-default">
                <Heart size={14} className="animate-pulse" /> ¡Gracias por el esfuerzo! ❤️
              </div>
              <p className="text-[10px] text-center text-gray-500 leading-normal">
                Al terminar, el progreso se guarda en tu perfil y el Axolotito descansa para recuperar energía. No se genera un saldo retirable.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Modos gratuitos y hoja de ruta de creadores */}
      <section className="py-24 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl sm:text-5xl font-black">Modos gratuitos y comunidad</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Practica, compite y crea sin cuotas de entrada. Los resultados sirven para clasificación y progreso interno.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-6 hover:border-white/10 transition-all flex flex-col justify-between">
              <div>
                <span className="inline-block px-2.5 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-4">Sala Inicial</span>
                <h3 className="font-black text-xl mb-2 text-white">Charco de Novatos</h3>
                <p className="text-gray-400 text-xs leading-relaxed mb-6">Perfecto para principiantes. Aprende las reglas, entrena a tus Axolotitos y prueba distintas composiciones sin arriesgar créditos.</p>
              </div>
              <div className="border-t border-white/5 pt-4">
                <div className="flex justify-between items-center text-xs text-gray-400 font-bold">
                  <span>Acceso:</span>
                  <span className="text-emerald-400">Gratis</span>
                </div>
              </div>
            </div>

            <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-6 hover:border-white/10 transition-all flex flex-col justify-between">
              <div>
                <span className="inline-block px-2.5 py-0.5 bg-red-500/10 border border-red-500/20 rounded-full text-red-400 text-[10px] font-bold uppercase tracking-wider mb-4">Sala Competitiva</span>
                <h3 className="font-black text-xl mb-2 text-white">Fosa del Campeón</h3>
                <p className="text-gray-400 text-xs leading-relaxed mb-6">Para jugadores experimentados. Usa tableros avanzados y coordina atributos para mejorar tu posición en la clasificación.</p>
              </div>
              <div className="border-t border-white/5 pt-4">
                <div className="flex justify-between items-center text-xs text-gray-400 font-bold">
                  <span>Acceso:</span>
                  <span className="text-[#FF8DA1]">Gratis</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500/10 to-transparent border border-yellow-500/35 rounded-3xl p-6 shadow-[0_0_30px_rgba(234,179,8,0.06)] flex flex-col justify-between hover:border-yellow-500/50 transition-all">
              <div>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-yellow-500/20 border border-yellow-500/40 rounded-full text-yellow-400 text-[10px] font-bold uppercase tracking-wider mb-4"><Users size={10} /> Hoja de ruta</span>
                <h3 className="font-black text-xl mb-2 text-yellow-400">Mercado de Creadores</h3>
                <p className="text-gray-300 text-xs leading-relaxed mb-6">Función futura en evaluación para que creadores adultos verificados publiquen artículos digitales revisados, con precio fijo y contenido conocido.</p>
              </div>
              <div className="border-t border-yellow-500/15 pt-4">
                <div className="flex justify-between items-center text-xs text-yellow-200 font-bold">
                  <span>Estado:</span>
                  <span className="text-yellow-400 text-sm font-black">No disponible</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Colecciones cosméticas de precio fijo */}
      <section className="py-24 px-6 bg-gradient-to-b from-transparent via-purple-950/10 to-transparent border-y border-white/5 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl sm:text-5xl font-black">Colecciones de personalización</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Cuando el catálogo se habilite, cada ficha mostrará el precio fijo, contenido y duración antes de confirmar. Nunca habrá contenido comprado al azar.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                tier: 'Coral',
                price: '100 AXF · PRECIO FIJO',
                color: 'border-pink-500/20 bg-pink-500/[0.02] text-pink-300 hover:border-pink-500/40',
                benefits: ['Paleta Coral para el perfil', 'Marco de avatar Coral', 'Paquete de 5 stickers identificados']
              },
              {
                tier: 'Dorado',
                price: '250 AXF · PRECIO FIJO',
                color: 'border-yellow-500/30 bg-yellow-500/[0.02] text-yellow-300 hover:border-yellow-500/50 shadow-[0_0_25px_rgba(234,179,8,0.05)]',
                benefits: ['Tema Dorado para el perfil', 'Marco y placa Dorada', 'Paquete de 8 stickers identificados', '2 emotes cosméticos']
              },
              {
                tier: 'Axolite',
                price: '500 AXF · PRECIO FIJO',
                color: 'border-purple-500/35 bg-purple-500/[0.03] text-purple-300 hover:border-purple-500/50 shadow-[0_0_35px_rgba(168,85,247,0.08)]',
                benefits: ['Tema Axolite para el perfil', 'Marco y placa Axolite', 'Paquete de 12 stickers identificados', '4 emotes cosméticos', 'Decoración de cueva Axolite']
              }
            ].map((club, idx) => (
              <div
                key={idx}
                className={`border rounded-3xl p-8 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between ${club.color}`}
              >
                <div>
                  <h3 className="font-black text-2xl mb-1 tracking-tight text-white">{club.tier}</h3>
                  <div className="text-sm font-black mb-6 uppercase tracking-wider">{club.price}</div>
                  
                  <ul className="space-y-3.5 text-xs text-gray-300">
                    {club.benefits.map((benefit, bIdx) => (
                      <li key={bIdx} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-white/40 shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="mt-8 pt-4 border-t border-white/5">
                  <span className="block text-center text-xs text-gray-500 uppercase tracking-widest font-bold">Contenido fijo · sin azar · catálogo aún no habilitado</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* LOGIN CTA */}
      <section className="py-16 px-6 max-w-lg mx-auto text-center relative z-10">
        <div className="bg-gradient-to-br from-[#E4007C]/15 to-purple-900/10 border border-[#E4007C]/30 rounded-3xl p-8 sm:p-12 shadow-[0_0_50px_rgba(228,0,124,0.15)] backdrop-blur-md">
          <div className="w-20 h-20 bg-[#E4007C]/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-[#E4007C]/30">
            <span className="text-5xl animate-pulse">🦎</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black mb-4 tracking-tight">¿Listo para comenzar?</h2>
          <p className="text-gray-300 text-sm leading-relaxed mb-8">
            Entra, completa el tutorial gratuito y recibe un Webito de prueba para comenzar tu colección. No necesitas comprar créditos ni artículos.
          </p>
          <button
            onClick={() => handleOpenPanel('join')}
            disabled={!ready}
            className="w-full py-4.5 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_40px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed text-white flex items-center justify-center gap-2"
          >
            {ready ? (
              <>¡Jugar Gratis Ahora! <ArrowRight size={18} /></>
            ) : (
              'Cargando protocolo...'
            )}
          </button>
          <p className="text-gray-500 text-xs mt-5 font-medium">
            Google · Apple · Email — Sin wallet, tarjeta ni compra inicial
          </p>
        </div>
      </section>

      {/* Code Redemption CTA (Corcholata) */}
      <section id="canjear" className="py-24 px-6 relative z-10">
        <div className="max-w-md mx-auto">
          <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-8 sm:p-10 text-center backdrop-blur-md shadow-2xl">
            <div className="mb-8">
              <div className="w-14 h-14 bg-purple-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-purple-500/25">
                <Gift className="w-7 h-7 text-purple-400" />
              </div>
              <h2 className="text-2xl sm:text-3xl font-black mb-3 tracking-tight">Regalo de Corcholata</h2>
              <p className="text-gray-400 text-sm leading-relaxed">
                {codeFromUrl
                  ? 'Tienes un código promocional enlazado. Inicia sesión para ver su contenido interno antes de canjearlo.'
                  : 'Si tienes un código promocional único de nuestras corcholatas físicas, canjéalo aquí para recibir un kit de inicio de uso exclusivo dentro del juego.'}
              </p>
            </div>

            <button
              onClick={() => handleOpenPanel('redeem')}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 rounded-full font-black text-base shadow-[0_0_30px_rgba(168,85,247,0.4)] transition-all transform hover:scale-105 active:scale-95 text-white"
            >
              Ingresar código promocional
            </button>

            {!codeFromUrl && (
              <p className="text-center text-gray-500 text-xs mt-6 font-medium">
                ¿No tienes una corcholata? Síguenos en redes sociales o visítanos en ferias de tecnología para conseguir la tuya.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 border-t border-white/5 text-center bg-[#050509]/80 relative z-10">
        <div className="max-w-5xl mx-auto space-y-4">
          <h2 className="text-2xl font-black text-[#FF8DA1] tracking-tighter">AXOLOTTO</h2>
          <p className="text-gray-500 text-sm">© 2026 axolot.to · Juego social gratuito de colección y creatividad</p>
          <div className="flex justify-center gap-6 text-xs text-gray-600 font-medium">
            <span className="hover:text-gray-400 cursor-pointer">Términos de Servicio</span>
            <span className="hover:text-gray-400 cursor-pointer">Política de Privacidad</span>
            <span className="hover:text-gray-400 cursor-pointer">Auditoría de Smart Contracts</span>
          </div>
        </div>
      </footer>

      {/* Modal CodeEntryPanel */}
      <CodeEntryPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        mode={panelMode}
      />
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
