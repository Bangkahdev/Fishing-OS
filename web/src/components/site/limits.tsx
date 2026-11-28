import { CpuIcon, LifeBuoyIcon } from "lucide-react"
import { Link } from "react-router-dom"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Section } from "@/components/section"
import { limitations } from "@/lib/site"

const requirements = [
  "Arsitektur x86_64 (64-bit).",
  "RAM minimal 2 GB; 4 GB disarankan untuk toolchain dan Docker.",
  "Firmware BIOS atau UEFI didukung.",
  "Secure Boot dimatikan sebelum boot.",
  "USB minimal 2 GB bila memakai media fisik.",
]

export function Limits() {
  return (
    <Section
      id="batasan"
      title="Apa yang perlu kamu tahu sebelum memakai"
      description="LiveOS dan installer archinstall adalah dua jalur yang berbeda. Perhatikan penyimpanan sesi live, keamanan, dan status Assistant sebelum melanjutkan."
    >
      <div className="grid items-start gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-xl border border-border/70 bg-card px-5">
          <Accordion defaultValue={["0"]}>
            {limitations.map((item, i) => (
              <AccordionItem key={item.q} value={String(i)}>
                <AccordionTrigger>{item.q}</AccordionTrigger>
                <AccordionContent className="text-[13.5px] leading-relaxed text-muted-foreground">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <CpuIcon className="size-4 text-primary" />
                Kebutuhan sistem
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc space-y-1.5 pl-4 text-[13.5px] leading-relaxed text-muted-foreground marker:text-primary">
                {requirements.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <LifeBuoyIcon className="size-4 text-primary" />
                Butuh bantuan?
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-[13.5px] leading-relaxed text-muted-foreground">
              <p>
                Panduan pemecahan masalah untuk boot, jaringan, Docker, dan data
                yang hilang tersedia di dokumentasi.
              </p>
              <div className="flex flex-col items-start gap-2">
                <Link
                  to="/docs/troubleshooting/"
                  className="text-[13px] text-primary hover:underline"
                >
                  Pemecahan masalah →
                </Link>
                <Link
                  to="/docs/"
                  className="text-[13px] text-primary hover:underline"
                >
                  Jelajahi dokumentasi →
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Section>
  )
}