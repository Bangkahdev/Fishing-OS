import { Outlet } from "react-router-dom"
import { Header } from "@/components/site/header"
import { Footer } from "@/components/site/footer"

export function SiteLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <Header />
      <main id="konten" className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
