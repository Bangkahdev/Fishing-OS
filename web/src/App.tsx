import { lazy, Suspense } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { SiteLayout } from "@/components/site/layout"
import { Hero } from "@/components/site/hero"
import { DocsApp } from "@/components/docs/docs-app"

const BelowFold = lazy(() => import("@/components/site/below-fold"))
const Blog = lazy(() => import("@/components/site/blog"))
const BlogPost = lazy(() => import("@/components/site/blog-post"))
const About = lazy(() => import("@/components/site/about"))
const NotFound = lazy(() => import("@/components/site/not-found"))

function Home() {
  return (
    <>
      <Hero />
      <Suspense fallback={null}>
        <BelowFold />
      </Suspense>
    </>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<SiteLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/blog" element={<Navigate to="/blog/" replace />} />
        <Route path="/blog/" element={<Blog />} />
        <Route path="/blog/:slug" element={<BlogPost />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
      <Route path="/docs" element={<Navigate to="/docs/" replace />} />
      <Route path="/docs/" element={<DocsApp />} />
      <Route path="/docs/:slug" element={<DocsApp />} />
    </Routes>
  )
}
