import { useCallback, useEffect, useState } from "react"
import { ChevronLeftIcon, ChevronRightIcon, ExpandIcon, XIcon } from "lucide-react"
import { cn } from "cn"
import { Section } from "@/components/section"
import { screenshots } from "@/lib/site"

function Shot({
  src,
  alt,
  className,
  onClick,
}: {
  src: string
  alt: string
  className?: string
  onClick: () => void
}) {
  const [failed, setFailed] = useState(false)

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Perbesar: ${alt}`}
      className={cn(
        "group relative block overflow-hidden rounded-xl border border-border/80 bg-card text-left shadow-sm transition-shadow hover:shadow-lg focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none",
        className
      )}
    >
      {failed ? (
        <div className="grid aspect-[4/3] place-items-center bg-gradient-to-br from-brand-deep to-brand-mid">
          <span className="font-mono text-xs text-white/70">{alt}</span>
        </div>
      ) : (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          width={1024}
          height={768}
          onError={() => setFailed(true)}
          className="block aspect-[4/3] w-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
        />
      )}
      <span className="absolute inset-x-0 bottom-0 flex items-end justify-between gap-3 bg-gradient-to-t from-black/70 via-black/20 to-transparent px-3 pt-8 pb-2.5 opacity-0 transition-opacity group-hover:opacity-100">
        <span className="text-[12px] font-medium text-white">{alt}</span>
        <ExpandIcon className="size-3.5 shrink-0 text-white/80" />
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

  return (
    <Section
      id="screenshot"
      eyebrow="Tampilan"
      title="Dijalankan di VirtualBox, bukan mockup"
      description="Semua tangkapan layar diambil dari ISO rilis yang dijalankan di mesin virtual 4 GB RAM: menu boot, desktop setelah autologin, hingga alat di terminal."
    >
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {screenshots.map((s, i) => (
          <figure key={s.src} className="flex flex-col gap-2">
            <Shot src={s.src} alt={s.title} onClick={() => setIndex(i)} />
            <figcaption className="text-[12.5px] leading-snug text-muted-foreground">
              <span className="font-medium text-foreground">{s.title}</span> — {s.caption}
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
            src={active.src}
            alt={active.title}
            onClick={(e) => e.stopPropagation()}
            className="max-h-[82vh] w-auto max-w-full rounded-lg shadow-2xl ring-1 ring-white/15"
          />
          <p className="max-w-2xl text-center text-[13px] text-white/75">
            {active.caption}
          </p>

          <button
            type="button"
            onClick={close}
            aria-label="Tutup"
            className="absolute top-3 right-3 grid size-9 place-items-center rounded-lg bg-white/10 text-white hover:bg-white/20"
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
            className="absolute top-1/2 left-2 grid size-10 -translate-y-1/2 place-items-center rounded-full bg-white/10 text-white hover:bg-white/20"
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
            className="absolute top-1/2 right-2 grid size-10 -translate-y-1/2 place-items-center rounded-full bg-white/10 text-white hover:bg-white/20"
          >
            <ChevronRightIcon className="size-5" />
          </button>
        </div>
      )}
    </Section>
  )
}
