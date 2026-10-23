import { useCallback, useEffect, useState } from "react"
import { ChevronLeftIcon, ChevronRightIcon, ExpandIcon, XIcon } from "lucide-react"
import { cn } from "cn"
import { Section } from "@/components/section"
import {
  screenshots,
  webpSrc,
  webpSrcSet,
  type Screenshot,
} from "@/lib/site"

const SIZES =
  "(min-width: 1280px) 25vw, (min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"

function Shot({
  shot,
  className,
  onClick,
}: {
  shot: Screenshot
  className?: string
  onClick: () => void
}) {
  const [failed, setFailed] = useState(false)
  const frame = shot.wide ? "aspect-[16/9]" : "aspect-[4/3]"

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Perbesar: ${shot.title}`}
      className={cn(
        "group relative block w-full overflow-hidden rounded-xl border border-border/80 bg-muted text-left transition-colors duration-300 hover:border-primary/30 focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none",
        className
      )}
    >
      {failed ? (
        <div className={cn("grid place-items-center bg-muted", frame)}>
          <span className="font-mono text-xs text-muted-foreground">
            {shot.title}
          </span>
        </div>
      ) : (
        <picture className="block">
          <source type="image/webp" srcSet={webpSrcSet(shot)} sizes={SIZES} />
          <img
            src={shot.src}
            alt={shot.alt}
            loading="lazy"
            width={shot.width}
            height={shot.height}
            onError={() => setFailed(true)}
            className={cn(
              "block w-full object-cover",
              shot.wide && "object-contain",
              frame
            )}
          />
        </picture>
      )}
      <span className="absolute top-2.5 right-2.5 grid size-7 place-items-center rounded-md bg-black/55 text-white opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-visible:opacity-100">
        <ExpandIcon className="size-3.5" />
      </span>
    </button>
  )
}

export function Gallery() {
  const [index, setIndex] = useState<number | null>(null)

  const close = useCallback(() => setIndex(null), [])
  const next = useCallback(
    () => setIndex((i) => (i === null ? i : (i + 1) % screenshots.length)),
    []
  )
  const prev = useCallback(
    () => setIndex((i) => (i === null ? i : (i - 1 + screenshots.length) % screenshots.length)),
    []
  )

  useEffect(() => {
    if (index === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close()
      if (e.key === "ArrowRight") next()
      if (e.key === "ArrowLeft") prev()
    }
    document.addEventListener("keydown", onKey)
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = "hidden"
    return () => {
      document.removeEventListener("keydown", onKey)
      document.body.style.overflow = prevOverflow
    }
  }, [index, close, next, prev])

  const active = index === null ? null : screenshots[index]
  const current = index ?? 0

  return (
    <Section
      id="screenshot"
      title="Dijalankan di VirtualBox, bukan mockup"
      description="Semua tangkapan layar diambil dari ISO rilis yang dijalankan di mesin virtual 4 GB RAM: menu boot, desktop setelah autologin, hingga alat di terminal."
    >
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {screenshots.map((s, i) => (
          <figure key={s.src} className="flex min-w-0 flex-col gap-2.5">
            <Shot shot={s} onClick={() => setIndex(i)} />
            <figcaption className="mt-2.5 text-[13px] leading-relaxed text-pretty text-muted-foreground">
              <span className="font-medium text-foreground">{s.title}</span>
              <span aria-hidden> — </span>
              {s.caption}
            </figcaption>
          </figure>
        ))}
      </div>

      {active && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={active.title}
          className="fixed inset-0 z-100 flex flex-col items-center justify-center gap-3 bg-black/85 p-4 backdrop-blur-sm"
          onClick={close}
        >
          <img
            src={webpSrc(active.src, active.variants[active.variants.length - 1])}
            alt={active.alt}
            width={active.width}
            height={active.height}
            onClick={(e) => e.stopPropagation()}
            className="max-h-[82vh] w-auto max-w-full rounded-lg shadow-lg ring-1 ring-white/15"
          />
          <p className="max-w-2xl text-center text-[13px] leading-relaxed text-white/75">
            {active.caption}
          </p>
          <p className="font-mono text-xs text-white/75">
            {current + 1} / {screenshots.length}
          </p>

          <button
            type="button"
            onClick={close}
            aria-label="Tutup"
            className="absolute top-3 right-3 grid size-9 place-items-center rounded-lg bg-white/10 text-white transition-colors hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/60"
          >
            <XIcon className="size-4.5" />
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              prev()
            }}
            aria-label="Sebelumnya"
            className="absolute top-1/2 left-2 grid size-10 -translate-y-1/2 place-items-center rounded-full bg-white/10 text-white transition-colors hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/60"
          >
            <ChevronLeftIcon className="size-5" />
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              next()
            }}
            aria-label="Berikutnya"
            className="absolute top-1/2 right-2 grid size-10 -translate-y-1/2 place-items-center rounded-full bg-white/10 text-white transition-colors hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/60"
          >
            <ChevronRightIcon className="size-5" />
          </button>
        </div>
      )}
    </Section>
  )
}
