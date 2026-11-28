import { useEffect, useState } from "react"
import { DownloadIcon, MenuIcon, XIcon } from "lucide-react"
import { Link } from "react-router-dom"
import { cn } from "cn"
import { Logo } from "@/components/logo"
import { GithubMark } from "@/components/github-mark"
import { ThemeToggle } from "@/components/theme-toggle"
import { buttonVariants } from "@/components/ui/button"
import { site } from "@/lib/site"

const links: { href: string; label: string; route?: boolean }[] = [
  { href: "/#fitur", label: "Fitur" },
  { href: "/#tangkapan-layar", label: "Tangkapan Layar" },
  { href: "/#alat", label: "Toolchain" },
  { href: "/#unduh", label: "Unduh" },
  { href: "/docs/", label: "Dokumentasi", route: true },
  { href: "/blog/", label: "Blog", route: true },
  { href: "/about", label: "Tentang", route: true },
]

export function Header() {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <>
      <a
        href="#konten"
        className="sr-only rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-100"
      >
        Lewati ke konten
      </a>

      <header
        className={cn(
          "sticky top-0 z-50 border-b border-border/60 transition-all",
          scrolled ? "glass border-border" : "bg-background",
        )}
      >
        <div className="mx-auto flex h-16 w-full max-w-screen-2xl items-center gap-2 px-4 sm:px-6 lg:px-8">
          <Link to="/" className="shrink-0 rounded-lg" aria-label="Fishing OS">
            <Logo />
          </Link>

          <nav aria-label="Navigasi utama" className="ml-5 hidden items-center gap-0.5 lg:flex">
            {links.map((l) =>
              l.route ? (
                <Link
                  key={l.href}
                  to={l.href}
                  className="rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                >
                  {l.label}
                </Link>
              ) : (
                <a
                  key={l.href}
                  href={l.href}
                  className="rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                >
                  {l.label}
                </a>
              ),
            )}
          </nav>

          <div className="ml-auto flex items-center gap-1.5">
            <a
              href={site.repo}
              target="_blank"
              rel="noreferrer"
              aria-label="Repositori GitHub"
              className={cn(buttonVariants({ variant: "ghost", size: "icon-sm" }))}
            >
              <GithubMark className="size-4" />
            </a>
            <ThemeToggle />
            <a
              href="/#unduh"
              className={cn(
                buttonVariants({ size: "sm" }),
                "hidden h-8 gap-1.5 rounded-lg px-3.5 sm:inline-flex",
              )}
            >
              <DownloadIcon className="size-3.5" />
              Unduh
            </a>
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-label={open ? "Tutup menu" : "Buka menu"}
              aria-expanded={open}
              className={cn(
                buttonVariants({ variant: "ghost", size: "icon-sm" }),
                "lg:hidden",
              )}
            >
              {open ? <XIcon className="size-4" /> : <MenuIcon className="size-4" />}
            </button>
          </div>
        </div>

        {open && (
          <nav
            aria-label="Navigasi seluler"
            className="glass border-t border-border px-4 pb-4 lg:hidden"
          >
            <div className="mx-auto flex max-w-screen-2xl flex-col py-1">
              {links.map((l) =>
                l.route ? (
                  <Link
                    key={l.href}
                    to={l.href}
                    onClick={() => setOpen(false)}
                    className="rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                  >
                    {l.label}
                  </Link>
                ) : (
                  <a
                    key={l.href}
                    href={l.href}
                    onClick={() => setOpen(false)}
                    className="rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                  >
                    {l.label}
                  </a>
                )
              )}
            </div>
          </nav>
        )}
      </header>
    </>
  )
}
