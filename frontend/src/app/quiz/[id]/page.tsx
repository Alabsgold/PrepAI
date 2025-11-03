"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import axios from "axios";
import { motion } from "framer-motion";
import withAuth from "@/components/withAuth";

interface Option {
  id: number;
  option_text: string;
  is_correct: boolean;
}

interface Question {
  id: number;
  question_text: string;
  options: Option[];
}

interface Quiz {
  id: number;
  title: string;
  questions: Question[];
}

function QuizPage() {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<{
    [key: number]: number;
  }>({});
  const [submitted, setSubmitted] = useState(false);
  const params = useParams();
  const id = params.id;

  useEffect(() => {
    if (id) {
      fetchQuiz();
    }
  }, [id]);

  const fetchQuiz = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/${id}/quiz`
      );
      setQuiz(response.data);
    } catch (error) {
      console.error("Failed to fetch quiz", error);
    }
  };

  const handleSelectAnswer = (questionId: number, optionId: number) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: optionId,
    });
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  if (!quiz) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="mb-8 text-3xl font-bold text-center">{quiz.title}</h1>
      </motion.div>
      <div className="space-y-8">
        {quiz.questions.map((q, index) => (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="p-6 bg-white rounded-lg shadow-md"
          >
            <h2 className="mb-4 text-xl font-semibold">{q.question_text}</h2>
            <div className="space-y-2">
              {q.options.map((option) => {
                const isSelected = selectedAnswers[q.id] === option.id;
                let bgColor = "bg-gray-200 hover:bg-gray-300";
                if (submitted) {
                  if (option.is_correct) {
                    bgColor = "bg-green-500 text-white";
                  } else if (isSelected) {
                    bgColor = "bg-red-500 text-white";
                  }
                } else if (isSelected) {
                  bgColor = "bg-indigo-500 text-white";
                }
                return (
                  <motion.button
                    key={option.id}
                    onClick={() => handleSelectAnswer(q.id, option.id)}
                    className={`w-full p-3 text-left rounded-md transition-colors duration-200 ${bgColor}`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {option.option_text}
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>
      <div className="mt-8 text-center">
        <motion.button
          onClick={handleSubmit}
          className="px-8 py-3 font-bold text-white bg-green-600 rounded-md hover:bg-green-700"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Submit Answers
        </motion.button>
      </div>
    </div>
  );
}

export default withAuth(QuizPage);
