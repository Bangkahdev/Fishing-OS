import type { ReactNode } from "react"
import { cn } from "cn"

type SectionProps = {
  id?: string
  title: ReactNode
  description?: ReactNode
  children: ReactNode
  className?: string
  bordered?: boolean
}

export function Section({
  id,
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
        "scroll-mt-16 py-16 sm:py-20",
        bordered && "border-y border-border/60 bg-muted/30",
        className
      )}
    >
      <div className="w-full px-4 sm:px-8 lg:px-12">
        <div className="w-full">
          <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-[2.1rem]">
            {title}
          </h2>
          {description && (
            <p className="mt-3.5 text-[15px] leading-relaxed text-pretty text-muted-foreground">
              {description}
            </p>
          )}
        </div>
        <div className="mt-9 w-full">{children}</div>
      </div>
    </section>
  )
}
