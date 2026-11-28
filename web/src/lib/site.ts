export const site = {
  name: "Fishing OS",
  tagline: "Live rescue ISO berbasis Arch Linux untuk pengembang",
  description:
    "Live/rescue ISO berbasis Arch Linux untuk pengembang. Boot ke LiveOS dari USB atau VM; menu boot juga menyediakan installer archinstall untuk menyiapkan sistem Arch di disk.",
  repo: "https://github.com/Bangkahdev/Fishing-OS",
  repoApi: "https://api.github.com/repos/Bangkahdev/Fishing-OS",
  releases: "https://github.com/Bangkahdev/Fishing-OS/releases",
  issues: "https://github.com/Bangkahdev/Fishing-OS/issues",
  blog: "https://github.com/Bangkahdev/Fishing-OS/discussions",
  docs: {
    readme: "https://github.com/Bangkahdev/Fishing-OS#readme",
    srs: "https://github.com/Bangkahdev/Fishing-OS/blob/main/docs/SRS-agent-v1.1.md",
    implementation:
      "https://github.com/Bangkahdev/Fishing-OS/blob/main/docs/COMPUTER_USE_ASSISTANT_IMPLEMENTATION.md",
    orchestrator:
      "https://github.com/Bangkahdev/Fishing-OS/blob/main/docs/ORCHESTRATOR.md",
    assistantPackage:
      "https://github.com/Bangkahdev/Fishing-OS/blob/main/packaging/assistant/README.md",
  },
  author: "Muhammad Dhiyaul Atha",
  authorUrl: "https://github.com/Bangkahdev",
  license: "GPL-3.0",
  fingerprint: "69AA 973A 33A3 930B B1C8 3850 F713 BCD7 D6E8 F591",
  fingerprintFlat: "69AA973A33A3930BB1C83850F713BCD7D6E8F591",
  signer: "Fishing OS CI <bangkah@mdhiyaulatha.me>",
  fallbackVersion: "2026.10.4",
  base: "Arch Linux x86_64",
  isoLimit: "2000 MiB",
}

export function releaseUrl(version: string) {
  return `${site.releases}/tag/v${version}`
}

export function assetUrl(version: string, asset: string) {
  return `${site.releases}/download/v${version}/${asset}`
}

export function isoName(version: string) {
  return `fishing-os-${version}-x86_64.iso`
}

export type Screenshot = {
  src: string
  title: string
  alt: string
  caption: string
  width: number
  height: number
  variants: number[]
  wide?: boolean
}

