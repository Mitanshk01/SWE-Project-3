// pages/index.js

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {createRepository} from "../components/Requests.js";
import { getUserRepos } from "../components/Requests.js";
import { Loader } from "../components/Loader";

interface Repository {
  id: number;
  name: string;
  description?: string;
}

const Home = () => {
  const [repositories, setRepositories] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newRepoName, setNewRepoName] = useState("");
  const [newRepoDescription, setNewRepoDescription] = useState("");
  const [trigger, setTrigger] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const user_id = typeof window !== 'undefined' ? localStorage.getItem("user_id") : null;

  const fetchRepositories = async () => {

    const fetchedRepositories = await getUserRepos(user_id);
    console.log(fetchedRepositories);
    console.log(fetchedRepositories);


    setRepositories(fetchedRepositories.repos);
  };

  useEffect(() => {
    fetchRepositories();
  }, [trigger]);

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  const addRepository = async () => {
    setIsLoading(true);
    const newRepository = {
      id: Date.now(), // unique identifier for the new repo
      name: newRepoName,
    };

    const response = await createRepository(user_id, newRepository.name);

    if (response.status === 200) {
      console.log("Repository created successfully");
    }
    else {
      console.log("Error creating repository");
    }

    setIsModalOpen(false);
    setIsLoading(false);
    setTrigger(!trigger);
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

      {isLoading && (
        <div className="fixed top-0 left-0 h-screen w-screen bg-black bg-opacity-50 flex items-center justify-center">
          <Loader type="ThreeDots" color="#00BFFF" height={100} width={100} />
        </div>
      )}

      <h2 className="text-xl font-bold mb-4">Current Repositories:</h2>
      <ul>
      {repositories && repositories.length > 0 ? (
          repositories.map((repository) => (
            <li key={repository} className="mb-2">
              <Link
                href={`/repository/${repository}`}
                className="text-blue-600 hover:text-blue-800"
              >
                {repository}
              </Link>
            </li>
          ))
        ) : null}
      </ul>
    </div>
  );
};

export default Home;
