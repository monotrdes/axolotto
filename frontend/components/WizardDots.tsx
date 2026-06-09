"use client";

import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface WizardDotsProps {
  steps: string[];
  current: number; // 0-based
  onBack: () => void;
}

export default function WizardDots({ steps, current, onBack }: WizardDotsProps) {
  return (
    <div className="flex items-center gap-2 mb-5">
      <button
        onClick={onBack}
        className="p-2 rounded-full bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-all shrink-0"
        aria-label="Volver"
      >
        <ArrowLeft size={15} />
      </button>

      <div className="flex items-center flex-1 justify-center gap-1">
        {steps.map((label, i) => {
          const isDone   = i < current;
          const isActive = i === current;
          return (
            <React.Fragment key={i}>
              <div className="flex flex-col items-center gap-1 min-w-[32px]">
                <div
                  className={`rounded-full transition-all duration-300 ${
                    isActive
                      ? 'w-3.5 h-3.5 bg-[var(--brand-hot)] shadow-[0_0_8px_var(--brand-glow)] animate-pulse'
                      : isDone
                        ? 'w-2.5 h-2.5 bg-emerald-500'
                        : 'w-2 h-2 bg-slate-700'
                  }`}
                />
                <span
                  className={`text-[9px] font-bold uppercase tracking-wider hidden sm:block transition-colors ${
                    isActive ? 'text-white' : isDone ? 'text-emerald-400' : 'text-slate-600'
                  }`}
                >
                  {label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`flex-1 h-px mb-4 max-w-12 transition-colors ${
                    isDone ? 'bg-emerald-500/40' : 'bg-slate-800'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
