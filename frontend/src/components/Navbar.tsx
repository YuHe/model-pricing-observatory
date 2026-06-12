import Link from 'next/link'

const links = [
  { href: '/', label: 'Home' },
  { href: '/models', label: 'Models' },
  { href: '/compare', label: 'Compare' },
  { href: '/providers', label: 'Providers' },
  { href: '/channels', label: 'Channels' },
  { href: '/plans', label: 'Plans' },
]

export function Navbar() {
  return (
    <nav className="border-b border-gray-800 bg-[#0a0a0a] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
        <Link href="/" className="font-bold text-lg">MPO</Link>
        {links.map(l => (
          <Link key={l.href} href={l.href} className="text-sm text-gray-400 hover:text-white transition">{l.label}</Link>
        ))}
        <Link href="/admin" className="ml-auto text-sm text-gray-500 hover:text-white">Admin</Link>
      </div>
    </nav>
  )
}
