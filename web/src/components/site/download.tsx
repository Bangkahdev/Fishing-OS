import { DownloadIcon, FileKeyIcon, ShieldCheckIcon } from "lucide-react"
import { cn } from "cn"
import { buttonVariants } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CodeBlock } from "@/components/code-block"
import { Section } from "@/components/section"
import { assetUrl, isoName, releaseUrl, site } from "@/lib/site"
import { formatSize, useLatestRelease } from "@/lib/use-release"

function verifyLinux(version: string) {
  return `VERSI=${version}

# 1. Impor kunci publik (aset rilis, atau berkas ci-key.asc di repo)
gpg --import ci-key.asc

# 2. Cocokkan fingerprint dengan yang tertera di halaman ini
gpg --fingerprint bangkah@mdhiyaulatha.me

# 3. Verifikasi tanda tangan checksum
gpg --verify sha256sums.txt.sig sha256sums.txt

# 4. Cocokkan checksum ISO dengan berkasnya
sha256sum -c --ignore-missing sha256sums.txt

# 5. Opsional: verifikasi tanda tangan ISO secara langsung
gpg --verify fishing-os-$VERSI-x86_64.iso.sig fishing-os-$VERSI-x86_64.iso`
}

function verifyWindows(version: string) {
  return `# Cocokkan checksum dengan PowerShell
Get-FileHash .\\fishing-os-${version}-x86_64.iso -Algorithm SHA256

# Hasilnya harus sama dengan baris ISO di sha256sums.txt.
# Untuk tanda tangan GPG, pakai Gpg4win atau WSL.`
}

const rows = [
  { key: "iso", label: "Image live", hint: "BIOS dan UEFI" },
  { key: "sig", label: "Tanda tangan ISO", hint: "GPG detached signature" },
  { key: "sums", label: "Checksum SHA-256", hint: "sha256sums.txt" },
  { key: "sumsSig", label: "Tanda tangan checksum", hint: "sha256sums.txt.sig" },
  { key: "fpr", label: "Fingerprint kunci", hint: "ci-key-fingerprint.txt" },
  { key: "key", label: "Kunci publik", hint: "ci-key.asc, armored" },
]

export function Download() {
  const release = useLatestRelease()
  const version = release?.version ?? site.fallbackVersion

  const assets: Record<string, string> = {
    iso: isoName(version),
    sig: `${isoName(version)}.sig`,
    sums: "sha256sums.txt",
    sumsSig: "sha256sums.txt.sig",
    fpr: "ci-key-fingerprint.txt",
    key: "ci-key.asc",
  }

  const sizeOf = (name: string) =>
    release?.assets.find((a) => a.name === name)?.size ?? 0

  return (
    <Section
      id="unduh"
      title="Ambil ISO, verifikasi, lalu boot"
      description="Rilis GitHub adalah kanal utama. Setiap image disertai checksum dan tanda tangan GPG; cocokkan fingerprint dari minimal dua sumber berbeda sebelum dipakai."
    >
      <div className="grid items-start gap-4 lg:grid-cols-[1fr_0.85fr]">
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-baseline gap-x-2.5 gap-y-1 text-[13px] text-muted-foreground">
              <span className="font-medium text-foreground">Rilis terbaru</span>
              <span aria-hidden>·</span>
              <span className="font-mono text-xs">v{version}</span>
              {release?.publishedAt && (
                <>
                  <span aria-hidden>·</span>
                  <span className="text-xs">
                    {new Date(release.publishedAt).toLocaleDateString("id-ID", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </span>
                </>
              )}
            </div>
            <CardTitle className="mt-1 font-mono text-[15px] break-all">
              {isoName(version)}
            </CardTitle>
          </CardHeader>

          <CardContent className="flex flex-col gap-4">
            <div className="flex flex-wrap gap-2">
              <a
                href={assetUrl(version, assets.iso)}
                className={cn(buttonVariants({ size: "lg" }), "h-11 gap-2 px-5 text-sm")}
              >
                <DownloadIcon className="size-4" />
                Unduh ISO
                {sizeOf(assets.iso) > 0 && (
                  <span className="font-mono text-[11.5px] opacity-70">
                    {formatSize(sizeOf(assets.iso))}
                  </span>
                )}
              </a>
              <a
                href={releaseUrl(version)}
                target="_blank"
                rel="noreferrer"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "h-11 px-5 text-sm"
                )}
              >
                Catatan rilis
              </a>
            </div>

            <Separator />

            <div>
              <h3 className="text-[11.5px] font-medium tracking-[0.12em] text-muted-foreground uppercase">
                Berkas rilis
              </h3>
              <ul className="mt-2 divide-y divide-border/60">
                {rows.map((r) => (
                  <li
                    key={r.key}
                    className="flex items-center gap-3 py-2.5"
                  >
                    <div className="min-w-0 flex-1">
                      <a
                        href={assetUrl(version, assets[r.key])}
                        className="block truncate font-mono text-xs text-primary hover:underline"
                        title={assets[r.key]}
                      >
                        {assets[r.key]}
                      </a>
                      <span className="text-[12.5px] text-muted-foreground">{r.hint}</span>
                    </div>
                    <span className="shrink-0 font-mono text-[12.5px] text-muted-foreground">
                      {sizeOf(assets[r.key]) > 0 ? formatSize(sizeOf(assets[r.key])) : ""}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <p className="text-[13px] leading-relaxed text-muted-foreground">
              Tautan selalu mengarah ke rilis terbaru.
            </p>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <ShieldCheckIcon className="size-4 text-primary" />
                Verifikasi unduhan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="linux">
                <TabsList className="w-full">
                  <TabsTrigger value="linux">Linux / WSL</TabsTrigger>
                  <TabsTrigger value="windows">Windows</TabsTrigger>
                </TabsList>
                <TabsContent value="linux" className="mt-2.5">
                  <CodeBlock code={verifyLinux(version)} compact />
                </TabsContent>
                <TabsContent value="windows" className="mt-2.5">
                  <CodeBlock code={verifyWindows(version)} language="powershell" compact />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <FileKeyIcon className="size-4 text-primary" />
                Kunci penandatangan
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-[13px]">
              <p className="text-muted-foreground">{site.signer}</p>
              <p className="font-mono text-xs leading-relaxed break-all text-balance">
                {site.fingerprint}
              </p>
              <p className="text-[13px] leading-relaxed text-muted-foreground">
                RSA 4096. Peringatan <em>User ID is not certified</em> itu normal;
                cocokkan fingerprint.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </Section>
  )
}
