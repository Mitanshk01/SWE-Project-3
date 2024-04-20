// pages/index.js

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import React, { useState, useEffect } from "react";
import Link from "next/link";

interface Repository {
  id: number;
  name: string;
  description?: string;
}

const Home = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newRepoName, setNewRepoName] = useState("");
  const [newRepoDescription, setNewRepoDescription] = useState("");

  const fetchRepositories = async () => {
    const fetchedRepositories: Repository[] = [
      { id: 1, name: "Repository 1" },
      { id: 2, name: "Repository 2" },
      { id: 3, name: "Repository 3" },
      { id: 4, name: "Repository 4" },
      { id: 5, name: "Repository 5" },
    ];
    setRepositories(fetchedRepositories);
  };

  useEffect(() => {
    fetchRepositories();
  }, []);

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  const addRepository = () => {
    const newRepository = {
      id: Date.now(), // unique identifier for the new repo
      name: newRepoName,
      description: newRepoDescription,
    };
    setRepositories([...repositories, newRepository]);
    setIsModalOpen(false);
    setNewRepoName("");
    setNewRepoDescription("");
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">User's Home Page</h1>
      <button
        onClick={toggleModal}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
      >
        {isModalOpen ? "Close Form" : "Create Repository"}
      </button>

      {isModalOpen && (
        <div className="mb-4 p-4 border-2 border-black rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold mb-4">
            Create a new Repository
          </h2>
          <div className="mb-4">
            <input
              type="text"
              value={newRepoName}
              onChange={(e) => setNewRepoName(e.target.value)}
              placeholder="Repository Name"
              className="border p-2 w-full"
              required
            />
          </div>
          <div className="mb-4">
            <textarea
              value={newRepoDescription}
              onChange={(e) => setNewRepoDescription(e.target.value)}
              placeholder="Repository Description (Optional)"
              className="border p-2 w-full"
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={addRepository}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Submit
            </button>
            <button
              onClick={toggleModal}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <h2 className="text-xl font-bold mb-4">Current Repositories:</h2>
      <ul>
        {repositories.map((repository) => (
          <li key={repository.id} className="mb-2">
            <Link
              href={`/repository/${repository.id}`}
              className="text-blue-600 hover:text-blue-800"
            >
              {repository.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Home;
