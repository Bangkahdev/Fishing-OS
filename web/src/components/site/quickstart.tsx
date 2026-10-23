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
      eyebrow="Memulai"
      title="Dari unduhan ke desktop dalam beberapa menit"
      description="Mesin virtual adalah cara tercepat untuk mencoba; USB dipakai bila ingin menjalankan langsung di perangkat keras. Secure Boot harus dimatikan di kedua jalur."
      bordered
    >
      <div className="grid items-start gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardContent className="pt-4">
            <Tabs defaultValue="vm">
              <TabsList>
                <TabsTrigger value="vm">Mesin virtual</TabsTrigger>
                <TabsTrigger value="usb">USB</TabsTrigger>
              </TabsList>

              <TabsContent value="vm" className="mt-3 space-y-3">
                <p className="text-[13px] leading-relaxed text-muted-foreground">
                  Butuh RAM 2 GB atau lebih. Contoh QEMU mode BIOS:
                </p>
                <CodeBlock
                  code={`qemu-system-x86_64 -enable-kvm -m 4G -smp 2 \\
  -cdrom ${isoName(version)} -boot d`}
                />
                <p className="text-[13px] leading-relaxed text-muted-foreground">
                  Untuk UEFI, tambahkan firmware OVMF sesuai distro kamu. Di
                  VirtualBox, VMware, atau Hyper-V, pasang ISO sebagai DVD dan
                  set firmware ke BIOS atau EFI.
                </p>
              </TabsContent>

              <TabsContent value="usb" className="mt-3 space-y-3">
                <p className="text-[13px] leading-relaxed text-muted-foreground">
                  Tulis ISO sebagai image mentah, bukan salin berkas. Perintah ini
                  menghapus seluruh isi perangkat.
                </p>
                <CodeBlock
                  code={`sudo dd if=${isoName(version)} of=/dev/sdX bs=4M \\
  status=progress oflag=sync`}
                />
                <p className="text-[13px] leading-relaxed text-muted-foreground">
                  Di Windows gunakan Rufus mode <strong>DD Image</strong>, atau
                  Ventoy. Ganti <code className="font-mono">/dev/sdX</code> dengan
                  perangkat yang benar.
                </p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-3 pt-4">
            <h3 className="text-[13.5px] font-medium">Setelah sampai desktop</h3>
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              LightDM masuk otomatis sebagai <code className="font-mono">liveuser</code>.
              Untuk konsol, buka terminal atau tekan{" "}
              <kbd className="rounded border border-border bg-muted px-1 py-0.5 font-mono text-[11px]">
                Ctrl+Alt+F2
              </kbd>
              . Shell default adalah zsh.
            </p>

            <div className="space-y-2">
              {commands.map((c) => (
                <div key={c.cmd} className="rounded-lg border border-border/70 p-2.5">
                  <code className="font-mono text-[12px] font-medium">{c.cmd}</code>
                  <p className="mt-1 text-[12px] leading-snug text-muted-foreground">
                    {c.desc}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex gap-2 rounded-lg bg-primary/5 p-2.5 ring-1 ring-primary/15">
              <InfoIcon className="mt-0.5 size-3.5 shrink-0 text-primary" />
              <p className="text-[12px] leading-relaxed text-muted-foreground">
                Docker berjalan di tmpfs, jadi image besar menghabiskan RAM. Cek
                dengan <code className="font-mono">sudo fishing-container status</code>.
                Untuk Wi-Fi pakai <code className="font-mono">iwctl</code>.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {[
          ["1", "Tulis atau pasang", "USB dengan dd/Rufus, atau ISO sebagai DVD di mesin virtual."],
          ["2", "Boot dan masuk", "Pilih entri live di menu boot; desktop XFCE tampil otomatis."],
          ["3", "Bekerja", "Jalankan fishing-check untuk melihat toolchain, lalu mulai."],
        ].map(([n, title, body]) => (
          <div key={n} className="flex gap-3 rounded-xl border border-border/70 bg-card/60 p-3.5">
            <span className="grid size-6 shrink-0 place-items-center rounded-md bg-brand-deep/10 font-mono text-[11.5px] font-semibold text-brand-deep ring-1 ring-brand-deep/15 dark:bg-brand-bright/10 dark:text-brand-bright dark:ring-brand-bright/20">
              {n}
            </span>
            <div>
              <p className="text-[13px] font-medium">{title}</p>
              <p className="mt-0.5 text-[12px] leading-relaxed text-muted-foreground">
                {body}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Section>
  )
}
