"use client";

import { useState } from "react";
import axios from "axios";
import { Send, FileText, Link as LinkIcon, Image as ImageIcon, FileUp, Loader2, Bot, CheckCircle } from "lucide-react";

interface GenerateResult {
  status: string;
  platform: string;
  content: string;
  iterations_count: number;
  editor_feedback: string;
}

const INPUT_TABS = [
  { key: "text", label: "Text", icon: FileText },
  { key: "url", label: "URL", icon: LinkIcon },
  { key: "pdf", label: "PDF/Doc", icon: FileUp },
  { key: "image", label: "Image", icon: ImageIcon },
] as const;

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/generate_content";

export default function Home() {
  const [inputType, setInputType] = useState("text");
  const [platform, setPlatform] = useState("Facebook");
  const [tone, setTone] = useState("Humorous");
  const [topic, setTopic] = useState("");
  const [keywords, setKeywords] = useState("");
  const [objective, setObjective] = useState("Sales/Conversion");
  const [targetAudience, setTargetAudience] = useState("");
  const [brandVoice, setBrandVoice] = useState("");
  const [cta, setCta] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [image, setImage] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!topic) {
      setError("Please enter a topic.");
      return;
    }
    setError("");
    setIsLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("input_type", inputType);
    formData.append("topic", topic);
    formData.append("platform", platform);
    formData.append("tone", tone);
    formData.append("keywords", keywords);
    formData.append("objective", objective);
    formData.append("target_audience", targetAudience);
    formData.append("brand_voice", brandVoice);
    formData.append("cta", cta);

    if (inputType === "url" && url) formData.append("url", url);
    if ((inputType === "pdf" || inputType === "docx") && file) formData.append("file", file);
    if (inputType === "image" && image) formData.append("image", image);

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err: unknown) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || "API request failed."
        : "An unexpected error occurred.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const tabClass = (key: string) =>
    `flex-1 flex items-center justify-center gap-1 py-1.5 text-xs font-medium rounded-md ${inputType === key ? "bg-white shadow-sm text-blue-600" : "text-gray-500 hover:text-gray-700"
    }`;

  const inputClass = "w-full border rounded-lg p-2 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none";

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row p-4 gap-6 font-sans">

      {/* Left Panel: Controls */}
      <div className="w-full md:w-1/3 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col gap-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Bot className="text-blue-600" /> OmniContent AI
          </h1>
          <p className="text-sm text-gray-500 mt-1">Multi-Agent Content Creator</p>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
            <select value={platform} onChange={(e) => setPlatform(e.target.value)} className={inputClass}>
              <option value="Facebook">Facebook</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Blog">Blog SEO</option>
              <option value="Instagram">Instagram</option>
              <option value="Email">Email Marketing</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
            <input type="text" value={tone} onChange={(e) => setTone(e.target.value)} className={inputClass} placeholder="e.g. Professional..." />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Topic <span className="text-red-500">*</span></label>
          <textarea value={topic} onChange={(e) => setTopic(e.target.value)} className={`${inputClass} h-24`} placeholder="What should the AI write about..." />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content Objective</label>
            <select value={objective} onChange={(e) => setObjective(e.target.value)} className={inputClass}>
              <option value="Sales/Conversion">Sales / Conversion</option>
              <option value="Brand Awareness">Brand Awareness</option>
              <option value="Education/News">Education / News</option>
              <option value="Engagement">Engagement</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Required Keywords</label>
            <input type="text" value={keywords} onChange={(e) => setKeywords(e.target.value)} className={inputClass} placeholder="discount, free..." />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
          <input type="text" value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} className={inputClass} placeholder="e.g. Gen Z 18-24, busy office workers..." />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brand Voice</label>
            <input type="text" value={brandVoice} onChange={(e) => setBrandVoice(e.target.value)} className={inputClass} placeholder="e.g. Luxury, playful..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Call-to-Action</label>
            <input type="text" value={cta} onChange={(e) => setCta(e.target.value)} className={inputClass} placeholder="e.g. DM us now..." />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Data Source</label>
          <div className="flex bg-gray-100 p-1 rounded-lg">
            {INPUT_TABS.map(({ key, label, icon: Icon }) => (
              <button key={key} onClick={() => setInputType(key)} className={tabClass(key)}>
                <Icon size={14} /> {label}
              </button>
            ))}
          </div>

          <div className="mt-3">
            {inputType === "text" && <p className="text-xs text-gray-500 italic">AI will use only its knowledge and the topic above.</p>}
            {inputType === "url" && <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} className={inputClass} placeholder="Paste article or website URL..." />}
            {inputType === "pdf" && <input type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />}
            {inputType === "image" && <input type="file" accept="image/*" onChange={(e) => setImage(e.target.files?.[0] || null)} className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100" />}
          </div>
        </div>

        {error && <p className="text-sm text-red-500 bg-red-50 p-2 rounded">{error}</p>}

        <button
          onClick={handleGenerate}
          disabled={isLoading}
          className="mt-auto w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:bg-blue-400"
        >
          {isLoading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
          {isLoading ? "Agents working..." : "Generate Content"}
        </button>
      </div>

      {/* Right Panel: Result */}
      <div className="w-full md:w-2/3 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col">
        <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Generated Content</h2>

        {isLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
            <Loader2 className="animate-spin w-10 h-10 text-blue-500 mb-4" />
            <p className="animate-pulse text-sm">Running pipeline (Writer → Editor)...</p>
            <p className="text-xs mt-2">This may take 15-30 seconds.</p>
          </div>
        ) : result ? (
          <div className="flex-1 flex flex-col gap-4">
            <div className="flex items-center gap-4 text-sm text-green-700 bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="flex items-center gap-1"><CheckCircle size={16} /> Approved</div>
              <div><strong>Platform:</strong> {result.platform}</div>
              <div><strong>Iterations:</strong> {result.iterations_count}</div>
            </div>

            <div className="flex-1 bg-gray-50 border rounded-xl p-5 overflow-auto whitespace-pre-wrap text-gray-800 leading-relaxed shadow-inner">
              {result.content}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
            Enter details on the left and click Generate to see results here.
          </div>
        )}
      </div>

    </div>
  );
}