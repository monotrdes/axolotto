"use client";

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import LoteriaCard from './LoteriaCard';

interface UnboxingModalProps {
  open: boolean;
  onClose: (tabDestino?: string) => void;
  pack: any; // Objeto del sobre / booster
  cards: any[]; // 7 cartas obtenidas en total
  txHash?: string;
  ownedCardIds?: Set<number>; // Conjunto de IDs de cartas que el usuario ya poseía
}

const getThemeStyles = (theme: string) => {
  switch (theme) {
    case 'fiesta':
      return {
        accentColor: '#E4007C',
        gradient: 'from-pink-500 via-[#E4007C] to-yellow-500',
        borderColor: 'border-yellow-450',
        glowColor: 'rgba(228, 0, 124, 0.4)',
        packLabel: 'Booster Fiesta 🎉',
        cardBackGradient: 'from-[#E4007C] via-purple-950 to-amber-950/40',
        cardBackBorder: 'border-yellow-400/80',
        cardBackSymbol: '🎉',
        modalBorder: 'border-pink-500/50',
        modalGlow: 'shadow-[0_0_60px_rgba(228,0,124,0.3)]',
        titleText: 'text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-[#E4007C] to-yellow-400',
      };
    case 'nido':
      return {
        accentColor: '#10B981',
        gradient: 'from-emerald-500 via-teal-600 to-green-700',
        borderColor: 'border-emerald-400',
        glowColor: 'rgba(16, 185, 129, 0.4)',
        packLabel: 'Booster Nido 🌿',
        cardBackGradient: 'from-emerald-950 via-slate-900 to-green-950/40',
        cardBackBorder: 'border-emerald-400/80',
        cardBackSymbol: '🌿',
        modalBorder: 'border-emerald-500/50',
        modalGlow: 'shadow-[0_0_60px_rgba(16,185,129,0.3)]',
        titleText: 'text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-500 to-green-400',
      };
    case 'cosmos':
      return {
        accentColor: '#818CF8',
        gradient: 'from-indigo-950 via-purple-900 to-indigo-900',
        borderColor: 'border-purple-400',
        glowColor: 'rgba(129, 140, 248, 0.4)',
        packLabel: 'Booster Cosmos 🌌',
        cardBackGradient: 'from-indigo-950 via-slate-900 to-purple-950/40',
        cardBackBorder: 'border-purple-400/80',
        cardBackSymbol: '🌌',
        modalBorder: 'border-indigo-500/50',
        modalGlow: 'shadow-[0_0_60px_rgba(129,140,248,0.3)]',
        titleText: 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-450 to-pink-500',
      };
    case 'foil':
      return {
        accentColor: '#F59E0B',
        gradient: 'from-amber-400 via-fuchsia-500 to-purple-600',
        borderColor: 'border-amber-400',
        glowColor: 'rgba(245, 158, 11, 0.5)',
        packLabel: 'Booster Brillante ✨',
        cardBackGradient: 'from-amber-950 via-slate-900 to-fuchsia-950/40',
        cardBackBorder: 'border-amber-400/80',
        cardBackSymbol: '✨',
        modalBorder: 'border-amber-400/70',
        modalGlow: 'shadow-[0_0_80px_rgba(245,158,11,0.4)]',
        titleText: 'text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-pink-500 to-purple-500 font-extrabold animate-pulse',
      };
    case 'pure':
    default:
      return {
        accentColor: '#9333EA',
        gradient: 'from-slate-700 via-slate-800 to-slate-900',
        borderColor: 'border-slate-500',
        glowColor: 'rgba(148, 163, 184, 0.3)',
        packLabel: 'Booster Mezclado 🃏',
        cardBackGradient: 'from-slate-950 via-slate-900 to-slate-900',
        cardBackBorder: 'border-slate-700',
        cardBackSymbol: '🃏',
        modalBorder: 'border-purple-500/50',
        modalGlow: 'shadow-[0_0_60px_rgba(168,85,247,0.3)]',
        titleText: 'text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-[#E4007C] to-pink-500',
      };
  }
};

interface TearCanvasProps {
  theme: string;
  themeStyles: any;
  onTearComplete: () => void;
}

