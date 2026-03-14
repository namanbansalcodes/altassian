import { useEffect } from 'react'

interface SEOHeadProps {
  title: string
  description?: string
  keywords?: string
  ogImage?: string
  ogType?: string
  canonicalUrl?: string
  noindex?: boolean
  schema?: Record<string, unknown>
}

function setMeta(property: string, content: string, isProperty = false): void {
  const attr = isProperty ? 'property' : 'name'
  let el = document.querySelector(`meta[${attr}="${property}"]`) as HTMLMetaElement | null
  if (content) {
    if (!el) {
      el = document.createElement('meta')
      el.setAttribute(attr, property)
      document.head.appendChild(el)
    }
    el.setAttribute('content', content)
  } else if (el) {
    el.remove()
  }
}

function setLink(rel: string, href: string): void {
  let el = document.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null
  if (href) {
    if (!el) {
      el = document.createElement('link')
      el.setAttribute('rel', rel)
      document.head.appendChild(el)
    }
    el.setAttribute('href', href)
  } else if (el) {
    el.remove()
  }
}

export default function SEOHead({
  title,
  description = '',
  keywords = '',
  ogImage = '',
  ogType = 'website',
  canonicalUrl = '',
  noindex = false,
  schema,
}: SEOHeadProps) {
  useEffect(() => {
    const prevTitle = document.title
    document.title = title ? `${title} — Altassian` : 'Altassian — Git-Powered Team Knowledge Base'

    setMeta('description', description)
    setMeta('keywords', keywords)
    setMeta('robots', noindex ? 'noindex, nofollow' : 'index, follow')

    setMeta('og:title', title, true)
    setMeta('og:description', description, true)
    setMeta('og:type', ogType, true)
    setMeta('og:image', ogImage, true)
    setMeta('og:site_name', 'Altassian', true)
    if (canonicalUrl) {
      setMeta('og:url', canonicalUrl, true)
    }

    setMeta('twitter:card', ogImage ? 'summary_large_image' : 'summary')
    setMeta('twitter:title', title)
    setMeta('twitter:description', description)
    if (ogImage) setMeta('twitter:image', ogImage)

    setLink('canonical', canonicalUrl || window.location.href)

    return () => {
      document.title = prevTitle
    }
  }, [title, description, keywords, ogImage, ogType, canonicalUrl, noindex])

  useEffect(() => {
    if (!schema) return

    const scriptId = 'seo-schema-markup'
    let el = document.getElementById(scriptId) as HTMLScriptElement | null
    if (!el) {
      el = document.createElement('script')
      el.id = scriptId
      el.type = 'application/ld+json'
      document.head.appendChild(el)
    }
    el.textContent = JSON.stringify(schema)

    return () => {
      el?.remove()
    }
  }, [schema])

  return null
}
