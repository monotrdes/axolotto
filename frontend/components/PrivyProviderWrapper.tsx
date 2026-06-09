"use client";

import { PrivyProvider } from "@privy-io/react-auth";
import { polygonAmoy } from "viem/chains";
import { ToastProvider } from "@/context/ToastContext";

const IS_LOCAL = process.env.NEXT_PUBLIC_CHAIN_ID === "31337";

export default function PrivyProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID as string}
      config={{
        loginMethods: ["google", "apple", "email"],
        // En staging/prod configuramos Polygon Amoy; en local Privy no necesita chain
        ...(!IS_LOCAL && {
          defaultChain: polygonAmoy,
          supportedChains: [polygonAmoy],
        }),
        embeddedWallets: {
          ethereum: {
            createOnLogin: "all-users",
          },
        },
        appearance: {
          theme: "dark",
          accentColor: "#E4007C",
        },
      }}
    >
      <ToastProvider>
        {children}
      </ToastProvider>
    </PrivyProvider>
  );
}