import { lazy, Suspense } from "react"
import { Header } from "@/components/site/header"
import { Hero } from "@/components/site/hero"
import { Footer } from "@/components/site/footer"

const BelowFold = lazy(() => import("@/components/site/below-fold"))

export default function App() {
  return (
    <div className="flex min-h-dvh flex-col">
      <Header />
      <main id="konten" className="flex-1">
        <Hero />
        <Suspense fallback={null}>
          <BelowFold />
        </Suspense>
      </main>
      <Footer />
    </div>
  )
}
