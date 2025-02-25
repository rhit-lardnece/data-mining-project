import React from "react";

const UsernameInput = ({ username, setUsername, fetchStats }) => {
  return (
    <div className="flex gap-2 mb-4">
      <input
        type="text"
        placeholder="Enter Chess Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="p-2 border rounded-lg"
      />
      <button
        onClick={fetchStats}
        className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-700"
      >
        Get Stats
      </button>
    </div>
  );
};

export default UsernameInput;
