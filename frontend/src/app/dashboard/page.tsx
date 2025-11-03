"use client";

import withAuth from "@/components/withAuth";
import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import axios from "axios";

interface Document {
  id: number;
  original_filename: string;
  status: string;
  created_at: string;
}

function Dashboard() {
  const { logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/`
      );
      setDocuments(response.data);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      fetchDocuments(); // Refresh the list after upload
    } catch (error) {
      console.error("Failed to upload file", error);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/${documentId}`
      );
      fetchDocuments(); // Refresh the list after deletion
    } catch (error) {
      console.error("Failed to delete document", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="flex items-center justify-between p-4 bg-white shadow-md">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={logout}
          className="px-4 py-2 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
        >
          Logout
        </button>
      </header>
      <main className="p-8">
        <div className="p-6 mb-8 bg-white rounded-lg shadow-md">
          <h2 className="mb-4 text-xl font-bold">Upload a Document</h2>
          <div className="flex items-center space-x-4">
            <input type="file" onChange={handleFileChange} />
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="px-4 py-2 font-bold text-white bg-indigo-600 rounded-md disabled:bg-gray-400 hover:bg-indigo-700"
            >
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </div>
        <div>
          <h2 className="mb-4 text-xl font-bold">Your Documents</h2>
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md"
              >
                <div>
                  <p className="font-bold">{doc.original_filename}</p>
                  <p className="text-sm text-gray-500">
                    Status: {doc.status}
                  </p>
                </div>
                <div>
                  <a
                    href={`/quiz/${doc.id}`}
                    className="mr-4 text-indigo-600 hover:underline"
                  >
                    View Quiz
                  </a>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default withAuth(Dashboard);
