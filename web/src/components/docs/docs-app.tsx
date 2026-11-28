import { useEffect, useMemo, useRef, useState } from "react"
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  ArrowUpRightIcon,
  BookOpenIcon,
  BotIcon,
  CompassIcon,
  DownloadIcon,
  HardDriveIcon,
  InfoIcon,
  LifeBuoyIcon,
  LightbulbIcon,
  MonitorIcon,
  PencilIcon,
  SearchIcon,
  TerminalIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
  TriangleAlertIcon,
  XIcon,
  type LucideIcon,
} from "lucide-react"
import { CodeBlock } from "@/components/code-block"
import { diagrams } from "@/components/docs/diagrams"
import { site } from "@/lib/site"
import { Link, useLocation, useParams } from "react-router-dom"
import {
  docsNavigation,
  docsPages,
  type DocsPage,
  type DocsSection,
} from "@/lib/docs-content"

const cardIcons: Record<string, LucideIcon> = {
  compass: CompassIcon,
  download: DownloadIcon,
  monitor: MonitorIcon,
  harddrive: HardDriveIcon,
  terminal: TerminalIcon,
  lifebuoy: LifeBuoyIcon,
  bot: BotIcon,
}

const noteStyles = {
  info: {
    Icon: InfoIcon,
    label: "Catatan",
    className: "border-primary/30 bg-primary/5",
    iconClass: "text-primary",
  },
  warning: {
    Icon: TriangleAlertIcon,
    label: "Peringatan",
    className: "border-destructive/35 bg-destructive/5",
    iconClass: "text-destructive",
  },
  tip: {
    Icon: LightbulbIcon,
    label: "Tips",
    className: "border-brand-mid/40 bg-brand-mid/10",
    iconClass: "text-brand-mid",
  },
} as const

function docsHref(slug: string) {
  return slug === "overview" ? "/docs/" : `/docs/${slug}/`
}

