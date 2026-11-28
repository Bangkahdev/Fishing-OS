import {
  ArrowRightIcon,
  BookOpenIcon,
  DownloadIcon,
  LifeBuoyIcon,
} from "lucide-react"
import { Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Section } from "@/components/section"

const links = [
  {
    icon: BookOpenIcon,
    title: "Panduan lengkap",
    description:
      "Semua panduan Fishing OS dalam satu tempat: dari pengantar, use case, sampai cara memakai tool bawaan.",
    href: "/docs/",
    label: "Buka dokumentasi",
  },
  {
    icon: DownloadIcon,
    title: "Unduh & verifikasi ISO",
    description:
      "Ambil ISO dari rilis resmi, verifikasi tanda tangan GPG, dan cocokkan checksum sebelum boot.",
    href: "/docs/download/",
    label: "Unduh dan verifikasi",
  },
  {
    icon: LifeBuoyIcon,
    title: "Pemecahan masalah",
    description:
      "Langkah awal untuk masalah boot, Wi-Fi, Docker, dan perubahan yang hilang setelah reboot.",
    href: "/docs/troubleshooting/",
    label: "Atasi masalah",
  },
]

export function Documentation() {
  return (
    <Section
      id="dokumentasi"
      title="Dokumentasi Fishing OS"
      description="Panduan terstruktur untuk mulai menggunakan Fishing OS, memahami use case, mengelola tool bawaan, dan mengatasi masalah umum."
      bordered
    >
      <div className="mb-6 flex flex-col gap-4 rounded-xl border border-primary/25 bg-primary/5 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-semibold">Buka portal dokumentasi</h3>
          <p className="mt-1 max-w-2xl text-[13.5px] leading-relaxed text-muted-foreground">
            Cari panduan berdasarkan tugas, jelajahi topik lewat navigasi, atau
            ikuti langkah dari unduh ISO sampai pemecahan masalah.
          </p>
        </div>
        <Link
          to="/docs/"
          className="inline-flex shrink-0 items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Jelajahi dokumentasi
          <ArrowRightIcon className="size-4" />
        </Link>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {links.map((item) => {
          const Icon = item.icon
          return (
            <Card key={item.title}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Icon className="size-4 text-primary" />
                  {item.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                  {item.description}
                </p>
                <Link
                  to={item.href}
                  className="inline-flex items-center gap-1 text-[13px] text-primary hover:underline"
                >
                  {item.label}
                  <ArrowRightIcon className="size-3.5" />
                </Link>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </Section>
  )
}