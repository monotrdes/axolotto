"use client";

/**
 * TutorialResetButton — Dev-only overlay badge.
 *
 * Visible when NEXT_PUBLIC_DEV_TOOLS=true in .env.local.
 * Sections:
 *   - Reset Tutorial: resets the authenticated user's tutorial state.
 *   - Multiplayer: fills a waiting room with mock players for testing.
 */

import { useState } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { API_BASE } from "@/lib/api";

interface Props {
  onReset?: () => void;
}

const DEV_TOOLS = process.env.NEXT_PUBLIC_DEV_TOOLS === "true";

export default function TutorialResetButton({ onReset }: Props) {
  if (!DEV_TOOLS) return null;

  const { getAccessToken, authenticated } = usePrivy();
  const [open, setOpen]           = useState(false);
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState<string | null>(null);
  const [deleteAxo, setDeleteAxo] = useState(false);

  // Multiplayer section state
  const [mpLoading, setMpLoading]   = useState(false);
  const [mpResult, setMpResult]     = useState<string | null>(null);
  const [mpRoomType, setMpRoomType] = useState<"rookie_pool" | "champion_abyss">("rookie_pool");
  const [mpCount, setMpCount]       = useState(3);
  const [mpAxfAmount, setMpAxfAmount] = useState(0);
  const [mpFrjAmount, setMpFrjAmount] = useState(10000);

  const handleReset = async () => {
    if (!authenticated) {
      setResult("⚠️ Necesitas iniciar sesión primero");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const token = await getAccessToken();
      const res = await fetch(
        `${API_BASE}/dev/reset-tutorial?delete_axolotito=${deleteAxo}`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      const data = await res.json();
      if (res.ok) {
        setResult(`✅ ${data.message}`);
        setTimeout(() => {
          if (onReset) {
            localStorage.setItem('dev_show_reward', '1');
            window.location.href = '/?show_reward=1';
          } else {
            window.location.reload();
          }
        }, 1200);
      } else {
        setResult(`❌ ${data.detail || "Error desconocido"}`);
      }
    } catch {
      setResult("❌ Error de red");
    } finally {
      setLoading(false);
    }
  };

  const handleFillRoom = async () => {
    setMpLoading(true);
    setMpResult(null);
    try {
      const token = await getAccessToken();
      const res = await fetch(
        `${API_BASE}/dev/fill-multiplayer-rooms?room_type=${mpRoomType}&count=${mpCount}&axf_amount=${mpAxfAmount}&frj_amount=${mpFrjAmount}`,
        {
          method: "POST",
          headers: {
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            "X-Dev-User": "admin",
          },
        }
      );
      const data = await res.json();
      if (res.ok) {
        const inscribed = (data.actions as string[]).filter((a: string) => a.includes("inscrito")).length;
        setMpResult(`✅ ${inscribed} mock(s) en sala. Únete para iniciar.`);
      } else {
        setMpResult(`❌ ${data.detail || "Error"}`);
      }
    } catch {
      setMpResult("❌ Error de red");
    } finally {
      setMpLoading(false);
    }
  };

  const panelStyle: React.CSSProperties = {
    position: "fixed",
    bottom: 52,
    right: 16,
    zIndex: 9998,
    background: "#0f0505",
    border: "1px solid #7f1d1d",
    borderRadius: "14px",
    padding: "14px 16px",
    fontSize: "11px",
    color: "#fca5a5",
    width: "250px",
    boxShadow: "0 4px 24px rgba(0,0,0,0.7)",
  };

  const btnStyle = (disabled: boolean): React.CSSProperties => ({
    width: "100%",
    padding: "7px",
    background: disabled ? "#1a0808" : "#7f1d1d",
    border: "1px solid #991b1b",
    borderRadius: "8px",
    color: disabled ? "#4b1111" : "#fca5a5",
    fontWeight: "bold",
    fontSize: "11px",
    cursor: disabled ? "not-allowed" : "pointer",
    letterSpacing: "0.05em",
  });

  const selectStyle: React.CSSProperties = {
    width: "100%",
    padding: "5px",
    background: "#1a0808",
    border: "1px solid #7f1d1d",
    borderRadius: "6px",
    color: "#fca5a5",
    fontSize: "11px",
    marginBottom: "6px",
    cursor: "pointer",
  };

  const dividerStyle: React.CSSProperties = {
    borderTop: "1px solid #3f0e0e",
    margin: "10px 0",
  };

  return (
    <>
      {/* Floating trigger pill */}
      <button
        onClick={() => setOpen(o => !o)}
        title="Dev Tools"
        style={{
          position: "fixed",
          bottom: 16,
          right: 16,
          zIndex: 9999,
          background: "#1a0808",
          border: "1px solid #7f1d1d",
          borderRadius: "20px",
          padding: "6px 12px",
          fontSize: "11px",
          fontWeight: "bold",
          color: "#f87171",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: "5px",
          boxShadow: "0 2px 12px rgba(0,0,0,0.5)",
          letterSpacing: "0.05em",
        }}
      >
        🛠️ DEV
      </button>

      {/* Panel */}
      {open && (
        <div style={panelStyle}>
          {/* ── Reset Tutorial ── */}
          <p style={{ fontWeight: 900, fontSize: "12px", marginBottom: "10px", color: "#f87171" }}>
            🛠️ DEV — Reset Tutorial
          </p>

          {!authenticated && (
            <p style={{ color: "#fb923c", marginBottom: "8px", fontSize: "10px" }}>
              ⚠️ Inicia sesión para poder resetear
            </p>
          )}

          <label style={{ display: "flex", alignItems: "center", gap: "7px", marginBottom: "10px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={deleteAxo}
              onChange={e => setDeleteAxo(e.target.checked)}
            />
            <span>Eliminar Axolotito nacido</span>
          </label>

          <button
            onClick={handleReset}
            disabled={loading || !authenticated}
            style={btnStyle(loading || !authenticated)}
          >
            {loading ? "Reseteando..." : "🔄 Reset Tutorial"}
          </button>

          {result && (
            <p style={{ marginTop: "8px", fontSize: "10px", lineHeight: 1.5, color: result.startsWith("✅") ? "#4ade80" : "#f87171" }}>
              {result}
            </p>
          )}

          {/* ── Multiplayer Testing ── */}
          <div style={dividerStyle} />

          <p style={{ fontWeight: 900, fontSize: "12px", marginBottom: "8px", color: "#f87171" }}>
            🎮 Llenar Sala Multijugador
          </p>

          <label style={{ fontSize: "10px", color: "#fca5a5", display: "block", marginBottom: "4px" }}>
            Sala
          </label>
          <select
            value={mpRoomType}
            onChange={e => setMpRoomType(e.target.value as "rookie_pool" | "champion_abyss")}
            style={selectStyle}
          >
            <option value="rookie_pool">Charco de Novatos (10 FRJ)</option>
            <option value="champion_abyss">Fosa del Campeón (50 FRJ)</option>
          </select>

          <label style={{ fontSize: "10px", color: "#fca5a5", display: "block", marginBottom: "4px" }}>
            Jugadores mock: {mpCount}
          </label>
          <input
            type="range"
            min={1}
            max={5}
            value={mpCount}
            onChange={e => setMpCount(Number(e.target.value))}
            style={{ width: "100%", marginBottom: "8px", accentColor: "#f87171" }}
          />

          <div style={{ display: "flex", gap: "6px", marginBottom: "8px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: "10px", color: "#fca5a5", display: "block", marginBottom: "3px" }}>
                AXF por mock
              </label>
              <input
                type="number"
                min={0}
                step={100}
                value={mpAxfAmount}
                onChange={e => setMpAxfAmount(Number(e.target.value))}
                style={{
                  width: "100%",
                  padding: "4px 6px",
                  background: "#1a0808",
                  border: "1px solid #7f1d1d",
                  borderRadius: "6px",
                  color: "#fca5a5",
                  fontSize: "11px",
                }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: "10px", color: "#fca5a5", display: "block", marginBottom: "3px" }}>
                FRJ por mock
              </label>
              <input
                type="number"
                min={0}
                step={500}
                value={mpFrjAmount}
                onChange={e => setMpFrjAmount(Number(e.target.value))}
                style={{
                  width: "100%",
                  padding: "4px 6px",
                  background: "#1a0808",
                  border: "1px solid #7f1d1d",
                  borderRadius: "6px",
                  color: "#fca5a5",
                  fontSize: "11px",
                }}
              />
            </div>
          </div>

          <button
            onClick={handleFillRoom}
            disabled={mpLoading}
            style={btnStyle(mpLoading)}
          >
            {mpLoading ? "Inscribiendo mocks..." : `👾 Llenar con ${mpCount} mock(s)`}
          </button>

          {mpResult && (
            <p style={{ marginTop: "8px", fontSize: "10px", lineHeight: 1.5, color: mpResult.startsWith("✅") ? "#4ade80" : "#f87171" }}>
              {mpResult}
            </p>
          )}
        </div>
      )}
    </>
  );
}
