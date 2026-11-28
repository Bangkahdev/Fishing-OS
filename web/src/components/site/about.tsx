import { Link } from "react-router-dom"
import { Section } from "@/components/section"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { site } from "@/lib/site"

export default function About() {
  return (
    <div className="mx-auto grid max-w-screen-2xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[14rem_minmax(0,1fr)_12rem] lg:px-8">
      <aside className="hidden lg:block">
        <nav aria-label="Navigasi About" className="space-y-7">
          <section>
            <h2 className="mb-2 px-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
              Tautan
            </h2>
            <ul className="space-y-0.5">
              <li>
                <Link to="/" className="block rounded-md px-3 py-2 text-[13px] transition-colors hover:bg-accent hover:text-foreground">
                  Beranda
                </Link>
              </li>
              <li>
                <Link to="/docs/" className="block rounded-md px-3 py-2 text-[13px] transition-colors hover:bg-accent hover:text-foreground">
                  Dokumentasi
                </Link>
              </li>
              <li>
                <a
                  href={site.repo}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-md px-3 py-2 text-[13px] transition-colors hover:bg-accent hover:text-foreground"
                >
                  Repositori
                </a>
              </li>
            </ul>
          </section>
        </nav>
      </aside>

      <div className="min-w-0">
        <article>
          <Section
            id="tentang"
            title="Tentang Fishing OS"
            description="Proyek sistem operasi lokal yang dikelola secara mandiri, bukan afiliasi resmi Arch Linux."
          >
            <p className="text-[15px] leading-relaxed text-muted-foreground">
              Fishing OS adalah live/rescue ISO berbasis Arch Linux x86_64 untuk
              pengembang. Dikelola oleh
              <a
                href={site.authorUrl}
                target="_blank"
                rel="noreferrer"
                className="font-medium text-foreground underline-offset-4 hover:underline"
              >
                {site.author}
              </a>
              dan diterbitkan sebagai proyek terbuka di GitHub.
            </p>
            <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
              Tujuan utamanya adalah menyediakan lingkungan darurat yang siap pakai
              tanpa mengubah disk: desktop XFCE, peramban, editor, dan toolchain
              pemrograman maupun DevOps. Image diuji di QEMU dan VirtualBox,
              lalu ditandatangani GPG sebelum diterbitkan.
            </p>
          </Section>

          <Section
            id="teknis"
            title="Detail teknis"
            description="Spesifikasi ringkas image dan kunci verifikasi rilis."
          >
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Versi", value: site.fallbackVersion },
                { label: "Arsitektur", value: site.base },
                { label: "Batas ISO", value: site.isoLimit },
                { label: "Lisensi", value: site.license },
              ].map((item) => (
                <Card key={item.label}>
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold">{item.label}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-mono text-xs text-foreground">{item.value}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-border/70 bg-muted/40 p-5">
              <h3 className="text-sm font-semibold mb-2">Kunci publik CI</h3>
              <p className="font-mono text-[12px] leading-relaxed text-muted-foreground">
                {site.fingerprint}
              </p>
              <p className="mt-2 text-[12.5px] text-muted-foreground">
                Penandatangan:{" "}
                <a
                  href="mailto:bangkah@mdhiyaulatha.me"
                  className="text-primary hover:underline"
                >
                  {site.signer}
                </a>
              </p>
              <p className="mt-2 text-[12.5px] text-muted-foreground">
                Unduh kunci publik dari aset rilis terbaru dan verifikasi tanda
                tangan sebelum memakai ISO.
              </p>
            </div>
          </Section>
        </article>

        <Section
          id="lisensi"
          title="Lisensi dan atribusi"
          description="Kode profil dilisensikan GPL-3.0; paket di dalam ISO mengikuti lisensi masing-masing."
          bordered
        >
          <p className="text-[13.5px] leading-relaxed text-muted-foreground">
            Kode profil Fishing OS dilisensikan di bawah{" "}
            <a
              href={`${site.repo}/blob/main/LICENSE`}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-foreground underline-offset-4 hover:underline"
            >
              GNU General Public License v3.0
            </a>
            . Paket perangkat lunak yang dibawa dalam ISO mengikuti lisensi
            masing-masing dari Arch Linux dan upstream.
          </p>
          <p className="mt-3 text-[13.5px] leading-relaxed text-muted-foreground">
            Fishing OS tidak berafiliasi dengan Arch Linux. "Arch Linux" adalah
            merek milik pemegangnya masing-masing. Bagian dari{" "}
            <a
              href="https://bangkah.tech"
              className="underline decoration-border underline-offset-2 hover:text-foreground"
            >
              Bangkah
            </a>
            .
          </p>
        </Section>
      </div>
    </div>
  )
}
