"use client";

/** Three slow-drifting light blobs that give the screen atmosphere */
export default function WorldOrbs() {
  return (
    <div aria-hidden="true">
      <div
        className="world-orb w-[600px] h-[600px] bg-[radial-gradient(circle,rgba(228,0,124,0.12)_0%,transparent_70%)]"
        style={{ top: '-9rem', left: '-9rem', animation: 'orb-drift-1 20s ease-in-out infinite' }}
      />
      <div
        className="world-orb w-[500px] h-[500px] bg-[radial-gradient(circle,rgba(6,182,212,0.10)_0%,transparent_70%)]"
        style={{ bottom: '-6rem', right: '-6rem', animation: 'orb-drift-2 26s ease-in-out infinite' }}
      />
      <div
        className="world-orb w-[400px] h-[400px] bg-[radial-gradient(circle,rgba(147,51,234,0.08)_0%,transparent_70%)]"
        style={{ top: '40%', left: '55%', animation: 'orb-drift-3 32s ease-in-out infinite' }}
      />
    </div>
  );
}
