import { useParams } from "react-router-dom"
import { Section } from "@/components/section"
import { Link } from "react-router-dom"
import { ArrowLeftIcon, ArrowRightIcon, ArrowUpRightIcon, TriangleAlertIcon } from "lucide-react"
import { blogPosts, type BlogPost } from "@/lib/blog-posts"
import { CodeBlock } from "@/components/code-block"

function renderSection(section: BlogPost["sections"][number]) {
  return (
    <section key={section.title} className="mt-8 border-t border-border/70 pt-6 scroll-mt-24">
      {section.title && (
        <h2 className="text-xl font-semibold tracking-tight">{section.title}</h2>
      )}
      {section.paragraphs?.map((p) => (
        <p key={p} className="mt-3 text-[15px] leading-7 text-muted-foreground">
          {p}
        </p>
      ))}
      {section.bullets && (
        <ul className="mt-4 list-disc space-y-2 pl-5 text-[15px] leading-7 text-muted-foreground marker:text-primary">
          {section.bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>
      )}
      {section.code && (
        <div className="mt-5 overflow-hidden rounded-lg">
          <CodeBlock code={section.code.value} language={section.code.language} />
        </div>
      )}
      {section.note && (
        <aside
          className="mt-5 flex gap-3 rounded-lg border border-destructive/35 bg-destructive/5 px-4 py-3 text-sm leading-relaxed text-foreground"
        >
          <span className="mt-0.5 size-4 shrink-0 text-destructive">
            <TriangleAlertIcon aria-hidden="true" />
          </span>
          <p>
            <span className="mr-1.5 font-semibold">Peringatan:</span>{" "}
            {section.note.text}
          </p>
        </aside>
      )}
      {section.links && (
        <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
          {section.links.map((l) => (
            <li key={l.href}>
              {l.href.startsWith("http") ? (
                <a
                  href={l.href}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                >
                  {l.label}
                  <ArrowUpRightIcon className="size-3.5" />
                </a>
              ) : (
                <Link
                  to={l.href}
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                >
                  {l.label}
                  <ArrowRightIcon className="size-3.5" />
                </Link>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default function BlogPost() {
  const { slug } = useParams<{ slug?: string }>()
  const post = blogPosts.find((p) => p.slug === slug)

  if (!post) {
    return (
      <Section id="blog" title="Blog & Rilis" description="Postingan tidak ditemukan.">
        <p className="text-muted-foreground">Postingan tidak ditemukan.</p>
        <Link to="/blog/" className="text-sm font-medium text-primary hover:underline">
          Kembali ke daftar blog
        </Link>
      </Section>
    )
  }

  return (
    <div className="mx-auto grid max-w-screen-2xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-10 lg:px-8 xl:grid-cols-[14rem_minmax(0,1fr)_12rem]">
      <aside className="hidden lg:block">
        <div className="sticky top-20 max-h-[calc(100dvh-4rem)] overflow-y-auto pr-2">
          <h2 className="mb-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Tulisan
          </h2>
          <ul className="space-y-2">
            {blogPosts.map((p) => (
              <li key={p.slug}>
                <Link
                  to={`/blog/${p.slug}/`}
                  className={`block rounded-md px-3 py-2 text-[13px] transition-colors ${
                    p.slug === slug
                      ? "bg-accent font-medium text-foreground"
                      : "text-muted-foreground hover:bg-accent/70 hover:text-foreground"
                  }`}
                >
                  {p.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <div className="min-w-0">
        <article>
          <nav aria-label="Breadcrumb" className="mb-5 text-xs text-muted-foreground">
            <ol className="flex flex-wrap items-center gap-2">
              <li>
                <Link to="/blog/" className="hover:text-foreground">
                  Blog
                </Link>
              </li>
              <li aria-hidden="true">/</li>
              <li>{post.title}</li>
            </ol>
          </nav>
          <header className="border-b border-border/70 pb-7">
            <p className="text-xs font-semibold tracking-wide text-primary uppercase">
              {new Date(post.date).toLocaleDateString("id-ID", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
              {post.title}
            </h1>
            <p className="mt-4 max-w-3xl text-lg leading-8 text-muted-foreground">
              {post.summary}
            </p>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center rounded-md border border-border px-2 py-0.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wider"
                >
                  {tag}
                </span>
              ))}
            </div>
          </header>
          <div className="space-y-8">{post.sections.map(renderSection)}</div>
          <footer className="mt-9 border-t border-border/70 pt-5">
            <Link
              to="/blog/"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              <ArrowLeftIcon className="size-4" />
              Kembali ke daftar blog
            </Link>
          </footer>
        </article>
      </div>
    </div>
  )
}
