import { Link } from "react-router-dom"
import { Logo } from "@/components/logo"
import { GithubMark } from "@/components/github-mark"
import { site } from "@/lib/site"

const YEAR = new Date().getFullYear()

const columns: {
  title: string
  links: { label: string; href: string; route?: boolean }[]
}[] = [
  {
    title: "Proyek",
    links: [
      { label: "Repositori", href: site.repo },
      { label: "Rilis", href: site.releases },
      { label: "Issues", href: site.issues },
      { label: "Blog", href: "/blog/", route: true },
      { label: "Tentang", href: "/about", route: true },
    ],
  },
  {
    title: "Dokumentasi",
    links: [
      { label: "Portal dokumentasi", href: "/docs/", route: true },
      { label: "Kapan memakai", href: "/docs/use-cases/", route: true },
      { label: "Unduh & verifikasi", href: "/docs/download/", route: true },
      { label: "Jalankan LiveOS", href: "/docs/liveos/", route: true },
      { label: "Installer ke disk", href: "/docs/installation/", route: true },
      { label: "Pemecahan masalah", href: "/docs/troubleshooting/", route: true },
    ],
  },
  {
    title: "Keamanan",
    links: [
      { label: "Verifikasi unduhan", href: "/#unduh" },
      { label: "Kunci publik", href: `${site.releases}/latest/download/ci-key.asc` },
      { label: "Lisensi GPL-3.0", href: `${site.repo}/blob/main/LICENSE` },
    ],
  },
]

export function Footer() {
  return (
    <footer className="border-t border-border bg-secondary/40">
      <div className="mx-auto w-full max-w-screen-2xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.3fr_repeat(3,0.7fr)]">
          <div>
            <Logo />
            <p className="mt-3 max-w-xs text-[13px] leading-relaxed text-pretty text-muted-foreground">
              {site.tagline}. Dibangun dengan archiso, diuji di QEMU dan
              VirtualBox, lalu ditandatangani sebelum terbit.
            </p>
            <a
              href={site.repo}
              target="_blank"
              rel="noreferrer"
              className="mt-3 inline-flex items-center gap-1.5 text-[13px] text-muted-foreground hover:text-foreground"
            >
              <GithubMark className="size-3.5" />
              Bangkahdev/Fishing-OS
            </a>
            <p className="mt-3 text-[12.5px] text-muted-foreground">
              Dibuat oleh{" "}
              <a
                href={site.authorUrl}
                target="_blank"
                rel="noreferrer"
                className="font-medium text-foreground underline-offset-4 hover:underline"
              >
                {site.author}
              </a>
            </p>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <h3 className="text-xs font-medium tracking-[0.12em] text-muted-foreground uppercase">
                {col.title}
              </h3>
              <ul className="mt-3 space-y-2">
                {col.links.map((l) => {
                  const className =
                    "text-[13px] text-muted-foreground transition-colors hover:text-foreground"
                  if (l.route) {
                    return (
                      <li key={l.label}>
                        <Link to={l.href} className={className}>
                          {l.label}
                        </Link>
                      </li>
                    )
                  }
                  return (
                    <li key={l.label}>
                      <a
                        href={l.href}
                        target={l.href.startsWith("#") || l.href.startsWith("/") ? undefined : "_blank"}
                        rel="noreferrer"
                        className={className}
                      >
                        {l.label}
                      </a>
                    </li>
                  )
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-[12px] text-muted-foreground">
            &copy; {YEAR} Fishing OS. Kode profil dilisensikan {site.license}. Paket
            di dalam ISO mengikuti lisensi masing-masing dari Arch Linux.
          </p>
          <p className="font-mono text-[11.5px] text-muted-foreground">
            Kunci CI / {site.fingerprintFlat.slice(-16)}
          </p>
        </div>
        <p className="mt-2 text-[11.5px] text-muted-foreground">
          Tidak berafiliasi dengan Arch Linux. "Arch Linux" adalah merek milik
          pemegangnya masing-masing. Bagian dari{" "}
          <a
            href="https://bangkah.tech"
            className="underline decoration-border underline-offset-2 hover:text-foreground"
          >
            Bangkah
          </a>
          .
        </p>
      </div>
    </footer>
  )
}
