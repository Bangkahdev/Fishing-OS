import {
  HardDriveIcon,
  MonitorIcon,
  PackageIcon,
  ShieldCheckIcon,
  TerminalIcon,
  WifiIcon,
} from "lucide-react"
import { Section } from "@/components/section"
import { features } from "@/lib/site"

const icons = {
  terminal: TerminalIcon,
  monitor: MonitorIcon,
  package: PackageIcon,
  wifi: WifiIcon,
  shield: ShieldCheckIcon,
  harddrive: HardDriveIcon,
}

export function Features() {
  return (
    <Section
      id="fitur"
      title="Pilih LiveOS atau siapkan instalasi Arch"
      description="LiveOS berjalan dari USB tanpa mengubah disk. Entri Installer to disk membuka archinstall untuk menyiapkan instalasi Arch secara terpisah; installer ini tidak menyalin semua paket dan konfigurasi LiveOS."
    >
      <div className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => {
          const Icon = icons[f.icon]
          return (
            <article key={f.title} className="rounded-xl border border-border bg-card p-6 hover:border-primary/30 transition-colors">
              <div className="flex items-center gap-2.5 mb-3">
                <Icon className="size-4 shrink-0 text-primary" strokeWidth={1.75} />
                <h3 className="text-[15px] font-medium tracking-tight">{f.title}</h3>
              </div>
              <p className="max-w-[42ch] text-[13.5px] leading-relaxed text-pretty text-muted-foreground">
                {f.body}
              </p>
            </article>
          )
        })}
      </div>
    </Section>
  )
}
