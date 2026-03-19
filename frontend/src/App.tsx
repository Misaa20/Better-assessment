import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { GroupListPage } from "./pages/GroupListPage";
import { GroupDetailPage } from "./pages/GroupDetailPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto flex h-14 max-w-4xl items-center px-4">
            <Link to="/" className="text-base font-semibold text-gray-900 tracking-tight">
              FairSplit
            </Link>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<GroupListPage />} />
            <Route path="/groups/:groupId" element={<GroupDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
