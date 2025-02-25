// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import PersonalizedStats from './pages/PersonalizedStats';
import PlayerClustering from './pages/PlayerClustering';
import PlayerComparison from './pages/PlayerComparison';
import TopPlayers from './pages/TopPlayers';

function App() {
  return (
    <Router>
      <NavBar />
      <div className="p-4">
        <Routes>
          <Route path="/" element={<PersonalizedStats />} />
          <Route path="/clustering" element={<PlayerClustering />} />
          <Route path="/comparison" element={<PlayerComparison />} />
          <Route path="/top-players" element={<TopPlayers />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
