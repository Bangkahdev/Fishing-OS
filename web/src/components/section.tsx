import type { ReactNode } from "react"
import { cn } from "cn"

type SectionProps = {
  id?: string
  eyebrow?: string
  title: ReactNode
  description?: ReactNode
  children: ReactNode
  className?: string
  bordered?: boolean
}

export function Section({
  id,
  eyebrow,
  title,
  description,
  children,
  className,
  bordered,
}: SectionProps) {
  return (
    <section
      id={id}
      className={cn(
        "scroll-mt-16 py-14 sm:py-16",
        bordered && "border-y border-border/70 bg-muted/30",
        className
      )}
    >
      <div className="mx-auto w-full max-w-6xl px-4 sm:px-6">
        <div className="max-w-2xl">
          {eyebrow && (
            <p className="font-mono text-[11px] tracking-[0.14em] text-primary uppercase">
              {eyebrow}
            </p>
          )}
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
            {title}
          </h2>
          {description && (
            <p className="mt-3 text-[14.5px] leading-relaxed text-muted-foreground">
              {description}
            </p>
          )}
        </div>
        <div className="mt-8">{children}</div>
      </div>
    </section>
  )
}
