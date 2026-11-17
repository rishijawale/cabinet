import { lazy, type ComponentType } from "react";
import { Route, Routes } from "react-router-dom";

import { RootLayout } from "./components/layout/RootLayout";

/**
 * Wrap a named page export in React.lazy. Every route is a separate chunk so
 * the first paint only ships the layout, router and shared UI.
 */
function lazyPage<K extends string, M extends Record<K, ComponentType>>(
  load: () => Promise<M>,
  exportName: K,
) {
  return lazy(async () => ({ default: (await load())[exportName] }));
}

const HomePage = lazyPage(() => import("./pages/HomePage"), "HomePage");
const ExplorePage = lazyPage(() => import("./pages/ExplorePage"), "ExplorePage");
const ObjectDetailPage = lazyPage(() => import("./pages/ObjectDetailPage"), "ObjectDetailPage");
const CollectionsPage = lazyPage(() => import("./pages/CollectionsPage"), "CollectionsPage");
const CollectionDetailPage = lazyPage(
  () => import("./pages/CollectionDetailPage"),
  "CollectionDetailPage",
);
const SavedPage = lazyPage(() => import("./pages/SavedPage"), "SavedPage");
const LoginPage = lazyPage(() => import("./pages/LoginPage"), "LoginPage");
const AboutPage = lazyPage(() => import("./pages/AboutPage"), "AboutPage");
const GuidelinesPage = lazyPage(() => import("./pages/GuidelinesPage"), "GuidelinesPage");
const LicensesPage = lazyPage(() => import("./pages/LicensesPage"), "LicensesPage");
const PrivacyPage = lazyPage(() => import("./pages/PrivacyPage"), "PrivacyPage");
const TermsPage = lazyPage(() => import("./pages/TermsPage"), "TermsPage");
const NotFoundPage = lazyPage(() => import("./pages/NotFoundPage"), "NotFoundPage");

// This page takes a prop, so it is wrapped directly instead of through the helper.
const ComingSoonPage = lazy(() =>
  import("./pages/ComingSoonPage").then((module) => ({ default: module.ComingSoonPage })),
);

export function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<HomePage />} />
        <Route path="explore" element={<ExplorePage />} />
        <Route path="explore/:category" element={<ExplorePage />} />
        <Route path="object/:slug" element={<ObjectDetailPage />} />
        <Route path="collections" element={<CollectionsPage />} />
        <Route path="collections/:slug" element={<CollectionDetailPage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="guidelines" element={<GuidelinesPage />} />
        <Route path="licenses" element={<LicensesPage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="terms" element={<TermsPage />} />
        <Route path="saved" element={<SavedPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="studio" element={<ComingSoonPage page="/studio" />} />
        <Route path="submit" element={<ComingSoonPage page="/submit" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