function TearCanvas({ theme, themeStyles, onTearComplete }: TearCanvasProps) {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const [dragX, setDragX] = React.useState(30);
  const [isDragging, setIsDragging] = React.useState(false);
  const [tearProgress, setTearProgress] = React.useState(0);

  // For the split animation
  const [isAnimatingOut, setIsAnimatingOut] = React.useState(false);
  const animProgressRef = React.useRef(0);

  // Sparks/confetti particles at the tear point
  const particlesRef = React.useRef<Array<{ x: number; y: number; vx: number; vy: number; color: string; size: number; alpha: number; life: number }>>([]);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let active = true;

    const render = () => {
      if (!active) return;

      // Update particles
      for (let i = particlesRef.current.length - 1; i >= 0; i--) {
        const p = particlesRef.current[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.15; // gravity
        p.alpha -= 0.02;
        p.life -= 1;
        if (p.life <= 0 || p.alpha <= 0) {
          particlesRef.current.splice(i, 1);
        }
      }

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const W = canvas.width;
      const H = canvas.height;
      const packX = 30;
      const packY = 40;
      const packW = W - 60;
      const packH = H - 80;
      const tearY = 120; // Y coordinate where the tear occurs

      // Render top and bottom parts with offsets if animating out
      let topYOffset = 0;
      let topXOffset = 0;
      let topRot = 0;
      let bottomYOffset = 0;
      let bottomXOffset = 0;
      let bottomRot = 0;
      let globalAlpha = 1;

      if (isAnimatingOut) {
        animProgressRef.current += 0.04;
        const p = animProgressRef.current;
        if (p >= 1) {
          active = false;
          onTearComplete();
          return;
        }

        // Ease out formulas
        const ease = 1 - Math.pow(1 - p, 3); // cubic ease out
        topYOffset = -ease * 120;
        topXOffset = -ease * 20;
        topRot = -ease * 0.15;

        bottomYOffset = ease * 180;
        bottomXOffset = ease * 10;
        bottomRot = ease * 0.08;
        globalAlpha = 1 - p;
      }

      const drawPackContent = (c: CanvasRenderingContext2D) => {
        // Background Gradient
        const grad = c.createLinearGradient(packX, packY, packX, packY + packH);
        if (theme === 'fiesta') {
          grad.addColorStop(0, '#ec4899');
          grad.addColorStop(0.5, '#E4007C');
          grad.addColorStop(1, '#eab308');
        } else if (theme === 'nido') {
          grad.addColorStop(0, '#10b981');
          grad.addColorStop(0.5, '#0d9488');
          grad.addColorStop(1, '#15803d');
        } else if (theme === 'cosmos') {
          grad.addColorStop(0, '#1e1b4b');
          grad.addColorStop(0.5, '#581c87');
          grad.addColorStop(1, '#312e81');
        } else if (theme === 'foil') {
          grad.addColorStop(0, '#fbbf24');
          grad.addColorStop(0.5, '#d946ef');
          grad.addColorStop(1, '#9333ea');
        } else {
          grad.addColorStop(0, '#334155');
          grad.addColorStop(0.5, '#1e293b');
          grad.addColorStop(1, '#0f172a');
        }

        c.fillStyle = grad;
        // Draw main pack body
        c.beginPath();
        if (typeof (c as any).roundRect === 'function') {
          (c as any).roundRect(packX, packY, packW, packH, 20);
        } else {
          const radius = 20;
          c.moveTo(packX + radius, packY);
          c.lineTo(packX + packW - radius, packY);
          c.quadraticCurveTo(packX + packW, packY, packX + packW, packY + radius);
          c.lineTo(packX + packW, packY + packH - radius);
          c.quadraticCurveTo(packX + packW, packY + packH, packX + packW - radius, packY + packH);
          c.lineTo(packX + radius, packY + packH);
          c.quadraticCurveTo(packX, packY + packH, packX, packY + packH - radius);
          c.lineTo(packX, packY + radius);
          c.quadraticCurveTo(packX, packY, packX + radius, packY);
        }
        c.fill();

        // Border
        c.lineWidth = 4;
        c.strokeStyle = themeStyles.accentColor || '#E4007C';
        c.stroke();

        // Foil shines/decorations
        c.fillStyle = 'rgba(255, 255, 255, 0.05)';
        c.beginPath();
        c.ellipse(packX + packW/2, packY + packH/2, packW * 0.7, packH * 0.25, Math.PI / 4, 0, Math.PI * 2);
        c.fill();

        // Symbol Emoji
        c.font = '72px Arial';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillStyle = '#fff';
        c.fillText(themeStyles.cardBackSymbol || '🃏', packX + packW/2, packY + packH/2 + 10);

        // Pack Title
        c.font = 'bold 16px Arial';
        c.fillStyle = '#fff';
        c.fillText(themeStyles.packLabel ? themeStyles.packLabel.split(' ')[0] : 'BOOSTER', packX + packW/2, packY + packH - 45);

        c.font = 'bold 8px Arial';
        c.fillStyle = 'rgba(255, 255, 255, 0.6)';
        c.fillText('7 CARTAS • AXOLOTTO 2.0', packX + packW/2, packY + packH - 25);
      };

      // Draw Top Piece
      ctx.save();
      ctx.globalAlpha = globalAlpha;
      ctx.translate(W/2 + topXOffset, tearY + topYOffset);
      ctx.rotate(topRot);
      ctx.translate(-W/2, -tearY);
      // Clip mask for top half
      ctx.beginPath();
      ctx.rect(0, 0, W, tearY);
      ctx.clip();
      drawPackContent(ctx);

      // Draw wavy tear edge at the bottom of top piece
      if (dragX > packX) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(packX, tearY);
        for (let x = packX; x <= Math.min(dragX, packX + packW); x += 5) {
          const dy = Math.sin(x * 0.3) * 2;
          ctx.lineTo(x, tearY + dy);
        }
        ctx.stroke();
      }
      ctx.restore();

      // Draw Bottom Piece
      ctx.save();
      ctx.globalAlpha = globalAlpha;
      ctx.translate(W/2 + bottomXOffset, tearY + bottomYOffset);
      ctx.rotate(bottomRot);
      ctx.translate(-W/2, -tearY);
      // Clip mask for bottom half
      ctx.beginPath();
      ctx.rect(0, tearY, W, H - tearY);
      ctx.clip();
      drawPackContent(ctx);

      // Draw wavy tear edge at the top of bottom piece
      if (dragX > packX) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(packX, tearY);
        for (let x = packX; x <= Math.min(dragX, packX + packW); x += 5) {
          const dy = Math.sin(x * 0.3) * 2;
          ctx.lineTo(x, tearY + dy);
        }
        ctx.stroke();
      }
      ctx.restore();

      // Draw Tear Guide Line & Swipe Target (only if not animating out)
      if (!isAnimatingOut) {
        ctx.save();
        // Dashed line
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(packX, tearY);
        ctx.lineTo(packX + packW, tearY);
        ctx.stroke();

        const pulse = 1 + Math.sin(Date.now() * 0.015) * 0.12;
        const dragLimitLeft = packX;

        // Draw progress trail
        if (dragX > dragLimitLeft) {
          ctx.strokeStyle = themeStyles.accentColor || '#E4007C';
          ctx.lineWidth = 4;
          ctx.setLineDash([]);
          ctx.beginPath();
          ctx.moveTo(dragLimitLeft, tearY);
          ctx.lineTo(dragX, tearY);
          ctx.stroke();
        }

        // Draw swipe handler handle (glowing circle + scissor emoji)
        ctx.shadowColor = themeStyles.accentColor || '#E4007C';
        ctx.shadowBlur = 12 * pulse;
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(dragX, tearY, 15 * pulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        ctx.font = '12px Arial';
        ctx.fillStyle = '#000';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('✂️', dragX, tearY);

        // Help text if not dragged much
        if (tearProgress < 0.2) {
          ctx.font = 'bold 11px Arial';
          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          ctx.fillText('ARRANCA EL SOBRE AQUÍ ➔', W / 2, tearY - 26);
        }
        ctx.restore();
      }

      // Draw sparks/particles
      ctx.save();
      particlesRef.current.forEach((p) => {
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.restore();

      requestAnimationFrame(render);
    };

    const handleId = requestAnimationFrame(render);
    return () => {
      active = false;
      cancelAnimationFrame(handleId);
    };
  }, [dragX, isDragging, tearProgress, isAnimatingOut, theme, themeStyles]);

  const handleStart = (clientX: number, clientY: number) => {
    if (isAnimatingOut) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    const tearY = 120;

    // Check if clicked near the current dragX and tearY
    const dx = x - dragX;
    const dy = y - tearY;
    if (Math.abs(dx) < 35 && Math.abs(dy) < 35) {
      setIsDragging(true);
    }
  };

  const handleMove = (clientX: number, clientY: number) => {
    if (!isDragging || isAnimatingOut) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    const W = canvas.width;
    const packX = 30;
    const packW = W - 60;
    const tearY = 120;

    // Constrain x to pack boundary
    const newX = Math.max(packX, Math.min(x, packX + packW));

    // Only allow dragging forward/to the right
    if (newX > dragX) {
      setDragX(newX);
      const progress = (newX - packX) / packW;
      setTearProgress(progress);

      // Spawn sparks
      const sparkColors = theme === 'foil' ? ['#fbbf24', '#f43f5e', '#fff'] : [themeStyles.accentColor, '#fff', '#ffd700'];
      for (let i = 0; i < 4; i++) {
        particlesRef.current.push({
          x: newX,
          y: tearY + (Math.random() - 0.5) * 6,
          vx: (Math.random() - 0.5) * 4 - 1.5,
          vy: -Math.random() * 3 - 0.5,
          color: sparkColors[Math.floor(Math.random() * sparkColors.length)],
          size: Math.random() * 3 + 1.5,
          alpha: 1,
          life: 30 + Math.random() * 20
        });
      }

      // Check for completion
      if (progress >= 0.95) {
        setIsDragging(false);
        setIsAnimatingOut(true);
        // Spawn massive explosion sparks
        for (let i = 0; i < 40; i++) {
          particlesRef.current.push({
            x: newX,
            y: tearY,
            vx: (Math.random() - 0.5) * 10,
            vy: -Math.random() * 8 - 2,
            color: sparkColors[Math.floor(Math.random() * sparkColors.length)],
            size: Math.random() * 5 + 2,
            alpha: 1,
            life: 40 + Math.random() * 30
          });
        }
      }
    }
  };

  const handleEnd = () => {
    setIsDragging(false);
  };

  return (
    <div className="flex flex-col items-center justify-center p-2">
      <canvas
        ref={canvasRef}
        width={300}
        height={420}
        className="touch-none mx-auto select-none bg-transparent cursor-grab active:cursor-grabbing max-w-full drop-shadow-[0_15px_30px_rgba(0,0,0,0.5)]"
        onMouseDown={(e) => handleStart(e.clientX, e.clientY)}
        onMouseMove={(e) => handleMove(e.clientX, e.clientY)}
        onMouseUp={handleEnd}
        onMouseLeave={handleEnd}
        onTouchStart={(e) => {
          if (e.touches[0]) handleStart(e.touches[0].clientX, e.touches[0].clientY);
        }}
        onTouchMove={(e) => {
          if (e.touches[0]) handleMove(e.touches[0].clientX, e.touches[0].clientY);
        }}
        onTouchEnd={handleEnd}
      />
    </div>
  );
}

