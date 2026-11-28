import { site } from "@/lib/site"

export type BlogPost = {
  slug: string
  title: string
  date: string
  summary: string
  tags: string[]
  sections: Array<{
    title?: string
    paragraphs?: string[]
    bullets?: string[]
    code?: { language: string; value: string }
    note?: { type: "info" | "warning" | "tip"; text: string }
    links?: { label: string; href: string }[]
  }>
}

export const blogPosts: BlogPost[] = [
  {
    slug: "rilis-2026-10-4",
    title: "Rilis Fishing OS v2026.10.4",
    date: "2026-10-04",
    summary:
      "ISO Live rescue berbasis Arch Linux versi 2026.10.4 telah diterbitkan. LiveOS dengan desktop XFCE dan toolchain pengembang, diverifikasi dengan tanda tangan GPG dan checksum SHA-256.",
    tags: ["rilis", "iso", "verifikasi"],
    sections: [
      {
        title: "Apa yang baru",
        paragraphs: [
          "Fishing OS v2026.10.4 adalah live/rescue ISO berbasis Arch Linux x86_64 untuk pengembang. Image dapat dijalankan dari USB atau mesin virtual dengan dukungan BIOS dan UEFI.",
          "Setiap berkas rilis disertai checksum SHA-256 dan tanda tangan GPG yang dapat diverifikasi sebelum boot.",
        ],
        bullets: [
          "Desktop XFCE dengan autologin sebagai liveuser.",
          "Firefox, zsh, dan terminal siap pakai.",
          "Toolchain: git, Python, Node.js, Go, compiler C/C++, Docker, kubectl, Helm, Terraform, Ansible.",
          "Jaringan: systemd-networkd dan iwctl.",
          "Batas ukuran ISO 2000 MiB mengikuti batas GitHub Releases.",
        ],
      },
      {
        title: "Verifikasi unduhan",
        code: {
          language: "shell",
          value: `gpg --import ci-key.asc
gpg --fingerprint bangkah@mdhiyaulatha.me
gpg --verify sha256sums.txt.sig sha256sums.txt
sha256sum -c --ignore-missing sha256sums.txt`,
        },
        note: {
          type: "warning",
          text: "Verifikasi tanda tangan GPG dan fingerprint kunci sebelum memakai ISO.",
        },
      },
      {
        title: "Unduh",
        links: [
          { label: "Buka Releases", href: site.releases },
          { label: "Panduan verifikasi ISO", href: "/docs/download/" },
        ],
      },
    ],
  },
  {
    slug: "assistant-fondasi-diterapkan",
    title: "Fondasi Computer-Use Assistant diterapkan (SRS v1.1)",
    date: "2026-11-20",
    summary:
      "SRS Computer-Use Assistant v1.1 telah diadopsi. Fondasi control plane, orchestrator, tool registry, AT-SPI2 grounding, model manager, dan Privilege Broker tersedia di repository dan diuji melalui lebih dari 190 unit test.",
    tags: ["assistant", "srs", "ai"],
    sections: [
      {
        title: "SRS v1.1",
        paragraphs: [
          "Spesifikasi Computer-Use Assistant v1.1 telah diadopsi sebagai panduan otoritatif. Assistant adalah fitur opsional untuk pemasangan ke disk, tidak disertakan di Live ISO, dan belum ditawarkan oleh installer.",
        ],
        links: [
          { label: "Baca SRS v1.1", href: site.docs.srs },
          { label: "Dokumen implementasi", href: site.docs.implementation },
        ],
      },
      {
        title: "Komponen tersedia",
        bullets: [
          "Control plane dengan task state, policy/approval, audit, dan cancellation.",
          "IPC lokal lewat Unix domain socket untuk task lintas antarmuka.",
          "AT-SPI2 grounding dan verifikasi pasca-aksi untuk aksi UI.",
          "Model manager dengan checksum SHA-256 dan signature GPG.",
          "Orchestrator, tool registry, dan HeuristicPlanner untuk instruksi bahasa alami.",
          "Privilege Broker dengan IPC terautentikasi dan audit elevated operasi.",
          "Artefak paket OS: launcher, desktop, systemd user service, PKGBUILD, install.sh.",
        ],
      },
      {
        title: "Masih terbuka",
        bullets: [
          "Model LLM/VLM dan backend inferensi siap pakai belum disediakan.",
          "Assistant belum disertakan di Live ISO maupun installer.",
          "Pengujian pada desktop Fishing OS Linux nyata masih diperlukan.",
        ],
      },
    ],
  },
]
