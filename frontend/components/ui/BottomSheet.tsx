"use client";

import React from 'react';
import { createPortal } from 'react-dom';

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  accent?: string;
}

export default function BottomSheet({ open, onClose, children, title, accent }: BottomSheetProps) {
  if (!open) return null;

  const content = (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm pointer-events-auto"
        onClick={onClose}
      />
      {/* Panel */}
      <div className="fixed bottom-0 left-0 right-0 w-full max-w-lg mx-auto animate-sheet-up max-h-[85dvh] flex flex-col bg-[#0D0D1F] rounded-t-[2rem]"
        style={accent ? { borderTop: `2px solid ${accent}` } : undefined}
      >
        {/* Handle bar */}
        <div className="w-10 h-1 bg-white/20 rounded-full mx-auto mt-3 mb-0 shrink-0" />
        {/* Optional title */}
        {title && (
          <div className="px-6 pt-4 pb-0 text-sm font-black uppercase tracking-widest text-slate-400 shrink-0">
            {title}
          </div>
        )}
        {/* Scrollable body */}
        <div className="flex-1 min-h-0 overflow-y-auto scrollbar-hide">
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}
