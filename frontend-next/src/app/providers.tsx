"use client";

import {Provider as JotaiProvider} from "jotai";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {useState} from "react";

export function Providers({children}: {children: React.ReactNode}) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: 0,
          },
        },
      }),
  );
  return (
    <QueryClientProvider client={client}>
      <JotaiProvider>{children}</JotaiProvider>
    </QueryClientProvider>
  );
}
