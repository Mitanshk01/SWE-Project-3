import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import axios from "axios";
import Repository from "../../components/Repository";
import Link from "next/link";

interface Run {
  id: number;
  name: string;
  status: string;
  metrics: {
    accuracy: number;
    loss: number;
  };
}

interface Repository {
  id: number;
  name: string;
  description: string;
  modelAdded: boolean;
  dataAdded: boolean;
}

const RepositoryPage = () => {
  const router = useRouter();
  const { repo_id } = router.query;

  const [repository, setRepository] = useState<Repository | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [newRunName, setNewRunName] = useState("");
  const [newRunDescription, setNewRunDescription] = useState("");

  const [openModal, setOpenModal] = useState<
    "train" | "fineTune" | "infer" | null
  >(null);
  const toggleModal = (modalName: "train" | "fineTune" | "infer") => {
    if (openModal === modalName) {
      setOpenModal(null); // Close the modal if it's already open
    } else {
      setOpenModal(modalName); // Open the selected modal and close any others
    }
  };

  const startAction = (actionName: "train" | "fineTune" | "infer") => {
    console.log(`Start ${actionName} with`, newRunName, newRunDescription);
    setOpenModal(null); // Close the modal after starting the action
    // Add your logic for each action here, possibly sending data to your backend
  };

  useEffect(() => {
    if (repo_id) {
      fetchRepository();
      fetchRuns();
    }
  }, [repo_id]);

  useEffect(() => {
    if (!repository) {
      console.log("Empty");
      return;
    }
    console.log("Changed Name!");
    console.log(repository.name);
  }, [repository]);

  const fetchRepository = async () => {
    // const response = await axios.get(`/${repo_id}`);
    const dummyData: Repository = {
      id: 1,
      name: "Repository Dummy",
      description: "This is a dummy repository.",
      modelAdded: false,
      dataAdded: false,
    };
    setRepository(dummyData);

    // TODO : Fetch repodetails from backend using repo_id
    //
  };

  const fetchRuns = async () => {
    // const response = await axios.get(`/${repo_id}/runs`);

    const dummyData: Run[] = [
      {
        id: 1,
        name: "Dummy Run 1",
        status: "completed",
        metrics: {
          accuracy: 0.9,
          loss: 0.1,
        },
      },
      {
        id: 2,
        name: "Dummy Run 2",
        status: "completed",
        metrics: {
          accuracy: 0.8,
          loss: 0.2,
        },
      },
    ];

    setRuns(dummyData);

    // TODO : Fetch runs from backend using repo_id
  };

  const handleUpdateModel = async () => {
    // await axios.put(`/${repo_id}/update_model`);
    // setRepository((prevRepository) => ({
    //   ...prevRepository,
    //   name: "Repository Dum Dum",
    //   modelAdded: true,
    // }));

    setRepository((prevRepository) => {
      if (prevRepository === null) return null; // Check if the previous state is null
      return {
        ...prevRepository,
        name: "Repository Dum Dum",
        modelAdded: true,
      };
    });

    // alert(repository.modelAdded);

    // TODO : Update model using backend
  };

  const handleUpdateData = async () => {
    // await axios.put(`/${repo_id}/update_data`);
    setRepository((prevRepository) => {
      if (prevRepository === null) return null;
      return {
        ...prevRepository,
        name: "Repository Dum Dum Dummer",
        dataAdded: true,
      };
    });

    // TODO : Update data using backend
  };

  const startTraining = () => {
    console.log("Start training with", newRunName, newRunDescription);
    // You would add your logic to initiate training here.
    // After starting the training, you can close the modal.
    setOpenModal(null);
  };

  const startFineTuning = () => {
    console.log("Start fine-tuning");
    setOpenModal(null);
    // Placeholder for actual start fine-tuning logic
  };

  const startInfer = () => {
    console.log("Starting inference");
    setOpenModal(null);
    // Placeholder for actual start infer logic
  };

  return (
    <div>
      {repository && (
        <>
          <Repository repository={repository} />
          <button onClick={handleUpdateModel} disabled={repository.modelAdded}>
            Add Model
          </button>
          <button onClick={handleUpdateData} disabled={repository.dataAdded}>
            Add Data
          </button>

          <button
            onClick={() => toggleModal("train")}
            disabled={!repository?.modelAdded || !repository?.dataAdded}
          >
            Train
          </button>

          <button
            onClick={() => toggleModal("fineTune")}
            disabled={!repository?.modelAdded || !repository?.dataAdded}
          >
            Fine-Tune
          </button>

          <button
            onClick={() => toggleModal("infer")}
            disabled={!repository?.modelAdded || !repository?.dataAdded}
          >
            Infer
          </button>
        </>
      )}

      {openModal === "train" && (
        <div className="mb-4 p-4 border-2 border-black rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold mb-4">
            Start a New Training Run
          </h2>
          <div className="mb-4">
            <input
              type="text"
              value={newRunName}
              onChange={(e) => setNewRunName(e.target.value)}
              placeholder="Run Name"
              className="border p-2 w-full"
              required
            />
          </div>
          <div className="mb-4">
            <textarea
              value={newRunDescription}
              onChange={(e) => setNewRunDescription(e.target.value)}
              placeholder="Run Description (Optional)"
              className="border p-2 w-full"
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={startTraining}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Start Training
            </button>
            <button
              onClick={() => setOpenModal(null)}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {openModal === "fineTune" && (
        <div className="mb-4 p-4 border-2 border-black rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold mb-4">
            Start a New Finetuning Run
          </h2>
          <div className="mb-4">
            <input
              type="text"
              value={newRunName}
              onChange={(e) => setNewRunName(e.target.value)}
              placeholder="Run Name"
              className="border p-2 w-full"
              required
            />
          </div>
          <div className="mb-4">
            <textarea
              value={newRunDescription}
              onChange={(e) => setNewRunDescription(e.target.value)}
              placeholder="Run Description (Optional)"
              className="border p-2 w-full"
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={startFineTuning}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Start Finetuning
            </button>
            <button
              onClick={() => setOpenModal(null)}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {openModal === "infer" && (
        <div className="mb-4 p-4 border-2 border-black rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold mb-4">
            Start a New Inference Run
          </h2>
          <div className="mb-4">
            <input
              type="text"
              value={newRunName}
              onChange={(e) => setNewRunName(e.target.value)}
              placeholder="Run Name"
              className="border p-2 w-full"
              required
            />
          </div>
          <div className="mb-4">
            <textarea
              value={newRunDescription}
              onChange={(e) => setNewRunDescription(e.target.value)}
              placeholder="Run Description (Optional)"
              className="border p-2 w-full"
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={startInfer}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Start Inference
            </button>
            <button
              onClick={() => setOpenModal(null)}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <h3> Runs </h3>
      {runs.map((run) => (
        <li key={run.id} className="mb-2">
          <Link
            href={`/run/${run.id}`}
            className="text-blue-600 hover:text-blue-800"
          >
            {run.id}
          </Link>
        </li>
      ))}
    </div>
  );
};

export default RepositoryPage;
