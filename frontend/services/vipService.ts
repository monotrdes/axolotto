// ═══════════════════════════════════════════════════════
// API SERVICE — VIP
// ═══════════════════════════════════════════════════════
import { API_BASE } from "@/lib/api";
import type { VipStatus } from "@/types/vip";

const API = `${API_BASE}`;

function authHeaders(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── Tiers and stats (delegating to lib/vip fetchers) ──
export { fetchVipTiers, fetchVipStats } from "@/lib/vip";

// ── VIP status ──
export async function fetchVipStatusAPI(
  token: string | null
): Promise<VipStatus | null> {
  try {
    const res = await fetch(`${API}/auth/vip-status`, {
      headers: authHeaders(token),
    });
    if (res.ok) return res.json();
  } catch {
    // silence
  }
  return null;
}

// ── Main axolotito ──
export async function fetchMainAxolotitoAPI(
  token: string | null,
  userId: string
): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${API}/auth/axolotitos/${userId}`, {
      headers: authHeaders(token),
    });
    if (res.ok) {
      const list = await res.json();
      const main = list.find((a: Record<string, unknown>) => a.is_main);
      return main || list[0] || null;
    }
  } catch {
    // silence
  }
  return null;
}

// ── Auto-renew toggle ──
export async function toggleAutoRenewAPI(
  token: string | null,
  enabled: boolean
): Promise<boolean> {
  try {
    const res = await fetch(`${API}/auth/vip/auto-renew`, {
      method: "POST",
      headers: { ...authHeaders(token), "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

// ── Purchase VIP ──
export async function purchaseVIPAPI(
  token: string | null,
  userId: string,
  tierId: string
): Promise<{ success: boolean; data?: Record<string, unknown>; error?: string }> {
  try {
    const catalogRes = await fetch(`${API}/shop/items`);
    const catalog = await catalogRes.json();
    const item = catalog.find((i: Record<string, unknown>) => {
      const meta = (i.item_metadata as Record<string, unknown>) || {};
      return meta.is_vip && meta.vip_tier === tierId;
    });
    if (!item) {
      return { success: false, error: "Producto no encontrado en la tienda." };
    }

    const res = await fetch(`${API}/shop/buy`, {
      method: "POST",
      headers: { ...authHeaders(token), "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        item_id: (item as Record<string, unknown>).id,
        payment_currency: "axoficha",
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = data.detail;
      const msg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail
              .map((e: Record<string, unknown>) => (e.msg as string) ?? JSON.stringify(e))
              .join(", ")
          : "Error al procesar la compra.";
      return { success: false, error: msg };
    }
    return { success: true, data };
  } catch {
    return { success: false, error: "Error de conexion." };
  }
}

// ── Claim daily FRJ ──
export async function claimDailyFrjAPI(
  token: string | null
): Promise<{ success: boolean; error?: string }> {
  try {
    const res = await fetch(`${API}/auth/vip/claim-daily-frj`, {
      method: "POST",
      headers: authHeaders(token),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = (data as Record<string, unknown>).detail;
      const msg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? (detail as Record<string, unknown>[])
              .map((e) => (e.msg as string) ?? JSON.stringify(e))
              .join(", ")
          : "Error al reclamar.";
      return { success: false, error: msg };
    }
    return { success: true };
  } catch {
    return { success: false, error: "Error de conexion." };
  }
}
