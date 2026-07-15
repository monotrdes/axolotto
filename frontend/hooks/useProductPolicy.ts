"use client";

import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export type ProductMode = string;
export type EconomyAuthority = "chain" | "database";
export type EconomyAuthorityStatus = "target_not_enforced" | "database_legacy";

export interface GameplayCapabilities {
  free_play: boolean;
  fixed_spending: boolean;
  paid_entries: boolean;
  token_rewards: boolean;
  passive_token_rewards: boolean;
  jackpot: boolean;
}

export interface CommerceCapabilities {
  fixed_item_shop: boolean;
  fiat_payments: boolean;
  crypto_checkout: boolean;
  player_marketplace: boolean;
  creator_payouts: boolean;
  vip_sales: boolean;
  purchased_random_rewards: boolean;
}

export interface TokenCapabilities {
  player_transfers: boolean;
  cashout: boolean;
}

export interface AssetCapabilities {
  card_crafting: boolean;
  board_mutations: boolean;
  hatching: boolean;
  legacy_asset_claims: boolean;
  reciclon: boolean;
}

export interface SafetyCapabilities {
  adult_required_for_commerce: boolean;
  client_reported_rewards: boolean;
  promotional_token_rewards: boolean;
}

export interface ProductPolicy {
  product_mode: ProductMode;
  economy_authority: EconomyAuthority;
  economy_authority_status: EconomyAuthorityStatus;
  gameplay: GameplayCapabilities;
  commerce: CommerceCapabilities;
  tokens: TokenCapabilities;
  assets: AssetCapabilities;
  safety: SafetyCapabilities;
}

export interface UseProductPolicyResult {
  policy: ProductPolicy;
  capabilities: ProductPolicy;
  loading: boolean;
  error: string | null;
}

/**
 * The client starts and fails closed. A capability is enabled only when the
 * policy endpoint explicitly returns the boolean value `true`.
 */
export const SAFE_PRODUCT_POLICY: ProductPolicy = {
  product_mode: "non_gambling",
  economy_authority: "chain",
  economy_authority_status: "target_not_enforced",
  gameplay: {
    free_play: false,
    fixed_spending: false,
    paid_entries: false,
    token_rewards: false,
    passive_token_rewards: false,
    jackpot: false,
  },
  commerce: {
    fixed_item_shop: false,
    fiat_payments: false,
    crypto_checkout: false,
    player_marketplace: false,
    creator_payouts: false,
    vip_sales: false,
    purchased_random_rewards: false,
  },
  tokens: {
    player_transfers: false,
    cashout: false,
  },
  assets: {
    card_crafting: false,
    board_mutations: false,
    hatching: false,
    legacy_asset_claims: false,
    reciclon: false,
  },
  safety: {
    adult_required_for_commerce: true,
    client_reported_rewards: false,
    promotional_token_rewards: false,
  },
};

type UnknownRecord = Record<string, unknown>;

function asRecord(value: unknown): UnknownRecord | null {
  return typeof value === "object" && value !== null
    ? (value as UnknownRecord)
    : null;
}

function enabled(record: UnknownRecord | null, key: string): boolean {
  return record?.[key] === true;
}

function requiredUnlessExplicitlyDisabled(record: UnknownRecord | null, key: string): boolean {
  return record?.[key] !== false;
}

function normalizePolicy(value: unknown): ProductPolicy {
  const root = asRecord(value);
  const gameplay = asRecord(root?.gameplay);
  const commerce = asRecord(root?.commerce);
  const tokens = asRecord(root?.tokens);
  const assets = asRecord(root?.assets);
  const safety = asRecord(root?.safety);

  const productMode = root?.product_mode;
  const economyAuthority = root?.economy_authority;
  const economyAuthorityStatus = root?.economy_authority_status;

  return {
    product_mode:
      typeof productMode === "string" ? productMode : SAFE_PRODUCT_POLICY.product_mode,
    economy_authority:
      economyAuthority === "chain" || economyAuthority === "database"
        ? economyAuthority
        : SAFE_PRODUCT_POLICY.economy_authority,
    economy_authority_status:
      economyAuthorityStatus === "target_not_enforced" || economyAuthorityStatus === "database_legacy"
        ? economyAuthorityStatus
        : SAFE_PRODUCT_POLICY.economy_authority_status,
    gameplay: {
      free_play: enabled(gameplay, "free_play"),
      fixed_spending: enabled(gameplay, "fixed_spending"),
      paid_entries: enabled(gameplay, "paid_entries"),
      token_rewards: enabled(gameplay, "token_rewards"),
      passive_token_rewards: enabled(gameplay, "passive_token_rewards"),
      jackpot: enabled(gameplay, "jackpot"),
    },
    commerce: {
      fixed_item_shop: enabled(commerce, "fixed_item_shop"),
      fiat_payments: enabled(commerce, "fiat_payments"),
      crypto_checkout: enabled(commerce, "crypto_checkout"),
      player_marketplace: enabled(commerce, "player_marketplace"),
      creator_payouts: enabled(commerce, "creator_payouts"),
      vip_sales: enabled(commerce, "vip_sales"),
      purchased_random_rewards: enabled(commerce, "purchased_random_rewards"),
    },
    tokens: {
      player_transfers: enabled(tokens, "player_transfers"),
      cashout: enabled(tokens, "cashout"),
    },
    assets: {
      card_crafting: enabled(assets, "card_crafting"),
      board_mutations: enabled(assets, "board_mutations"),
      hatching: enabled(assets, "hatching"),
      legacy_asset_claims: enabled(assets, "legacy_asset_claims"),
      reciclon: enabled(assets, "reciclon"),
    },
    safety: {
      adult_required_for_commerce: requiredUnlessExplicitlyDisabled(safety, "adult_required_for_commerce"),
      client_reported_rewards: enabled(safety, "client_reported_rewards"),
      promotional_token_rewards: enabled(safety, "promotional_token_rewards"),
    },
  };
}

export function useProductPolicy(): UseProductPolicyResult {
  const [policy, setPolicy] = useState<ProductPolicy>(SAFE_PRODUCT_POLICY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadPolicy() {
      try {
        const response = await fetch(`${API_BASE}/product/policy`, {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Policy request failed (${response.status})`);
        }

        const nextPolicy = normalizePolicy(await response.json());
        if (!active) return;

        setPolicy(nextPolicy);
        setError(null);
      } catch (cause) {
        if (!active || controller.signal.aborted) return;

        setPolicy(SAFE_PRODUCT_POLICY);
        setError(cause instanceof Error ? cause.message : "Unable to load product policy");
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadPolicy();

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return { policy, capabilities: policy, loading, error };
}