export const screenshots: Screenshot[] = [
  {
    src: "/screenshots/01-boot-menu.png",
    title: "Menu boot",
    alt: "Menu boot Fishing OS dengan entri LiveOS, boot dengan speech, memtest86+, HDT, dan Installer to disk",
    caption:
      "Menu boot menyediakan LiveOS (sesi sementara) dan entri Installer to disk yang membuka archinstall untuk pemasangan Arch ke disk.",
    width: 624,
    height: 476,
    variants: [480, 624],
    wide: true,
  },
  {
    src: "/screenshots/02-desktop.png",
    title: "Desktop XFCE",
    alt: "Desktop XFCE Fishing OS setelah autologin sebagai liveuser",
    caption:
      "LightDM masuk otomatis sebagai liveuser. Tidak ada dialog login yang menghalangi.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
  {
    src: "/screenshots/03-fishing-check.png",
    title: "fishing-check",
    alt: "Terminal fishing-check menampilkan versi git, Docker, kubectl, Helm, Terraform, dan Ansible",
    caption:
      "Satu perintah untuk melihat versi git, Docker, kubectl, Helm, Terraform, Ansible, dan bahasa yang tersedia.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
  {
    src: "/screenshots/04-fastfetch.png",
    title: "fastfetch",
    alt: "fastfetch menampilkan ringkasan kernel, desktop, paket, dan memori Fishing OS",
    caption: "Ringkasan sistem live: kernel, desktop, paket, dan memori.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
  {
    src: "/screenshots/05-htop.png",
    title: "htop",
    alt: "htop memantau proses dan penggunaan memori di Fishing OS live",
    caption:
      "Pemantauan proses tanpa instalasi. Docker berjalan di tmpfs, jadi memori perlu diawasi.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
  {
    src: "/screenshots/06-firefox.png",
    title: "Firefox",
    alt: "Firefox terbuka di desktop XFCE Fishing OS untuk mengakses dokumentasi",
    caption:
      "Peramban siap pakai untuk dokumentasi, dashboard, atau konsol cloud.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
  {
    src: "/screenshots/07-terminal-tools.png",
    title: "Perkakas bawaan",
    alt: "Skrip Fishing OS di /usr/local/bin dan perkakas terminal siap dipakai",
    caption:
      "Skrip Fishing OS di /usr/local/bin, kernel, dan antarmuka jaringan langsung tersedia dari shell.",
    width: 1024,
    height: 768,
    variants: [480, 768, 1024],
  },
]

export function webpSrc(src: string, width: number) {
  return src.replace(/\.png$/, `-${width}.webp`)
}

export function webpSrcSet(shot: Screenshot) {
  return shot.variants.map((w) => `${webpSrc(shot.src, w)} ${w}w`).join(", ")
}

export const features = [
  {
    icon: "terminal",
    title: "LiveOS atau installer Arch",
    body: "LiveOS berjalan dari USB/VM tanpa menulis ke disk. Entri Installer to disk membuka archinstall untuk mengatur pemasangan Arch secara terpisah; prosesnya tidak menyalin seluruh isi LiveOS.",
  },
  {
    icon: "monitor",
    title: "Desktop dan konsol",
    body: "Desktop XFCE dengan Firefox untuk pekerjaan GUI, atau zsh di TTY untuk perbaikan sistem yang tidak butuh grafis.",
  },
  {
    icon: "package",
    title: "Toolchain untuk pengembangan",
    body: "git, Python, Node.js, Go, compiler C/C++, Docker, kubectl, Helm, Terraform, dan Ansible sudah terpasang.",
  },
  {
    icon: "wifi",
    title: "Jaringan siap",
    body: "systemd-networkd menangani Ethernet dan WWAN, iwctl untuk Wi-Fi. DHCP otomatis saat antarmuka muncul.",
  },
  {
    icon: "shield",
    title: "Rilis terverifikasi",
    body: "Setiap ISO ditandatangani GPG dan disertai checksum SHA-256, plus smoke test di QEMU sebelum diterbitkan.",
  },
  {
    icon: "harddrive",
    title: "BIOS dan UEFI",
    body: "Menu boot tersedia untuk firmware lama maupun modern. Secure Boot perlu dimatikan karena bootloader belum ditandatangani.",
  },
] as const

export const assistantFeatures = [
  {
    title: "AT-SPI2 grounding",
    body: "Penelusuran elemen UI dan aksi tombol yang terverifikasi melalui pyatspi, tanpa dependensi output model mentah.",
  },
  {
    title: "Orchestrator + tool registry",
    body: "Instruksi bahasa alami diubah menjadi rencana tool call, divalidasi schema, dicek policy, lalu dieksekusi dan diverifikasi hasilnya.",
  },
  {
    title: "Model manager & tanda tangan",
    body: "Manifest model dengan verifikasi checksum SHA-256 dan signature GPG; load, unload, dan status OOM tercatat.",
  },
  {
    title: "Privilege Broker",
    body: "IPC Unix socket terautentikasi (SO_PEERCRED) yang memediasi operasi elevated via sudo, lengkap audit tanpa menyimpan kredensial.",
  },
  {
    title: "Artefak paket OS",
    body: "Launcher, entri desktop, systemd user service, PKGBUILD, dan install.sh untuk pemasangan ke Fishing OS yang sudah terpasang ke disk.",
  },
] as const

export const toolGroups = [
  {
    label: "Version control",
    items: ["git", "gh"],
  },
  {
    label: "Kontainer & orkestrasi",
    items: ["docker", "docker-compose", "kubectl", "helm"],
  },
  {
    label: "Infrastructure as Code",
    items: ["terraform", "ansible-core"],
  },
  {
    label: "Bahasa & build",
    items: ["python3", "pip", "nodejs", "npm", "go", "gcc", "make", "cmake", "gdb"],
  },
  {
    label: "Jaringan & debug",
    items: ["curl", "wget", "jq", "tcpdump", "nmap", "socat", "mtr", "traceroute", "ssh", "iproute2"],
  },
  {
    label: "Shell & editor",
    items: ["zsh", "fish", "bash", "vim", "neovim", "nano", "tmux", "fzf", "bat", "fd", "ripgrep", "htop"],
  },
  {
    label: "Desktop",
    items: ["XFCE", "LightDM", "Firefox"],
  },
  {
    label: "Sistem & perangkat keras",
    items: ["fastfetch", "dmidecode", "pciutils", "usbutils", "memtest86+"],
  },
]

export const commands = [
  {
    cmd: "fishing-check",
    desc: "Menampilkan alat yang terpasang beserta versinya.",
  },
  {
    cmd: "sudo fishing-container up",
    desc: "Menjalankan Docker daemon.",
  },
  {
    cmd: "sudo fishing-setup",
    desc: "Mengaktifkan jaringan dan menyiapkan user dev di grup wheel & docker.",
  },
]

export const limitations = [
  {
    q: "Apa bedanya LiveOS dan Installer to disk?",
    a: "LiveOS berjalan dari USB dan perubahan sesi hilang saat reboot. Installer to disk membuka archinstall untuk menyiapkan instalasi Arch Linux secara terpisah; ini bukan salinan otomatis seluruh paket dan setelan LiveOS. Kamu memilih disk dan konfigurasi sendiri, dan perubahan partisi dapat menghapus data.",
  },
  {
    q: "Apakah Computer-Use Assistant sudah siap dipakai?",
    a: "Belum untuk penggunaan umum. Fondasi control plane, orchestrator, tool registry, AT-SPI2 grounding, model manager, dan Privilege Broker tersedia di repository. Assistant tidak disertakan di Live ISO dan belum ditawarkan oleh installer; model LLM/VLM serta backend inferensi siap pakai belum disediakan.",
  },
  {
    q: "Bagaimana dengan keamanan kredensial?",
    a: "LiveOS masuk otomatis sebagai liveuser; akun root dan liveuser tidak memakai password. Layanan sshd aktif dan mengizinkan autentikasi password serta login root. Jangan hubungkan LiveOS ke jaringan yang tidak tepercaya sebelum menonaktifkan SSH atau mengamankan autentikasi dan firewall. fishing-setup meminta password untuk user dev yang dibuatnya.",
  },
  {
    q: "Kenapa Secure Boot harus dimatikan?",
    a: "Bootloader pada ISO belum ditandatangani untuk Secure Boot. Matikan Secure Boot di firmware sebelum boot dari USB.",
  },
  {
    q: "Berapa besar ISO dan kenapa dibatasi?",
    a: "Batas 2000 MiB mengikuti batas berkas GitHub Releases. Desktop XFCE dan Firefox masih muat di dalam batas ini.",
  },
  {
    q: "Apakah ada repositori paket sendiri?",
    a: "Tidak. pacman memakai mirror Arch Linux resmi, jadi paket tambahan mengikuti ketersediaan di Arch.",
  },
  {
    q: "Apakah Ansible lengkap?",
    a: "Yang dibawa adalah ansible-core tanpa koleksi lengkap agar ISO tetap kecil. Pasang koleksi yang dibutuhkan dengan ansible-galaxy collection install.",
  },
]
