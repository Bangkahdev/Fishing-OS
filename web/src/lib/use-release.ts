import { useEffect, useState } from "react"
import { site } from "@/lib/site"

type ReleaseInfo = {
  version: string
  publishedAt: string | null
  assets: { name: string; size: number; url: string }[]
  htmlUrl: string
}

type ApiRelease = {
  tag_name?: string
  published_at?: string
  html_url?: string
  assets?: { name: string; size: number; browser_download_url: string }[]
}

function parse(data: ApiRelease): ReleaseInfo {
  const version = (data.tag_name ?? "").replace(/^v/, "")
  if (!version) throw new Error("rilis tanpa tag")

  return {
    version,
    publishedAt: data.published_at ?? null,
    htmlUrl: data.html_url ?? `${site.releases}/tag/v${version}`,
    assets: (data.assets ?? []).map((a) => ({
      name: a.name,
      size: a.size,
      url: a.browser_download_url,
    })),
  }
}

export function useLatestRelease() {
  const [release, setRelease] = useState<ReleaseInfo | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${site.repoApi}/releases/latest`, {
      signal: controller.signal,
      headers: { Accept: "application/vnd.github+json" },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: ApiRelease) => setRelease(parse(data)))
      .catch(() => {})

    return () => controller.abort()
  }, [])

  return release
}

export function formatSize(bytes: number) {
  if (!bytes) return "—"
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KiB`
  const mib = bytes / (1024 * 1024)
  return mib >= 1024 ? `${(mib / 1024).toFixed(2)} GiB` : `${mib.toFixed(1)} MiB`
}
