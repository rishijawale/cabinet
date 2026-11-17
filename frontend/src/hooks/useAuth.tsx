import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  fetchAccount,
  mergeLocalFavorites,
  type Account,
} from "../services/api/account";
import {
  authEnabled,
  getSupabase,
} from "../services/supabase";
import { clearLocalSaved, getLocalSavedSlugs } from "./useSaved";

export type AuthStatus = "disabled" | "loading" | "signedOut" | "signedIn";

interface AuthContextValue {
  status: AuthStatus;
  account: Account | null;
  sendMagicLink: (email: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  status: authEnabled ? "loading" : "disabled",
  account: null,
  sendMagicLink: async () => undefined,
  signOut: async () => undefined,
});

/**
 * Bridges Supabase Auth with the archive API.
 *
 * When a session appears, `/auth/me` provisions (or links) the local account,
 * and any favorites saved in this browser before sign-in are merged to the
 * server exactly once, after which the local store is cleared — favorites now
 * follow the account between devices.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(authEnabled ? "loading" : "disabled");
  const [account, setAccount] = useState<Account | null>(null);
  const mergedRef = useRef(false);

  useEffect(() => {
    if (!authEnabled) return;
    let cancelled = false;
    let unsubscribe: (() => void) | undefined;

    async function start() {
      const client = await getSupabase();
      if (!client || cancelled) return;

      const syncAccount = async (sessionToken: string | null) => {
        if (!sessionToken) {
          setAccount(null);
          setStatus("signedOut");
          return;
        }
        try {
          const me = await fetchAccount();
          if (cancelled) return;
          setAccount(me);
          setStatus("signedIn");
          if (!mergedRef.current) {
            mergedRef.current = true;
            const slugs = getLocalSavedSlugs();
            if (slugs.length > 0) {
              await mergeLocalFavorites(slugs);
              if (!cancelled) clearLocalSaved();
            }
          }
        } catch {
          if (!cancelled) {
            setAccount(null);
            setStatus("signedOut");
          }
        }
      };

      const {
        data: { subscription },
      } = client.auth.onAuthStateChange((_event, session) => {
        void syncAccount(session?.access_token ?? null);
      });

      const {
        data: { session },
      } = await client.auth.getSession();
      await syncAccount(session?.access_token ?? null);

      unsubscribe = () => subscription.unsubscribe();
    }

    void start();
    return () => {
      cancelled = true;
      unsubscribe?.();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      account,
      sendMagicLink: async (email: string) => {
        const client = await getSupabase();
        if (!client) throw new Error("Accounts are not available.");
        const { error } = await client.auth.signInWithOtp({
          email,
          options: {
            // Supabase only follows redirects it knows about; configure this
            // origin in Authentication > URL Configuration on the dashboard.
            emailRedirectTo: `${window.location.origin}/login`,
          },
        });
        if (error) throw error;
      },
      signOut: async () => {
        const client = await getSupabase();
        if (!client) return;
        await client.auth.signOut();
        setAccount(null);
        setStatus("signedOut");
      },
    }),
    [status, account],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
