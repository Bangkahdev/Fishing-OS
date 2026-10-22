import {
  HardDriveIcon,
  MonitorIcon,
  PackageIcon,
  ShieldCheckIcon,
  TerminalIcon,
  WifiIcon,
} from "lucide-react"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
      eyebrow="Kenapa Fishing OS"
      title="Dirancang untuk dipakai, bukan dipasang"
      description="Tanpa langkah instalasi, tanpa partisi. Semua yang dibutuhkan untuk memperbaiki mesin, mencoba konfigurasi, atau bekerja dari komputer pinjaman sudah ada di satu image."
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => {
          const Icon = icons[f.icon]
          return (
            <Card key={f.title} className="bg-card/60">
              <CardHeader>
                <span className="mb-1 grid size-8 place-items-center rounded-lg bg-primary/10 text-primary ring-1 ring-primary/15">
                  <Icon className="size-4" />
                </span>
                <CardTitle>{f.title}</CardTitle>
                <CardDescription className="leading-relaxed">{f.body}</CardDescription>
              </CardHeader>
            </Card>
          )
        })}
      </div>
    </Section>
  )
}
