'use client';
import { useWallets } from '@privy-io/react-auth';

/**
 * Abre el widget de MoonPay directamente con la publishable key del sandbox.
 *
 * Por qué standalone en vez de Privy's useFundWallet:
 * - Con el widget directo usamos nuestra propia API key y controlamos el asset/chain
 * - Polygon Amoy: usar NEXT_PUBLIC_MOONPAY_CURRENCY=usdc_polygon
 *
 * En sandbox no se requiere firma de URL (el entorno es permisivo).
 * En producción, la firma HMAC-SHA256 debe generarse en el backend.
 *
 * Docs MoonPay: https://docs.moonpay.com/moonpay/onramp/web-sdk/configuration
 */

const MOONPAY_PK = process.env.NEXT_PUBLIC_MOONPAY_PK ?? '';
const IS_SANDBOX = process.env.NEXT_PUBLIC_MOONPAY_SANDBOX === 'true';

// URL base del widget (sandbox usa buy-sandbox, prod usa buy)
const MOONPAY_BASE = IS_SANDBOX
  ? 'https://buy-sandbox.moonpay.com'
  : 'https://buy.moonpay.com';

// Moneda default para la wallet del usuario.
// En sandbox podemos usar cualquier moneda soportada por MoonPay.
// Polygon Amoy → usdc_polygon | Prod Polygon → usdc_polygon
// Verificar asset code en https://docs.moonpay.com/moonpay/onramp/currencies
const DEFAULT_CURRENCY = process.env.NEXT_PUBLIC_MOONPAY_CURRENCY ?? 'usdc_base';

export interface OpenMoonPayOptions {
  amountUsd?: number;
  currency?: string;     // override del asset (ej. 'usdt_ethereum' para staging)
  walletAddress?: string; // override manual de la dirección destino
}

export function useMoonPayWidget() {
  const { wallets } = useWallets();

  const openWidget = ({ amountUsd, currency, walletAddress }: OpenMoonPayOptions = {}) => {
    const embeddedWallet = wallets.find(w => w.walletClientType === 'privy');
    const destination = walletAddress ?? embeddedWallet?.address;

    if (!destination) {
      console.error('[MoonPay] No se encontró wallet destino');
      return;
    }
    if (!MOONPAY_PK) {
      console.error('[MoonPay] NEXT_PUBLIC_MOONPAY_PK no configurado');
      return;
    }

    const params = new URLSearchParams({
      apiKey:       MOONPAY_PK,
      currencyCode: currency ?? DEFAULT_CURRENCY,
      walletAddress: destination,
      colorCode:    '%23E4007C',  // Rosa mexicano (#E4007C URL-encoded)
      theme:        'dark',
      language:     'es',
    });

    if (amountUsd) {
      // quoteCurrencyAmount = cantidad de USD que el usuario quiere gastar
      params.set('quoteCurrencyAmount', String(amountUsd));
    }

    const url = `${MOONPAY_BASE}?${params.toString()}`;

    // Popup centrado — MoonPay recomienda al menos 480×660
    const w = 480, h = 660;
    const left = Math.round(window.screenX + (window.outerWidth - w) / 2);
    const top  = Math.round(window.screenY + (window.outerHeight - h) / 2);
    window.open(url, 'moonpay_widget', `width=${w},height=${h},left=${left},top=${top},menubar=no,toolbar=no,scrollbars=yes`);
  };

  return { openWidget, isConfigured: !!MOONPAY_PK };
}
