import { Routes, Route } from 'react-router-dom';
import { useState, createContext, useContext } from 'react';
import Layout from './components/Layout';
import Landing from './pages/Landing';
import Recommendations from './pages/Recommendations';
import Search from './pages/Search';
import SchemeDetailPage from './pages/SchemeDetail';
import Compare from './pages/Compare';
import Saved from './pages/Saved';
import ML from './pages/ML';
import Privacy from './pages/Privacy';
import type { UserProfile } from './api';

interface ProfileCtx {
  profile: UserProfile;
  setProfile: (p: UserProfile) => void;
  sessionId: string;
  savedIds: Set<number>;
  toggleSaved: (id: number) => void;
}

export const ProfileContext = createContext<ProfileCtx>({
  profile: {},
  setProfile: () => {},
  sessionId: '',
  savedIds: new Set(),
  toggleSaved: () => {},
});

export const useProfile = () => useContext(ProfileContext);

function App() {
  const [profile, setProfile] = useState<UserProfile>({});
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());
  const sessionId = 'local-session-' + (localStorage.getItem('sid') || (() => {
    const id = Math.random().toString(36).slice(2);
    localStorage.setItem('sid', id);
    return id;
  })());

  const toggleSaved = (id: number) => {
    setSavedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <ProfileContext.Provider value={{ profile, setProfile, sessionId, savedIds, toggleSaved }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="search" element={<Search />} />
          <Route path="schemes/:id" element={<SchemeDetailPage />} />
          <Route path="compare" element={<Compare />} />
          <Route path="saved" element={<Saved />} />
          <Route path="ml" element={<ML />} />
          <Route path="privacy" element={<Privacy />} />
        </Route>
      </Routes>
    </ProfileContext.Provider>
  );
}

export default App;
