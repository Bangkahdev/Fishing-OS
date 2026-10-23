import { Badge } from "@/components/ui/badge"
import { Section } from "@/components/section"
import { toolGroups } from "@/lib/site"

export function Toolchain() {
  return (
    <Section
      id="alat"
      title="Perkakas yang biasanya butuh satu jam untuk dipasang"
      description="Semuanya sudah ada di PATH sejak boot pertama. Versi mengikuti repositori Arch saat image dibangun."
      bordered
    >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {toolGroups.map((g) => (
          <div
            key={g.label}
            className="rounded-xl border border-border/70 bg-card p-4"
          >
            <h3 className="font-mono text-xs tracking-[0.12em] text-muted-foreground uppercase">
              {g.label}
            </h3>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {g.items.map((item) => (
                <Badge key={item} variant="secondary" className="font-mono text-xs">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-5 max-w-3xl text-[13.5px] leading-relaxed text-muted-foreground">
        Ansible dibawa sebagai <code className="rounded bg-muted px-1 py-0.5 font-mono text-xs">ansible-core</code>{" "}
        agar ISO tetap kecil. Pasang koleksi yang dibutuhkan dengan{" "}
        <code className="rounded bg-muted px-1 py-0.5 font-mono text-xs">ansible-galaxy collection install</code>.
      </p>
    </Section>
  )
}
