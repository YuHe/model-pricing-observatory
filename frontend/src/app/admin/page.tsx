'use client'
import { useState } from 'react'

export default function AdminPage() {
  const [key, setKey] = useState('')
  const [authed, setAuthed] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])
  const [deleteDate, setDeleteDate] = useState('')
  const [msg, setMsg] = useState('')

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

  const triggerCrawl = () => {
    fetch('/api/v1/admin/trigger-crawl', { method: 'POST', headers: { 'X-Admin-Key': key } })
      .then(r => r.json())
      .then(() => { setMsg('Crawl task queued'); setTimeout(() => setMsg(''), 3000) })
  }

  const deleteByDate = () => {
    if (!deleteDate || !confirm(`Delete all snapshots for ${deleteDate}?`)) return
    fetch(`/api/v1/admin/snapshots?target_date=${deleteDate}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } })
      .then(r => r.json())
      .then(d => { setMsg(`Deleted ${d.deleted_price_snapshots} price + ${d.deleted_subscription_snapshots} subscription snapshots`); setTimeout(() => setMsg(''), 5000) })
  }

  if (!authed) return (
    <div className="max-w-sm mx-auto mt-20 space-y-4">
      <h1 className="text-xl font-bold">Admin</h1>
      <input type="password" className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2" placeholder="Admin Key" value={key} onChange={e => setKey(e.target.value)} />
      <button onClick={login} className="w-full bg-blue-600 rounded py-2 font-medium">Login</button>
    </div>
  )

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin</h1>
      {msg && <div className="bg-green-900/30 border border-green-800 rounded px-3 py-2 text-sm text-green-300">{msg}</div>}
      <div className="flex gap-4 items-end flex-wrap">
        <button onClick={triggerCrawl} className="px-4 py-2 bg-blue-600 rounded font-medium text-sm hover:bg-blue-700">Trigger Crawl Now</button>
        <div className="flex gap-2 items-end">
          <input type="date" value={deleteDate} onChange={e => setDeleteDate(e.target.value)} className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm" />
          <button onClick={deleteByDate} className="px-4 py-2 bg-red-600 rounded font-medium text-sm hover:bg-red-700">Delete Day</button>
        </div>
      </div>
      <h2 className="text-lg font-semibold">Crawl Jobs</h2>
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
