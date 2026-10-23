export const site = {
  name: "Fishing OS",
  tagline: "Live rescue ISO untuk developer dan engineer DevOps",
  description:
    "Live/rescue ISO berbasis Arch Linux. Boot dari USB atau mesin virtual, langsung dapat git, Docker, kubectl, Helm, Terraform, Ansible, toolchain pemrograman, dan desktop XFCE tanpa instalasi.",
  repo: "https://github.com/Bangkahdev/Fishing-OS",
  repoApi: "https://api.github.com/repos/Bangkahdev/Fishing-OS",
  releases: "https://github.com/Bangkahdev/Fishing-OS/releases",
  issues: "https://github.com/Bangkahdev/Fishing-OS/issues",
  license: "GPL-3.0",
  fingerprint: "69AA 973A 33A3 930B B1C8 3850 F713 BCD7 D6E8 F591",
  fingerprintFlat: "69AA973A33A3930BB1C83850F713BCD7D6E8F591",
  signer: "Fishing OS CI <bangkah@mdhiyaulatha.me>",
  fallbackVersion: "2026.10.24",
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
  caption: string
  wide?: boolean
}

export const screenshots: Screenshot[] = [
  {
    src: "/screenshots/01-boot-menu.png",
    title: "Menu boot",
    caption:
      "Entri live, boot dengan speech, memtest86+, dan HDT. BIOS dan UEFI didukung.",
    wide: true,
  },
  {
    src: "/screenshots/02-desktop.png",
    title: "Desktop XFCE",
    caption:
      "LightDM masuk otomatis sebagai liveuser. Tidak ada dialog login yang menghalangi.",
  },
  {
    src: "/screenshots/03-fishing-check.png",
    title: "fishing-check",
    caption:
      "Satu perintah untuk melihat versi git, Docker, kubectl, Helm, Terraform, Ansible, dan bahasa yang tersedia.",
  },
  {
    src: "/screenshots/04-fastfetch.png",
    title: "fastfetch",
    caption: "Ringkasan sistem live: kernel, desktop, paket, dan memori.",
  },
  {
    src: "/screenshots/05-htop.png",
    title: "htop",
    caption:
      "Pemantauan proses tanpa instalasi. Docker berjalan di tmpfs, jadi memori perlu diawasi.",
  },
  {
    src: "/screenshots/06-firefox.png",
    title: "Firefox",
    caption:
      "Peramban siap pakai untuk dokumentasi, dashboard, atau konsol cloud.",
  },
  {
    src: "/screenshots/07-terminal-tools.png",
    title: "Perkakas bawaan",
    caption:
      "Skrip Fishing OS di /usr/local/bin, kernel, dan antarmuka jaringan langsung tersedia dari shell.",
  },
]

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
    title: "Toolchain DevOps lengkap",
    body: "git, gh, Docker, kubectl, Helm, Terraform, Ansible, Python, Node.js, Go, dan compiler C/C++ sudah terpasang.",
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
