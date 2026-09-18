import { useState, useEffect } from 'react';
import axios from 'axios';
import QuizPage from './QuizPage';
import { ClipLoader } from 'react-spinners';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const App = () => {
  const [file, setFile] = useState(null);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [fileMeta, setFileMeta] = useState(null);
  const [topic, setTopic] = useState('');
  const [rawText, setRawText] = useState('');
  const [inputMode, setInputMode] = useState('pdf'); // 'pdf' | 'text' | 'sample'
  const [difficulty, setDifficulty] = useState('Medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [provider, setProvider] = useState('auto');
  const [quizResult, setQuizResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sampleTopics, setSampleTopics] = useState([]);

  useEffect(() => {
    // Fetch sample topics on mount
    axios.get(`${API_BASE}/api/sample-topics`)
      .then(res => setSampleTopics(res.data))
      .catch(err => console.warn('Could not load sample topics', err));
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFileUploaded(true);
      setFileMeta(response.data);
      setRawText(response.data.extracted_text);
      if (!topic) {
        setTopic(response.data.filename.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
      }
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.detail || 'Failed to upload and parse PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = async () => {
    setLoading(true);
    setError(null);

    let contentToUse = rawText;
    if (inputMode === 'pdf' && !contentToUse) {
      setError('Please upload a PDF first');
      setLoading(false);
      return;
    }
    if (inputMode === 'text' && !contentToUse.trim()) {
      setError('Please paste study text or notes');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/api/generate`, {
        topic: topic || 'General Study',
        content: contentToUse,
        num_questions: parseInt(numQuestions),
        difficulty: difficulty,
        provider: provider,
      });
      setQuizResult(response.data);
    } catch (err) {
      console.error('Error generating quiz:', err);
      setError(err.response?.data?.detail || 'Failed to generate quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (sample) => {
    setTopic(sample.title);
    setRawText(sample.text);
    setInputMode('sample');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setQuizResult(null)}>
            <img src="/logo.jpg" alt="Phoenix" className="w-10 h-10 rounded-xl object-cover shadow-md shadow-orange-500/20" />
            <div>
              <span className="text-xl font-extrabold text-orange-600">Phoenix</span>
              <span className="text-xs ml-2 px-2 py-0.5 rounded-full font-semibold bg-orange-50 text-orange-700 border border-orange-200">AI</span>
            </div>
          </div>
          <div className="text-xs text-slate-500 font-medium">
            FastAPI + React Interactive Quiz Engine
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {quizResult ? (
          <QuizPage
            quizResult={quizResult}
            onRestart={() => setQuizResult(null)}
          />
        ) : (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
                Transform Materials into Interactive Quizzes
              </h1>
              <p className="text-sm text-slate-600">
                Upload lecture slides, past exams, study guides, or paste text to generate instant questions with answer explanations.
              </p>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 font-medium flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError(null)} className="text-red-500 font-bold">✕</button>
              </div>
            )}

            {/* Input Selection Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              {/* Input Mode Tabs */}
              <div className="flex border-b border-slate-200 bg-slate-50 text-sm font-semibold">
                <button
                  onClick={() => setInputMode('pdf')}
                  className={`flex-1 py-3.5 px-4 text-center border-b-2 transition ${
                    inputMode === 'pdf' ? 'border-orange-600 text-orange-600 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900'
                  }`}
                >
                  📄 Upload PDF
                </button>
                <button
                  onClick={() => setInputMode('text')}
                  className={`flex-1 py-3.5 px-4 text-center border-b-2 transition ${
                    inputMode === 'text' ? 'border-orange-600 text-orange-600 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900'
                  }`}
                >
                  ✍️ Paste Text
                </button>
                <button
                  onClick={() => setInputMode('sample')}
                  className={`flex-1 py-3.5 px-4 text-center border-b-2 transition ${
                    inputMode === 'sample' ? 'border-orange-600 text-orange-600 bg-white' : 'border-transparent text-slate-600 hover:text-slate-900'
                  }`}
                >
                  💡 Sample Topics
                </button>
              </div>

              <div className="p-6 space-y-5">
                {/* PDF Mode */}
                {inputMode === 'pdf' && (
                  <div className="space-y-4">
                    <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-orange-500 transition cursor-pointer bg-slate-50/50">
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-5 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                      />
                      <p className="text-xs text-slate-400 mt-2">Supports any PDF document with extractable text</p>
                    </div>

                    {file && !fileUploaded && (
                      <button
                        onClick={handleUpload}
                        disabled={loading}
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-2.5 px-4 rounded-xl text-sm transition shadow-sm"
                      >
                        {loading ? 'Extracting text...' : 'Upload & Process PDF'}
                      </button>
                    )}

                    {fileUploaded && fileMeta && (
                      <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center justify-between">
                        <div>
                          <span className="font-bold">{fileMeta.filename}</span>
                          <span className="ml-2 text-emerald-600">({fileMeta.page_count} pages, ~{fileMeta.word_count} words)</span>
                        </div>
                        <span className="font-bold text-emerald-700">✓ Ready</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Text Mode */}
                {inputMode === 'text' && (
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Paste Notes / Content</label>
                    <textarea
                      rows={6}
                      value={rawText}
                      onChange={(e) => setRawText(e.target.value)}
                      placeholder="Paste textbook excerpt, lecture notes, or syllabus here..."
                      className="w-full p-3.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-orange-500 focus:outline-none text-sm"
                    />
                  </div>
                )}

                {/* Sample Mode */}
                {inputMode === 'sample' && (
                  <div className="space-y-3">
                    <p className="text-xs text-slate-500">Choose a pre-packaged topic to test immediately:</p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                      {sampleTopics.map((s) => (
                        <button
                          key={s.id}
                          onClick={() => handleSelectSample(s)}
                          className={`p-3 rounded-xl border text-left text-xs transition ${
                            topic === s.title ? 'border-orange-600 bg-orange-50/70 font-semibold' : 'border-slate-200 hover:border-orange-300 bg-slate-50'
                          }`}
                        >
                          <div className="font-bold text-slate-900">{s.title}</div>
                          <div className="text-slate-500 mt-1 line-clamp-2">{s.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quiz Settings */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-200">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Questions</label>
                    <select
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-orange-500 focus:outline-none"
                    >
                      <option value="3">3 Questions</option>
                      <option value="5">5 Questions</option>
                      <option value="10">10 Questions</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Difficulty</label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-orange-500 focus:outline-none"
                    >
                      <option value="Easy">Easy</option>
                      <option value="Medium">Medium</option>
                      <option value="Hard">Hard</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    onClick={handleStartQuiz}
                    disabled={loading}
                    className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-xl text-sm shadow-md transition flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <ClipLoader color="#ffffff" size={20} />
                    ) : (
                      <>
                        <span>✨</span>
                        <span>Generate & Start Quiz</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
