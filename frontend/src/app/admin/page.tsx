'use client'
import { useState } from 'react'

export default function AdminPage() {
  const [key, setKey] = useState('')
  const [authed, setAuthed] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])

  const login = () => {
    fetch('/api/v1/admin/jobs', { headers: { 'X-Admin-Key': key } })
      .then(r => { if (r.ok) { setAuthed(true); return r.json() } throw new Error() })
      .then(setJobs)
      .catch(() => alert('Invalid key'))
  }

  const retry = (source: string) => {
    fetch(`/api/v1/admin/jobs/${source}/retry`, { method: 'POST', headers: { 'X-Admin-Key': key } })
      .then(() => login())
  }

  if (!authed) return (
    <div className="max-w-sm mx-auto mt-20 space-y-4">
      <h1 className="text-xl font-bold">Admin</h1>
      <input type="password" className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2" placeholder="Admin Key" value={key} onChange={e => setKey(e.target.value)} />
      <button onClick={login} className="w-full bg-blue-600 rounded py-2 font-medium">Login</button>
    </div>
  )

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Admin - Crawl Jobs</h1>
      <table className="w-full text-sm">
        <thead><tr className="border-b border-gray-800"><th className="text-left py-2">Source</th><th>Status</th><th>Models</th><th>Time</th><th></th></tr></thead>
        <tbody>
          {jobs.map((j: any) => (
            <tr key={j.id} className="border-b border-gray-800/50">
              <td className="py-2">{j.source}</td>
              <td><span className={j.status === 'success' ? 'text-green-400' : j.status === 'failed' ? 'text-red-400' : 'text-yellow-400'}>{j.status}</span></td>
              <td>{j.models_synced}</td>
              <td className="text-gray-500">{j.finished_at?.slice(0, 16)}</td>
              <td>{j.status === 'failed' && <button onClick={() => retry(j.source)} className="text-blue-400 text-xs">Retry</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
