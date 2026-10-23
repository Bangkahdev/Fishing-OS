import { Logo } from "@/components/logo"
import { GithubMark } from "@/components/github-mark"
import { site } from "@/lib/site"

const YEAR = new Date().getFullYear()

const columns = [
  {
    title: "Proyek",
    links: [
      { label: "Repositori", href: site.repo },
      { label: "Rilis", href: site.releases },
      { label: "Issues", href: site.issues },
    ],
  },
  {
    title: "Dokumentasi",
    links: [
      { label: "README", href: `${site.repo}#readme` },
      { label: "Membangun ISO", href: `${site.repo}#membangun-iso` },
      { label: "CI/CD", href: `${site.repo}#cicd-dan-rilis` },
      { label: "Struktur repo", href: `${site.repo}#struktur-repositori` },
    ],
  },
  {
    title: "Keamanan",
    links: [
      { label: "Verifikasi unduhan", href: "#unduh" },
      { label: "Kunci publik", href: `${site.releases}/latest/download/ci-key.asc` },
      { label: "Lisensi GPL-3.0", href: `${site.repo}/blob/main/LICENSE` },
    ],
  },
]

export function Footer() {
  return (
    <footer className="border-t border-border/70 bg-muted/30">
      <div className="mx-auto w-full px-4 py-10 sm:px-8 lg:px-12">
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
              <ul className="mt-2.5 space-y-1.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={l.href}
                      target={l.href.startsWith("#") ? undefined : "_blank"}
                      rel="noreferrer"
                      className="text-[13px] text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-col gap-3 border-t border-border/70 pt-5 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-[12px] text-muted-foreground">
            © {YEAR} Fishing OS · Kode profil dilisensikan{" "}
            {site.license}. Paket di dalam ISO mengikuti lisensi masing-masing dari
            Arch Linux.
          </p>
          <p className="font-mono text-[11.5px] text-muted-foreground">
            Kunci CI · {site.fingerprintFlat.slice(-16)}
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
