import React from 'react';

const ExampleUsernames = ({ examples, setUsername }) => {
  return (
    <div className="mt-4">
      <h3 className="font-semibold">Example Usernames:</h3>
      <div className="flex space-x-2 mt-2">
        {examples.map((ex, index) => (
          <button
            key={index}
            onClick={() => setUsername(ex)}
            className="p-2 bg-blue-200 rounded hover:bg-blue-300"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExampleUsernames;
