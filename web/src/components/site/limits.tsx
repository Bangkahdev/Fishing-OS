import { GitBranchIcon, TerminalIcon } from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CodeBlock } from "@/components/code-block"
import { Section } from "@/components/section"
import { limitations, site } from "@/lib/site"

export function Limits() {
  return (
    <Section
      id="batasan"
      eyebrow="Batasan & build"
      title="Apa yang perlu kamu tahu sebelum memakai"
      description="Fishing OS adalah live/rescue medium, bukan sistem yang dipasang ke disk. Batasan berikut disengaja dan didokumentasikan."
    >
      <div className="grid items-start gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-xl border border-border/70 bg-card/60 px-4">
          <Accordion defaultValue={["0"]}>
            {limitations.map((item, i) => (
              <AccordionItem key={item.q} value={String(i)}>
                <AccordionTrigger>{item.q}</AccordionTrigger>
                <AccordionContent className="text-[12.5px] leading-relaxed text-muted-foreground">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-[13.5px]">
                <TerminalIcon className="size-4 text-primary" />
                Bangun sendiri
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2.5">
              <p className="text-[12.5px] leading-relaxed text-muted-foreground">
                Butuh Arch Linux atau container Arch dengan paket{" "}
                <code className="font-mono text-[11.5px]">archiso</code>.
              </p>
              <CodeBlock
                compact
                code={`sudo pacman -S archiso
sudo mkarchiso -v -w work -o out profile
bash tests/check_bootmenu.sh
bash tests/test_iso.sh out/*.iso`}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-[13.5px]">
                <GitBranchIcon className="size-4 text-primary" />
                Kontribusi
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-[12.5px] leading-relaxed text-muted-foreground">
              <p>
                Kirim Pull Request ke <code className="font-mono">main</code>. CI
                menjalankan shellcheck, yamllint, validasi menu boot, build ISO,
                dan smoke test di QEMU.
              </p>
              <p>
                Sebelum mengirim PR, jalankan shellcheck pada skrip yang diubah dan{" "}
                <code className="font-mono text-[11.5px]">bash tests/check_bootmenu.sh</code>.
              </p>
              <a
                href={`${site.repo}/blob/main/docs/SRS.md`}
                target="_blank"
                rel="noreferrer"
                className="inline-block text-[12.5px] text-primary hover:underline"
              >
                Baca SRS (spesifikasi kebutuhan) →
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </Section>
  )
}