function InlineText({ text }: { text: string }) {
  return text.split(/(`[^`]+`)/g).map((part, index) =>
    part.startsWith("`") && part.endsWith("`") ? (
      <code
        key={`${part}-${index}`}
        className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.9em] text-foreground"
      >
        {part.slice(1, -1)}
      </code>
    ) : (
      part
    )
  )
}

function getSearchText(page: DocsPage) {
  return [
    page.title,
    page.summary,
    page.intro,
    ...page.keywords,
    ...page.sections.flatMap((section) => [
      section.title,
      ...(section.paragraphs ?? []),
      ...(section.bullets ?? []),
      ...(section.steps ?? []),
      section.code?.value ?? "",
      section.note?.text ?? "",
      ...(section.links?.map((link) => link.label) ?? []),
    ]),
    ...(page.cards?.flatMap((card) => [card.title, card.description]) ?? []),
  ]
    .join(" ")
    .toLocaleLowerCase("id")
}

function DocSidebar({ currentSlug }: { currentSlug: string | null }) {
  return (
    <nav aria-label="Navigasi dokumentasi" className="space-y-7">
      {docsNavigation.map((group) => (
        <section key={group.title}>
          <h2 className="mb-2 px-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            {group.title}
          </h2>
          <ul className="space-y-0.5">
            {group.slugs.map((slug) => {
              const page = docsPages.find((item) => item.slug === slug)
              if (!page) return null
              const active = page.slug === currentSlug
              return (
                <li key={page.slug}>
                  <Link
                    to={docsHref(page.slug)}
                    aria-current={active ? "page" : undefined}
                    className={`block rounded-md px-3 py-2 text-[13px] transition-colors ${
                      active
                        ? "bg-accent font-medium text-foreground"
                        : "text-muted-foreground hover:bg-accent/70 hover:text-foreground"
                    }`}
                  >
                    {page.title}
                  </Link>
                </li>
              )
            })}
          </ul>
        </section>
      ))}
    </nav>
  )
}

function SearchBox() {
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const results = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("id")
    if (!needle) return []
    return docsPages
      .filter((page) => getSearchText(page).includes(needle))
      .slice(0, 6)
  }, [query])

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault()
        inputRef.current?.focus()
        setOpen(true)
      } else if (event.key === "Escape") {
        setOpen(false)
        inputRef.current?.blur()
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  return (
    <div className="relative w-full sm:max-w-sm">
      <label htmlFor="docs-search" className="sr-only">
        Cari dokumentasi
      </label>
      <SearchIcon
        aria-hidden="true"
        className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
      />
      <input
        ref={inputRef}
        id="docs-search"
        type="search"
        value={query}
        onChange={(event) => {
          setQuery(event.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => window.setTimeout(() => setOpen(false), 120)}
        aria-expanded={open && query.trim().length > 0}
        aria-controls="docs-search-results"
        placeholder="Cari panduan..."
        className="h-10 w-full rounded-lg border border-border bg-background pr-14 pl-9 text-sm placeholder:text-muted-foreground focus-visible:border-ring"
      />
      {query ? (
        <button
          type="button"
          onClick={() => {
            setQuery("")
            inputRef.current?.focus()
          }}
          aria-label="Hapus pencarian"
          className="absolute top-1/2 right-2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"
        >
          <XIcon className="size-4" />
        </button>
      ) : (
        <kbd className="absolute top-1/2 right-2 -translate-y-1/2 rounded border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
          Ctrl K
        </kbd>
      )}

      {open && query.trim() && (
        <div
          id="docs-search-results"
          role="region"
          aria-live="polite"
          aria-label="Hasil pencarian dokumentasi"
          className="absolute top-full right-0 left-0 z-30 mt-2 overflow-hidden rounded-lg border border-border bg-card shadow-xl"
        >
          {results.length ? (
            <ul>
              {results.map((page) => (
                <li key={page.slug}>
                  <Link
                    to={docsHref(page.slug)}
                    onClick={() => setOpen(false)}
                    className="block border-b border-border/70 px-4 py-3 last:border-0 hover:bg-accent"
                  >
                    <span className="block text-sm font-medium">{page.title}</span>
                    <span className="mt-1 block text-xs leading-relaxed text-muted-foreground">
                      {page.summary}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-4 py-3 text-sm text-muted-foreground" role="status">
              Tidak ada panduan yang cocok.
            </p>
          )}
        </div>
      )}
    </div>
  )
}

function renderSection(section: DocsSection) {
  return (
    <section
      key={section.id}
      id={section.id}
      className="scroll-mt-24 border-t border-border/70 pt-7"
    >
      <h2 className="text-xl font-semibold tracking-tight">{section.title}</h2>
      {section.paragraphs?.map((paragraph) => (
        <p
          key={paragraph}
          className="mt-3 text-[15px] leading-7 text-muted-foreground"
        >
          <InlineText text={paragraph} />
        </p>
      ))}
      {section.bullets && (
        <ul className="mt-4 list-disc space-y-2 pl-5 text-[15px] leading-7 text-muted-foreground marker:text-primary">
          {section.bullets.map((item) => (
            <li key={item}>
              <InlineText text={item} />
            </li>
          ))}
        </ul>
      )}
      {section.steps && (
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-[15px] leading-7 text-muted-foreground marker:font-mono marker:text-primary">
          {section.steps.map((item) => (
            <li key={item}>
              <InlineText text={item} />
            </li>
          ))}
        </ol>
      )}
      {section.code && (
        <div className="mt-5 overflow-hidden rounded-lg">
          <CodeBlock code={section.code.value} language={section.code.language} />
        </div>
      )}
      {section.figure && (
        <figure className="mt-5 overflow-hidden rounded-lg border border-border bg-muted/40 p-4">
          {(() => {
            const Diagram = diagrams[section.figure.diagram]
            return <Diagram />
          })()}
          <figcaption className="mt-3 text-center text-xs leading-relaxed text-muted-foreground">
            {section.figure.caption}
          </figcaption>
        </figure>
      )}
      {section.table && (
        <div className="mt-5 overflow-x-auto rounded-lg border border-border">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-muted/60">
                {section.table.headers.map((header) => (
                  <th
                    key={header}
                    className="border-b border-border px-4 py-2.5 text-xs font-semibold tracking-wide text-foreground uppercase"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.table.rows.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className="border-b border-border/60 last:border-0"
                >
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className="px-4 py-2.5 align-top text-[14px] leading-relaxed text-muted-foreground"
                    >
                      <InlineText text={cell} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {section.note && (
        <aside
          aria-label={noteStyles[section.note.type].label}
          className={`mt-5 flex gap-3 rounded-lg border px-4 py-3 text-sm leading-relaxed text-foreground ${noteStyles[section.note.type].className}`}
        >
          {(() => {
            const { Icon, iconClass } = noteStyles[section.note.type]
            return (
              <Icon
                aria-hidden="true"
                className={`mt-0.5 size-4 shrink-0 ${iconClass}`}
              />
            )
          })()}
          <p>
            <span className="mr-1.5 font-semibold">
              {noteStyles[section.note.type].label}:
            </span>
            <InlineText text={section.note.text} />
          </p>
        </aside>
      )}
      {section.links && (
        <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
          {section.links.map((link) => {
            const external = link.href.startsWith("http")
            const className =
              "inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            return (
              <li key={link.href}>
                {external ? (
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noreferrer"
                    className={className}
                  >
                    {link.label}
                    <ArrowUpRightIcon aria-hidden="true" className="size-3.5" />
                  </a>
                ) : (
                  <Link to={link.href} className={className}>
                    {link.label}
                  </Link>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}

function OverviewHero({ page }: { page: DocsPage }) {
  return (
    <section className="relative mb-7 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/10 via-card to-card p-6 sm:p-8">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
        <span className="inline-flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary/15 text-primary">
          <BookOpenIcon aria-hidden="true" className="size-7" />
        </span>
        <div className="min-w-0">
          <p className="text-xs font-semibold tracking-wide text-primary uppercase">
            Dokumentasi
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
            {page.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[15px] leading-7 text-muted-foreground">
            {page.summary}
          </p>
        </div>
      </div>
      <div className="mt-6 flex flex-wrap gap-2.5">
        <Link
          to="/docs/download/"
          className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
        >
          <DownloadIcon aria-hidden="true" className="size-4" />
          Unduh ISO
        </Link>
        <Link
          to="/docs/liveos/"
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          <MonitorIcon aria-hidden="true" className="size-4 text-primary" />
          Jalankan LiveOS
        </Link>
      </div>
    </section>
  )
}

function PageFooter({ editHref }: { editHref: string }) {
  const [feedback, setFeedback] = useState<"yes" | "no" | null>(null)
  return (
    <footer className="mt-9 border-t border-border/70 pt-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs text-muted-foreground">
          <p>Konten mengikuti repository proyek Fishing OS.</p>
          <a
            href={editHref}
            target="_blank"
            rel="noreferrer"
            className="mt-1 inline-flex items-center gap-1 font-medium text-primary hover:underline"
          >
            <PencilIcon aria-hidden="true" className="size-3.5" />
            Edit halaman ini
          </a>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          {feedback ? (
            <span role="status" className="font-medium text-foreground">
              Terima kasih atas masukannya.
            </span>
          ) : (
            <>
              <span>Apakah halaman ini membantu?</span>
              <button
                type="button"
                onClick={() => setFeedback("yes")}
                aria-label="Ya, halaman ini membantu"
                className="inline-flex items-center gap-1 rounded-md border border-border px-2.5 py-1.5 font-medium transition-colors hover:bg-accent hover:text-foreground"
              >
                <ThumbsUpIcon aria-hidden="true" className="size-3.5" />
                Ya
              </button>
              <button
                type="button"
                onClick={() => setFeedback("no")}
                aria-label="Tidak, halaman ini kurang membantu"
                className="inline-flex items-center gap-1 rounded-md border border-border px-2.5 py-1.5 font-medium transition-colors hover:bg-accent hover:text-foreground"
              >
                <ThumbsDownIcon aria-hidden="true" className="size-3.5" />
                Tidak
              </button>
            </>
          )}
        </div>
      </div>
    </footer>
  )
}

export function DocsApp() {
  const location = useLocation()
  const { slug } = useParams<{ slug?: string }>()
  const currentSlug = slug ?? "overview"
  const page = docsPages.find((item) => item.slug === currentSlug) ?? null
  const currentIndex = page
    ? docsPages.findIndex((item) => item.slug === page.slug)
    : -1
  const previous = currentIndex > 0 ? docsPages[currentIndex - 1] : null
  const next =
    currentIndex >= 0 && currentIndex < docsPages.length - 1
      ? docsPages[currentIndex + 1]
      : null

  useEffect(() => {
    if (location.hash) {
      const target = document.getElementById(location.hash.slice(1))
      if (target) {
        target.scrollIntoView()
        return
      }
    }
    window.scrollTo(0, 0)
  }, [location.pathname, location.hash])

  useEffect(() => {
  const title = page
    ? `${page.title} — Dokumentasi Fishing OS`
    : "Halaman tidak ditemukan — Dokumentasi Fishing OS"
  const description =
    page?.summary ?? "Panduan dokumentasi Fishing OS tidak ditemukan."
  const canonicalPath =
    currentSlug === "overview" ? "/docs/" : `/docs/${currentSlug}/`
  const canonicalUrl = `${window.location.origin}${canonicalPath}`

    document.title = title
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute("content", description)
    document
      .querySelector('meta[property="og:title"]')
      ?.setAttribute("content", title)
    document
      .querySelector('meta[property="og:description"]')
      ?.setAttribute("content", description)
    document
      .querySelector('meta[property="og:url"]')
      ?.setAttribute("content", canonicalUrl)
    document
      .querySelector('meta[name="twitter:title"]')
      ?.setAttribute("content", title)
    document
      .querySelector('meta[name="twitter:description"]')
      ?.setAttribute("content", description)
    document
      .querySelector('meta[property="og:type"]')
      ?.setAttribute("content", "article")
    let sectionMeta = document.querySelector<HTMLMetaElement>(
      'meta[property="article:section"]'
    )
    if (!sectionMeta) {
      sectionMeta = document.createElement("meta")
      sectionMeta.setAttribute("property", "article:section")
      document.head.append(sectionMeta)
    }
    sectionMeta.setAttribute("content", page?.group ?? "Dokumentasi")
    document
      .querySelector('meta[name="keywords"]')
      ?.setAttribute(
        "content",
        page ? page.keywords.join(", ") : "Fishing OS, dokumentasi"
      )

    let canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]')
    if (!canonical) {
      canonical = document.createElement("link")
      canonical.rel = "canonical"
      document.head.append(canonical)
    }
    canonical.href = canonicalUrl

    let articleSchema = document.querySelector<HTMLScriptElement>(
      'script[data-docs-article="true"]'
    )
    if (!articleSchema) {
      articleSchema = document.createElement("script")
      articleSchema.type = "application/ld+json"
      articleSchema.dataset.docsArticle = "true"
      document.head.append(articleSchema)
    }
    articleSchema.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "TechArticle",
      headline: title,
      description,
      url: canonicalUrl,
      inLanguage: "id-ID",
      author: {
        "@type": "Organization",
        name: site.name,
        url: site.repo,
      },
    })

    const origin = window.location.origin
    const crumbs = [
      { name: "Beranda", url: `${origin}/` },
      { name: "Dokumentasi", url: `${origin}/docs/` },
    ]
    if (page && page.slug !== "overview") {
      crumbs.push({ name: page.title, url: canonicalUrl })
    }
    let breadcrumbSchema = document.querySelector<HTMLScriptElement>(
      'script[data-docs-crumbs="true"]'
    )
    if (!breadcrumbSchema) {
      breadcrumbSchema = document.createElement("script")
      breadcrumbSchema.type = "application/ld+json"
      breadcrumbSchema.dataset.docsCrumbs = "true"
      document.head.append(breadcrumbSchema)
    }
    breadcrumbSchema.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: crumbs.map((crumb, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: crumb.name,
        item: crumb.url,
      })),
    })
    }, [currentSlug, location.pathname, page])

  return (
    <div className="min-h-dvh bg-background text-foreground">
      <header className="glass sticky top-0 z-50 border-b border-border">
        <div className="mx-auto flex max-w-screen-2xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:px-6 lg:px-8">
          <Link to="/docs/" className="flex shrink-0 items-center gap-2 font-semibold">
            <BookOpenIcon aria-hidden="true" className="size-5 text-primary" />
            <span>Fishing OS</span>
            <span className="font-normal text-muted-foreground">Dokumentasi</span>
          </Link>
          <div className="flex min-w-0 flex-1 items-center gap-4 sm:justify-end">
            <SearchBox />
            <Link
              to="/"
              className="hidden shrink-0 text-sm text-muted-foreground hover:text-foreground sm:inline-flex sm:items-center sm:gap-1"
            >
              <ArrowLeftIcon aria-hidden="true" className="size-3.5" />
              Situs utama
            </Link>
            <Link
              to="/"
              aria-label="Kembali ke situs utama"
              className="shrink-0 rounded px-2 py-1 text-sm text-muted-foreground hover:bg-accent hover:text-foreground sm:hidden"
            >
              Kembali
            </Link>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-screen-2xl px-4 sm:px-6 lg:px-8">
        <details className="border-b border-border py-3 lg:hidden">
          <summary className="cursor-pointer text-sm font-medium">
            Buka navigasi dokumentasi
          </summary>
          <div className="pt-4">
            <DocSidebar currentSlug={page?.slug ?? null} />
          </div>
        </details>

        <div className="grid gap-8 py-8 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-10 lg:py-10 xl:grid-cols-[14rem_minmax(0,1fr)_12rem]">
          <aside className="hidden lg:block">
            <div className="sticky top-20 max-h-[calc(100dvh-6rem)] overflow-y-auto pr-2">
              <DocSidebar currentSlug={page?.slug ?? null} />
            </div>
          </aside>

          <main id="konten" className="min-w-0">
            {page ? (
              <article>
                {page.slug === "overview" && <OverviewHero page={page} />}
                <nav aria-label="Breadcrumb" className="mb-5 text-xs text-muted-foreground">
                  <ol className="flex flex-wrap items-center gap-2">
                    <li>
                      <Link to="/docs/" className="hover:text-foreground">
                        Dokumentasi
                      </Link>
                    </li>
                    {page.slug !== "overview" && (
                      <>
                        <li aria-hidden="true">/</li>
                        <li>{page.group}</li>
                      </>
                    )}
                  </ol>
                </nav>
                <header className="border-b border-border/70 pb-7">
                  {page.slug === "overview" ? (
                    <p className="max-w-3xl text-[15px] leading-7 text-muted-foreground">
                      {page.intro}
                    </p>
                  ) : (
                    <>
                      <p className="text-xs font-semibold tracking-wide text-primary uppercase">
                        {page.group}
                      </p>
                      <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
                        {page.title}
                      </h1>
                      <p className="mt-4 max-w-3xl text-lg leading-8 text-muted-foreground">
                        {page.summary}
                      </p>
                      <p className="mt-4 max-w-3xl text-[15px] leading-7">
                        {page.intro}
                      </p>
                    </>
                  )}
                </header>

                {page.sections.length > 0 && (
                  <details className="my-5 rounded-lg border border-border p-3 xl:hidden">
                    <summary className="cursor-pointer text-sm font-medium">
                      Di halaman ini
                    </summary>
                    <nav aria-label="Isi halaman" className="pt-3">
                      <ul className="space-y-2 border-l border-border pl-3">
                        {page.sections.map((section) => (
                          <li key={section.id}>
                            <a
                              href={`#${section.id}`}
                              className="text-sm text-muted-foreground hover:text-primary"
                            >
                              {section.title}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </nav>
                  </details>
                )}

                {page.cards && (
                  <div className="grid gap-3 py-7 sm:grid-cols-2 xl:grid-cols-3">
                    {page.cards.map((card) => {
                      const Icon = card.icon ? cardIcons[card.icon] : undefined
                      return (
                        <Link
                          key={card.slug}
                          to={docsHref(card.slug)}
                          className="group rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/40 hover:bg-accent/50"
                        >
                          <span className="flex items-center justify-between gap-3">
                            {Icon && (
                              <span className="inline-flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                <Icon aria-hidden="true" className="size-4.5" />
                              </span>
                            )}
                            <ArrowRightIcon
                              aria-hidden="true"
                              className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5"
                            />
                          </span>
                          <span className="mt-3 block text-sm font-semibold">
                            {card.title}
                          </span>
                          <span className="mt-2 block text-[13px] leading-relaxed text-muted-foreground">
                            {card.description}
                          </span>
                        </Link>
                      )
                    })}
                  </div>
                )}

                <div className="space-y-8">
                  {page.sections.map(renderSection)}
                </div>

                {page.related && (
                  <section className="mt-9 border-t border-border/70 pt-6">
                    <h2 className="text-sm font-semibold">Lanjutkan membaca</h2>
                    <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                      {page.related.map((link) => {
                        const external = link.href.startsWith("http")
                        const className =
                          "flex items-center justify-between gap-2 rounded-lg border border-border bg-card px-3 py-2.5 text-sm text-primary hover:bg-accent"
                        const content = (
                          <>
                            {link.label}
                            {external ? (
                              <ArrowUpRightIcon aria-hidden="true" className="size-3.5" />
                            ) : (
                              <ArrowRightIcon aria-hidden="true" className="size-3.5" />
                            )}
                          </>
                        )
                        return (
                          <li key={link.href}>
                            {external ? (
                              <a
                                href={link.href}
                                target="_blank"
                                rel="noreferrer"
                                className={className}
                              >
                                {content}
                              </a>
                            ) : (
                              <Link to={link.href} className={className}>
                                {content}
                              </Link>
                            )}
                          </li>
                        )
                      })}
                    </ul>
                  </section>
                )}

                <nav
                  aria-label="Navigasi halaman dokumentasi"
                  className="mt-9 grid gap-3 border-t border-border/70 pt-5 sm:grid-cols-2"
                >
                  {previous ? (
                    <Link
                      to={docsHref(previous.slug)}
                      className="rounded-lg border border-border p-3 hover:bg-accent"
                    >
                      <span className="flex items-center gap-1 text-xs text-muted-foreground">
                        <ArrowLeftIcon aria-hidden="true" className="size-3" />
                        Sebelumnya
                      </span>
                      <span className="mt-1 block text-sm font-medium">
                        {previous.title}
                      </span>
                    </Link>
                  ) : (
                    <span />
                  )}
                  {next && (
                    <Link
                      to={docsHref(next.slug)}
                      className="rounded-lg border border-border p-3 text-right hover:bg-accent"
                    >
                      <span className="flex items-center justify-end gap-1 text-xs text-muted-foreground">
                        Berikutnya
                        <ArrowRightIcon aria-hidden="true" className="size-3" />
                      </span>
                      <span className="mt-1 block text-sm font-medium">
                        {next.title}
                      </span>
                    </Link>
                  )}
                </nav>

                <PageFooter
                  editHref={`${site.repo}/edit/main/web/src/lib/docs-content.ts`}
                />
              </article>
            ) : (
              <section className="py-12">
                <p className="text-xs font-semibold tracking-wide text-primary uppercase">
                  404
                </p>
                <h1 className="mt-2 text-3xl font-semibold">Halaman tidak ditemukan</h1>
                <p className="mt-3 text-muted-foreground">
                  Tautan mungkin sudah berubah. Pilih panduan dari navigasi atau
                  kembali ke halaman dokumentasi.
                </p>
                <Link
                  to="/docs/"
                  className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
                >
                  <ArrowLeftIcon aria-hidden="true" className="size-4" />
                  Buka dokumentasi
                </Link>
              </section>
            )}
          </main>

          {page && (
            <aside className="hidden xl:block">
              <div className="sticky top-8">
                <h2 className="mb-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Di halaman ini
                </h2>
                <nav aria-label="Isi halaman">
                  <ul className="space-y-2 border-l border-border pl-3">
                    {page.sections.map((section) => (
                      <li key={section.id}>
                        <a
                          href={`#${section.id}`}
                          className="text-xs leading-relaxed text-muted-foreground hover:text-primary"
                        >
                          {section.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </nav>
              </div>
            </aside>
          )}
        </div>
      </div>

      <footer className="border-t border-border/70 bg-card/50">
        <div className="mx-auto flex max-w-screen-2xl flex-col gap-2 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p>Dokumentasi Fishing OS · konten teknis mengikuti repository proyek.</p>
          <div className="flex gap-4">
            <Link to="/" className="hover:text-foreground">
              Situs utama
            </Link>
            <a href="https://github.com/Bangkahdev/Fishing-OS/issues" target="_blank" rel="noreferrer" className="hover:text-foreground">
              Laporkan masalah
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
