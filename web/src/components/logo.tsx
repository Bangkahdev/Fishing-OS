import { cn } from "cn"

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <img
        src="/media/fishing-logo.png"
        alt=""
        width={512}
        height={512}
        className="size-8 rounded-lg shadow-sm ring-1 ring-brand-deep/30 ring-inset"
      />
      <span className="text-[15px] font-semibold tracking-tight">
        Fishing<span className="text-primary"> OS</span>
      </span>
    </span>
  )
}
