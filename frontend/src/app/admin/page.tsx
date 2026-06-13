'use client'
import { useState, useEffect, useRef } from 'react'

export default function AdminPage() {
  const [key, setKey] = useState('')
  const [authed, setAuthed] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])
  const [progress, setProgress] = useState<any[]>([])
  const [crawling, setCrawling] = useState(false)
  const [deleteDate, setDeleteDate] = useState('')
  const [msg, setMsg] = useState('')
  const [errorModal, setErrorModal] = useState<any>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const headers = { 'X-Admin-Key': key }

  const login = () => {
    fetch('/api/v1/admin/jobs', { headers })
      .then(r => { if (r.ok) { setAuthed(true); return r.json() } throw new Error() })
      .then(setJobs)
      .catch(() => alert('Invalid key'))
  }

  const retry = (source: string) => {
    fetch(`/api/v1/admin/jobs/${source}/retry`, { method: 'POST', headers }).then(() => login())
  }

  const fetchProgress = () => {
    fetch('/api/v1/admin/crawl-progress', { headers })
      .then(r => r.json())
      .then(d => {
        setProgress(d.items || [])
        const hasRunning = (d.items || []).some((j: any) => j.status === 'running')
        if (!hasRunning && (d.items || []).length > 0) {
          setCrawling(false)
          if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null }
          login()
        }
      })
  }

  const triggerCrawl = () => {
    fetch('/api/v1/admin/trigger-crawl', { method: 'POST', headers })
      .then(r => r.json())
      .then(() => {
        setCrawling(true)
        setMsg('Crawl task queued')
        setTimeout(() => setMsg(''), 3000)
        pollRef.current = setInterval(fetchProgress, 3000)
      })
  }

  useEffect(() => { return () => { if (pollRef.current) clearInterval(pollRef.current) } }, [])

  const deleteByDate = () => {
    if (!deleteDate || !confirm(`Delete all snapshots for ${deleteDate}?`)) return
    fetch(`/api/v1/admin/snapshots?target_date=${deleteDate}`, { method: 'DELETE', headers })
      .then(r => r.json())
      .then(d => { setMsg(`Deleted ${d.deleted_price_snapshots} price + ${d.deleted_subscription_snapshots} subscription snapshots`); setTimeout(() => setMsg(''), 5000) })
  }

  const doneCount = progress.filter(j => j.status === 'success' || j.status === 'failed').length
  const totalCount = progress.length

  if (!authed) return (
    <div className="max-w-sm mx-auto mt-20 space-y-4">
      <h1 className="text-xl font-bold">Admin</h1>
      <input type="password" className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2" placeholder="Admin Key" value={key} onChange={e => setKey(e.target.value)} onKeyDown={e => e.key === 'Enter' && login()} />
      <button onClick={login} className="w-full bg-blue-600 rounded py-2 font-medium">Login</button>
    </div>
  )

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin</h1>
      {msg && <div className="bg-green-900/30 border border-green-800 rounded px-3 py-2 text-sm text-green-300">{msg}</div>}
      <div className="flex gap-4 items-end flex-wrap">
        <button onClick={triggerCrawl} disabled={crawling} className="px-4 py-2 bg-blue-600 rounded font-medium text-sm hover:bg-blue-700 disabled:opacity-50">{crawling ? 'Crawling...' : 'Trigger Crawl Now'}</button>
        <div className="flex gap-2 items-end">
          <input type="date" value={deleteDate} onChange={e => setDeleteDate(e.target.value)} className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm" />
          <button onClick={deleteByDate} className="px-4 py-2 bg-red-600 rounded font-medium text-sm hover:bg-red-700">Delete Day</button>
        </div>
      </div>
      {crawling && totalCount > 0 && (
        <div className="space-y-3">
          <div className="flex justify-between text-sm text-gray-400"><span>Progress</span><span>{doneCount} / {totalCount}</span></div>
          <div className="h-2 bg-gray-800 rounded overflow-hidden"><div className="h-full bg-blue-500 transition-all" style={{ width: `${totalCount ? (doneCount / totalCount) * 100 : 0}%` }} /></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {progress.map(j => (
              <div key={j.id} className={`px-2 py-1 rounded text-xs border ${j.status === 'success' ? 'border-green-800 text-green-400' : j.status === 'failed' ? 'border-red-800 text-red-400 cursor-pointer' : 'border-yellow-800 text-yellow-400 animate-pulse'}`} onClick={() => j.status === 'failed' && setErrorModal(j)}>
                {j.source} — {j.status}
              </div>
            ))}
          </div>
        </div>
      )}
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
              <td className="flex gap-2">
                {j.status === 'failed' && <button onClick={() => retry(j.source)} className="text-blue-400 text-xs">Retry</button>}
                {j.error_message && <button onClick={() => setErrorModal(j)} className="text-red-400 text-xs">Error</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {errorModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setErrorModal(null)}>
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-red-400">Error: {errorModal.source}</h3>
              <button onClick={() => setErrorModal(null)} className="text-gray-400 hover:text-white text-xl">&times;</button>
            </div>
            <p className="text-sm text-gray-300 mb-2">{errorModal.error_message}</p>
            {errorModal.stack_trace && <pre className="text-xs text-gray-500 bg-gray-950 p-3 rounded overflow-auto whitespace-pre-wrap">{errorModal.stack_trace}</pre>}
          </div>
        </div>
      )}
    </div>
  )
}
