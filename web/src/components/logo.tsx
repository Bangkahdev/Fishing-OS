import { cn } from "cn"

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <picture>
        <source type="image/webp" srcSet="/media/fishing-logo-128.webp" />
        <img
          src="/media/fishing-logo-128.png"
          alt=""
          width={128}
          height={128}
          className="size-9 rounded-xl ring-1 ring-border"
        />
      </picture>
      <span className="text-[15.5px] font-semibold tracking-tight">
        Fishing<span className="text-primary"> OS</span>
      </span>
    </span>
  )
}
