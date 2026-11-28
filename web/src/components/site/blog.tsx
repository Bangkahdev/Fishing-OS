import { Link } from "react-router-dom"
import { Section } from "@/components/section"
import { blogPosts } from "@/lib/blog-posts"
import { ArrowRightIcon } from "lucide-react"

export default function Blog() {
  const posts = [...blogPosts].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  )

  return (
    <Section
      id="blog"
      title="Blog & Rilis"
      description="Berita terbaru, catatan rilis, dan perkembangan Fishing OS serta Computer-Use Assistant."
    >
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => {
          return (
            <article
              key={post.slug}
              className="rounded-xl border border-border/70 bg-card p-6 hover:border-primary/30 transition-colors group"
            >
              <div className="flex flex-wrap gap-1.5 mb-3">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center rounded-md border border-border px-2 py-0.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wider"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <time className="text-[12px] text-muted-foreground">
                {new Date(post.date).toLocaleDateString("id-ID", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
              </time>
              <h3 className="mt-2 text-xl font-semibold tracking-tight group-hover:text-primary transition-colors">
                {post.title}
              </h3>
              <p className="mt-3 text-[13.5px] leading-relaxed text-muted-foreground">
                {post.summary}
              </p>
              <Link
                to={`/blog/${post.slug}/`}
                className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
              >
                Baca selengkapnya <ArrowRightIcon className="size-3.5" />
              </Link>
            </article>
          )
        })}
      </div>
    </Section>
  )
}
