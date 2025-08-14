// src/components/AnswerCard.tsx
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import { Badge } from "@/components/ui/badge";
import { Loader2, AlertTriangle, Copy, Download } from "lucide-react";
import { toast } from "sonner";

type AnswerCardProps = {
  role: "user" | "assistant" | "system";
  content: string | null;
  createdAt: string;
  isLoading?: boolean;
  isError?: boolean;
  images?: string[];
};

export default function AnswerCard({
  role,
  content,
  createdAt,
  isLoading = false,
  isError = false,
  images,
}: AnswerCardProps) {
  const time = new Date(createdAt).toLocaleTimeString();

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Copied to clipboard");
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-xl px-4 py-3 rounded-lg shadow-sm text-sm bg-white border self-start animate-pulse">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="outline" className="text-xs border-gray-400 text-gray-700">
            Assistant
          </Badge>
          <span className="text-[10px] text-gray-400 ml-auto">{time}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-500">
          <Loader2 className="w-4 h-4 animate-spin" />
          Generating response...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-xl px-4 py-3 rounded-lg shadow-sm text-sm bg-red-50 border border-red-300 self-start">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="outline" className="text-xs border-red-500 text-red-600">
            System
          </Badge>
          <span className="text-[10px] text-gray-400 ml-auto">{time}</span>
        </div>
        <div className="flex items-center gap-2 text-red-600">
          <AlertTriangle className="w-4 h-4" />
          An error occurred. Please try again.
        </div>
      </div>
    );
  }

  const parseSections = (text: string) => {
    const result: { finalAnswer: string | null; analysis: string | null; code: string | null } = {
      finalAnswer: null,
      analysis: null,
      code: null,
    };
  
    // Stop at the next header OR true end-of-string
    const re =
    /^\s*=== (FINAL ANSWER|ANALYSIS|CODE) ===\s*([\s\S]*?)(?=^\s*=== (?:FINAL ANSWER|ANALYSIS|CODE) ===\s*|(?![\s\S]))/gm;

    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      const section = m[1];
      const body = m[2].trim();
      if (section === "FINAL ANSWER") result.finalAnswer = body;
      else if (section === "ANALYSIS") result.analysis = body;
      else if (section === "CODE") result.code = body;
    }
  
    return result;
  };  

  const { finalAnswer, analysis, code } = parseSections(content || "");

  async function downloadImage(src: string, filename: string) {
        try{
        const response = await fetch(src);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        toast.error("Failed to download image");
    }
  }

  return (
    <div
      className={`relative group max-w-xl px-4 py-3 rounded-lg shadow-sm text-sm ${
        role === "user" ? "bg-amber-100 self-end ml-auto" : "bg-white border self-start"
      }`}
    >
      {content && (
        <div className="absolute top-2 right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
          <div className="relative group/tooltip">
            <button
              onClick={() => handleCopy(content)}
              className="text-gray-400 hover:text-gray-600"
            >
              <Copy size={14} />
            </button>
            <div className="absolute right-0 bottom-full mb-1 hidden group-hover/tooltip:block bg-gray-800 text-white text-xs px-2 py-1 rounded shadow-sm z-10 whitespace-nowrap">
              Copy message
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center gap-2 mb-1">
        <Badge
          variant="outline"
          className={`text-xs ${
            role === "user"
              ? "border-amber-600 text-amber-700"
              : "border-gray-400 text-gray-700"
          }`}
        >
          {role === "user" ? "You" : "Assistant"}
        </Badge>
        <span className="text-[10px] text-gray-400 ml-auto">{time}</span>
      </div>

      {finalAnswer && (
        <div className="mb-2">
          <p className="font-semibold text-gray-800">✅ Final Answer</p>
          <div className="prose prose-sm text-gray-800 whitespace-pre-wrap">
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{finalAnswer}</ReactMarkdown>
          </div>
        </div>
      )}

      {analysis && (
        <details className="mb-2">
          <summary className="cursor-pointer text-sm font-medium text-gray-700">🧠 Analysis</summary>
          <div className="mt-2 prose prose-sm text-gray-700 whitespace-pre-wrap">
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{analysis}</ReactMarkdown>
          </div>
        </details>
      )}

      {code && (
        <details>
          <summary className="cursor-pointer text-sm font-medium text-gray-700">🧾 Code</summary>
          <div className="prose prose-sm whitespace-pre-wrap [&_code]:text-xs [&_pre]:text-xs [&_pre]:p-2">
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{"```python\n" + code + "\n```"}</ReactMarkdown>
          </div>
        </details>
      )}

      {!finalAnswer && !analysis && !code && content && (
        <div className="prose prose-sm text-gray-800 whitespace-pre-wrap">
          <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{content}</ReactMarkdown>
        </div>
      )}

    {images && images.length > 0 && (
    <div className="mt-2 space-y-4">
        {images.map((src, i) => (
        <div key={i} className="flex flex-col items-start gap-1">
            <img
            src={src}
            alt={`attachment ${i + 1}`}
            className="rounded shadow max-w-full"
            loading="lazy"
            decoding="async"
            />
            <button
            onClick={() => downloadImage(src, `plot-${i + 1}.png`)}
            className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
            <Download size={12} />
            Download
            </button>
        </div>
        ))}
        </div>
    )}
    </div>
  );
}
