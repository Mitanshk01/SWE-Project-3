import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import axios from "axios";
import Repository from "../../components/Repository";
import Link from "next/link";
import { uploadCodeToRepo } from "@/components/Requests";
import { getCodeFileMetadataFromRepo } from "../../components/Requests.js";
import { getDataFileMetadataFromRepo } from "../../components/Requests.js";
import { getRunsFromRepo } from "../../components/Requests.js";

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
  name: string;
  description: string;
  modelAdded: boolean;
  dataAdded: boolean;
}

const RepositoryPage = () => {
  const router = useRouter();
  const { repo_id } = router.query;

  const [repository, setRepository] = useState<Repository | null>();
  const [runs, setRuns] = useState<Run[]>([]);
  const [newRunName, setNewRunName] = useState("");
  const [newRunDescription, setNewRunDescription] = useState("");

  const [file, setFile] = useState(null);
  const [datasetFile, setDatasetFile] = useState(null);
  const [uploadComplete, setUploadComplete] = useState(false);

  const [codeDetails, setCodeDetails] = useState([]);
  const [dataDetails, setDataDetails] = useState([]);

  var user_id =
    typeof window !== "undefined" ? localStorage.getItem("user_id") : null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleDatasetFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setDatasetFile(e.target.files[0]);
    }
  };

  const handleFileInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (files) {
      setFileToUpload(files[0]);
    }
  };

  // Handler for file upload
  const handleFileUpload = async () => {
    console.log("Uploading file", file);
    console.log("Repository", repository);
    if (file && repository) {
      console.log("Atleast both file and repository are present");
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("userid", user_id); // Replace with actual user ID
        formData.append("repoName", repository.name);
        formData.append("filename", file.name);
        console.log("File name: ", file.name);
        console.log("Requesting to upload file on file server");
        console.log("User ID: ", user_id);
        console.log("Repository Name: ", repository.name);

        for (let [key, value] of formData.entries()) {
          console.log(`${key}: ${value}`);
        }

        const response = await axios.post(
          "http://localhost:8004/upload_code_to_repo",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        // uploadCodeToRepo(repo)

        console.log("File uploaded successfully", response.data);
        setUploadComplete(true);
        setOpenModal(null); // Close the modal on successful upload
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    }
  };

  const handleDatasetUpload = async () => {
    const chunkSize = 1024 * 1024; // 1MB chunk size
    const totalSize = datasetFile.size;
    const totalChunks = Math.ceil(totalSize / chunkSize);

    console.log("Uploading file", datasetFile, "with", totalChunks, "chunks");

    let currentChunkIndex = 0;

    const readNextChunk = async () => {
      console.log("Reading chunk index", currentChunkIndex);

      const fileReader = new FileReader();
      const offset = currentChunkIndex * chunkSize;
      const blob = datasetFile.slice(offset, offset + chunkSize);

      fileReader.onload = async () => {
        const chunk = fileReader.result;
        const blobChunk = new Blob([chunk]); // Convert ArrayBuffer to Blob
        const fileChunk = new File([blobChunk], datasetFile.name); // Convert Blob to File

        const formData = new FormData();
        formData.append("file", fileChunk);
        formData.append("offset", offset);
        formData.append("currentChunkIndex", currentChunkIndex);
        formData.append("totalChunks", totalChunks);
        formData.append("totalSize", totalSize);
        formData.append("filename", datasetFile.name);
        formData.append("filetype", datasetFile.type);
        formData.append("userid", user_id);
        formData.append("repoName", repo_id);

        for (let [key, value] of formData.entries()) {
          console.log(`${key}: ${value}`);
        }

        try {
          const response = await axios.post(
            "http://localhost:8004/upload_dataset_to_repo",
            formData,
            {
              headers: {
                "Content-Type": "multipart/form-data",
              },
            }
          );
          console.log("Response: ", response.data);
          currentChunkIndex++;

          if (currentChunkIndex < totalChunks) {
            readNextChunk();
          } else {
            console.log("Dataset uploaded successfully");
            setUploadComplete(true);
          }
        } catch (error) {
          console.error("Error uploading dataset chunk:", error);
        }
      };

      fileReader.readAsArrayBuffer(blob);
    };

    readNextChunk();
  };

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

    user_id = localStorage.getItem("user_id");

    // get code details
    const codeDetails = await getCodeFileMetadataFromRepo(user_id, repo_id);
    console.log("Code Details: ", codeDetails);
    setCodeDetails(codeDetails);

    // get data details
    const dataDetails = await getDataFileMetadataFromRepo(user_id, repo_id);
    console.log("Data Details: ", dataDetails);
    setDataDetails(dataDetails);

    // get runs
    const runs = await getRunsFromRepo(user_id, repo_id);
    console.log("Runs: ", runs);

    const checkModel = (codeDetails) => {
      if (!codeDetails) return false
      if (codeDetails.length > 0) {
        console.log("Model added");
        return true
      }
      return false
    }
  
    const checkData = (dataDetails) => {
      if (!dataDetails) return false
      if (dataDetails.length > 0) {
        return true
      }
      return false
    }

    setRepository({
      name: repo_id,
      description: "This is a dummy repository",
      modelAdded: checkModel(codeDetails),
      dataAdded: checkData(dataDetails),
    });

    // setRuns(runs);
  };

  useEffect(() => {
    fetchRepository();
  }, [repo_id]);

  useEffect(() => {
    if (uploadComplete) {
      fetchRepository();
      setUploadComplete(false); // Reset the flag
    }
  }, [uploadComplete]);

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

  const startTraining = async () => {

    if (codeDetails.length > 0) {
      console.log("Training will start with the following code : ", codeDetails.name);
      console.log("And with the following : ", codeDetails.id);

      //ping the backend to start training
      const response = await axios.post(`http://localhost:8004/start_training`, {
        file_id: codeDetails.id,
        file_name: codeDetails.name,
        user_id: user_id,
        repo_name: repo_id,
        run_description: newRunDescription
      });

    } else {
      console.error("No code files available for training.");
    }
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

  const fetchCodeFileMetadata = async () => {
    try {
      const user_id = localStorage.getItem("user_id");
      const repo_name = repository?.name; // Ensure you have the repository name from your state
  
      if (user_id && repo_name) {
        const response = await axios.get(`http://localhost:8004/get_code_file_metadata_from_repo`, {
          params: {
            user_id: user_id,
            repo_name: repo_name
          }
        });
        console.log("Code file metadata:", response.data);
        return response.data;
      } else {
        console.error("User ID or Repository Name is missing");
        return [];
      }
    } catch (error) {
      console.error("Failed to fetch code file metadata", error);
      return [];
    }
  };

  return (
    <div>
      {repository && (
        <>
          <Repository repository={repository} />
          {/* <button onClick={handleUpdateModel} disabled={repository.modelAdded}>
            Add Code
          </button>
          <button onClick={handleUpdateData} disabled={repository.dataAdded}>
            Add Data
          </button> */}

          <div>
            <input
              type="file"
              disabled={repository.modelAdded}
              onChange={(e) =>
                setFile(e.target.files ? e.target.files[0] : null)
              }
            />
            <button onClick={handleFileUpload} disabled={repository.modelAdded}>
              Upload Code
            </button>
          </div>

          <div>
            <input
              type="file"
              disabled={repository.dataAdded}
              onChange={handleDatasetFileChange}
            />
            <button
              onClick={handleDatasetUpload}
              disabled={repository.dataAdded}
            >
              Upload Dataset
            </button>
          </div>

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
