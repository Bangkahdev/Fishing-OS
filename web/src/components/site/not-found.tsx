import { Link } from "react-router-dom"
import { Section } from "@/components/section"
import { ArrowLeftIcon } from "lucide-react"

export default function NotFound() {
  return (
    <Section id="not-found" title="Halaman tidak ditemukan" description="Tautan mungkin sudah berubah.">
      <div className="max-w-2xl">
        <p className="text-xs font-semibold tracking-wide text-primary uppercase">
          404
        </p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">
          Halaman tidak ditemukan
        </h1>
        <p className="mt-4 max-w-lg text-[15px] leading-7 text-muted-foreground">
          Tautan yang kamu buka mungkin sudah berpindah atau tidak tersedia. Pilih
          panduan dari navigasi atau kembali ke halaman utama.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            <ArrowLeftIcon className="size-4" />
            Kembali ke beranda
          </Link>
          <Link
            to="/docs/"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-5 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
          >
            Buka dokumentasi
          </Link>
        </div>
      </div>
    </Section>
  )
}
