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

  return (
    <section
      id="atas"
      className="relative overflow-hidden border-b border-border bg-background"
    >
      <div
        aria-hidden
        className="grid-bg pointer-events-none absolute inset-0 opacity-40 [mask-image:radial-gradient(75%_55%_at_50%_0%,black,transparent)]"
      />
      <div aria-hidden className="glow pointer-events-none absolute inset-x-0 top-0 h-[460px]" />
      <div className="relative mx-auto grid w-full max-w-screen-2xl gap-10 px-4 pt-14 pb-16 sm:px-6 lg:grid-cols-[1.15fr_1fr] lg:items-center lg:gap-14 lg:px-8 lg:pt-24 lg:pb-24">
        <div className="min-w-0">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1 text-xs font-semibold text-primary uppercase tracking-wider">
            Rilis v{version}
          </span>

          <h1 className="mt-5 text-[2.5rem] leading-[1.05] font-bold tracking-tight text-balance sm:text-5xl lg:text-[4rem]">
            Satu USB,<br />
            <span className="text-primary">toolchain programmer siap pakai.</span>
          </h1>

          <p className="mt-6 max-w-xl text-[16px] leading-relaxed text-pretty text-muted-foreground sm:text-lg">
            Live/rescue ISO berbasis Arch Linux untuk pengembang. Jalankan LiveOS
            dari USB atau mesin virtual, atau siapkan instalasi Arch lewat menu
            Installer to disk. Setiap rilis ditandatangani GPG dan disertai
            checksum SHA-256.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <a
              href={assetUrl(version, isoName(version))}
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-12 gap-2 rounded-lg px-6 text-sm font-medium",
              )}
            >
              <DownloadIcon className="size-4" />
              Unduh ISO
            </a>
            <a
              href="#mulai"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-12 gap-2 rounded-lg px-6 text-sm font-medium",
              )}
            >
              Cara menjalankan <ArrowRightIcon className="size-4" />
            </a>
          </div>

          <p className="mt-12 flex flex-wrap gap-x-3 gap-y-2 border-t border-border pt-6 font-mono text-xs leading-relaxed text-muted-foreground">
            {["v" + version, "Arch Linux x86_64", "≤ 2000 MiB", "BIOS + UEFI", site.license].map(
              (spec) => (
                <span key={spec}>{spec}</span>
              ),
            )}
          </p>
        </div>

        <figure className="relative mx-auto w-full min-w-0 max-w-lg lg:mx-0 lg:justify-self-end">
          <div
            aria-hidden
            className="absolute -inset-3 -z-10 rounded-3xl bg-gradient-to-tr from-primary/25 via-brand-mid/10 to-transparent blur-2xl"
          />
          <div className="rounded-2xl border border-border bg-card p-1.5 shadow-2xl ring-1 ring-black/5">
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
                  className="block w-full rounded-xl"
                />
              </picture>
            ) : (
              <div className="grid aspect-[4/3] place-items-center rounded-xl bg-secondary">
                <span className="font-mono text-sm text-muted-foreground">Fishing OS</span>
              </div>
            )}
          </div>
          <figcaption className="mt-4 text-center text-[12px] font-mono text-muted-foreground">
            Contoh desktop XFCE setelah autologin sebagai liveuser.
          </figcaption>
        </figure>
      </div>
    </section>
  )
}
