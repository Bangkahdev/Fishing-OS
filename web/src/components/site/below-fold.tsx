import { Features } from "@/components/site/features"
import { Gallery } from "@/components/site/gallery"
import { Toolchain } from "@/components/site/toolchain"
import { Download } from "@/components/site/download"
import { Quickstart } from "@/components/site/quickstart"
import { Documentation } from "@/components/site/documentation"
import { Section } from "@/components/section"
import { assistantFeatures } from "@/lib/site"
import { Limits } from "@/components/site/limits"

export default function BelowFold() {
  return (
    <>
      <Features />
      <Gallery />
      <Toolchain />
      <Download />
      <Quickstart />
      <Documentation />
      <Assistant />
      <Limits />
    </>
  )
}

function Assistant() {
  return (
    <Section
      id="assistant"
      title="Computer-Use Assistant (dalam pengembangan)"
      description="Fitur AI opsional untuk pemasangan ke disk, bukan LiveOS. Fondasi sudah tersedia; model LLM/VLM belum dipaketkan."
      bordered
    >
      <div className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
        {assistantFeatures.map((f) => (
          <article key={f.title} className="rounded-xl border border-border bg-card p-6 hover:border-primary/30 transition-colors">
            <div className="flex items-center gap-2.5 mb-3">
              <span className="size-4 shrink-0 text-primary">◆</span>
              <h3 className="text-[15px] font-medium tracking-tight">{f.title}</h3>
            </div>
            <p className="max-w-[40ch] text-[13.5px] leading-relaxed text-muted-foreground">
              {f.body}
            </p>
          </article>
        ))}
      </div>
    </Section>
  )
}
