import { InfoIcon } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CodeBlock } from "@/components/code-block"
import { Section } from "@/components/section"
import { commands, isoName, site } from "@/lib/site"
import { useLatestRelease } from "@/lib/use-release"

export function Quickstart() {
  const release = useLatestRelease()
  const version = release?.version ?? site.fallbackVersion

  return (
    <Section
      id="mulai"
      title="Cara menjalankan LiveOS"
      description="Coba ISO di mesin virtual atau tulis ke USB untuk boot langsung. Secure Boot harus dimatikan pada kedua jalur."
      bordered
    >
      <div className="grid items-start gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardContent>
            <Tabs defaultValue="vm">
              <TabsList>
                <TabsTrigger value="vm">Mesin virtual</TabsTrigger>
                <TabsTrigger value="usb">USB</TabsTrigger>
              </TabsList>

              <TabsContent value="vm" className="mt-3 space-y-3">
                <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                  Butuh RAM 2 GB. Contoh QEMU (BIOS):
                </p>
                <CodeBlock
                  code={`qemu-system-x86_64 -enable-kvm -m 4G -smp 2 \\
  -cdrom ${isoName(version)} -boot d`}
                />
                <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                  Untuk UEFI, tambahkan firmware OVMF sesuai distro kamu. Di
                  VirtualBox, VMware, atau Hyper-V, pasang ISO sebagai DVD dan
                  set firmware ke BIOS atau EFI.
                </p>
              </TabsContent>

              <TabsContent value="usb" className="mt-3 space-y-3">
                <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                  Tulis ISO sebagai image mentah, bukan salin berkas. Perintah ini
                  menghapus seluruh isi perangkat.
                </p>
                <CodeBlock
                  code={`sudo dd if=${isoName(version)} of=/dev/sdX bs=4M \\
  status=progress oflag=sync`}
                />
                <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                  Di Windows gunakan Rufus mode <strong>DD Image</strong>, atau
                  Ventoy. Ganti <code className="font-mono">/dev/sdX</code> dengan
                  perangkat yang benar.
                </p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-3">
            <h3 className="text-sm font-medium">Setelah sampai desktop</h3>
            <p className="text-[13.5px] leading-relaxed text-muted-foreground">
              LightDM masuk otomatis sebagai <code className="font-mono">liveuser</code>.
              Untuk konsol, buka terminal atau tekan{" "}
              <kbd className="rounded border border-border bg-muted px-1 py-0.5 font-mono text-xs">
                Ctrl+Alt+F2
              </kbd>
              . Shell default adalah zsh.
            </p>

            <div className="space-y-3 border-t border-border/60 pt-3">
              {commands.map((c) => (
                <div key={c.cmd} className="border-t border-border/60 pt-2.5 first:border-0 first:pt-0">
                  <code className="font-mono text-[12.5px] font-medium">{c.cmd}</code>
                  <p className="mt-1 text-[13px] leading-snug text-muted-foreground">
                    {c.desc}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex gap-2 border-t border-border/60 pt-3">
              <InfoIcon className="mt-0.5 size-3.5 shrink-0 text-primary" />
              <p className="text-[13px] leading-relaxed text-muted-foreground">
                Docker berjalan di tmpfs, jadi image besar menghabiskan RAM. Cek
                dengan <code className="font-mono">sudo fishing-container status</code>.
                Untuk Wi-Fi pakai <code className="font-mono">iwctl</code>.
              </p>
            </div>
            <div className="space-y-1.5 border-t border-border/60 pt-3 text-[13px] leading-relaxed text-muted-foreground">
              <p className="font-medium text-foreground">Ingin memasang Arch ke disk?</p>
              <p>
                Pilih <strong>Installer to disk</strong> pada menu boot untuk
                membuka archinstall. Atur disk dan profil sendiri; proses ini
                bukan salinan LiveOS dan dapat menghapus data pada disk tujuan.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <ol className="mt-6 grid gap-x-8 gap-y-5 border-t border-border/60 pt-5 sm:grid-cols-3">
        {[
          ["01", "Tulis ISO", "USB lewat dd/Rufus, atau pasang sebagai DVD VM."],
          ["02", "Pilih LiveOS", "Pilih entri LiveOS di menu boot untuk sesi live."],
          ["03", "Bekerja", "Jalankan fishing-check untuk melihat toolchain."],
        ].map(([n, title, body]) => (
          <li key={n} className="flex gap-3">
            <span className="font-mono text-xs leading-5 text-primary">{n}</span>
            <div>
              <p className="text-[13.5px] font-medium">{title}</p>
              <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
                {body}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </Section>
  )
}
