import type { ReactNode } from "react"

type NodeProps = {
  x: number
  y: number
  w: number
  h: number
  label: string
  sub?: string
  accent?: boolean
  muted?: boolean
}

function Node({ x, y, w, h, label, sub, accent, muted }: NodeProps) {
  const stroke = muted
    ? "stroke-muted-foreground/50"
    : accent
      ? "stroke-primary"
      : "stroke-border"
  const fill = accent ? "fill-primary/10" : "fill-card"
  const labelFill = muted
    ? "fill-muted-foreground"
    : accent
      ? "fill-primary"
      : "fill-foreground"
  const cx = x + w / 2
  const labelY = sub ? y + h / 2 - 3 : y + h / 2 + 4
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={9}
        strokeWidth={1.5}
        strokeDasharray={muted ? "5 4" : undefined}
        className={`${fill} ${stroke}`}
      />
      <text
        x={cx}
        y={labelY}
        textAnchor="middle"
        className={`${labelFill} text-[12px] font-semibold`}
      >
        {label}
      </text>
      {sub && (
        <text
          x={cx}
          y={y + h / 2 + 14}
          textAnchor="middle"
          className="fill-muted-foreground text-[10px]"
        >
          {sub}
        </text>
      )}
    </g>
  )
}

function ArrowV({ x, y1, y2 }: { x: number; y1: number; y2: number }) {
  return (
    <g className="stroke-muted-foreground/70">
      <line x1={x} y1={y1} x2={x} y2={y2 - 6} strokeWidth={1.5} />
      <polygon points={`${x - 4},${y2 - 7} ${x + 4},${y2 - 7} ${x},${y2}`} className="fill-muted-foreground/70 stroke-none" />
    </g>
  )
}

function ArrowH({ y, x1, x2 }: { y: number; x1: number; x2: number }) {
  return (
    <g className="stroke-muted-foreground/70">
      <line x1={x1} y1={y} x2={x2 - 6} y2={y} strokeWidth={1.5} />
      <polygon points={`${x2 - 7},${y - 4} ${x2 - 7},${y + 4} ${x2},${y}`} className="fill-muted-foreground/70 stroke-none" />
    </g>
  )
}

function Figure({ viewBox, children, label }: { viewBox: string; children: ReactNode; label: string }) {
  return (
    <svg
      viewBox={viewBox}
      role="img"
      aria-label={label}
      className="h-auto w-full"
    >
      {children}
    </svg>
  )
}

export function DiagramBoot() {
  return (
    <Figure viewBox="0 0 560 272" label="Diagram alur boot: ISO menuju menu boot, lalu bercabang ke LiveOS atau Installer to disk">
      <Node x={200} y={14} w={160} h={44} label="ISO Fishing OS" />
      <ArrowV x={280} y1={58} y2={84} />
      <Node x={180} y={84} w={200} h={44} label="Menu boot" sub="BIOS / UEFI" />
      <line x1={280} y1={128} x2={280} y2={150} className="stroke-muted-foreground/70" strokeWidth={1.5} />
      <line x1={150} y1={150} x2={410} y2={150} className="stroke-muted-foreground/70" strokeWidth={1.5} />
      <ArrowV x={150} y1={150} y2={170} />
      <ArrowV x={410} y1={150} y2={170} />
      <Node x={40} y={170} w={220} h={50} label="LiveOS" sub="sesi sementara" accent />
      <Node x={300} y={170} w={220} h={50} label="Installer to disk" sub="archinstall" />
      <text x={150} y={242} textAnchor="middle" className="fill-muted-foreground text-[10px]">
        Desktop XFCE · toolchain
      </text>
      <text x={150} y={256} textAnchor="middle" className="fill-muted-foreground text-[10px]">
        perubahan hilang saat reboot
      </text>
      <text x={410} y={242} textAnchor="middle" className="fill-muted-foreground text-[10px]">
        Arch Linux di disk
      </text>
      <text x={410} y={256} textAnchor="middle" className="fill-muted-foreground text-[10px]">
        konfigurasi pilih sendiri
      </text>
    </Figure>
  )
}

export function DiagramVerify() {
  const nodes = [
    { x: 10, label: "Unduh" },
    { x: 122, label: "Impor kunci" },
    { x: 234, label: "Verifikasi sig" },
    { x: 346, label: "Cek SHA-256" },
    { x: 458, label: "Boot" },
  ]
  return (
    <Figure viewBox="0 0 560 108" label="Diagram pipeline verifikasi: unduh, impor kunci, verifikasi tanda tangan, cocokkan SHA-256, lalu boot">
      {nodes.map((node, index) => (
        <Node
          key={node.label}
          x={node.x}
          y={26}
          w={92}
          h={56}
          label={node.label}
          accent={index === nodes.length - 1}
        />
      ))}
      {nodes.slice(0, -1).map((node, index) => (
        <ArrowH key={node.label} y={54} x1={node.x + 92} x2={nodes[index + 1].x} />
      ))}
    </Figure>
  )
}

export function DiagramAssistant() {
  return (
    <Figure viewBox="0 0 560 248" label="Diagram lapisan Computer-Use Assistant: antarmuka, orchestrator, tool registry dan Privilege Broker, backend inferensi yang belum dipaketkan">
      <Node x={40} y={14} w={480} h={44} label="Antarmuka" sub="GUI · TUI · CLI" />
      <ArrowV x={280} y1={58} y2={76} />
      <Node x={40} y={76} w={480} h={44} label="Orchestrator" sub="planner · policy gate · audit" accent />
      <ArrowV x={280} y1={120} y2={138} />
      <Node x={40} y={138} w={480} h={44} label="Tool registry" sub="Privilege Broker · tool lokal" />
      <ArrowV x={280} y1={182} y2={200} />
      <Node x={40} y={200} w={480} h={40} label="Backend inferensi LLM / VLM" sub="belum dipaketkan" muted />
    </Figure>
  )
}

export const diagrams = {
  boot: DiagramBoot,
  verify: DiagramVerify,
  assistant: DiagramAssistant,
} as const

export type DiagramName = keyof typeof diagrams