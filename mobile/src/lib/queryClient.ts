import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // FR-7: verification must survive flaky/offline networks — stale data
      // shown instantly, refetched in the background rather than blocking.
      staleTime: 30_000,
      retry: 2,
    },
  },
});
