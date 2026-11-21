---
title: SRS - Fishing OS Computer-Use Assistant (v1.1)
source: Fishing_OS_Computer_Use_Assistant_SRS_v1.1.docx (otoritatif)
tanggal: 21 November 2026
---

> Catatan: berkas ini adalah rendering teks dari DOCX di atas. DOCX adalah sumber otoritatif; bila ada selisih, DOCX menang.


FISHING OS
COMPUTER-USE
ASSISTANT
SOFTWARE REQUIREMENTS SPECIFICATION
Versi 1.1  |  Revisi Akses Administratif  |  21 November 2026
Fitur AI terintegrasi dan opsional untuk instalasi Fishing OS ke disk
Kendali Dokumen
Atribut
Nilai
Nama dokumen
Software Requirements Specification (SRS) - Fishing OS Computer-Use Assistant
Versi
1.0 - Final Baseline
Tanggal
1.1 - Revisi Akses Administratif
Status
Revisi baseline untuk kapabilitas kendali perangkat menyeluruh dan operasi administratif melalui sudo/privilege broker
Produk induk
Fishing OS
Jenis fitur
Fitur sistem operasi opsional; bukan proyek/aplikasi lintas-distro
Target distribusi
Instalasi Fishing OS ke disk; tidak disertakan pada Live ISO
Bahasa dokumen
Bahasa Indonesia
Riwayat Perubahan
Versi
Tanggal
Perubahan
1.0
21-11-2026
Menetapkan Assistant sebagai fitur resmi Fishing OS yang opsional pada instalasi ke disk; dikeluarkan sepenuhnya dari Live ISO; menetapkan strategi model hybrid, antarmuka GUI dan CLI/TUI, serta prioritas capability-first.
1.1
21-11-2026
Menambahkan kapabilitas kendali perangkat secara luas, eksekusi perintah yang diotorisasi, akses administratif melalui sudo/Polkit dan privilege broker, serta persyaratan autentikasi, persetujuan, pembatalan, dan audit tindakan privileged.
Daftar Isi
1. Pendahuluan
2. Deskripsi Umum Produk
3. Arsitektur dan Desain Sistem
4. Persyaratan Antarmuka Eksternal
5. Persyaratan Fungsional
6. Persyaratan Data
7. Persyaratan Non-Fungsional
8. Keamanan, Keselamatan, dan Privasi
8.6 Akses Administratif dan Kendali Perangkat
9. Persyaratan Distribusi, Paket, dan Installer
10. Strategi Verifikasi dan Pengujian
11. Kriteria Penerimaan
12. Tahapan Implementasi
13. Ketergantungan, Risiko, dan Keputusan yang Belum Dikunci
Lampiran A. Matriks Keterlacakan
1. Pendahuluan
1.1 Tujuan Dokumen
Dokumen ini menetapkan kebutuhan fungsional, non-fungsional, arsitektur tingkat tinggi, batasan, antarmuka, keamanan, distribusi, dan kriteria penerimaan untuk Fishing OS Computer-Use Assistant. Dokumen menjadi acuan bersama bagi perancangan, implementasi, integrasi dengan Fishing OS, pengujian, dan pemeliharaan fitur.
1.2 Tujuan Produk
Fishing OS Computer-Use Assistant adalah fitur AI lokal yang memungkinkan pengguna memberikan instruksi bahasa alami untuk membantu menjalankan pekerjaan produktivitas pada desktop Fishing OS. Assistant dapat memahami permintaan, menyusun langkah, menggunakan tool yang diizinkan, berinteraksi dengan aplikasi desktop aktif, dan melaporkan hasil kepada pengguna.
Assistant merupakan salah satu nilai tambah Fishing OS. Ia bukan produk mandiri, bukan distribusi portabel, dan tidak ditujukan untuk dipindahkan atau dipasang sebagai aplikasi generik pada distro Linux lain.
1.3 Konvensi Persyaratan
Setiap persyaratan diberi ID unik. Prioritas Critical berarti wajib untuk rilis; High berarti penting untuk kemampuan inti; Medium berarti dapat dijadwalkan setelah alur inti stabil. Istilah “harus” menyatakan persyaratan normatif. “Disarankan” menyatakan rekomendasi desain yang dapat disesuaikan melalui keputusan teknis terdokumentasi.
1.4 Definisi dan Singkatan
Istilah
Definisi
Fishing OS Live ISO
Image Live untuk menjalankan Fishing OS dan memulai proses instalasi. Image ini tidak memuat Computer-Use Assistant.
Installed Fishing OS
Sistem Fishing OS yang telah dipasang pada disk target pengguna.
Computer-Use Assistant
Fitur AI terintegrasi yang mengorkestrasi model lokal dan tool produktivitas desktop.
LLM
Large Language Model; digunakan untuk memahami instruksi, menyusun rencana, dan memilih tool.
VLM
Vision-Language Model; digunakan untuk memahami screenshot dan konteks visual desktop.
AT-SPI2
Infrastruktur accessibility Linux untuk memperoleh informasi semantik dari aplikasi yang mendukungnya.
UI grounding
Proses mengidentifikasi target interaksi seperti tombol, menu, field, atau area tampilan.
Tool registry
Daftar tool bertipe dan diizinkan yang dapat dipanggil oleh orchestrator.
Capability-first
Strategi pengembangan yang memprioritaskan kemampuan inti dan keandalan sebelum penyempurnaan kosmetik antarmuka.
Privilege Broker
Komponen sistem minimal yang memediasi operasi administratif dengan hak root atas permintaan Control Service setelah otorisasi pengguna; tidak menjalankan sesi desktop atau model AI sebagai root.
Administrator Mode
Mode yang diaktifkan secara sadar oleh pengguna setelah autentikasi sistem, untuk mengizinkan Assistant menggunakan kapabilitas administratif selama sesi yang dapat dicabut.
2. Deskripsi Umum Produk
2.1 Perspektif Produk
Computer-Use Assistant merupakan komponen resmi dari Fishing OS. Distribusi dan pengelolaannya mengikuti mekanisme paket, repository, konfigurasi, dan pembaruan Fishing OS. Komponen ini tidak menjadi dependensi wajib sistem dasar.
2.2 Model Distribusi dan Batas Instalasi
Varian Fishing OS
Ketersediaan Assistant
Ketentuan
Live ISO
Tidak tersedia
Tidak boleh menyertakan paket core, runtime, launcher, UI, service, model LLM, model VLM, maupun konfigurasi khusus Assistant.
Instalasi ke disk - tanpa pilihan Assistant
Tidak tersedia
Installer memasang sistem dasar saja. Tidak boleh ada service atau launcher Assistant yang tertinggal.
Instalasi ke disk - dengan pilihan Assistant
Tersedia
Installer memasang paket dan model yang diperlukan dari sumber resmi Fishing OS ke target sistem.
Installed Fishing OS - pemasangan setelah instalasi
Dapat dipasang
Pengguna dapat memasang Assistant melalui mekanisme paket resmi setelah OS terpasang, jika repository dan prasyarat tersedia.
Keputusan wajib: Live ISO tidak membawa Assistant dalam bentuk apa pun. Pilihan pemasangan hanya berlaku untuk target instalasi ke disk.
2.3 Profil Pengguna
Pengguna desktop: memberi instruksi, melihat rencana, menyetujui operasi berisiko, memantau proses, dan menghentikan tugas.
Pengguna teknis: menggunakan CLI/TUI untuk menjalankan tugas, melihat status, mengatur konfigurasi, dan membaca log.
Maintainer Fishing OS: membangun paket, memelihara repository, menandatangani rilis, mengintegrasikan installer, dan menjalankan pengujian rilis.
2.4 Lingkungan Operasi
Sistem operasi target: Fishing OS berbasis Arch Linux sesuai baseline proyek.
Sesi desktop target: Hyprland/Wayland sesuai konfigurasi Fishing OS.
Akses desktop: berjalan pada sesi pengguna yang sedang login. Control Service dan UI tetap berjalan sebagai pengguna biasa; operasi administratif dilakukan melalui Privilege Broker terpisah setelah autentikasi dan otorisasi pengguna.
Integrasi layanan: service per pengguna melalui systemd user session, atau mekanisme setara yang disetujui arsitektur Fishing OS.
Hardware referensi pengembangan/evaluasi: Intel Core i7-14650HX, RAM 16 GB, NVIDIA RTX 4050 6 GB VRAM, dan SSD 512 GB. Ini adalah profil referensi, bukan pernyataan spesifikasi minimum universal.
2.5 Asumsi dan Batasan
Fitur inti AI berjalan secara lokal. Pengiriman prompt, screenshot, dokumen, atau isi file ke layanan cloud bukan bagian dari operasi normal.
Koneksi internet boleh digunakan saat instalasi atau pembaruan untuk mengunduh paket dan model dari sumber resmi; hal tersebut berbeda dari inferensi AI saat fitur digunakan.
Aplikasi desktop tidak selalu menyediakan accessibility metadata yang lengkap. VLM dan interaksi berbasis koordinat menjadi fallback dengan verifikasi tambahan.
Assistant ditujukan untuk mengelola perangkat secara luas, termasuk file pengguna, konfigurasi sistem, aplikasi, paket, service, proses, jaringan, dan perangkat penyimpanan lokal. Akses terhadap resource yang memerlukan hak administrator dilakukan melalui Privilege Broker dan mekanisme autentikasi sistem; batas hak akses OS tetap berlaku.
Fitur tidak dirancang agar dapat dipindahkan sebagai instalasi mandiri ke distro lain atau dijalankan secara portable dari media eksternal.
3. Arsitektur dan Desain Sistem
3.1 Prinsip Arsitektur
1.  OS-integrated: paket, konfigurasi, launcher, service, dan pembaruan dikelola sebagai bagian dari Fishing OS.
2.  Optional-by-installation: komponen Assistant tidak wajib untuk sistem dasar dan hanya dipasang jika dipilih pengguna.
3.  Local-first: inferensi LLM/VLM dan eksekusi tool berlangsung di perangkat pengguna.
4.  One control plane: GUI dan CLI/TUI menggunakan service, state, izin, dan log yang sama.
5.  Deterministic execution: model merencanakan dan memilih tool; kode tool yang tervalidasi menjalankan tindakan.
6.  Visible and interruptible: aktivitas desktop harus berada pada sesi pengguna yang terlihat dan dapat dihentikan.
3.2 Gambaran Komponen
Lapisan/Komponen
Tanggung jawab
Fishing OS Installer
Menampilkan opsi Assistant dan memasang paket ke root filesystem target bila dipilih.
Fishing OS Package Repository
Mendistribusikan paket yang ditandatangani, metadata versi, dependency, dan manifest model.
OS Integration Layer
Launcher, konfigurasi, user service, permission, desktop entry, dan integrasi pembaruan.
Assistant Control Service
Mengelola sesi, task lifecycle, IPC, pembatalan, status, dan akses antarmuka.
Task Orchestrator
Memecah instruksi menjadi rencana, memilih tool, memvalidasi state, serta mengendalikan model.
Local Model Manager
Memuat, melepas, dan memilih model LLM/VLM sesuai kebutuhan serta batas hardware.
LLM Planner
Memahami instruksi, membuat rencana, dan menghasilkan pemanggilan tool berdasarkan schema.
VLM Perception
Memahami screenshot untuk membantu identifikasi elemen dan konteks visual.
UI Grounding
Menggabungkan AT-SPI2, metadata aplikasi, screenshot, dan koordinat target.
Action Executor
Menjalankan aksi keyboard, pointer, scroll, dan interaksi terkontrol pada desktop.
Productivity Tools
Menangani operasi file dan pembuatan/pengeditan dokumen secara langsung melalui library yang tervalidasi.
GUI Control Panel dan CLI/TUI
Menjadi antarmuka pengguna untuk prompt, rencana, persetujuan, status, log, dan kontrol.
Privilege Broker
Menyediakan operasi system-wide dan administratif melalui API/tool bertipe, memverifikasi identitas/otorisasi pengguna, menjalankan operasi elevated, dan mengembalikan hasil secara terkontrol.
3.3 Alur Kerja Tugas
1.  Pengguna membuka Assistant melalui launcher GUI atau perintah CLI/TUI.
2.  Control Service memulai sesi pengguna dan memastikan model/tool yang diperlukan tersedia.
3.  Pengguna memberikan instruksi; orchestrator meminta LLM membuat rencana dan daftar tool bertipe.
4.  Orchestrator memvalidasi rencana, izin, batas direktori, dan kebutuhan konfirmasi.
5.  Jika tugas melibatkan GUI, UI Grounding mencari target melalui AT-SPI2 terlebih dahulu; screenshot/VLM digunakan ketika informasi tidak memadai.
6.  Action Executor melakukan satu atau beberapa aksi yang telah divalidasi, dengan jeda dan pemeriksaan state yang sesuai.
7.  Orchestrator memeriksa hasil, memperbarui status tugas, dan meminta persetujuan baru bila tindakan berisiko atau konteks berubah.
8.  Assistant melaporkan ringkasan hasil, kegagalan, dan lokasi output. Log audit lokal diperbarui.
3.4 Strategi Model Hybrid
Sistem menggunakan dua peran model yang berbeda. LLM berperan sebagai planner dan pengarah tool. VLM berperan sebagai pemahaman visual ketika dibutuhkan. Model tidak diberi kewenangan untuk mengeksekusi perintah sistem secara langsung.
Model
Tugas
Pemanggilan
Local LLM
Memahami instruksi bahasa alami, menyusun rencana bertahap, memilih tool terdaftar, merangkum hasil.
Dipanggil saat menerima instruksi, saat perlu revisi rencana, dan saat interpretasi hasil memerlukan reasoning.
Local VLM
Memahami screenshot, mengenali elemen visual, membantu menentukan lokasi target dan menilai tampilan setelah aksi.
Dipanggil hanya saat UI grounding berbasis accessibility tidak cukup atau verifikasi visual diperlukan.
Target hardware referensi memiliki VRAM 6 GB dan RAM 16 GB. Oleh karena itu model awal harus dievaluasi pada ukuran kecil dan quantization yang sesuai. Kisaran kelas 3B-4B untuk LLM dan 2B-3B untuk VLM dapat digunakan sebagai kandidat benchmark awal, bukan ketetapan model final. Model spesifik, quantization, runtime, context length, dan strategi CPU offload harus dipilih berdasarkan hasil pengujian.
Model Manager harus menghindari pemuatan dua model GPU besar secara bersamaan apabila berisiko menyebabkan kehabisan VRAM.
Model dapat dimuat sesuai kebutuhan dan dilepas setelah idle berdasarkan kebijakan konfigurasi.
Model harus memiliki manifest versi, checksum, sumber, dan informasi lisensi.
Perubahan model tidak boleh mengubah schema tool atau permission policy tanpa perubahan versi dan pengujian.
3.5 Antarmuka GUI dan CLI/TUI
Antarmuka
Kemampuan minimum
GUI Control Panel
Input instruksi; tampilan rencana; status task; indikator tindakan aktif; permintaan persetujuan; stop; ringkasan dan log.
CLI/TUI
Menjalankan task; menampilkan rencana/status; menerima approval; menampilkan log; melihat status model; mengatur opsi dasar; stop task.
Control Service
Sumber state tunggal; mengatur task, permission, model, cancellation, dan IPC untuk kedua antarmuka.
GUI dan CLI/TUI tidak boleh memiliki implementasi executor terpisah. Keduanya harus memanggil Control Service yang sama melalui IPC lokal, misalnya Unix domain socket dengan permission per pengguna.
3.6 Diagram Konteks Logis
Fishing OS Installed System
  ├─ Fishing OS Desktop (Hyprland / Wayland)
  ├─ Assistant Control Service
  │    ├─ Task Orchestrator
  │    ├─ Local Model Manager
  │    │    ├─ Local LLM (planning)
  │    │    └─ Local VLM (visual perception)
  │    ├─ UI Grounding (AT-SPI2 + screenshot fallback)
  │    ├─ Action Executor (keyboard / pointer / scroll)
  │    └─ Productivity Tools (files / documents / presentations)
  ├─ GUI Control Panel ─┐
  └─ CLI / TUI ─────────┴─ Local IPC to Control Service
