import { Route, Routes } from "react-router-dom";

import { RootLayout } from "./components/layout/RootLayout";
import { AboutPage } from "./pages/AboutPage";
import { CollectionDetailPage } from "./pages/CollectionDetailPage";
import { CollectionsPage } from "./pages/CollectionsPage";
import { ComingSoonPage } from "./pages/ComingSoonPage";
import { ExplorePage } from "./pages/ExplorePage";
import { GuidelinesPage } from "./pages/GuidelinesPage";
import { HomePage } from "./pages/HomePage";
import { LicensesPage } from "./pages/LicensesPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ObjectDetailPage } from "./pages/ObjectDetailPage";
import { PrivacyPage } from "./pages/PrivacyPage";
import { SavedPage } from "./pages/SavedPage";
import { TermsPage } from "./pages/TermsPage";

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
        <Route path="studio" element={<ComingSoonPage page="/studio" />} />
        <Route path="submit" element={<ComingSoonPage page="/submit" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
