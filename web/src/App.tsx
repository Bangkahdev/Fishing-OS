import { Header } from "@/components/site/header"
import { Hero } from "@/components/site/hero"
import { Features } from "@/components/site/features"
import { Gallery } from "@/components/site/gallery"
import { Toolchain } from "@/components/site/toolchain"
import { Download } from "@/components/site/download"
import { Quickstart } from "@/components/site/quickstart"
import { Limits } from "@/components/site/limits"
import { Footer } from "@/components/site/footer"

export default function App() {
  return (
    <div className="flex min-h-dvh flex-col">
      <Header />
      <main className="flex-1">
        <Hero />
        <Features />
        <Gallery />
        <Toolchain />
        <Download />
        <Quickstart />
        <Limits />
      </main>
      <Footer />
    </div>
  )
}
