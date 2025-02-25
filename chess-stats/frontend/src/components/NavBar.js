import React from 'react';
import { Link } from 'react-router-dom';

const NavBar = () => {
  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="text-white text-lg font-bold">
          <Link to="/">Chess Stats</Link>
        </div>
        <ul className="flex space-x-4 text-white ">
          <Link to="/" className="hover:underline">Personalized Stats</Link>
          <Link to="/clustering" className="hover:underline">Player Clustering</Link>
          <Link to="/comparison" className="hover:underline">Player Comparison</Link>
          <Link to="/top-players" className="hover:underline">Top Players</Link>
        </ul>
      </div>
    </nav>
  );
};

export default NavBar;
