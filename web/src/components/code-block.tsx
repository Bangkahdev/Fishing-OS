import { useState } from "react"
import { CheckIcon, CopyIcon } from "lucide-react"
import { cn } from "cn"

type CodeBlockProps = {
  code: string
  language?: string
  className?: string
  compact?: boolean
}

export function CodeBlock({ code, language, className, compact }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1600)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div
      className={cn(
        "group relative -mx-4 overflow-hidden bg-[oklch(0.19_0.02_240)] text-[oklch(0.93_0.01_210)]",
        className
      )}
    >
      <div className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-1.5">
          <span className="font-mono text-xs tracking-wide text-white/70">
          {language ?? "shell"}
        </span>
        <button
          type="button"
          onClick={copy}
          aria-label="Salin perintah"
            className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-xs text-white/80 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/60"
        >
          {copied ? (
            <CheckIcon className="size-3.5" />
          ) : (
            <CopyIcon className="size-3.5" />
          )}
          {copied ? "Tersalin" : "Salin"}
        </button>
      </div>
      <pre
        className={cn(
          "px-4 font-mono leading-relaxed whitespace-pre-wrap break-words",
          compact ? "py-3 text-[13px]" : "py-4 text-[13.5px]"
        )}
      >
        <code>{code}</code>
      </pre>
    </div>
  )
}