export default function UnboxingModal({
  open,
  onClose,
  pack,
  cards,
  txHash,
  ownedCardIds = new Set()
}: UnboxingModalProps) {
  const [unboxingState, setUnboxingState] = useState<'pack' | 'tearing' | 'opening' | 'reveal' | 'summary'>('pack');
  const [currentRevealIndex, setCurrentRevealIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [particles, setParticles] = useState<any[]>([]);

  // Restablecer estados al abrir/cambiar de pack
  useEffect(() => {
    if (open) {
      setUnboxingState('pack');
      setCurrentRevealIndex(0);
      setIsFlipped(false);
    }
  }, [open, pack]);

  // Generar partículas temáticas
  useEffect(() => {
    if (!open || !pack) {
      setParticles([]);
      return;
    }

    if (unboxingState === 'opening' || unboxingState === 'reveal' || unboxingState === 'summary') {
      const theme = pack.item_metadata?.pack_theme || 'pure';
      const count = theme === 'foil' ? 100 : 30;
      const items = [];
      for (let i = 0; i < count; i++) {
        const size = Math.random() * 12 + 8;
        const left = Math.random() * 100;
        const delay = Math.random() * 2;
        const duration = Math.random() * 3 + 2.5;
        const drift = (Math.random() - 0.5) * 120;
        const rot = Math.random() * 720 - 360;

        let content = '✨';
        let color = '#fff';

        if (theme === 'fiesta') {
          const symbols = ['🎉', '🎈', '🎊', '✨', '💛', '💗', '🌶️', '🌮', '🎺'];
          content = symbols[Math.floor(Math.random() * symbols.length)];
          const colors = ['#ec4899', '#f43f5e', '#eab308', '#22c55e', '#3b82f6'];
          color = colors[Math.floor(Math.random() * colors.length)];
        } else if (theme === 'nido') {
          const symbols = ['🌿', '🍃', '🌱', '💚', '🍀', '🌸', '🌻'];
          content = symbols[Math.floor(Math.random() * symbols.length)];
          const colors = ['#10b981', '#34d399', '#059669', '#a7f3d0', '#fb7185'];
          color = colors[Math.floor(Math.random() * colors.length)];
        } else if (theme === 'cosmos') {
          const symbols = ['⭐', '✨', '🌌', '💜', '🌙', '☄️', '🪐', '🔮'];
          content = symbols[Math.floor(Math.random() * symbols.length)];
          const colors = ['#a78bfa', '#c084fc', '#818cf8', '#fbbf24', '#e879f9'];
          color = colors[Math.floor(Math.random() * colors.length)];
        } else if (theme === 'foil') {
          const symbols = ['✨', '🌟', '💎', '👑', '💛', '💖', '🌈', '⭐', '💫', '🔥', '💠', '🏆', '⚡', '🎆', '🔮', '🌀', '💥', '🎇'];
          content = symbols[Math.floor(Math.random() * symbols.length)];
          const colors = ['#fbbf24', '#f472b6', '#c084fc', '#60a5fa', '#34d399', '#f43f5e', '#fb923c', '#a78bfa', '#e879f9'];
          color = colors[Math.floor(Math.random() * colors.length)];
        } else {
          const symbols = ['✨', '💎', '🃏', '⚪', '🔵', '⚡'];
          content = symbols[Math.floor(Math.random() * symbols.length)];
          const colors = ['#cbd5e1', '#38bdf8', '#60a5fa', '#a855f7'];
          color = colors[Math.floor(Math.random() * colors.length)];
        }

        items.push({
          id: i,
          content,
          color,
          size,
          left,
          delay,
          duration,
          drift,
          rot
        });
      }
      setParticles(items);
    } else {
      setParticles([]);
    }
  }, [open, unboxingState, pack]);

  // Transición automática de 'opening' a 'reveal'
  useEffect(() => {
    if (!open || unboxingState !== 'opening') return;

    const timer = setTimeout(() => {
      setUnboxingState('reveal');
      setCurrentRevealIndex(0);
      setIsFlipped(false);
    }, 1500); // 1.5s de animación para la explosión del sobre

    return () => clearTimeout(timer);
  }, [open, unboxingState]);

  // Revelación automática temporizada
  useEffect(() => {
    if (!open || unboxingState !== 'reveal') return;

    let activeTimeout: NodeJS.Timeout;

    if (!isFlipped) {
      activeTimeout = setTimeout(() => {
        setIsFlipped(true);
      }, 300);
    } else {
      const isFinal = currentRevealIndex === 6;
      const displayDuration = isFinal ? 3000 : 1200;

      activeTimeout = setTimeout(() => {
        if (currentRevealIndex < 6) {
          setIsFlipped(false);
          setTimeout(() => {
            setCurrentRevealIndex(prev => prev + 1);
          }, 150);
        } else {
          setUnboxingState('summary');
        }
      }, displayDuration);
    }

    return () => clearTimeout(activeTimeout);
  }, [open, unboxingState, currentRevealIndex, isFlipped]);

  if (!open || !pack) return null;

  const theme = pack.item_metadata?.pack_theme || 'pure';
  const themeStyles = getThemeStyles(theme);

  const handleRevealClick = () => {
    if (unboxingState !== 'reveal') return;
    if (!isFlipped) {
      setIsFlipped(true);
    } else {
      if (currentRevealIndex < 6) {
        setIsFlipped(false);
        setCurrentRevealIndex(prev => prev + 1);
      } else {
        setUnboxingState('summary');
      }
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (unboxingState === 'summary') {
      if (e.target === e.currentTarget) {
        onClose();
      }
    } else if (unboxingState === 'reveal') {
      handleRevealClick();
    }
  };

  const modalContent = (
    <div
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-in fade-in duration-300 pointer-events-auto"
    >
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes booster-shake {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          10% { transform: translate(-2px, -1.5px) rotate(-1.5deg); }
          20% { transform: translate(-3px, 0px) rotate(1.5deg); }
          30% { transform: translate(0px, 2px) rotate(0deg); }
          40% { transform: translate(2px, -1px) rotate(1deg); }
          50% { transform: translate(-1px, 2px) rotate(-1deg); }
          60% { transform: translate(-3px, 1px) rotate(0deg); }
          70% { transform: translate(2px, 1.5px) rotate(-1.5deg); }
          80% { transform: translate(-1px, -1px) rotate(1deg); }
          90% { transform: translate(2px, 2px) rotate(0deg); }
        }
        @keyframes pack-explode {
          0% { transform: scale(1) rotate(0deg); filter: brightness(1); opacity: 1; }
          15% { transform: scale(1.05) rotate(-3deg); filter: brightness(1.2); }
          30% { transform: scale(0.98) rotate(3deg); filter: brightness(1.1); }
          45% { transform: scale(1.1) rotate(-2deg); filter: brightness(1.4) drop-shadow(0 0 30px rgba(168,85,247,0.8)); }
          60% { transform: scale(1.05) rotate(2deg); filter: brightness(1.3); }
          75% { transform: scale(1.15) rotate(0deg); filter: brightness(1.8) drop-shadow(0 0 45px rgba(228,0,124,0.9)); }
          100% { transform: scale(0) rotate(0deg); filter: brightness(3); opacity: 0; }
        }
        @keyframes final-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(245,158,11,0.5), inset 0 0 10px rgba(245,158,11,0.3); }
          50% { box-shadow: 0 0 40px rgba(245,158,11,0.9), 0 0 60px rgba(228,0,124,0.4), inset 0 0 20px rgba(245,158,11,0.6); }
        }
        @keyframes float-particle {
          0% { transform: translateY(30px) translateX(0) rotate(0deg); opacity: 0; }
          15% { opacity: 0.85; }
          85% { opacity: 0.85; }
          100% { transform: translateY(-380px) translateX(var(--drift-x)) rotate(var(--rot-deg)); opacity: 0; }
        }
        .animate-booster-shake { animation: booster-shake 0.4s infinite; }
        .animate-booster-hover-shake:hover { animation: booster-shake 0.2s infinite; }
        .animate-pack-explode { animation: pack-explode 1.2s forwards ease-in-out; }
        .animate-final-glow { animation: final-glow 2s infinite ease-in-out; }
        .animate-float-particle { animation: float-particle 3.5s infinite linear; }
        .perspective-1000 { perspective: 1000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
        .transition-transform-600 { transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
        .holographic-shine {
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.45) 50%, rgba(255,255,255,0) 70%);
          background-size: 200% 200%;
          animation: shine-sweep 3s infinite linear;
          pointer-events: none;
          z-index: 5;
          mix-blend-mode: overlay;
          border-radius: 0.75rem;
        }
        @keyframes shine-sweep {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        @keyframes foil-explode {
          0% { transform: scale(1) rotate(0deg); filter: brightness(1); opacity: 1; }
          10% { transform: scale(1.08) rotate(-5deg); filter: brightness(1.3); }
          25% { transform: scale(0.95) rotate(6deg); filter: brightness(1.6) drop-shadow(0 0 40px rgba(245,158,11,1)); }
          40% { transform: scale(1.18) rotate(-4deg); filter: brightness(2.2) drop-shadow(0 0 70px rgba(245,158,11,1)); }
          60% { transform: scale(1.1) rotate(3deg); filter: brightness(2) drop-shadow(0 0 90px rgba(228,0,124,1)); }
          78% { transform: scale(1.25) rotate(0deg); filter: brightness(3.5) drop-shadow(0 0 120px rgba(168,85,247,1)); }
          100% { transform: scale(0) rotate(20deg); filter: brightness(6); opacity: 0; }
        }
        @keyframes golden-ring {
          0% { transform: scale(0.2) translateX(-50%) translateY(-50%); opacity: 1; border-width: 8px; }
          40% { transform: scale(1.2) translateX(-50%) translateY(-50%); opacity: 0.9; }
          100% { transform: scale(3.5) translateX(-50%) translateY(-50%); opacity: 0; border-width: 1px; }
        }
        @keyframes card-land {
          0% { transform: translateY(-40px) scale(0.75) rotate(-8deg); opacity: 0; }
          55% { transform: translateY(5px) scale(1.06) rotate(1.5deg); opacity: 1; }
          80% { transform: translateY(-2px) scale(0.98) rotate(-0.5deg); }
          100% { transform: translateY(0) scale(1) rotate(0deg); opacity: 1; }
        }
        .animate-foil-explode { animation: foil-explode 1.5s forwards ease-in-out; }
        .animate-golden-ring { animation: golden-ring 0.9s forwards ease-out; }
        .shiny-card-bg {
          background: linear-gradient(135deg, rgba(124,58,237,0.2) 0%, rgba(219,39,119,0.2) 50%, rgba(245,158,11,0.2) 100%) !important;
          box-shadow: 0 0 25px rgba(236,72,153,0.6), inset 0 0 15px rgba(255,255,255,0.15) !important;
          border-color: #f472b6 !important;
        }
        .shiny-first-edition-card-bg {
          background: linear-gradient(135deg, rgba(245,158,11,0.25) 0%, rgba(236,72,153,0.25) 50%, rgba(99,102,241,0.25) 100%) !important;
          box-shadow: 0 0 35px rgba(245,158,11,0.8), inset 0 0 20px rgba(255,255,255,0.2) !important;
          border-color: #fbbf24 !important;
        }
      `}} />

      <div className={`border-2 ${themeStyles.modalBorder} rounded-3xl p-6 sm:p-10 max-w-4xl w-full text-center ${themeStyles.modalGlow} transform transition-all scale-100 animate-in zoom-in-95 relative overflow-hidden ${
        theme === 'foil'
          ? 'bg-gradient-to-b from-indigo-950/45 via-slate-900 to-slate-900/95 border-amber-400/80 shadow-[0_0_50px_rgba(245,158,11,0.25)]'
          : 'bg-slate-900'
      }`}>
        
        {/* Particle Overlay */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-3xl z-0">
          {particles.map((p) => (
            <div
              key={p.id}
              className="absolute bottom-0 text-center animate-float-particle select-none"
              style={{
                left: `${p.left}%`,
                fontSize: `${p.size}px`,
                color: p.color,
                animationDelay: `${p.delay}s`,
                animationDuration: `${p.duration}s`,
                '--drift-x': `${p.drift}px`,
                '--rot-deg': `${p.rot}deg`,
                opacity: 0,
              } as React.CSSProperties}
            >
              {p.content}
            </div>
          ))}
        </div>

        {/* X Close Button (Summary only) */}
        {unboxingState === 'summary' && (
          <button
            onClick={() => onClose()}
            className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors p-2 rounded-full hover:bg-slate-800/80 z-50 cursor-pointer"
          >
            <X size={20} />
          </button>
        )}

        {/* PHASE 1: PACK STATE */}
        {unboxingState === 'pack' && (
          <div className="py-6 flex flex-col items-center animate-in fade-in duration-300 relative z-10">
            <h2 className={`text-3xl sm:text-4xl font-black italic ${themeStyles.titleText} mb-2 uppercase tracking-widest animate-pulse`}>
              ¡SOBRE ADQUIRIDO!
            </h2>
            <p className="text-slate-400 text-sm mb-10">Haz clic en el sobre para abrirlo.</p>
            
            <div
              onClick={() => setUnboxingState('tearing')}
              className={`w-56 h-80 sm:w-64 sm:h-[360px] rounded-2xl bg-gradient-to-br ${themeStyles.gradient} border-4 ${themeStyles.borderColor} p-4 shadow-[0_10px_35px_${themeStyles.glowColor}] flex flex-col items-center justify-between cursor-pointer transform hover:scale-105 active:scale-95 transition-all duration-300 group relative overflow-hidden animate-booster-hover-shake animate-booster-shake`}
            >
              <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.05)_50%,transparent_75%)] bg-[length:250%_250%] group-hover:animate-[shiny-card_3s_infinite]" />
              <div className="absolute top-0 left-0 right-0 h-4 bg-black/40 border-b border-white/10 flex justify-around items-center px-2">
                <span className="w-1.5 h-1.5 rounded-full bg-pink-500 animate-ping" />
                <span className="text-[6px] text-white/70 font-black tracking-widest">AXOLOTTO ORIGINAL</span>
                <span className="w-1.5 h-1.5 rounded-full bg-pink-500" />
              </div>

              <div className="flex-1 flex flex-col items-center justify-center mt-6">
                <span className="text-7xl sm:text-8xl drop-shadow-[0_0_20px_rgba(255,255,255,0.4)] animate-bounce">{themeStyles.cardBackSymbol}</span>
                <h3 className="text-xl sm:text-2xl font-black italic text-white tracking-tighter mt-4 text-center leading-none">
                  {themeStyles.packLabel}
                </h3>
                <p className="text-[10px] text-white/80 font-black uppercase tracking-widest mt-2">7 CARTAS AL AZAR</p>
              </div>

              <div className="w-full bg-black/60 rounded-xl py-2 px-1 border border-white/5 text-center">
                <span className="text-[9px] sm:text-[11px] font-black text-white uppercase tracking-widest animate-pulse">
                  ¡ABRIR SOBRE!
                </span>
              </div>
            </div>
          </div>
        )}

        {/* PHASE 1.5: SWIPE TO TEAR */}
        {unboxingState === 'tearing' && (
          <div className="py-4 flex flex-col items-center animate-in fade-in duration-300 relative z-10">
            <h2 className={`text-2xl sm:text-3xl font-black italic ${themeStyles.titleText} mb-1 uppercase tracking-widest animate-pulse`}>
              ¡DESGARRA EL SOBRE!
            </h2>
            <p className="text-slate-400 text-xs mb-4">Desliza la tijera ✂️ de izquierda a derecha para rasgar el papel.</p>
            
            <TearCanvas
              theme={theme}
              themeStyles={themeStyles}
              onTearComplete={() => setUnboxingState('opening')}
            />
          </div>
        )}

        {/* PHASE 2: TEARING/OPENING */}
        {unboxingState === 'opening' && (
          <div className="py-20 flex flex-col items-center justify-center relative z-10">
            {theme === 'foil' && (
              <div
                className="animate-golden-ring absolute pointer-events-none rounded-full border-4 border-amber-400"
                style={{ width: '160px', height: '160px', left: '50%', top: '40%', transformOrigin: 'center' }}
              />
            )}
            <div className={`w-56 h-80 sm:w-64 sm:h-[360px] rounded-2xl bg-gradient-to-br ${themeStyles.gradient} border-4 ${themeStyles.borderColor} p-4 shadow-[0_0_50px_${themeStyles.glowColor}] flex flex-col items-center justify-between relative overflow-hidden ${
              theme === 'foil' ? 'animate-foil-explode' : 'animate-pack-explode'
            }`}>
              <span className="text-7xl sm:text-8xl my-auto animate-ping">{themeStyles.cardBackSymbol}</span>
            </div>
            <h3 className={`text-2xl font-black italic mt-8 tracking-widest uppercase animate-pulse ${
              theme === 'foil' ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-pink-500 to-purple-500' : 'text-purple-400'
            }`}>
              {theme === 'foil' ? '✨ ¡SOBRE BRILLANTE ABIERTO! ✨' : '¡Abriendo sobre...!'}
            </h3>
          </div>
        )}

        {/* PHASE 3 & 4: REVEAL AND SUMMARY */}
        {(unboxingState === 'reveal' || unboxingState === 'summary') && (
          <div className="py-2 animate-in fade-in duration-300 relative z-10">
            <h2 className={`text-2xl sm:text-4xl font-black italic ${themeStyles.titleText} mb-1 uppercase tracking-widest text-center animate-pulse`}>
              {unboxingState === 'summary'
                ? '¡SOBRE COMPLETADO!'
                : currentRevealIndex === 6
                ? '✨ ¡REVELACIÓN FINAL! ✨'
                : 'REVELANDO CARTAS...'}
            </h2>
            <p className="text-slate-400 text-xs text-center mb-6">
              {unboxingState === 'summary'
                ? 'Estas son las 7 cartas añadidas a tu colección.'
                : 'Haz clic en cualquier parte para acelerar el unboxing ⚡'}
            </p>

            <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-8 max-w-3xl mx-auto items-center pt-4">
              {cards.map((carta, index) => {
                const isNew = !ownedCardIds.has(carta.id);
                const isFinal = index === 6;

                const getFrontRarityBorder = (rarity: string) => {
                  switch (rarity) {
                    case 'Legendaria':
                      return 'border-amber-400 shadow-[0_0_25px_rgba(245,158,11,0.7)] bg-gradient-to-b from-slate-950 via-slate-900 to-amber-950/40';
                    case 'Épica':
                      return 'border-fuchsia-500 shadow-[0_0_20px_rgba(217,70,239,0.5)] bg-gradient-to-b from-slate-950 via-slate-900 to-fuchsia-950/40';
                    case 'Rara':
                      return 'border-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.5)] bg-gradient-to-b from-slate-950 via-slate-900 to-cyan-950/40';
                    case 'Poco Común':
                      return 'border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.4)] bg-gradient-to-b from-slate-950 via-slate-900 to-emerald-950/40';
                    case 'Común':
                    default:
                      return 'border-slate-700 shadow-[0_0_10px_rgba(148,163,184,0.15)] bg-gradient-to-b from-slate-950 via-slate-900 to-slate-900';
                  }
                };

                // 1. REVEALED CARDS
                if (index < currentRevealIndex || unboxingState === 'summary') {
                  const isShiny = carta.is_shiny;
                  const isFirstEd = carta.is_first_edition;
                  return (
                    <div
                      key={index}
                      style={{ animation: `card-land 0.5s ease-out ${index * 0.05}s both` }}
                      className="relative animate-in zoom-in-90"
                    >
                      {isShiny && isFirstEd && (
                        <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-400 via-pink-500 to-purple-600 text-white text-[4.5px] sm:text-[6.5px] font-black px-1.5 py-0.5 rounded-full border border-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.5)] z-30 tracking-widest uppercase animate-pulse whitespace-nowrap">
                          ✨⭐ 1st Ed. Shiny
                        </div>
                      )}
                      {!isShiny && isFirstEd && (
                        <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-900 text-[5px] sm:text-[7px] font-black px-1.5 py-0.5 rounded-full border border-amber-300 shadow-[0_0_8px_rgba(245,158,11,0.3)] z-30 tracking-widest uppercase whitespace-nowrap">
                          ⭐ 1st Edition
                        </div>
                      )}
                      {isShiny && !isFirstEd && (
                        <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[5px] sm:text-[7px] font-black px-1.5 py-0.5 rounded-full border border-pink-400 shadow-[0_0_8px_rgba(236,72,153,0.4)] z-30 tracking-widest uppercase animate-pulse whitespace-nowrap">
                          ✨ Shiny
                        </div>
                      )}
                      {!isShiny && !isFirstEd && isNew && (
                        <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-[6px] sm:text-[8px] font-black px-2 py-0.5 rounded-full border border-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.4)] z-30 animate-pulse tracking-widest">
                          NUEVA
                        </div>
                      )}

                      <LoteriaCard
                        card={carta}
                        size="lg"
                        interactive
                        isFirstEdition={isFirstEd}
                        showQty={false}
                      />
                    </div>
                  );
                }

                // 2. ACTIVE REVEALING CARD (Volteo 3D)
                if (index === currentRevealIndex && unboxingState === 'reveal') {
                  const isShiny = carta.is_shiny;
                  const isFirstEd = carta.is_first_edition;
                  return (
                    <div
                      key={index}
                      className={`relative aspect-[2/3] rounded-xl perspective-1000 transition-all duration-500 z-30 ${
                        isFinal && isFlipped
                          ? 'scale-110 sm:scale-115 -translate-y-3 rotate-1'
                          : 'scale-105 sm:scale-110 -translate-y-2'
                      }`}
                    >
                      <div className={`w-full h-full preserve-3d transition-transform-600 relative ${isFlipped ? 'rotate-y-180' : ''}`}>
                        {/* Back */}
                        <div className={`absolute inset-0 backface-hidden w-full h-full rounded-xl border-2 p-2 flex flex-col items-center justify-between shadow-2xl ${isFinal ? 'animate-final-glow border-amber-400/80 shadow-[0_0_20px_rgba(245,158,11,0.5)] bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950' : `${themeStyles.cardBackBorder} bg-gradient-to-br ${themeStyles.cardBackGradient}`}`}>
                          <div className="w-full h-full border border-white/5 rounded-lg p-1.5 flex flex-col items-center justify-between bg-black/40">
                            <span className="text-[5px] sm:text-[7px] text-white/55 font-black tracking-wider uppercase">AXOLOTTO</span>
                            <span className="text-2xl drop-shadow-md animate-pulse">{themeStyles.cardBackSymbol}</span>
                            <span className="text-[6px] sm:text-[8px] text-white/70 font-bold uppercase tracking-wider animate-pulse">
                              {isFinal ? 'ÚLTIMA' : 'Revelando'}
                            </span>
                          </div>
                        </div>

                        {/* Front */}
                        <div className={`absolute inset-0 backface-hidden rotate-y-180 w-full h-full rounded-xl border-2 p-2 flex flex-col items-center justify-between shadow-2xl ${
                          isShiny && isFirstEd ? 'shiny-first-edition-card-bg' : isShiny ? 'shiny-card-bg' : getFrontRarityBorder(carta.dynamic_rarity)
                        }`}>
                          <div className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
                            {isShiny && <div className="holographic-shine" />}
                          </div>
                          <div className="absolute inset-0 rounded-xl bg-radial-gradient from-white/5 to-transparent pointer-events-none opacity-50" />
                          
                          {isShiny && isFirstEd && (
                            <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-400 via-pink-500 to-purple-600 text-white text-[4.5px] sm:text-[6.5px] font-black px-1.5 py-0.5 rounded-full border border-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.5)] z-30 tracking-widest uppercase animate-pulse whitespace-nowrap">
                              ✨⭐ 1st Ed. Shiny
                            </div>
                          )}
                          {!isShiny && isFirstEd && (
                            <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-900 text-[5px] sm:text-[7px] font-black px-1.5 py-0.5 rounded-full border border-amber-300 shadow-[0_0_8px_rgba(245,158,11,0.3)] z-30 tracking-widest uppercase whitespace-nowrap">
                              ⭐ 1st Edition
                            </div>
                          )}
                          {isShiny && !isFirstEd && (
                            <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[5px] sm:text-[7px] font-black px-1.5 py-0.5 rounded-full border border-pink-400 shadow-[0_0_8px_rgba(236,72,153,0.4)] z-30 tracking-widest uppercase animate-pulse whitespace-nowrap">
                              ✨ Shiny
                            </div>
                          )}
                          {!isShiny && !isFirstEd && isNew && (
                            <div className="absolute -top-2.5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-[6px] sm:text-[8px] font-black px-2 py-0.5 rounded-full border border-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.4)] z-30 animate-pulse tracking-widest">
                              NUEVA
                            </div>
                          )}

                          <div className="w-full flex justify-between items-start z-10">
                            <span className="text-[8px] sm:text-[9px] font-black text-slate-500">
                              #{carta.item_metadata?.numero_loteria || "?"}
                            </span>
                            <span className="text-[5px] sm:text-[6px] font-black px-1.5 py-0.5 rounded border border-white/10 bg-white/5 uppercase text-slate-300">
                              {carta.dynamic_rarity}
                            </span>
                          </div>

                          <div className="flex-1 flex items-center justify-center my-1 z-10">
                            <span className={`text-3xl sm:text-4xl drop-shadow-md ${isShiny ? 'animate-bounce' : ''}`}>
                              {isShiny ? '✨' : '🃏'}
                            </span>
                          </div>

                          <div className="w-full bg-slate-950/95 rounded-lg py-1 px-1.5 border border-white/5 z-10">
                            <p className="text-[7px] sm:text-[8px] font-black text-center text-white uppercase tracking-wider truncate">
                              {carta.name.replace("El ", "").replace("La ", "")}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                }

                // 3. UNREVEALED CARDS
                const isFoilPack = theme === "foil";
                return (
                  <div
                    key={index}
                    className={`relative aspect-[2/3] rounded-xl border-2 p-2 flex flex-col items-center justify-between shadow-lg opacity-60 animate-in fade-in ${
                      isFoilPack
                        ? 'border-amber-500/40 bg-gradient-to-br from-amber-950/45 to-slate-900/60 shadow-[0_0_15px_rgba(245,158,11,0.1)]'
                        : 'border-slate-800/80 bg-gradient-to-br from-indigo-950/40 to-slate-900/60'
                    }`}
                  >
                    <div className={`w-full h-full border rounded-lg p-1.5 flex flex-col items-center justify-between bg-black/20 ${isFoilPack ? 'border-amber-500/10' : 'border-purple-500/5'}`}>
                      <span className={`text-[5px] sm:text-[7px] font-black tracking-wider uppercase ${isFoilPack ? 'text-amber-400/35' : 'text-purple-400/20'}`}>AXOLOTTO</span>
                      <span className={`text-xl sm:text-2xl ${isFoilPack ? 'opacity-25' : 'opacity-10'}`}>{isFoilPack ? '✨' : '🃏'}</span>
                      <span className={`text-[6px] sm:text-[7px] font-bold uppercase tracking-wider ${isFoilPack ? 'text-amber-300/20 animate-pulse' : 'text-purple-300/10'}`}>Listo</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Footer button */}
            {unboxingState === 'summary' && (
              <div className="flex flex-col gap-3 items-center justify-center animate-in fade-in duration-500">
                <button
                  onClick={() => onClose('cartas')}
                  className="px-10 py-3.5 bg-gradient-to-r from-[#E4007C] to-purple-600 hover:from-[#FF1493] hover:to-purple-500 text-white font-black rounded-xl uppercase tracking-widest text-sm transition-all shadow-lg active:scale-95 cursor-pointer"
                >
                  ¡Al Inventario!
                </button>

                {txHash && (
                  <a
                    href={`https://amoy.polygonscan.com/tx/${txHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 bg-slate-800/80 hover:bg-slate-700 text-[10px] text-slate-400 hover:text-white font-black rounded-lg transition-colors border border-slate-700/50 flex items-center gap-1 mt-1 tracking-widest uppercase"
                  >
                    🔗 Ver Tx Blockchain
                  </a>
                )}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
