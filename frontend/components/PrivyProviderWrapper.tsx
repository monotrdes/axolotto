"use client";

import { useEffect } from "react";
import { PrivyProvider } from "@privy-io/react-auth";
import { polygonAmoy } from "viem/chains";
import { ToastProvider } from "@/context/ToastContext";
import PwaInstallBanner from "@/components/PwaInstallBanner";

const IS_LOCAL = process.env.NEXT_PUBLIC_CHAIN_ID === "31337";

export default function PrivyProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      const registerSW = () => {
        navigator.serviceWorker.register("/sw.js")
          .then((reg) => {
            console.log("ServiceWorker registrado con éxito:", reg.scope);
          })
          .catch((err) => {
            console.error("Fallo al registrar ServiceWorker:", err);
          });
      };

      if (document.readyState === "complete") {
        registerSW();
      } else {
        window.addEventListener("load", registerSW);
        return () => window.removeEventListener("load", registerSW);
      }
    }
  }, []);

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
        <PwaInstallBanner />
      </ToastProvider>
    </PrivyProvider>
  );
}