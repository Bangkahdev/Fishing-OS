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
        "group relative overflow-hidden rounded-xl border border-border/80 bg-[oklch(0.19_0.02_240)] text-[oklch(0.93_0.01_210)]",
        className
      )}
    >
      <div className="flex items-center justify-between gap-3 border-b border-white/10 px-3 py-1.5">
        <span className="font-mono text-[11px] tracking-wide text-white/45">
          {language ?? "shell"}
        </span>
        <button
          type="button"
          onClick={copy}
          aria-label="Salin perintah"
          className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-[11px] text-white/55 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/40"
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
          "overflow-x-auto px-3.5 font-mono leading-relaxed",
          compact ? "py-2.5 text-[12.5px]" : "py-3.5 text-[13px]"
        )}
      >
        <code>{code}</code>
      </pre>
    </div>
  )
}
