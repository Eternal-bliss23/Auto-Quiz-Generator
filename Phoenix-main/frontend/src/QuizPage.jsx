import { useState, useEffect } from 'react';

const QuizPage = ({ quizResult, onRestart }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [revealedExplanations, setRevealedExplanations] = useState({});

  const questions = quizResult?.questions || [];
  const currentQ = questions[currentIndex];

  useEffect(() => {
    if (submitted) return;
    const interval = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [submitted]);

  const handleSelectOption = (letter) => {
    if (submitted) return;
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQ.id]: letter,
    });
  };

  const calculateScore = () => {
    let score = 0;
    questions.forEach((q) => {
      if (selectedAnswers[q.id] === q.correct_answer) {
        score++;
      }
    });
    return score;
  };

  const formatTimer = (totalSeconds) => {
    const mins = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const secs = String(totalSeconds % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  };

  if (!questions.length) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl shadow-sm border border-slate-200">
        <p className="text-slate-600 mb-4">No questions available.</p>
        <button onClick={onRestart} className="px-4 py-2 bg-orange-600 text-white rounded-xl text-sm font-bold">
          Go Back
        </button>
      </div>
    );
  }

  const score = calculateScore();
  const accuracy = Math.round((score / questions.length) * 100);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Top Header Card */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-orange-50 text-orange-700">
              {quizResult.topic || 'Quiz'}
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">
              {quizResult.difficulty || 'Standard'}
            </span>
          </div>
          <h2 className="text-base font-bold text-slate-800 mt-1">
            Question {currentIndex + 1} of {questions.length}
          </h2>
        </div>

        <div className="flex items-center space-x-4">
          <div className="font-mono text-xs font-bold px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700">
            ⏱️ {formatTimer(seconds)}
          </div>
          <button
            onClick={onRestart}
            className="text-xs font-semibold text-slate-500 hover:text-slate-800 border border-slate-200 px-3 py-1.5 rounded-lg transition"
          >
            Exit
          </button>
        </div>
      </div>

      {!submitted ? (
        /* Quiz Active Question Card */
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-5">
          {/* Progress Bar */}
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-orange-600 h-1.5 transition-all duration-300 rounded-full"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>

          <h3 className="text-lg font-bold text-slate-900 leading-snug">
            {currentQ.question}
          </h3>

          <div className="space-y-2.5">
            {currentQ.options.map((opt, idx) => {
              const letter = opt.substring(0, 1);
              const isSelected = selectedAnswers[currentQ.id] === letter;
              return (
                <button
                  key={idx}
                  onClick={() => handleSelectOption(letter)}
                  className={`w-full text-left p-4 rounded-xl border text-sm font-medium transition flex items-center space-x-3 ${
                    isSelected
                      ? 'border-orange-600 bg-orange-50/70 text-orange-900 font-semibold ring-1 ring-orange-500'
                      : 'border-slate-200 hover:border-orange-300 bg-white text-slate-700'
                  }`}
                >
                  <span
                    className={`w-6 h-6 rounded-lg text-xs font-bold flex items-center justify-center shrink-0 ${
                      isSelected ? 'bg-orange-600 text-white' : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {letter}
                  </span>
                  <span>{opt.replace(/^[A-D]\)\s*/, '')}</span>
                </button>
              );
            })}
          </div>

          {/* Nav Controls */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition disabled:opacity-30"
            >
              ← Previous
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex((prev) => prev + 1)}
                className="px-5 py-2.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white text-xs font-bold shadow-sm transition"
              >
                Next Question →
              </button>
            ) : (
              <button
                onClick={() => setSubmitted(true)}
                className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md transition"
              >
                Finish & Submit 🏁
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Results & Review View */
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 text-center space-y-4">
            <div className="w-14 h-14 mx-auto rounded-full bg-emerald-100 flex items-center justify-center text-2xl">
              {accuracy >= 70 ? '🎉' : '📖'}
            </div>
            <h3 className="text-xl font-extrabold text-slate-900">Quiz Completed!</h3>

            <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-100 text-center">
              <div>
                <div className="text-xl font-black text-orange-600">{score} / {questions.length}</div>
                <div className="text-xs text-slate-400">Score</div>
              </div>
              <div>
                <div className="text-xl font-black text-emerald-600">{accuracy}%</div>
                <div className="text-xs text-slate-400">Accuracy</div>
              </div>
              <div>
                <div className="text-xl font-black text-slate-700">{formatTimer(seconds)}</div>
                <div className="text-xs text-slate-400">Time</div>
              </div>
            </div>

            <div className="flex justify-center space-x-3 pt-2">
              <button
                onClick={() => {
                  setSelectedAnswers({});
                  setSubmitted(false);
                  setCurrentIndex(0);
                  setSeconds(0);
                }}
                className="px-5 py-2.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white text-xs font-bold transition"
              >
                🔄 Retake Quiz
              </button>
              <button
                onClick={onRestart}
                className="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50 transition"
              >
                ← Back
              </button>
            </div>
          </div>

          {/* Detailed Question Explanations */}
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-800">Answer Explanations</h4>
            {questions.map((q, idx) => {
              const userChoice = selectedAnswers[q.id];
              const isCorrect = userChoice === q.correct_answer;
              return (
                <div
                  key={q.id || idx}
                  className={`p-5 rounded-2xl border bg-white shadow-sm space-y-3 ${
                    isCorrect ? 'border-emerald-200' : 'border-red-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <h5 className="font-bold text-sm text-slate-900">
                      <span className="text-orange-600 mr-1.5">Q{idx + 1}.</span> {q.question}
                    </h5>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-bold shrink-0 ml-2 ${
                        isCorrect ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                  </div>

                  <div className="text-xs space-y-1">
                    <p className="text-slate-600">
                      <span className="font-bold">Your answer:</span> {userChoice ? `${userChoice})` : 'Not answered'}
                    </p>
                    <p className="text-emerald-700 font-bold">
                      Correct answer: {q.correct_answer})
                    </p>
                  </div>

                  {q.explanation && (
                    <div className="space-y-2">
                      <button
                        onClick={() =>
                          setRevealedExplanations((prev) => ({
                            ...prev,
                            [q.id || idx]: !prev[q.id || idx],
                          }))
                        }
                        className="px-4 py-2 rounded-xl bg-amber-100 hover:bg-amber-200 text-amber-800 text-xs font-bold transition"
                      >
                        💡 {revealedExplanations[q.id || idx] ? 'Hide Hint' : 'Show Hint'}
                      </button>
                      {revealedExplanations[q.id || idx] && (
                        <div className="p-3 rounded-xl bg-slate-50 text-xs text-slate-600 border border-slate-100">
                          <span className="font-bold text-slate-800">Explanation: </span>
                          {q.explanation}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizPage;
