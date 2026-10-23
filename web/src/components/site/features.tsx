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
      title="Dirancang untuk dipakai, bukan dipasang"
      description="Tanpa langkah instalasi, tanpa partisi. Semua yang dibutuhkan untuk memperbaiki mesin, mencoba konfigurasi, atau bekerja dari komputer pinjaman sudah ada di satu image."
    >
      <div className="grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => {
          const Icon = icons[f.icon]
          return (
            <article key={f.title} className="border-t border-border/70 pt-4">
              <div className="flex items-center gap-2.5">
                <Icon className="size-4 shrink-0 text-primary" strokeWidth={1.75} />
                <h3 className="text-[15px] font-medium tracking-[-0.01em]">{f.title}</h3>
              </div>
              <p className="mt-2.5 max-w-[42ch] text-[13.5px] leading-relaxed text-pretty text-muted-foreground">
                {f.body}
              </p>
            </article>
          )
        })}
      </div>
    </Section>
  )
}
