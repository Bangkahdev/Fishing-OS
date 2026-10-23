export const site = {
  name: "Fishing OS",
  tagline: "Live rescue ISO berbasis Arch Linux untuk programmer",
  description:
    "Live/rescue ISO berbasis Arch Linux. Boot dari USB atau mesin virtual dan langsung dapat editor, compiler, Python, Node.js, Go, git, Docker, dan desktop XFCE tanpa instalasi.",
  repo: "https://github.com/Bangkahdev/Fishing-OS",
  repoApi: "https://api.github.com/repos/Bangkahdev/Fishing-OS",
  releases: "https://github.com/Bangkahdev/Fishing-OS/releases",
  issues: "https://github.com/Bangkahdev/Fishing-OS/issues",
  author: "Muhammad Dhiyaul Atha",
  authorUrl: "https://github.com/Bangkahdev",
  license: "GPL-3.0",
  fingerprint: "69AA 973A 33A3 930B B1C8 3850 F713 BCD7 D6E8 F591",
  fingerprintFlat: "69AA973A33A3930BB1C83850F713BCD7D6E8F591",
  signer: "Fishing OS CI <bangkah@mdhiyaulatha.me>",
  fallbackVersion: "2026.10.25",
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
    alt: "Menu boot Fishing OS dengan entri live, boot dengan speech, memtest86+, dan HDT",
    caption:
      "Entri live, boot dengan speech, memtest86+, dan HDT. BIOS dan UEFI didukung.",
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
    title: "Langsung pakai, tanpa instalasi",
    body: "Boot dari USB atau mesin virtual, lalu bekerja. Tidak ada langkah pasang, tidak ada partisi yang disentuh.",
  },
  {
    icon: "monitor",
    title: "Desktop dan konsol",
    body: "Desktop XFCE dengan Firefox untuk pekerjaan GUI, atau zsh di TTY untuk perbaikan sistem yang tidak butuh grafis.",
  },
  {
    icon: "package",
    title: "Perkakas programmer lengkap",
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
    desc: "Menjalankan Docker daemon. Gunakan down atau status untuk menghentikan dan memeriksa.",
  },
  {
    cmd: "sudo fishing-setup",
    desc: "Mengaktifkan layanan jaringan dan membuat user dev dengan grup wheel dan docker.",
  },
]

export const limitations = [
  {
    q: "Apakah data saya tersimpan?",
    a: "Tidak. Fishing OS adalah live medium: semua perubahan hilang setelah reboot. Installer ke disk belum ada dan direncanakan pada fase berikutnya.",
  },
  {
    q: "Bagaimana dengan keamanan kredensial?",
    a: "root dan liveuser tanpa password adalah perilaku bawaan live medium, dan sshd aktif sejak boot. Jangan pakai di jaringan yang tidak tepercaya tanpa mengganti kredensial. User dev yang dibuat fishing-setup memakai password yang kamu tentukan.",
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
