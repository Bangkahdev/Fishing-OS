import { Badge } from "@/components/ui/badge"
import { Section } from "@/components/section"
import { toolGroups } from "@/lib/site"

export function Toolchain() {
  return (
    <Section
      id="alat"
      eyebrow="Isi image"
      title="Alat yang biasanya butuh satu jam untuk dipasang"
      description="Semuanya sudah ada di PATH sejak boot pertama. Versi mengikuti repositori Arch saat image dibangun."
      bordered
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {toolGroups.map((g) => (
          <div
            key={g.label}
            className="rounded-xl border border-border/70 bg-card/60 p-4"
          >
            <h3 className="font-mono text-[11px] tracking-[0.12em] text-muted-foreground uppercase">
              {g.label}
            </h3>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {g.items.map((item) => (
                <Badge key={item} variant="secondary" className="font-mono text-[11.5px]">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-4 max-w-3xl text-[12.5px] leading-relaxed text-muted-foreground">
        Ansible dibawa sebagai <code className="rounded bg-muted px-1 py-0.5 font-mono text-[11.5px]">ansible-core</code>{" "}
        agar ISO tetap kecil. Pasang koleksi yang dibutuhkan dengan{" "}
        <code className="rounded bg-muted px-1 py-0.5 font-mono text-[11.5px]">ansible-galaxy collection install</code>.
      </p>
    </Section>
  )
}
