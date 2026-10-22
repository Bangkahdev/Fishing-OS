import { useState } from "react"
import { ArrowRightIcon, DownloadIcon } from "lucide-react"
import { cn } from "cn"
import { buttonVariants } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { assetUrl, isoName, site } from "@/lib/site"
import { GithubMark } from "@/components/github-mark"
import { useLatestRelease } from "@/lib/use-release"

export function Hero() {
  const release = useLatestRelease()
  const version = release?.version ?? site.fallbackVersion
  const [shotOk, setShotOk] = useState(true)

  return (
    <section id="atas" className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(120%_80%_at_50%_-10%,var(--color-accent)_0%,transparent_55%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.35] [background-image:linear-gradient(to_right,var(--color-border)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-border)_1px,transparent_1px)] [background-size:64px_64px] [mask-image:radial-gradient(70%_60%_at_50%_0%,black,transparent)]"
      />

      <div className="mx-auto grid w-full max-w-6xl gap-10 px-4 pt-12 pb-14 sm:px-6 lg:grid-cols-[1.05fr_1fr] lg:items-center lg:gap-8 lg:pt-16 lg:pb-20">
        <div>
          <Badge variant="outline" className="gap-1.5 border-primary/30 bg-primary/5 text-primary">
            <span className="relative flex size-1.5">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
              <span className="relative inline-flex size-1.5 rounded-full bg-primary" />
            </span>
            Rilis v{version} · {site.base}
          </Badge>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-[3.4rem] lg:leading-[1.05]">
            Satu USB,{" "}
            <span className="bg-gradient-to-br from-brand-mid to-brand-bright bg-clip-text text-transparent">
              seluruh toolchain
            </span>{" "}
            siap pakai.
          </h1>

          <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-muted-foreground sm:text-base">
            {site.description}
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-2.5">
            <a
              href={assetUrl(version, isoName(version))}
              className={cn(buttonVariants({ size: "lg" }), "h-10 gap-2 px-4 text-sm")}
            >
              <DownloadIcon className="size-4" />
              Unduh ISO
            </a>
            <a
              href={site.repo}
              target="_blank"
              rel="noreferrer"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-10 gap-2 px-4 text-sm"
              )}
            >
              <GithubMark className="size-4" />
              Lihat sumber
            </a>
            <a
              href="#mulai"
              className="inline-flex items-center gap-1 px-1.5 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              Cara menjalankan
              <ArrowRightIcon className="size-3.5" />
            </a>
          </div>

          <dl className="mt-8 grid max-w-md grid-cols-2 gap-x-6 gap-y-3 text-[13px] sm:grid-cols-4">
            {[
              ["Dasar", "Arch Linux"],
              ["Ukuran", "≤ 2000 MiB"],
              ["Firmware", "BIOS + UEFI"],
              ["Lisensi", site.license],
            ].map(([k, v]) => (
              <div key={k}>
                <dt className="text-[11px] tracking-wide text-muted-foreground uppercase">
                  {k}
                </dt>
                <dd className="mt-0.5 font-medium">{v}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="relative">
          <div
            aria-hidden
            className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-tr from-brand-deep/25 via-brand-mid/15 to-brand-bright/20 blur-2xl"
          />
          <figure className="overflow-hidden rounded-xl border border-border/80 bg-card shadow-2xl shadow-brand-deep/20 ring-1 ring-black/5">
            <div className="flex items-center gap-1.5 border-b border-border/70 bg-muted/60 px-3 py-2">
              <span className="size-2 rounded-full bg-[oklch(0.7_0.17_25)]" />
              <span className="size-2 rounded-full bg-[oklch(0.78_0.15_85)]" />
              <span className="size-2 rounded-full bg-[oklch(0.72_0.14_145)]" />
              <span className="ml-2 font-mono text-[10.5px] text-muted-foreground">
                Fishing OS Live User — XFCE
              </span>
            </div>
            {shotOk ? (
              <img
                src="/screenshots/02-desktop.png"
                alt="Desktop XFCE Fishing OS setelah boot otomatis sebagai liveuser"
                width={1024}
                height={768}
                onError={() => setShotOk(false)}
                className="block w-full"
              />
            ) : (
              <div className="grid aspect-[4/3] place-items-center bg-gradient-to-br from-brand-deep to-brand-mid">
                <span className="font-mono text-sm text-white/70">Fishing OS</span>
              </div>
            )}
          </figure>
        </div>
      </div>
    </section>
  )
}
