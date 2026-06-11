"use client";
import { API_BASE } from "@/lib/api";





import { usePrivy } from "@privy-io/react-auth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AdminOverview from "@/components/admin/AdminOverview";
import AdminPlayerList from "@/components/admin/AdminPlayerList";
import AdminEconomyCharts from "@/components/admin/AdminEconomyCharts";
import AdminSimReport from "@/components/admin/AdminSimReport";
import AdminChaosSimV2 from "@/components/admin/AdminChaosSimV2";
import AdminCardDistribution from "@/components/admin/AdminCardDistribution";



const API = `${API_BASE}`;

type Tab = "resumen" | "jugadores" | "economia" | "cartas" | "simulacion" | "caos";
const TABS: { id: Tab; label: string; emoji: string }[] = [
  { id: "resumen",    label: "Resumen",    emoji: "📊" },
  { id: "jugadores",  label: "Jugadores",  emoji: "👥" },
  { id: "economia",   label: "Economía",   emoji: "💹" },
  { id: "cartas",     label: "Cartas",     emoji: "🃏" },
  { id: "simulacion", label: "Simulación", emoji: "🧪" },
  { id: "caos",       label: "Caos V2",    emoji: "⚡" },
];

function parsePrivyDid(token: string | null): string {
  if (!token) return "";
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub || "";
  } catch {
    return "";
  }
}

export default function AdminPage() {
  const { ready, authenticated, getAccessToken } = usePrivy();
  const router = useRouter();
  const [checking, setChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("resumen");

  useEffect(() => {
    if (!ready) return;
    if (!authenticated) {
      router.replace("/");
      return;
    }
    (async () => {
      try {
        const t = await getAccessToken();
        setToken(t);
        const userDid = parsePrivyDid(t);
        const res = await fetch(`${API}/admin/me`, {
          headers: { Authorization: `Bearer ${t}` },
        });
        const data = await res.json();
        if (!res.ok) {
          console.error("[Admin] API error:", res.status, data);
          setErrorMsg(
            `Error del servidor (${res.status}): ${data.detail || "No se pudo verificar acceso."}`
          );
          return;
        }
        if (!data.is_admin) {
          console.warn("[Admin] No es admin. Tu DID:", userDid, "Config DID:", data.configured_did || "no configurado");
          setErrorMsg(
            `No tienes acceso de administrador. Tu Privy DID no está en la lista de admins.\n\nTu DID: ${userDid || "no disponible"}`
          );
          return;
        }
        setIsAdmin(true);
      } catch (err: any) {
        console.error("[Admin] Error de red o parsing:", err);
        setErrorMsg(
          `No se pudo contactar al servidor.\n\n${err?.message || "Error de red desconocido."}`
        );
      } finally {
        setChecking(false);
      }
    })();
  }, [ready, authenticated]);

  if (!ready || checking) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "#060610" }}>
        <p className="text-[#FF8DA1] text-xl font-bold animate-pulse">Verificando acceso…</p>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "#060610" }}>
        <div className="text-center max-w-md px-6">
          <p className="text-4xl mb-4">🛡️</p>
          <h1 className="text-[#FF8DA1] text-xl font-bold mb-4">Acceso denegado</h1>
          <p className="text-gray-400 text-sm whitespace-pre-wrap mb-6">{errorMsg}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => { setErrorMsg(null); setChecking(true); window.location.reload(); }}
              className="px-5 py-2 rounded-lg bg-[#E4007C]/20 text-[#FF8DA1] border border-[#E4007C]/40 text-sm font-semibold hover:bg-[#E4007C]/30 transition-colors"
            >
              Reintentar
            </button>
            <a
              href="/"
              className="px-5 py-2 rounded-lg bg-white/5 text-gray-400 border border-white/10 text-sm font-semibold hover:bg-white/10 transition-colors"
            >
              Volver al inicio
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen text-white" style={{ background: "#060610" }}>
      <header className="fixed top-0 left-0 right-0 z-40 h-14 flex items-center justify-between px-6 bg-[#060610]/80 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-xl">🛡️</span>
          <span className="font-extrabold text-[#FF8DA1] tracking-tight">AXOLOTTO ADMIN</span>
        </div>
        <a href="/" className="text-gray-500 hover:text-white text-sm transition-colors">← Volver al juego</a>
      </header>

      <nav className="fixed top-14 left-0 right-0 z-30 flex gap-1 px-4 py-2 bg-[#0D0D1F]/90 backdrop-blur-md border-b border-white/5">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === tab.id
                ? "bg-[#E4007C]/20 text-[#FF8DA1] border border-[#E4007C]/40"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            <span>{tab.emoji}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>

      <main className="pt-28 pb-10 max-w-7xl mx-auto px-4 sm:px-6">
        {activeTab === "resumen"    && <AdminOverview token={token} />}
        {activeTab === "jugadores"  && <AdminPlayerList token={token} />}
        {activeTab === "economia"   && <AdminEconomyCharts token={token} />}
        {activeTab === "cartas"     && <AdminCardDistribution token={token} />}
        {activeTab === "simulacion" && <AdminSimReport token={token} />}
        {activeTab === "caos" && <AdminChaosSimV2 token={token} />}
      </main>
    </div>
  );
}