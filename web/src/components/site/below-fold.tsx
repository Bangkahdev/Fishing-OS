import { Features } from "@/components/site/features"
import { Gallery } from "@/components/site/gallery"
import { Toolchain } from "@/components/site/toolchain"
import { Download } from "@/components/site/download"
import { Quickstart } from "@/components/site/quickstart"
import { Limits } from "@/components/site/limits"

export default function BelowFold() {
  return (
    <>
      <Features />
      <Gallery />
      <Toolchain />
      <Download />
      <Quickstart />
      <Limits />
    </>
  )
}
