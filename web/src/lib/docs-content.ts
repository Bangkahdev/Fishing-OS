import { site } from "@/lib/site"

export type DocsLink = {
  label: string
  href: string
}

export type DocsSection = {
  id: string
  title: string
  paragraphs?: string[]
  bullets?: string[]
  steps?: string[]
  code?: {
    language: string
    value: string
  }
  figure?: {
    diagram: "boot" | "verify" | "assistant"
    caption: string
  }
  table?: {
    headers: string[]
    rows: string[][]
  }
  note?: {
    type: "info" | "warning" | "tip"
    text: string
  }
  links?: DocsLink[]
}

export type DocsPage = {
  slug: string
  group: string
  title: string
  summary: string
  intro: string
  keywords: string[]
  sections: DocsSection[]
  cards?: Array<{
    slug: string
    title: string
    description: string
    icon?: string
  }>
  related?: DocsLink[]
}

export const docsPages: DocsPage[] = [
  {
    slug: "overview",
    group: "Dokumentasi",
    title: "Dokumentasi Fishing OS",
    summary:
      "Panduan untuk mengunduh, menjalankan, dan memakai Fishing OS sebagai LiveOS maupun instalasi Arch Linux.",
    intro:
      "Fishing OS adalah live/rescue ISO berbasis Arch Linux untuk pengembang. Pilih panduan sesuai tujuanmu. Beberapa hal penting—terutama perbedaan LiveOS dan installer—dijelaskan lebih dulu sebelum langkah teknis.",
    keywords: ["mulai", "dokumentasi", "panduan", "live", "instalasi", "use case"],
    cards: [
      {
        slug: "use-cases",
        title: "Kapan memakai Fishing OS",
        description:
          "Lihat skenario umum: mencoba Arch, memulihkan sistem yang gagal boot, bekerja darurat, dan mendemonstrasikan toolchain.",
        icon: "compass",
      },
      {
        slug: "download",
        title: "Unduh dan verifikasi",
        description:
          "Ambil ISO dari rilis resmi dan verifikasi tanda tangan serta checksum sebelum boot.",
        icon: "download",
      },
      {
        slug: "liveos",
        title: "Jalankan LiveOS",
        description:
          "Coba di mesin virtual atau USB, lalu pahami apa yang terjadi setelah reboot.",
        icon: "monitor",
      },
      {
        slug: "installation",
        title: "Installer ke disk",
        description:
          "Ketahui fungsi archinstall, pilihan konfigurasi, dan risiko terhadap disk.",
        icon: "harddrive",
      },
      {
        slug: "tools",
        title: "Gunakan tool bawaan",
        description:
          "Perintah Fishing OS, jaringan Wi-Fi, Docker, dan batas koleksi Ansible.",
        icon: "terminal",
      },
      {
        slug: "troubleshooting",
        title: "Atasi masalah umum",
        description:
          "Langkah awal untuk masalah boot, jaringan, Docker, dan data yang tidak tersimpan.",
        icon: "lifebuoy",
      },
      {
        slug: "assistant",
        title: "Computer-Use Assistant",
        description:
          "Fitur AI opsional untuk pemasangan ke disk yang sedang dikembangkan.",
        icon: "bot",
      },
    ],
    sections: [
      {
        id: "pilih-alur",
        title: "Pilih alur yang tepat",
        paragraphs: [
          "LiveOS adalah sesi sementara yang berjalan dari media ISO. Gunakan untuk mencoba Fishing OS atau melakukan pekerjaan darurat tanpa memasang sistem ke disk.",
          "Entri Installer to disk membuka archinstall untuk menyiapkan instalasi Arch Linux secara terpisah. Installer ini bukan proses penyalinan LiveOS: paket dan konfigurasi Fishing OS tidak otomatis dipasang ke sistem di disk.",
        ],
        figure: {
          diagram: "boot",
          caption:
            "Alur boot Fishing OS: satu ISO bercabang menjadi LiveOS sementara atau instalasi Arch ke disk melalui archinstall.",
        },
      },
      {
        id: "status-proyek",
        title: "Status proyek secara ringkas",
        paragraphs: [
          "Fishing OS menyediakan desktop XFCE, toolchain pengembangan, dan utilitas sistem di LiveOS. Versi paket mengikuti repositori Arch saat image dibangun.",
          "Computer-Use Assistant masih dalam pengembangan. Fondasi control plane, orchestrator, tool registry, AT-SPI2 grounding, model manager, dan Privilege Broker tersedia di repository. Assistant belum disertakan di Live ISO, belum ditawarkan oleh installer, dan belum memiliki model serta backend inferensi siap pakai.",
        ],
        links: [
          { label: "Status Computer-Use Assistant", href: "/docs/assistant/" },
          { label: "Repository Fishing OS", href: site.repo },
        ],
      },
    ],
    related: [
      { label: "Kapan memakai Fishing OS", href: "/docs/use-cases/" },
      { label: "Unduh dan verifikasi ISO", href: "/docs/download/" },
      { label: "Jalankan LiveOS", href: "/docs/liveos/" },
    ],
  },
  {
    slug: "use-cases",
    group: "Mulai cepat",
    title: "Kapan memakai Fishing OS",
    summary:
      "Skenario umum: mencoba Arch Linux, memulihkan sistem yang gagal boot, bekerja darurat, dan mendemonstrasikan toolchain.",
    intro:
      "Fishing OS dirancang sebagai LiveOS sementara. Artinya kamu dapat memakainya untuk banyak keperluan tanpa mengubah disk, selama kamu memahami bahwa perubahan sesi hilang saat reboot.",
    keywords: ["use case", "kasus", "rescue", "darurat", "coba arch", "demo"],
    sections: [
      {
        id: "coba-arch",
        title: "Mencoba Arch Linux tanpa memasang",
        paragraphs: [
          "Boot LiveOS untuk merasakan Arch Linux, memeriksa dukungan perangkat keras, dan mencoba desktop XFCE tanpa menyentuh partisi. Cocok untuk memutuskan apakah Arch cocok sebelum memasang ke disk.",
        ],
        links: [{ label: "Cara menjalankan LiveOS", href: "/docs/liveos/" }],
      },
      {
        id: "rescue",
        title: "Memulihkan sistem yang gagal boot",
        paragraphs: [
          "LiveOS berisi utilitas pemulihan. Mount partisi sistem yang bermasalah, periksa log, perbaiki bootloader, atau pulihkan data penting dari mesin yang tidak bisa menyala.",
        ],
        code: {
          language: "shell",
          value: `lsblk
sudo mount /dev/sdXN /mnt
sudo arch-chroot /mnt`,
        },
        note: {
          type: "warning",
          text: "Khusus operasi yang menulis ke disk, pastikan kamu memilih partisi dan perangkat yang benar. Salah perangkat dapat menghapus data.",
        },
      },
      {
        id: "kerja-darurat",
        title: "Bekerja darurat saat sistem utama bermasalah",
        paragraphs: [
          "Saat mesin utama gagal, LiveOS menyediakan desktop, peramban, editor, dan jaringan untuk mencari solusi, mengunduh berkas, atau mengakses konsol cloud. Toolchain seperti git, Docker, dan compiler juga tersedia.",
        ],
      },
      {
        id: "demo-toolchain",
        title: "Mendemonstrasikan toolchain",
        paragraphs: [
          "Perlihatkan alur kerja kontainer dan orkestrasi dengan Docker, kubectl, Helm, Terraform, dan Ansible yang sudah terpasang. Karena berjalan di tmpfs, sesi ini cocok untuk demonstrasi singkat tanpa instalasi.",
        ],
        links: [{ label: "Tool bawaan dan cara pakai", href: "/docs/tools/" }],
      },
    ],
    related: [
      { label: "Jalankan LiveOS", href: "/docs/liveos/" },
      { label: "Tool bawaan", href: "/docs/tools/" },
      { label: "Pemecahan masalah", href: "/docs/troubleshooting/" },
    ],
  },
  {
    slug: "download",
    group: "Mulai cepat",
    title: "Unduh dan verifikasi ISO",
    summary:
      "Gunakan rilis resmi, verifikasi tanda tangan GPG, lalu cocokkan checksum ISO sebelum boot.",
    intro:
      "Unduh ISO dan berkas verifikasinya dari satu rilis Fishing OS. Jangan boot image sebelum memastikan tanda tangan dan checksum sesuai.",
    keywords: ["download", "rilis", "iso", "sha256", "gpg", "signature"],
    sections: [
      {
        id: "unduh-rilis",
        title: "Ambil berkas dari rilis resmi",
        paragraphs: [
          "Halaman Releases adalah kanal unduhan utama. Unduh ISO, `sha256sums.txt`, tanda tangan checksum, dan kunci publik/fingerprint yang disertakan pada rilis.",
        ],
        links: [{ label: "Buka Fishing OS Releases", href: site.releases }],
      },
      {
        id: "verifikasi-tanda-tangan",
        title: "Verifikasi tanda tangan dan checksum",
        paragraphs: [
          "Jalankan perintah dari direktori tempat berkas rilis disimpan. Cocokkan fingerprint kunci dengan sumber tepercaya sebelum mempercayai tanda tangan.",
        ],
        code: {
          language: "shell",
          value: `gpg --import ci-key.asc
gpg --fingerprint bangkah@mdhiyaulatha.me
gpg --verify sha256sums.txt.sig sha256sums.txt
sha256sum -c --ignore-missing sha256sums.txt`,
        },
        figure: {
          diagram: "verify",
          caption:
            "Urutan verifikasi rilis: unduh, impor kunci, verifikasi tanda tangan, cocokkan checksum, baru boot.",
        },
        note: {
          type: "warning",
          text: "Jangan menganggap checksum saja membuktikan asal file. Verifikasi tanda tangan GPG dan fingerprint kunci dari sumber kedua sebelum menggunakan ISO.",
        },
      },
      {
        id: "windows",
        title: "Memeriksa checksum di Windows",
        paragraphs: [
          "PowerShell dapat menghitung SHA-256 ISO. Cocokkan hasilnya dengan entri ISO di `sha256sums.txt`; untuk autentikasi rilis, verifikasi tanda tangan memakai Gpg4win atau WSL.",
        ],
        code: {
          language: "powershell",
          value: "Get-FileHash .\\fishing-os-VERSI-x86_64.iso -Algorithm SHA256",
        },
      },
    ],
    related: [
      { label: "Cara menjalankan LiveOS", href: "/docs/liveos/" },
      { label: "Kapan memakai Fishing OS", href: "/docs/use-cases/" },
    ],
  },
  {
    slug: "liveos",
    group: "Mulai cepat",
    title: "Jalankan LiveOS",
    summary:
      "Boot image dari mesin virtual atau USB tanpa memasang sistem ke disk.",
    intro:
      "LiveOS adalah pilihan default pada menu boot. Sesi berjalan dari media live; perubahan lokal tidak dirancang untuk bertahan setelah reboot.",
    keywords: ["live", "usb", "qemu", "virtualbox", "uefi", "bios", "secure boot"],
    sections: [
      {
        id: "prasyarat",
        title: "Periksa prasyarat",
        bullets: [
          "Arsitektur x86_64; firmware BIOS dan UEFI didukung.",
          "Sediakan RAM minimal 2 GB; mesin virtual dengan 4 GB memberi ruang lebih untuk toolchain dan Docker.",
          "Matikan Secure Boot karena bootloader image belum ditandatangani untuk Secure Boot.",
        ],
      },
      {
        id: "mesin-virtual",
        title: "Coba di mesin virtual",
        paragraphs: [
          "Mesin virtual adalah cara aman untuk mencoba tanpa menulis ke disk fisik. Contoh berikut untuk host Linux dengan KVM dan memakai mode BIOS; untuk UEFI siapkan firmware OVMF sesuai sistem host. VirtualBox, VMware, atau Hyper-V juga dapat memasang ISO sebagai DVD virtual.",
        ],
        code: {
          language: "shell",
          value: `qemu-system-x86_64 -enable-kvm -m 4G -smp 2 \\
  -cdrom fishing-os-VERSI-x86_64.iso -boot d`,
        },
      },
      {
        id: "usb",
        title: "Boot dari USB",
        paragraphs: [
          "Tulis ISO sebagai image mentah menggunakan alat yang mendukung mode DD. Di Windows, gunakan Rufus dengan DD Image atau Ventoy.",
        ],
        code: {
          language: "shell",
          value: "sudo dd if=fishing-os-VERSI-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync",
        },
        note: {
          type: "warning",
          text: "Perintah dd menghapus seluruh isi perangkat tujuan. Pastikan /dev/sdX benar-benar perangkat USB yang dimaksud sebelum menjalankan perintah.",
        },
      },
      {
        id: "masuk-desktop",
        title: "Masuk ke desktop",
        paragraphs: [
          "Pilih LiveOS pada menu boot. LightDM masuk otomatis ke desktop XFCE sebagai `liveuser`; untuk TTY, tekan Ctrl+Alt+F2. Shell default adalah zsh.",
          "Pilih entri `with speech` bila membutuhkan pembaca layar saat boot.",
        ],
        note: {
          type: "tip",
          text: "Untuk sesi yang lebih cepat, gunakan TTY (Ctrl+Alt+F2) dan andalkan zsh tanpa memuat desktop grafis.",
        },
      },
      {
        id: "penyimpanan-live",
        title: "Pahami penyimpanan sesi",
        paragraphs: [
          "Perubahan pada LiveOS—termasuk file yang dibuat di sistem live—hilang ketika komputer reboot. Salin hasil kerja ke media eksternal atau penyimpanan jaringan sebelum mematikan sesi.",
        ],
        links: [{ label: "Perbedaan LiveOS dan installer", href: "/docs/installation/" }],
      },
    ],
    related: [
      { label: "Unduh dan verifikasi ISO", href: "/docs/download/" },
      { label: "Gunakan tool bawaan", href: "/docs/tools/" },
      { label: "Atasi masalah umum", href: "/docs/troubleshooting/" },
    ],
  },
  {
    slug: "installation",
    group: "Menggunakan Fishing OS",
    title: "Installer ke disk: apa yang dipasang?",
    summary:
      "Entri installer menjalankan archinstall untuk menyiapkan Arch Linux; bukan untuk mengkloning seluruh isi LiveOS.",
    intro:
      "Penting: menu bernama Installer to disk membuka `archinstall`. Ini memberi alur instalasi Arch Linux yang kamu konfigurasi sendiri, bukan installer profil Fishing OS yang menyalin seluruh desktop, toolchain, dan setelan LiveOS.",
    keywords: ["install", "installer", "archinstall", "partisi", "disk", "xfce"],
    sections: [
      {
        id: "mulai-installer",
        title: "Mulai installer",
        steps: [
          "Boot ISO dan pilih Installer to disk pada menu boot.",
          "Wrapper `fishingos-install` memeriksa prasyarat, menampilkan peringatan, lalu membuka archinstall setelah konfirmasi.",
          "Di archinstall, pilih disk, skema partisi, user harian, dan profil yang diperlukan. Pilih XFCE bila membutuhkan desktop grafis.",
        ],
        code: {
          language: "shell",
          value: "sudo fishingos-install",
        },
      },
      {
        id: "hasil-instalasi",
        title: "Hasil instalasi berbeda dari LiveOS",
        paragraphs: [
          "archinstall menyiapkan instalasi Arch berdasarkan pilihanmu. Daftar tool, konfigurasi, autologin, dan tampilan LiveOS tidak otomatis ikut terpasang; pasang serta konfigurasi paket tambahan sendiri setelah instalasi.",
          "Computer-Use Assistant juga belum menjadi pilihan installer. Fitur ini masih dalam pengembangan dan belum merupakan paket siap pakai.",
        ],
      },
      {
        id: "risiko-disk",
        title: "Lindungi data sebelum melanjutkan",
        paragraphs: [
          "Instalasi mengubah tabel partisi dan filesystem pada disk yang dipilih. Cadangkan data penting, pastikan perangkat tujuan benar, dan jangan lanjutkan bila belum yakin terhadap pilihan partisi.",
        ],
        note: {
          type: "warning",
          text: "Instalasi dapat menghapus data pada disk tujuan. LiveOS default adalah pilihan yang tepat jika hanya ingin mencoba Fishing OS tanpa mengubah disk.",
        },
      },
    ],
    related: [
      { label: "Jalankan LiveOS tanpa memasang ke disk", href: "/docs/liveos/" },
      { label: "Kapan memakai Fishing OS", href: "/docs/use-cases/" },
    ],
  },
  {
    slug: "tools",
    group: "Menggunakan Fishing OS",
    title: "Tool bawaan dan tugas umum",
    summary:
      "Perintah untuk memeriksa toolchain, mengelola Docker, menyiapkan user dev, dan terhubung ke Wi-Fi.",
    intro:
      "Toolchain tersedia pada sesi LiveOS. Versi mengikuti repositori Arch yang digunakan saat image dibangun; image dan konfigurasi live berjalan sementara.",
    keywords: ["tools", "toolchain", "docker", "wifi", "iwctl", "ansible", "fishing-check"],
    sections: [
      {
        id: "perintah-fishing",
        title: "Perintah Fishing OS",
        bullets: [
          "`fishing-check` menampilkan tool yang tersedia beserta versinya.",
          "`sudo fishing-container up` menjalankan Docker daemon; gunakan `sudo fishing-container status` untuk memeriksa status.",
          "`sudo fishing-setup` menjalankan setup awal, termasuk layanan jaringan dan pembuatan user `dev`.",
        ],
        code: {
          language: "shell",
          value: `fishing-check
sudo fishing-container up
sudo fishing-container status
sudo fishing-setup`,
        },
      },
      {
        id: "ringkasan-perintah",
        title: "Ringkasan perintah",
        paragraphs: [
          "Perintah Fishing OS mencakup pemeriksaan toolchain, pengelolaan Docker, dan penyiapan awal.",
        ],
        table: {
          headers: ["Perintah", "Fungsi"],
          rows: [
            ["`fishing-check`", "Menampilkan tool yang terpasang beserta versinya."],
            ["`sudo fishing-container up`", "Menjalankan Docker daemon."],
            ["`sudo fishing-container status`", "Memeriksa status Docker daemon."],
            ["`sudo fishing-setup`", "Mengaktifkan jaringan dan menyiapkan user `dev`."],
          ],
        },
      },
      {
        id: "wifi",
        title: "Terhubung ke Wi-Fi",
        paragraphs: [
          "Gunakan `iwctl` untuk memindai jaringan dan menghubungkan interface Wi-Fi. Nama interface dapat berbeda, jadi periksa nama yang tersedia terlebih dahulu.",
        ],
        code: {
          language: "shell",
          value: `iwctl
# di dalam iwctl:
device list
station wlan0 scan
station wlan0 get-networks
station wlan0 connect NAMA-WIFI`,
        },
      },
      {
        id: "docker-storage",
        title: "Batas penyimpanan Docker",
        paragraphs: [
          "Docker daemon dijalankan manual. Penyimpanan image berada di tmpfs pada sesi live, sehingga image besar memakai RAM dan akan hilang saat reboot. Periksa pemakaian sebelum menarik image berukuran besar.",
        ],
        note: {
          type: "tip",
          text: "Untuk image besar, tambah RAM mesin virtual atau kurangi ukuran image agar tmpfs tidak penuh.",
        },
      },
      {
        id: "ansible",
        title: "Ansible dan koleksi",
        paragraphs: [
          "Image membawa `ansible-core`, bukan semua koleksi Ansible. Pasang koleksi yang dibutuhkan dengan `ansible-galaxy collection install NAMA_KOLEKSI` saat jaringan dan ruang penyimpanan tersedia.",
        ],
      },
    ],
    related: [
      { label: "Atasi masalah jaringan dan Docker", href: "/docs/troubleshooting/" },
      { label: "Kapan memakai Fishing OS", href: "/docs/use-cases/" },
    ],
  },
  {
    slug: "security",
    group: "Keamanan",
    title: "Keamanan dan batas LiveOS",
    summary:
      "LiveOS ditujukan untuk penggunaan lokal sementara, bukan lingkungan yang sudah diperkeras untuk jaringan publik.",
    intro:
      "Pahami profil keamanan sebelum menghubungkan perangkat ke jaringan. Kenyamanan autologin pada LiveOS berbeda dari konfigurasi sistem produksi.",
    keywords: ["security", "keamanan", "ssh", "root", "password", "secure boot", "gpg"],
    sections: [
      {
        id: "akun-live",
        title: "Akun dan akses SSH",
        paragraphs: [
          "LiveOS masuk otomatis sebagai `liveuser`; akun `root` dan `liveuser` tidak memakai password. Layanan `sshd` aktif, dan konfigurasi image mengizinkan autentikasi password serta login root.",
          "Gunakan LiveOS hanya pada jaringan yang kamu percaya atau lingkungan terisolasi. Jangan mengekspos SSH ke internet atau jaringan publik. Aturan sudo bawaan untuk `liveuser` dibatasi pada beberapa helper Fishing OS.",
        ],
        note: {
          type: "warning",
          text: "LiveOS bukan image yang diperkeras untuk penggunaan server. Jika membutuhkan sistem harian atau layanan jaringan, siapkan instalasi Arch terpisah dan atur autentikasi serta firewall secara sadar.",
        },
      },
      {
        id: "secure-boot",
        title: "Secure Boot",
        paragraphs: [
          "Bootloader ISO belum ditandatangani untuk Secure Boot. Matikan Secure Boot di firmware sebelum boot dari USB atau mesin virtual.",
        ],
      },
      {
        id: "integritas-iso",
        title: "Integritas unduhan",
        paragraphs: [
          "Verifikasi tanda tangan GPG dan checksum sebelum boot. Cocokkan fingerprint kunci dari lebih dari satu sumber tepercaya; halaman rilis menyediakan fingerprint untuk rilis terkait.",
        ],
        links: [{ label: "Panduan verifikasi ISO", href: "/docs/download/" }],
      },
    ],
    related: [
      { label: "Unduh dan verifikasi ISO", href: "/docs/download/" },
      { label: "Jalankan LiveOS", href: "/docs/liveos/" },
    ],
  },
  {
    slug: "troubleshooting",
    group: "Bantuan",
    title: "Pemecahan masalah",
    summary:
      "Periksa beberapa penyebab umum sebelum mengunduh ulang ISO atau mengubah konfigurasi.",
    intro:
      "Mulai dari gejala yang terlihat dan lakukan pemeriksaan satu per satu. Untuk masalah yang belum tercakup, sertakan versi rilis, perangkat/VM, dan langkah reproduksi saat membuka issue.",
    keywords: ["troubleshoot", "help", "boot", "wifi", "docker", "issue"],
    sections: [
      {
        id: "gagal-boot",
        title: "USB atau ISO tidak bisa boot",
        bullets: [
          "Pastikan Secure Boot dimatikan.",
          "Tulis image sebagai DD/raw image; jangan hanya menyalin berkas ISO ke USB.",
          "Pastikan firmware memakai BIOS atau UEFI yang didukung dan image sesuai arsitektur x86_64.",
          "Verifikasi tanda tangan dan checksum untuk memastikan file unduhan tidak rusak.",
        ],
      },
      {
        id: "wifi-tidak-terhubung",
        title: "Wi-Fi tidak tersambung",
        paragraphs: [
          "Periksa perangkat Wi-Fi dengan `iwctl device list`, lalu scan dan hubungkan melalui `iwctl`. Gunakan nama interface yang benar, bukan mengasumsikan selalu `wlan0`.",
        ],
        code: {
          language: "shell",
          value: `iwctl
device list
station NAMA_INTERFACE scan
station NAMA_INTERFACE get-networks
station NAMA_INTERFACE connect NAMA_WIFI`,
        },
      },
      {
        id: "docker-bermasalah",
        title: "Docker tidak berjalan atau kehabisan memori",
        paragraphs: [
          "Docker daemon tidak otomatis dijalankan. Gunakan `sudo fishing-container up`; periksa status dengan `sudo fishing-container status`. Penyimpanan image menggunakan tmpfs, jadi kurangi ukuran image atau tambah RAM VM jika ruang habis.",
        ],
      },
      {
        id: "perubahan-hilang",
        title: "File atau perubahan hilang setelah reboot",
        paragraphs: [
          "Itu perilaku normal LiveOS. Simpan file ke media eksternal atau jaringan sebelum reboot. Installer archinstall menyiapkan sistem disk terpisah, tetapi tidak menyalin seluruh isi LiveOS.",
        ],
        links: [{ label: "Pahami perbedaan LiveOS dan installer", href: "/docs/installation/" }],
      },
      {
        id: "laporkan-masalah",
        title: "Laporkan masalah",
        paragraphs: [
          "Sebelum membuka issue, catat tag rilis, jenis perangkat atau hypervisor, pesan error, serta langkah yang menghasilkan masalah. Hapus informasi sensitif dari log sebelum membagikannya.",
        ],
        links: [{ label: "Buka GitHub Issues", href: site.issues }],
      },
    ],
    related: [
      { label: "Jalankan LiveOS", href: "/docs/liveos/" },
      { label: "Gunakan tool bawaan", href: "/docs/tools/" },
    ],
  },
  {
    slug: "assistant",
    group: "Tentang proyek",
    title: "Computer-Use Assistant",
    summary:
      "Fitur AI opsional yang sedang dikembangkan untuk Fishing OS yang dipasang ke disk.",
    intro:
      "Computer-Use Assistant dirancang sebagai fitur lokal opsional yang dapat mengendalikan komputer lewat antarmuka, model AI, dan tool lokal. Saat ini fitur ini masih dalam pengembangan dan belum siap dipakai pengguna umum.",
    keywords: ["assistant", "ai", "model", "experimental", "fitur"],
    cards: [
      {
        slug: "assistant",
        title: "Lapisan arsitektur",
        description: "Antarmuka → orchestrator → tool registry → Privilege Broker.",
        icon: "bot",
      },
    ],
    sections: [
      {
        id: "apa-itu",
        title: "Apa itu Computer-Use Assistant",
        paragraphs: [
          "Assistant adalah lapisan yang memungkinkan interaksi berbasis AI dengan komputer secara lokal: membaca layar, mengendalikan antarmuka, dan menjalankan tool yang diizinkan. Dirancang untuk Fishing OS versi instalasi, bukan LiveOS sementara.",
        ],
        figure: {
          diagram: "assistant",
          caption:
            "Lapisan Computer-Use Assistant. Fondasi antarmuka, orchestrator, dan tool sudah tersedia; backend inferensi LLM/VLM belum dipaketkan.",
        },
      },
      {
        id: "status",
        title: "Status saat ini",
        bullets: [
          "Belum disertakan pada Live ISO.",
          "Belum ditawarkan sebagai komponen opsional oleh installer.",
          "Model LLM/VLM dan backend inferensi siap pakai belum disediakan.",
          "Pengujian menyeluruh pada desktop Fishing OS Linux nyata masih diperlukan.",
        ],
        note: {
          type: "warning",
          text: "Jangan menganggap fitur ini sudah siap dipasang dan digunakan. Pantau repository dan rilis untuk status terbaru.",
        },
      },
      {
        id: "fondasi",
        title: "Fondasi yang sudah tersedia",
        paragraphs: [
          "Berikut komponen inti Assistant yang tersimpan di repository dan telah diuji melalui unit test:",
        ],
        bullets: [
          "Control plane: Control Service, task state, policy/approval, audit redaction, cancellation, dan IPC lokal lewat Unix domain socket.",
          "Perception: grounding AT-SPI2 via pyatspi, tangkapan layar, dan verifikasi pasca-aksi; aksi tombol UI yang terverifikasi.",
          "Model manager: manifest model, verifikasi checksum SHA-256, load/unload, status OOM, dan tanda tangan GPG.",
          "Orchestrator + tool registry + planner: instruksi bahasa alami → rencana tool call → validasi schema → policy gate → eksekusi → verifikasi; HeuristicPlanner deterministik sebagai fallback offline.",
          "Privilege Broker: IPC Unix socket terautentikasi (SO_PEERCRED) yang memediasi operasi elevated via sudo, lengkap audit tanpa menyimpan kredensial.",
          "Artefak paket: launcher, entri desktop, systemd user service, PKGBUILD, dan install.sh untuk pemasangan ke Fishing OS yang sudah terpasang ke disk.",
        ],
      },
      {
        id: "tautan",
        title: "Tautan terkait",
        paragraphs: [
          "Kode dan informasi terbaru tersedia di repository proyek.",
        ],
        links: [
          { label: "Repository Fishing OS", href: site.repo },
          { label: "Rilis Fishing OS", href: site.releases },
          { label: "Implementasi Assistant", href: site.docs.implementation },
          { label: "Orchestrator", href: site.docs.orchestrator },
          { label: "SRS v1.1", href: site.docs.srs },
        ],
      },
    ],
    related: [{ label: "Kapan memakai Fishing OS", href: "/docs/use-cases/" }],
  },
]

export const docsNavigation = [
  {
    title: "Mulai cepat",
    slugs: ["overview", "use-cases", "download", "liveos"],
  },
  {
    title: "Menggunakan Fishing OS",
    slugs: ["installation", "tools", "troubleshooting"],
  },
  {
    title: "Keamanan",
    slugs: ["security"],
  },
  {
    title: "Tentang proyek",
    slugs: ["assistant"],
  },
] as const
