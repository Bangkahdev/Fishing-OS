import { useState } from "react"
import { ArrowRightIcon, DownloadIcon } from "lucide-react"
import { cn } from "cn"
import { buttonVariants } from "@/components/ui/button"
import { assetUrl, isoName, site } from "@/lib/site"
import { useLatestRelease } from "@/lib/use-release"

export function Hero() {
  const release = useLatestRelease()
  const version = release?.version ?? site.fallbackVersion
  const [shotOk, setShotOk] = useState(true)

  const specs = [
    `rilis ${version}`,
    "Arch Linux x86_64",
    "\u2264 2000 MiB",
    "BIOS + UEFI",
    site.license,
  ]

  return (
    <section
      id="atas"
      className="relative overflow-x-clip border-b border-border/60 bg-accent/25 dark:bg-accent/15"
    >
      <div className="grid w-full gap-10 px-4 pt-14 pb-14 sm:px-8 lg:grid-cols-[1.05fr_1fr] lg:items-center lg:gap-14 lg:px-12 lg:pt-20 lg:pb-20">
        <div className="min-w-0">
          <h1 className="text-[2.35rem] leading-[1.06] font-semibold tracking-tight text-balance sm:text-5xl lg:text-[3.6rem]">
            Satu USB, semua alat programmer siap pakai.
          </h1>

          <p className="mt-5 max-w-xl text-[15.5px] leading-relaxed text-pretty text-muted-foreground sm:text-base">
            {site.description}
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-3">
            <a
              href={assetUrl(version, isoName(version))}
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 gap-2 rounded-lg px-5 text-sm"
              )}
            >
              <DownloadIcon className="size-4" />
              Unduh ISO
            </a>
            <a
              href="#mulai"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline"
            >
              Cara menjalankan
              <ArrowRightIcon className="size-3.5" />
            </a>
          </div>

          <p className="mt-8 flex flex-wrap gap-x-3 gap-y-1 border-t border-border/70 pt-4 font-mono text-xs leading-relaxed text-muted-foreground">
            {specs.map((spec) => (
              <span key={spec}>{spec}</span>
            ))}
          </p>
        </div>

        <figure className="min-w-0">
          {shotOk ? (
            <picture>
              <source
                type="image/webp"
                srcSet="/screenshots/02-desktop-480.webp 480w, /screenshots/02-desktop-768.webp 768w, /screenshots/02-desktop-1024.webp 1024w"
                sizes="(min-width: 1024px) 45vw, 100vw"
              />
              <img
                src="/screenshots/02-desktop.png"
                alt="Desktop XFCE Fishing OS setelah boot otomatis sebagai liveuser"
                width={1024}
                height={768}
                fetchPriority="high"
                decoding="async"
                onError={() => setShotOk(false)}
                className="block w-full rounded-lg border border-border/80"
              />
            </picture>
          ) : (
            <div className="grid aspect-[4/3] place-items-center rounded-lg border border-border/80 bg-brand-deep">
              <span className="font-mono text-sm text-white/80">Fishing OS</span>
            </div>
          )}
          <figcaption className="mt-2.5 font-mono text-xs text-muted-foreground">
            Desktop XFCE setelah autologin · rilis {version}
          </figcaption>
        </figure>
      </div>
    </section>
  )
}
