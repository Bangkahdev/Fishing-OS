import { useEffect, useState } from "react"
import { DownloadIcon, MenuIcon, XIcon } from "lucide-react"
import { cn } from "cn"
import { Logo } from "@/components/logo"
import { GithubMark } from "@/components/github-mark"
import { ThemeToggle } from "@/components/theme-toggle"
import { buttonVariants } from "@/components/ui/button"
import { site } from "@/lib/site"

const links = [
  { href: "#fitur", label: "Fitur" },
  { href: "#screenshot", label: "Screenshot" },
  { href: "#alat", label: "Toolchain" },
  { href: "#unduh", label: "Unduh" },
  { href: "#mulai", label: "Memulai" },
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
    <header
      className={cn(
        "sticky top-0 z-50 border-b border-transparent transition-colors",
        scrolled && "glass border-border/70"
      )}
    >
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center gap-3 px-4 sm:px-6">
        <a href="#atas" className="shrink-0" aria-label="Fishing OS">
          <Logo />
        </a>

        <nav className="ml-4 hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="rounded-md px-2.5 py-1.5 text-[13.5px] text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              {l.label}
            </a>
          ))}
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
            href="#unduh"
            className={cn(buttonVariants({ size: "sm" }), "hidden gap-1.5 sm:inline-flex")}
          >
            <DownloadIcon className="size-3.5" />
            Unduh
          </a>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Menu"
            aria-expanded={open}
            className={cn(buttonVariants({ variant: "ghost", size: "icon-sm" }), "md:hidden")}
          >
            {open ? <XIcon className="size-4" /> : <MenuIcon className="size-4" />}
          </button>
        </div>
      </div>

      {open && (
        <nav className="glass border-t border-border/70 px-4 pb-3 md:hidden">
          <div className="flex flex-col py-1">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
              >
                {l.label}
              </a>
            ))}
          </div>
        </nav>
      )}
    </header>
  )
}
