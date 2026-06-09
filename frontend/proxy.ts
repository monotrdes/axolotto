import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const hostname = request.headers.get('host') ?? ''
  if (hostname.startsWith('play.') || hostname.startsWith('app.') || hostname.startsWith('juego.') || hostname.startsWith('juega.')) {
    const pathname = request.nextUrl.pathname
    if (/\.\w+$/.test(pathname)) return NextResponse.next()
    const rewritePath = pathname === '/' ? '/play' : `/play${pathname}`
    return NextResponse.rewrite(new URL(rewritePath, request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