Install-time distribution path:
Live ISO Installer -> Official Fishing OS Repository -> Target Disk
(Live ISO itself contains no Assistant component or model)
4. Persyaratan Antarmuka Eksternal
4.1 Antarmuka Pengguna
GUI harus menampilkan status: stopped, starting, ready, planning, waiting for approval, executing, verifying, completed, failed, dan cancelled.
GUI harus membedakan rencana dari aksi yang telah benar-benar dieksekusi.
CLI/TUI harus menyediakan cara untuk memulai task, melihat status, melihat log, menyetujui aksi, dan menghentikan task.
Kegagalan service atau model harus ditampilkan sebagai pesan yang dapat ditindaklanjuti, bukan sekadar timeout tanpa penjelasan.
4.2 Antarmuka Desktop dan Accessibility
AT-SPI2 menjadi sumber utama informasi semantik seperti role, name, state, dan posisi elemen bila tersedia.
Screenshot/VLM menjadi fallback untuk aplikasi yang tidak menyediakan metadata memadai.
Setiap target visual harus dianggap sementara; koordinat tidak boleh digunakan kembali setelah perubahan layout tanpa verifikasi ulang.
Aksi input harus berjalan pada sesi Wayland/Hyprland milik pengguna dan tidak boleh memerlukan daemon input dengan hak akses yang lebih luas daripada kebutuhan.
Mekanisme screenshot dan input Wayland harus diuji pada versi Hyprland serta konfigurasi Fishing OS yang dirilis.
4.3 Antarmuka Sistem File
File tools harus menggunakan API/library yang sesuai untuk operasi file dan format dokumen. Cakupan file adalah seluruh filesystem lokal yang dapat diakses akun pengguna; resource privileged diakses melalui Privilege Broker setelah autentikasi. Operasi GUI tidak boleh menjadi satu-satunya cara menghasilkan file terstruktur bila pembuatan langsung melalui library lebih andal.
4.4 Antarmuka Repository dan Paket
Installer menggunakan repository resmi Fishing OS atau sumber resmi yang dikelola proyek.
Paket dan metadata repository harus diverifikasi melalui mekanisme signature package manager Fishing OS.
Model yang didistribusikan terpisah harus diverifikasi berdasarkan manifest dan checksum/signature yang didefinisikan.
Assistant runtime tidak boleh mengambil model atau kode eksekusi dari sumber tidak tepercaya saat berjalan.
4.5 Antarmuka IPC
GUI dan CLI/TUI berkomunikasi dengan Control Service melalui IPC lokal. IPC wajib membatasi akses ke pengguna yang berwenang, memvalidasi payload, menerapkan timeout, dan mendukung pembatalan task. Detail protokol dapat dipilih pada tahap desain rinci, tetapi kontrak API dan versi protokol harus terdokumentasi.
5. Persyaratan Fungsional
Persyaratan berikut mendefinisikan perilaku yang wajib disediakan oleh rilis fitur. Prioritas Critical merupakan syarat minimum untuk rilis pertama.
ID
Persyaratan
Prioritas
Kriteria penerimaan ringkas
FR-01
Assistant hanya boleh tersedia sebagai fitur pada Fishing OS yang terpasang ke disk; bukan aplikasi lintas-distro.
Critical
Terpasang dan terdaftar sebagai komponen Fishing OS target.
FR-02
Live ISO tidak boleh menyertakan paket, launcher, runtime, service, model, atau konfigurasi Computer-Use Assistant.
Critical
Audit isi ISO dan filesystem Live tidak menemukan komponen Assistant.
FR-03
Installer harus menyediakan pilihan eksplisit untuk memasang atau tidak memasang Assistant.
Critical
Pilihan terlihat pada langkah optional features dan memengaruhi paket target.
FR-04
Pengguna harus dapat menyelesaikan instalasi Fishing OS tanpa Assistant.
Critical
Instalasi dasar berhasil dan tidak meninggalkan launcher/service Assistant.
FR-05
Jika dipilih, installer harus memasang komponen Assistant yang diperlukan ke target sistem.
Critical
Setelah boot pertama, Assistant dapat dijalankan dan pemeriksaan dependensi lulus.
FR-06
Kegagalan unduhan atau repository Assistant tidak boleh menggagalkan instalasi OS dasar.
Critical
Installer menampilkan status gagal/tertunda dan tetap menyelesaikan instalasi dasar.
FR-07
Assistant harus dapat dipasang setelah OS terinstal melalui mekanisme paket resmi Fishing OS.
High
Pemasangan pasca-instalasi menghasilkan konfigurasi setara dengan pilihan installer.
FR-08
Assistant harus menerima instruksi bahasa alami melalui GUI dan CLI/TUI.
Critical
Instruksi dapat dikirim dan status penerimaan ditampilkan.
FR-09
LLM harus menghasilkan rencana tindakan dan pemanggilan tool berdasarkan tool schema yang terdaftar.
Critical
Output di luar schema ditolak dan tidak dieksekusi.
FR-10
Orchestrator harus memvalidasi rencana, parameter tool, izin, dan urutan aksi sebelum eksekusi.
Critical
Parameter tidak valid atau tidak berizin diblokir.
FR-11
Assistant harus dapat mencari, membaca, membuat, mengubah, menyalin, memindahkan, mengganti nama, dan menghapus file di seluruh filesystem lokal sesuai hak akun pengguna; operasi pada resource privileged dilakukan melalui Privilege Broker.
High
Operasi pada area user dan system-wide berhasil sesuai otorisasi; akses privileged meminta autentikasi dan hasilnya diverifikasi.
FR-12
Assistant harus dapat membuat dan mengedit dokumen terstruktur serta membuka hasilnya pada aplikasi desktop yang sesuai bila diminta.
High
Dokumen dapat dibuka dan diverifikasi dengan format yang ditargetkan.
FR-13
Assistant harus dapat membuat dan mengedit presentasi serta memverifikasi file hasil.
High
Presentasi valid, slide dapat dibuka, dan konten utama sesuai instruksi.
FR-14
Assistant harus dapat meluncurkan aplikasi dan melakukan navigasi menu serta interaksi GUI dasar.
High
Skenario aplikasi target dapat dijalankan secara berulang.
FR-15
Assistant harus mendukung interaksi keyboard, pointer, scroll, seleksi teks, klik kanan, dan pengaturan format yang dibutuhkan.
High
Aksi yang didukung dapat dilakukan dan hasilnya diverifikasi.
FR-16
UI Grounding harus menggunakan AT-SPI2 terlebih dahulu bila metadata aplikasi tersedia.
High
Log diagnostik menunjukkan sumber grounding dan elemen yang dipilih.
FR-17
VLM/screenshot fallback harus tersedia saat accessibility tree tidak memadai.
High
Assistant dapat mengenali target visual dan melakukan verifikasi sebelum/ sesudah aksi.
FR-18
Assistant harus memverifikasi hasil aksi dan mendeteksi perubahan state atau kegagalan.
Critical
Kegagalan tidak dilaporkan sebagai keberhasilan; aksi lanjutan dihentikan atau dievaluasi ulang.
FR-19
Pengguna harus dapat menghentikan task dari GUI, CLI/TUI, atau Ctrl+C pada sesi foreground.
Critical
Tidak ada aksi baru setelah cancellation diterima.
FR-20
Harus tersedia mekanisme penghentian darurat proses/service yang spesifik.
High
Service dapat dihentikan tanpa mematikan proses desktop atau service sistem lain.
FR-21
Assistant harus menyediakan permission gate dan konfirmasi untuk operasi berisiko.
Critical
Aksi berisiko tidak berjalan sebelum persetujuan eksplisit.
FR-22
Assistant harus mencatat trace lokal untuk rencana, tool, hasil, error, approval, dan cancellation.
High
Log dapat diperiksa dan tidak menyimpan konten sensitif berlebihan secara default.
FR-23
GUI dan CLI/TUI harus menggunakan state dan Control Service yang sama.
Critical
Task yang dimulai dari satu interface terlihat dan dapat dikontrol dari interface lain.
FR-24
Assistant harus mengelola status model, pemuatan, kegagalan, dan pelepasan model.
High
Status model ditampilkan dan kegagalan model ditangani tanpa crash sistem.
FR-25
Assistant harus dapat ditutup/dihentikan tanpa meninggalkan proses anak atau input automation yang berjalan.
Critical
Proses anak dihentikan dan resource dilepas setelah shutdown.
FR-26
Assistant harus menyediakan kapabilitas pengelolaan perangkat secara luas, termasuk aplikasi, paket, service, proses, konfigurasi sistem, jaringan, akun lokal, mount, dan perangkat penyimpanan, sepanjang didukung sistem dan diotorisasi pengguna.
Critical
Tiap kategori kapabilitas dapat dipanggil melalui tool yang terdaftar; keterbatasan perangkat/OS dilaporkan dengan jelas.
FR-27
Assistant harus mendukung penggunaan sudo untuk operasi administratif lokal melalui Privilege Broker; Polkit atau mekanisme native setara dapat digunakan bila sesuai dengan alur desktop.
Critical
Perintah yang membutuhkan root memanggil sudo atau autentikasi native; operasi hanya berjalan setelah otorisasi berhasil.
FR-28
Assistant harus menyediakan tool eksekusi perintah lokal untuk perintah yang diminta pengguna, termasuk opsi elevated, dengan command, argumen, working directory, dan dampak yang dapat diperiksa.
Critical
Perintah dijalankan oleh executor; perintah privileged melewati Privilege Broker; output dan exit status dikembalikan.
FR-29
Pengguna harus dapat mengaktifkan dan mencabut Administrator Mode melalui GUI atau CLI/TUI menggunakan autentikasi sistem.
High
Mode hanya aktif setelah autentikasi, memiliki status/masa berlaku yang jelas, dan dapat dicabut segera.
FR-30
Assistant tidak boleh menolak tugas administrasi lokal yang sah hanya karena tugas tersebut memerlukan hak administrator; Assistant harus meminta autentikasi atau persetujuan yang diperlukan.
Critical
Tugas privileged yang didukung berlanjut setelah autentikasi/approval; bila gagal, alasan teknis atau otorisasi dijelaskan.
FR-31
Assistant harus meminta persetujuan eksplisit untuk tindakan berdampak tinggi atau sulit dipulihkan, termasuk penghapusan/format disk, perubahan partisi, bootloader, akun, firewall, izin sistem, dan perubahan konfigurasi keamanan.
Critical
Aksi tidak dijalankan sebelum pengguna menyetujui ringkasan target, perintah, dan dampaknya.
FR-32
Privilege Broker harus mencatat identitas pemanggil, tool/perintah, waktu, hasil, exit status, dan keputusan autentikasi/approval tanpa merekam password atau token rahasia.
Critical
Log audit tersedia dan tidak mengandung kredensial.
FR-33
Pengguna harus dapat menghentikan operasi privileged yang sedang berjalan dan mencabut Administrator Mode.
Critical
Pembatalan menghentikan proses anak yang dapat dihentikan, mencabut sesi elevated, dan mencegah aksi lanjutan.
6. Persyaratan Data
6.1 Kategori Data
Data
Lokasi/masa simpan
Ketentuan
Konfigurasi sistem
Lokasi konfigurasi Fishing OS di /etc atau lokasi resmi yang ditetapkan.
Konfigurasi sistem hanya dapat diubah oleh administrator; konfigurasi user tidak boleh ditimpa saat update tanpa migrasi.
Konfigurasi pengguna
Direktori konfigurasi user, misalnya XDG_CONFIG_HOME.
Menyimpan preferensi interface, model, izin, dan opsi runtime.
Model LLM/VLM
Lokasi aset model yang dikelola paket/model manager di disk target.
Versi, checksum, sumber, dan lisensi harus tercatat; model tidak boleh dieksekusi dari sumber tak tepercaya.
Workspace/output
Direktori kerja yang dipilih pengguna.
File baru harus memiliki lokasi output yang jelas; overwrite memerlukan konfirmasi.
Task state
Memori proses dan/atau state lokal sementara.
Task state harus pulih secara aman atau dibatalkan setelah crash; tidak boleh meneruskan aksi GUI secara otomatis setelah restart.
Log
Lokasi log user/system yang ditetapkan.
Log menyimpan event dan hasil operasi, dengan redaksi konten sensitif.
Screenshot sementara
Memori atau cache sementara sesuai kebutuhan.
Tidak disimpan permanen secara default; retensi harus minimal dan dapat dikendalikan.
6.2 Struktur Log Minimum
Timestamp, task ID, status task, sumber interface, dan versi aplikasi.
Ringkasan instruksi atau identifier task; konten lengkap dapat disamarkan sesuai kebijakan privasi.
Nama tool, parameter yang telah disanitasi, hasil, durasi, dan kode error.
Sumber UI grounding (AT-SPI2 atau VLM), tanpa menyimpan screenshot penuh secara default.
Persetujuan pengguna, pembatalan, dan tindakan yang diblokir.
6.3 Retensi dan Penghapusan
Log harus memiliki kebijakan retensi yang dapat dikonfigurasi. Penghapusan log tidak boleh menghapus file kerja pengguna. Menghapus paket Assistant tidak boleh menghapus dokumen hasil kerja pengguna atau konfigurasi pribadi tanpa persetujuan eksplisit.
7. Persyaratan Non-Fungsional
ID
Persyaratan
Prioritas
NFR-01
Inferensi LLM dan VLM serta eksekusi tool untuk fungsi inti harus berlangsung lokal.
Critical
NFR-02
Live ISO tidak boleh membesar karena paket, runtime, UI, atau model Assistant.
Critical
NFR-03
Assistant tidak boleh menjadi dependency wajib Fishing OS dasar.
Critical
NFR-04
Assistant harus bekerja pada profil hardware referensi RAM 16 GB dan VRAM 6 GB tanpa OOM pada skenario beban rilis yang disepakati.
Critical
NFR-05
Model Manager harus mengendalikan penggunaan RAM/VRAM dan menyediakan strategi unload atau CPU offload.
High
NFR-06
Assistant tidak boleh memulai pemuatan model besar secara otomatis saat boot/login tanpa permintaan atau kebijakan eksplisit pengguna.
High
NFR-07
Startup, pemuatan model, respons instruksi, grounding, dan eksekusi harus diukur dengan benchmark berulang.
High
NFR-08
Performa harus tetap dapat digunakan pada konfigurasi hardware minimum yang ditetapkan sebelum rilis; angka minimum harus dibuktikan melalui pengujian.
High
NFR-09
Pembatalan task harus mencegah aksi berikutnya dan membersihkan proses anak.
Critical
NFR-10
Kegagalan model, IPC, accessibility, atau aplikasi target tidak boleh menyebabkan desktop crash.
Critical
NFR-11
Komponen harus modular sehingga model, UI, executor, dan productivity tools dapat diperbarui secara terpisah dengan kompatibilitas versi terdokumentasi.
High
NFR-12
Paket Assistant harus mengikuti standar paket, signature, dan update Fishing OS.
Critical
NFR-13
GUI dan CLI/TUI harus konsisten terhadap state, izin, dan log task.
Critical
NFR-14
Output dokumen/presentasi harus valid dan dapat dibuka menggunakan aplikasi yang didukung.
High
NFR-15
Log dan screenshot harus menerapkan minimisasi data dan redaksi konten sensitif.
High
NFR-16
Penghapusan Assistant tidak boleh merusak komponen dasar Fishing OS atau file hasil pengguna.
Critical
NFR-17
Seluruh aksi automation harus berjalan pada sesi desktop pengguna yang aktif dan terlihat.
Critical
NFR-18
Privilege separation: Control Service, model, GUI, dan CLI/TUI tidak boleh berjalan sebagai root; operasi elevated harus melalui Privilege Broker minimal.
Critical
NFR-19
Privilege Broker harus menerima permintaan melalui IPC terautentikasi, memvalidasi payload dan target, menerapkan otorisasi native, dan mendukung operasi administratif luas termasuk command yang diminta pengguna; broker tidak menyediakan root shell tanpa autentikasi.
Critical
NFR-20
Password sudo, token autentikasi, dan kredensial lain tidak boleh disimpan oleh model, Control Service, log, atau file konfigurasi Assistant.
Critical
NFR-21
Administrator Mode harus memerlukan autentikasi native OS, menampilkan status aktif, dapat dicabut, dan tidak boleh diaktifkan otomatis saat boot/login.
Critical
NFR-22
Operasi privileged harus memiliki timeout/cancellation, penanganan proses anak, serta audit event yang dapat ditinjau pengguna.
Critical
NFR-23
Assistant tidak boleh mengubah konfigurasi autentikasi, sudoers, atau mekanisme keamanan untuk memberikan dirinya akses permanen tanpa permintaan dan persetujuan administratif eksplisit.
Critical
7.1 Target Pengukuran Performa
SRS ini mewajibkan pengukuran performa, tetapi tidak mengunci angka latensi model yang belum dibuktikan pada hardware target. Pada tahap benchmark, tim harus menetapkan batas numerik untuk startup service, waktu load/unload model, waktu respons LLM, waktu inferensi VLM, keberhasilan grounding, dan konsumsi puncak RAM/VRAM. Ambang tersebut harus dicatat sebagai baseline rilis dan diuji ulang pada perubahan model/runtime.
8. Keamanan, Keselamatan, dan Privasi
8.1 Prinsip Keamanan
Control Service, model runtime, GUI, dan CLI/TUI berjalan sebagai pengguna biasa. Assistant dapat meminta operasi administratif melalui Privilege Broker terpisah; menjalankan model atau sesi desktop sebagai root dilarang.
Model tidak boleh mengeksekusi output mentah secara langsung. Operasi sistem dan shell command harus melalui tool registry, validasi parameter, proses otorisasi, dan executor. Tool command dapat menjalankan perintah lokal yang diminta pengguna, termasuk dengan hak sudo, melalui jalur eksekusi yang terlihat dan diaudit.
Tool filesystem harus menerapkan canonical path check, mencegah path traversal, dan menghormati permission filesystem. Cakupan operasi tidak dibatasi hanya pada home/workspace: resource system-wide dapat diakses sesuai hak akun atau melalui Privilege Broker setelah otorisasi administratif.
IPC hanya boleh diakses oleh pengguna yang berwenang; socket dan file state memiliki permission yang ketat.
Paket dan model didistribusikan melalui sumber resmi yang tervalidasi. Lisensi model harus ditinjau sebelum dimasukkan ke distribusi.
8.2 Klasifikasi Risiko Tindakan
Kategori
Contoh
Perilaku wajib
Rendah
Membaca/list file, mencari, membuka aplikasi, memeriksa status sistem, melihat service/proses.
Dapat dijalankan sesuai hak akun dan konfigurasi pengguna; laporkan sumber data dan hasil.
Sedang
Mengubah file/config, memasang paket, mengelola service, mengubah pengaturan desktop atau jaringan yang dapat dipulihkan.
Jalankan sesuai otorisasi; tampilkan rencana. Minta autentikasi sudo/Polkit bila diperlukan dan persetujuan sesuai dampak.
Tinggi / kritis
Menghapus/format disk, mengubah partisi/bootloader, menghapus akun, mengubah firewall atau izin keamanan, operasi massal yang sulit dipulihkan.
Wajib tampilkan target, perintah, konsekuensi, dan minta persetujuan eksplisit terpisah sebelum menjalankan.
Dibatasi oleh keselamatan dan otorisasi
Tindakan tanpa otorisasi terhadap pihak lain, pencurian kredensial, penyamaran aktivitas, atau upaya melewati kontrol akses yang bukan milik pengguna.
Tidak dijalankan. Assistant menjelaskan batas yang relevan dan dapat menawarkan cara administrasi lokal yang sah.
8.3 Prompt Injection dan Konten Tidak Tepercaya
Isi dokumen, halaman, nama file, teks aplikasi, dan screenshot harus diperlakukan sebagai data, bukan instruksi sistem. Konten yang meminta Assistant mengabaikan kebijakan, membuka kredensial, menjalankan perintah, atau mengirim data harus diabaikan kecuali pengguna memberikan instruksi terpisah yang sah dan tindakan tetap lolos policy gate. Instruksi yang berasal dari file tidak boleh mengubah tool allowlist atau izin.
8.4 Privasi
Tidak ada pengiriman konten pengguna ke API LLM/VLM cloud untuk fungsi inti.
Screenshot tidak disimpan secara permanen secara default.
Log tidak boleh merekam password, token, kunci privat, atau isi dokumen lengkap secara default.
Pengguna harus mengetahui lokasi output dan jenis operasi yang dilakukan Assistant.
8.5 Penghentian Aman
Control Service menyediakan cancellation token yang diperiksa sebelum setiap aksi. Ctrl+C menghentikan task pada sesi foreground; GUI dan CLI/TUI menyediakan stop command. Mekanisme darurat harus dapat menghentikan service/proses Assistant secara spesifik, misalnya melalui perintah stop resmi, penghentian unit user service, atau perintah spesifik seperti `pkill -TERM -x <nama-proses-assistant>`. Menghentikan Assistant tidak boleh menghentikan compositor, desktop shell, atau service Fishing OS lain.
8.6 Akses Administratif dan Kendali Perangkat
Tujuan kapabilitas Assistant adalah mampu membantu mengelola perangkat Fishing OS secara luas, bukan hanya direktori home atau workspace. Cakupan meliputi filesystem lokal, aplikasi, package manager, service, proses, konfigurasi sistem, jaringan, akun lokal, mount, dan perangkat penyimpanan yang tersedia pada perangkat.
Control Service, GUI, CLI/TUI, dan model harus tetap berjalan sebagai pengguna biasa pada sesi desktop. Assistant tidak boleh menjalankan seluruh proses AI atau desktop sebagai root. Untuk tugas yang membutuhkan hak administrator, Control Service meminta Privilege Broker menjalankan sudo sebagai jalur utama; Polkit atau mekanisme native Fishing OS setara dapat digunakan bila sesuai.
Privilege Broker harus menjadi komponen kecil dengan antarmuka IPC terautentikasi, validasi tool dan parameter, pembatasan proses, timeout, cancellation, serta audit. Broker tidak boleh menyediakan akses root tanpa autentikasi. Installer tidak boleh menambahkan aturan sudoers NOPASSWD atau menyimpan password pengguna untuk kepentingan Assistant.
Assistant tidak boleh menolak tugas administrasi lokal yang sah hanya karena memerlukan sudo. Sudo merupakan kapabilitas yang didukung secara eksplisit, bukan kondisi yang otomatis menyebabkan penolakan. Assistant harus menjelaskan kebutuhan hak akses, memanggil autentikasi sistem, dan melanjutkan setelah otorisasi berhasil. Administrator Mode dapat diaktifkan pengguna untuk sesi tertentu dan harus dapat dicabut. Mode ini tidak menghilangkan konfirmasi untuk operasi berdampak tinggi atau sulit dipulihkan.
Untuk eksekusi command, Assistant harus menampilkan perintah, argumen, target, working directory, dan ringkasan dampak sebelum tindakan privileged dijalankan. Password, token, dan rahasia tidak boleh diserahkan ke model atau ditulis ke log. Kegagalan autentikasi, permission denied, keterbatasan hardware, atau operasi yang tidak didukung harus dilaporkan secara jujur; Assistant tidak boleh mengklaim tindakan berhasil bila tidak ada bukti hasil.
Istilah “akses penuh” pada SRS ini berarti cakupan kapabilitas pengelolaan perangkat yang luas melalui hak akun dan elevasi yang disahkan pemilik perangkat. Istilah tersebut tidak berarti proses AI selalu berjalan sebagai root, melewati autentikasi OS, atau menjalankan semua tindakan tanpa persetujuan.
9. Persyaratan Distribusi, Paket, dan Installer
9.1 Pemisahan Artefak
Artefak
Memuat Assistant?
Tujuan
Fishing OS Live ISO
Tidak
Boot Live dan menjalankan installer; image tetap ringan.
Fishing OS Base Packages
Tidak
Menyediakan sistem dasar tanpa dependensi Assistant.
Assistant Core Packages
Ya
Control Service, orchestrator, executor, tool, dan integrasi OS.
Assistant UI Packages
Ya
GUI Control Panel dan CLI/TUI.
Assistant Model Assets
Ya
Model LLM/VLM, manifest, checksum, dan informasi lisensi.
9.2 Alur Instalasi
1.  Pengguna boot Live ISO dan membuka installer.
2.  Pengguna menyelesaikan konfigurasi disk dan sistem dasar.
3.  Installer menampilkan pilihan Computer-Use Assistant sebagai fitur opsional.
4.  Jika tidak dipilih, installer tidak memasang paket atau model Assistant.
5.  Jika dipilih, installer memeriksa jaringan, ruang disk, kompatibilitas hardware, dan ketersediaan repository.
6.  Installer mengunduh metadata/paket/model dari sumber resmi, memverifikasi signature/checksum, lalu memasang komponen ke target disk.
7.  Jika unduhan atau pemasangan Assistant gagal, installer mencatat status dan melanjutkan pemasangan OS dasar bila kondisi sistem memungkinkan.
8.  Setelah boot ke sistem terpasang, Assistant tersedia melalui launcher dan CLI/TUI apabila pemasangan berhasil.
9.3 Perilaku Offline dan Kegagalan Repository
Instalasi Fishing OS dasar harus tetap dapat diselesaikan tanpa internet. Jika pengguna memilih Assistant tetapi paket/model tidak dapat diunduh atau diverifikasi, installer harus menjelaskan bahwa Assistant belum terpasang, tidak boleh mengklaim pemasangan berhasil, dan tetap menyelesaikan instalasi OS dasar. Pengguna dapat memasang Assistant kemudian melalui repository resmi.
9.4 Siklus Hidup Paket
Paket harus memiliki versi dan dependency yang konsisten serta dapat diperbarui melalui package manager Fishing OS.
Pembaruan Assistant dan model tidak boleh mengharuskan reinstall OS.
Uninstall harus menghapus paket, unit service, launcher, dan file sistem milik Assistant, tetapi mempertahankan file output pengguna.
Migrasi konfigurasi harus memiliki mekanisme versi dan backup bila format konfigurasi berubah.
Repository harus memisahkan metadata paket executable dari model asset berukuran besar bila diperlukan untuk efisiensi distribusi.
9.5 Persyaratan Isi Live ISO
Pipeline rilis Live ISO harus memiliki pemeriksaan eksplisit yang gagal bila menemukan salah satu komponen berikut: paket Assistant, runtime AI khusus Assistant, launcher/menu entry, systemd unit/service Assistant, konfigurasi Assistant, model LLM/VLM Assistant, atau direktori aset khusus Assistant. Pemeriksaan dilakukan pada artefak ISO final, bukan hanya daftar package build.
10. Strategi Verifikasi dan Pengujian
10.1 Tingkat Pengujian
Jenis uji
Fokus
Contoh bukti
Unit test
Validasi tool, path check, schema, permission, cancellation, parser konfigurasi, model manager.
Hasil pytest/unit test dan coverage.
White-box test
Cabang internal policy gate, state machine task, penanganan error, dan jalur cancellation.
Branch coverage, code review, mutation test bila tersedia.
Black-box test
Perilaku dari sudut pandang pengguna tanpa mengandalkan detail internal.
Test case dengan input, aksi, output, dan expected result.
Integration test
Interaksi Control Service, model runtime, AT-SPI2, executor, GUI/CLI, filesystem, dan package manager.
Log integrasi dan hasil task.
Installer/distribution test
Pilihan pemasangan, kegagalan repository, hasil target root, dan audit Live ISO.
Install test matrix dan laporan audit ISO.
Performance test
RAM/VRAM, latensi model, startup, unload, dan kestabilan task panjang.
Benchmark pada hardware target.
Security test
Path traversal, tool injection, prompt injection, akses IPC, permission bypass, dan secret leakage.
Laporan security test dan bukti penolakan.
Regression test
Menjaga perilaku yang sebelumnya lulus setelah perubahan kode, model, atau paket.
Hasil CI dan release test report.
Privilege broker test
Autentikasi native, IPC permission, sudo/Polkit, cancellation, audit, dan isolasi hak root.
Hasil uji broker; bukti proses model tetap berjalan sebagai user; tidak ada secret di log.
10.2 Black-Box Test Cases Minimum
ID
Skenario
Langkah/input
Hasil yang diharapkan
BB-01
Instalasi tanpa Assistant
Pilih tidak saat installer menawarkan Assistant.
Fishing OS terpasang; tidak ada launcher, service, paket, atau model Assistant.
BB-02
Instalasi dengan Assistant
Pilih Assistant dengan repository tersedia.
Paket dan model valid terpasang; Assistant dapat dijalankan setelah boot.
BB-03
Repository tidak tersedia
Pilih Assistant ketika repository tidak dapat diakses.
OS dasar tetap terpasang; status Assistant dinyatakan gagal/tertunda.
BB-04
Audit Live ISO
Boot dan periksa isi Live ISO.
Tidak ada komponen Assistant.
BB-05
Prompt produktivitas
Minta pencarian file pada direktori yang diizinkan.
File yang cocok ditemukan dan sumber hasil dilaporkan.
BB-06
Akses ke resource sistem
Minta membaca atau mengubah file konfigurasi root-owned di area sistem, misalnya /etc.
Assistant menggunakan hak user bila cukup; bila butuh root, meminta autentikasi sudo dan melanjutkan setelah otorisasi.
BB-07
Pembuatan dokumen
Minta dokumen dengan heading dan tabel.
Dokumen valid, tersimpan pada lokasi yang disetujui, dapat dibuka.
BB-08
Pembuatan presentasi
Minta presentasi dengan beberapa slide.
File presentasi valid dan dapat dibuka.
BB-09
UI grounding
Minta interaksi pada tombol aplikasi yang didukung AT-SPI2.
Target dipilih melalui metadata dan hasil aksi diverifikasi.
BB-10
Visual fallback
Gunakan aplikasi/elemen yang tidak expose accessibility lengkap.
VLM membantu grounding; aksi tetap diverifikasi sebelum lanjut.
BB-11
Konfirmasi overwrite
Minta membuat file pada lokasi yang sudah berisi file.
Assistant meminta persetujuan sebelum menimpa.
BB-12
Stop task
Hentikan task dari GUI, CLI/TUI, Ctrl+C, atau mekanisme darurat proses spesifik.
Tidak ada aksi baru setelah cancellation; proses anak dibersihkan.
BB-13
Konsistensi interface
Mulai task dari GUI, lihat dan hentikan dari CLI/TUI.
Keduanya menampilkan state task yang sama.
BB-14
Uninstall
Hapus paket Assistant.
Assistant hilang; OS dasar dan file output pengguna tetap tersedia.
BB-15
Operasi system-wide non-privileged
Minta Assistant memeriksa aplikasi terpasang, service, proses, dan filesystem lokal.
Informasi dikembalikan dari sumber lokal; tidak memerlukan sudo untuk data yang memang dapat diakses akun.
BB-16
Operasi membutuhkan sudo
Minta perubahan konfigurasi sistem yang sah dan memerlukan root.
Assistant memanggil autentikasi native; operasi hanya berjalan setelah otorisasi berhasil.
BB-17
Autentikasi sudo gagal
Batalkan atau masukkan kredensial salah pada prompt sistem.
Operasi privileged tidak berjalan; Assistant menjelaskan kegagalan dan tidak mencoba bypass.
BB-18
Administrator Mode
Aktifkan mode melalui GUI, lakukan tugas administratif, lalu cabut mode.
Mode aktif hanya setelah autentikasi; status terlihat; pencabutan mencegah operasi elevated berikutnya.
BB-19
Perintah lokal dengan sudo
Minta perintah administrasi lokal dengan target dan tujuan yang jelas.
Perintah dan dampaknya dapat diperiksa; eksekusi melalui Privilege Broker; hasil dan exit status dicatat.
BB-20
Operasi destruktif
Minta format disk atau perubahan partisi.
Assistant menampilkan device/partisi dan konsekuensi; meminta persetujuan eksplisit terpisah; tidak berjalan tanpa approval.
BB-21
Audit dan kerahasiaan kredensial
Jalankan tugas sudo dan periksa log.
Log merekam tindakan dan hasil tetapi tidak menyimpan password, token, atau secret.
BB-22
Pembatalan operasi elevated
Hentikan command privileged yang sedang berjalan.
Pembatalan diteruskan ke proses anak; tidak ada langkah lanjutan; status final dicatat.
10.3 White-Box Test Focus
Semua operasi tool melewati schema validation dan permission gate; tidak ada jalur eksekusi langsung dari output model.
Cancellation diperiksa sebelum dan sesudah setiap aksi eksternal yang memungkinkan; state terminal task tidak boleh kembali ke executing.
Path canonicalization diuji terhadap ../, symlink, absolute path, path encoding, dan race condition yang relevan.
State machine mencakup ready, planning, approval, executing, verifying, completed, failed, dan cancelled dengan transisi yang sah.
Failure handling diuji pada model timeout, model OOM, IPC putus, aplikasi tertutup, target UI hilang, AT-SPI2 gagal, dan executor berhenti.
10.4 CI/CD dan Quality Gate
Pipeline CI/CD paket Assistant harus berjalan terpisah dari pipeline pembangunan Live ISO, tetapi keduanya memiliki tes integrasi rilis. Pull request yang mengubah Assistant harus menjalankan pemeriksaan berikut sesuai lingkup perubahan:
Linting, formatting, static type checking, dependency/security scanning, dan pemeriksaan lisensi dependency/model.
Unit test serta white-box test untuk tool registry, permission, task state, dan cancellation.
Black-box test menggunakan fixture dan mock desktop/model pada runner yang sesuai.
Integration test untuk model runtime, AT-SPI2, Wayland/Hyprland, GUI/CLI, dan file tools; tes yang membutuhkan sesi desktop dijalankan pada runner khusus atau job manual terkontrol.
Build paket, dependency resolution, signature/staging validation, dan install/uninstall test pada Fishing OS target.
Audit Live ISO untuk memastikan seluruh komponen Assistant tidak ikut terbawa.
Hardware benchmark pada profil referensi sebelum rilis model/runtime utama.
Rilis tidak boleh dipromosikan bila ada kegagalan pada test Critical, verifikasi signature, audit Live ISO, atau pengujian penghentian aman. Hasil CI harus menyimpan versi commit, versi paket, versi model, konfigurasi benchmark, dan artefak laporan.
11. Kriteria Penerimaan
ID
Area
Kriteria penerimaan
AC-01
Live ISO
Live ISO boot dan installer berfungsi; tidak ada paket, launcher, runtime, service, konfigurasi, maupun model Assistant.
AC-02
Instalasi tanpa Assistant
Instalasi OS dasar berhasil; tidak ada komponen Assistant pada target.
AC-03
Instalasi dengan Assistant
Pilihan installer memasang seluruh dependency yang diperlukan; verifikasi paket/model berhasil; Assistant dapat dijalankan.
AC-04
Degradasi instalasi
Kegagalan repository/model tidak membatalkan pemasangan OS dasar dan ditampilkan secara jelas.
AC-05
Kemampuan inti
File search, operasi file yang diizinkan, pembuatan dokumen, dan presentasi lulus skenario black-box.
AC-06
Desktop automation
AT-SPI2 diprioritaskan, VLM fallback tersedia, dan aksi UI diverifikasi.
AC-07
Hybrid model
LLM dan VLM berjalan sesuai peran dengan manajemen memori yang lulus benchmark hardware target.
AC-08
Dua antarmuka
GUI dan CLI/TUI mengakses Control Service dan state task yang sama.
AC-09
Safety
Tidak ada eksekusi langsung dari output model; operasi system-wide mengikuti permission OS, sudo melalui Privilege Broker, dan aksi berisiko memerlukan konfirmasi.
AC-10
Stop dan shutdown
Stop dari GUI/CLI/Ctrl+C membatalkan aksi lanjutan dan membersihkan proses anak.
AC-11
CI/CD
Quality gate Critical lulus; hasil tes dan metadata build tersedia.
AC-12
Pemeliharaan
Update dan uninstall tidak merusak Fishing OS dasar atau data kerja pengguna.
AC-13
Kendali perangkat system-wide
Assistant dapat memeriksa dan mengelola kapabilitas lokal di luar home/workspace sesuai hak akun serta izin administratif.
AC-14
Sudo dan Privilege Broker
Operasi yang memerlukan root menggunakan autentikasi native melalui broker; Control Service dan model tetap berjalan sebagai user.
AC-15
Administrator Mode
Pengguna dapat mengaktifkan/mencabut mode setelah autentikasi; mode tidak aktif otomatis dan statusnya terlihat.
AC-16
Eksekusi command
Perintah yang diotorisasi dijalankan melalui executor; perintah elevated dapat diperiksa sebelum eksekusi dan hasilnya diaudit.
AC-17
Keselamatan operasi kritis
Format disk, partisi, bootloader, penghapusan akun, dan perubahan keamanan memerlukan konfirmasi eksplisit target dan konsekuensi.
AC-18
Kerahasiaan kredensial
Password sudo/Polkit tidak disimpan, tidak dikirim ke model, dan tidak muncul pada log.
12. Tahapan Implementasi
Urutan kerja mengikuti strategi capability-first. Tahapan dapat berjalan iteratif, tetapi dependensi keamanan, cancellation, dan integrasi OS harus dibangun sejak awal.
Tahap
Fokus
Exit criteria
Phase 0 - OS integration foundation
Tetapkan struktur package group, repository, manifest model, konfigurasi, lifecycle service, dan kontrak installer.
Desain paket dan integrasi; build paket minimal; test instalasi/uninstall dasar.
Phase 1 - Core control plane
Bangun Control Service, orchestrator, tool registry, permission gate, state machine, IPC, dan cancellation.
Task dummy end-to-end; stop dari CLI dan GUI stub; audit tool schema.
Phase 2 - Capability dasar
Implementasi file search/read/create/copy/move/rename dan pembuatan dokumen/presentasi melalui library.
Skenario black-box file, dokumen, dan presentasi lulus.
Phase 3 - Desktop automation
Integrasikan Wayland/Hyprland input, AT-SPI2, screenshot capture, dan verifikasi pasca-aksi.
Skenario GUI dasar lulus pada aplikasi target.
Phase 4 - Hybrid AI
Integrasikan LLM planner, VLM perception, model manager, quantization, dan resource controls.
Benchmark hardware; tool invocation tervalidasi; fallback visual lulus.
Phase 5 - GUI dan CLI/TUI
Selesaikan kedua antarmuka pada Control Service yang sama.
Task dapat dimulai, dipantau, disetujui, dan dihentikan dari kedua interface.
Phase 6 - Installer dan release hardening
Integrasikan opsi installer, repository, signature, kegagalan offline, uninstall, serta audit Live ISO.
Matriks instalasi dan acceptance criteria rilis lulus.
13. Ketergantungan, Risiko, dan Keputusan yang Belum Dikunci
13.1 Ketergantungan Eksternal
Repository resmi Fishing OS dan infrastruktur signing paket.
Mekanisme installer Fishing OS untuk pemilihan optional feature dan pemasangan ke target root filesystem.
Runtime inferensi lokal yang sesuai dengan platform CPU/GPU dan model quantized.
AT-SPI2, mekanisme screenshot Wayland/Hyprland, serta metode input yang kompatibel dengan sesi desktop Fishing OS.
Aplikasi desktop target untuk pengujian dokumen, presentasi, dan interaksi GUI.
13.2 Risiko dan Mitigasi
Risiko
Dampak
Mitigasi
Ukuran model besar
Pemasangan lambat dan kebutuhan disk tinggi.
Pisahkan model dari paket core; tampilkan estimasi disk; gunakan model quantized dan manifest.
VRAM 6 GB terbatas
OOM atau latensi tinggi.
Model kecil, pemuatan sesuai kebutuhan, unload, CPU offload, dan benchmark nyata.
Accessibility tidak lengkap
Target GUI salah atau tidak ditemukan.
AT-SPI2 dengan fallback VLM; verifikasi target dan state setelah aksi.
Perubahan Hyprland/Wayland
Metode input/capture dapat rusak setelah update.
Lapisan adapter, versi kompatibilitas, integration test pada release candidate.
Repository/jaringan gagal
Assistant tidak terpasang saat instalasi.
Jangan gagalkan OS dasar; sediakan status dan instalasi ulang pasca-boot.
Prompt injection dari dokumen/UI
Tool dipakai di luar maksud pengguna.
Pisahkan instruksi dan data; schema tool; permission gate; approval untuk aksi berisiko.
Task berjalan terlalu lama
Desktop tidak responsif atau tindakan berulang.
Batas aksi/waktu, cancellation token, status yang terlihat, dan stop darurat.
13.3 Keputusan Teknis yang Belum Dikunci
SRS ini mengunci perilaku produk dan batas integrasi, tetapi tidak mengunci pilihan implementasi yang harus dibuktikan melalui prototipe. Hal-hal berikut wajib diputuskan melalui benchmark, threat modeling, atau pengujian kompatibilitas sebelum rilis:
Nama dan versi model LLM/VLM, quantization, context length, dan lisensi distribusinya.
Runtime model final dan strategi GPU/CPU offload.
Framework GUI/TUI dan protokol IPC yang dipakai.
Metode final screenshot capture dan input automation pada Wayland/Hyprland.
Daftar aplikasi desktop yang secara resmi didukung pada rilis pertama.
Direktori awal yang diprioritaskan untuk workspace, retensi log, dan ambang numerik benchmark performa.
Lampiran A. Matriks Keterlacakan
Matriks berikut menghubungkan tujuan produk dengan persyaratan dan validasi utama.
Tujuan
Persyaratan terkait
Validasi utama
Assistant menjadi nilai tambah terintegrasi Fishing OS
FR-01 s.d. FR-07; NFR-02, NFR-03, NFR-12
Audit paket, uji installer, uji repository, update/uninstall.
Live ISO tetap ringan dan tanpa AI Assistant
FR-02; NFR-02
Audit artefak ISO final dan boot test.
Pengguna dapat memilih Assistant saat instalasi
FR-03 s.d. FR-06
Black-box install matrix: yes/no/offline/repository failure.
Mendukung produktivitas file dan office
FR-11 s.d. FR-15
Black-box file/document/presentation dan verifikasi output.
Memiliki automation desktop yang adaptif
FR-16 s.d. FR-18; NFR-17
Integration test AT-SPI2, VLM fallback, dan verifikasi aksi.
Menggunakan AI hybrid lokal
FR-09, FR-24; NFR-01, NFR-04, NFR-05
Model/tool tests, benchmark RAM/VRAM, dan model failure test.
GUI dan CLI/TUI konsisten
FR-08, FR-19, FR-23; NFR-13
Cross-interface task state dan cancellation tests.
Aman, dapat dihentikan, dan menjaga privasi
FR-19 s.d. FR-22, FR-25; NFR-09, NFR-10, NFR-15
White-box, security, privacy, cancellation, dan shutdown tests.
Mendukung kendali system-wide dan operasi sudo yang diotorisasi
FR-26 s.d. FR-33; NFR-18 s.d. NFR-23
Black-box privileged test, broker security test, audit log test, dan cancellation test.
Lampiran B. Keputusan Baseline Produk
Aspek
Keputusan final SRS v1.1
Posisi produk
Fitur resmi Fishing OS, bukan proyek mandiri.
Distribusi
Hanya untuk instalasi Fishing OS ke disk.
Live ISO
Assistant sepenuhnya dikeluarkan dari Live ISO.
Instalasi
Pengguna ditanya saat instalasi apakah ingin memasang Assistant.
Kondisi offline
Instalasi OS dasar tetap dapat berjalan; Assistant dapat dipasang kemudian.
Model AI
Strategi hybrid: local LLM untuk planning dan local VLM untuk visual understanding.
Antarmuka
GUI dan CLI/TUI, keduanya menggunakan satu Control Service.
Prioritas
Capability-first: kapabilitas produktivitas dan keandalan didahulukan.
Eksekusi
Terlihat pada desktop aktif, dijalankan sebagai user, dapat dihentikan.
Operasi inti
Lokal; tidak mengandalkan cloud inference.
Portabilitas
Tidak dirancang untuk dipindahkan atau dijalankan sebagai aplikasi lintas-distro.
Cakupan akses
Kapabilitas pengelolaan perangkat system-wide; bukan hanya home/workspace, sesuai hak OS dan autentikasi administratif.
Hak administrator
Sudo/Polkit melalui Privilege Broker; model dan desktop session tidak berjalan sebagai root.
Prinsip respons
Tidak menolak tugas administrasi lokal yang sah hanya karena membutuhkan hak administrator; autentikasi, approval, dan batas teknis tetap berlaku.
Operasi kritis
Operasi destruktif atau sulit dipulihkan memerlukan persetujuan eksplisit terhadap target dan dampak.
