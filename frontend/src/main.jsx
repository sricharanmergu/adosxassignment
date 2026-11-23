import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'

const reasons = ['MISSING_IN_B', 'ORPHAN_IN_B', 'DUPLICATE_IN_B', 'VALUE_MISMATCH', 'LOCATION_MISMATCH', 'DATE_MISMATCH']

function App() {
  const [org, setOrg] = useState('ORG-A')
  const [reason, setReason] = useState('')
  const [sort, setSort] = useState('value')
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const params = new URLSearchParams({ org, sort })
    if (reason) params.set('reason', reason)

    setLoading(true)
    setError('')
    fetch(`/api/disagreements/?${params}`)
      .then(response => response.ok ? response.json() : response.json().then(body => Promise.reject(body.error)))
      .then(data => { if (active) setRows(data) })
      .catch(problem => { if (active) setError(String(problem)) })
      .finally(() => { if (active) setLoading(false) })

    return () => { active = false }
  }, [org, reason, sort])

  const issueTypes = new Set(rows.map(row => row.reason)).size
  const toggleSort = () => setSort(current => current === 'value' ? '-value' : 'value')

  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">A</div>
          <div><span className="eyebrow">ADOSX · FINANCE OPERATIONS</span><p className="brand-caption">Ledger review workspace</p></div>
        </div>
        <label className="org-picker"><span>Organization</span><select value={org} onChange={event => setOrg(event.target.value)}><option>ORG-A</option><option>ORG-B</option></select></label>
      </header>

      <section className="hero">
        <div>
          <span className="eyebrow">RECONCILIATION CENTER</span>
          <h1>Exceptions overview</h1>
          <p>Review ledger entries that need a closer look across your source systems.</p>
        </div>
        <div className="hero-chip"><span className="status-dot" /> Source comparison</div>
      </section>

      <section className="summary-grid" aria-label="Review summary">
        <article className="summary-card summary-primary"><span className="summary-label">Items in this view</span><strong>{loading ? '—' : rows.length}</strong><span className="summary-foot">Filtered exceptions for {org}</span></article>
        <article className="summary-card"><span className="summary-label">Exception types</span><strong>{loading ? '—' : issueTypes}</strong><span className="summary-foot">Present in the current results</span></article>
        <article className="summary-card"><span className="summary-label">Comparison</span><strong className="summary-word">System A <span>↔</span> System B</strong><span className="summary-foot">Matched records are excluded</span></article>
      </section>

      <section className="work-panel">
        <div className="panel-toolbar">
          <div><span className="eyebrow">REVIEW QUEUE</span><h2>Exception register</h2></div>
          <label className="filter-picker"><span>Filter by reason</span><select value={reason} onChange={event => setReason(event.target.value)}><option value="">All disagreement types</option>{reasons.map(item => <option key={item}>{item}</option>)}</select></label>
        </div>

        {error ? <div className="state-message state-error" role="alert"><strong>Could not load the review list</strong><span>{error}</span></div>
          : loading ? <div className="state-message" role="status">Loading reconciliation results…</div>
            : rows.length === 0 ? <div className="state-message"><strong>Nothing needs review here</strong><span>No disagreements match the selected organization and filter.</span></div>
              : <div className="table-wrap"><table><thead><tr><th>Reason</th><th>Record ID</th><th>Location</th><th><button className="sort-button" onClick={toggleSort}>System A value <span>{sort === 'value' ? '↑' : '↓'}</span></button></th><th>System B value</th><th>Difference</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.reason}-${row.record_id}-${index}`}><td><span className="badge">{row.reason.replaceAll('_', ' ')}</span></td><td className="record-id">{row.record_id}</td><td>{row.a_location || row.location || ''}{row.b_location && row.b_location !== row.a_location ? <span className="location-pair"> / {row.b_location}</span> : ''}</td><td className="amount">{row.a_value ?? '—'}</td><td className="amount">{row.b_value ?? '—'}</td><td className="difference">{row.difference ?? '—'}</td></tr>)}</tbody></table></div>}
        <div className="panel-footer"><span>Showing exception results for <strong>{org}</strong></span><span>{loading ? 'Updating…' : `${rows.length} ${rows.length === 1 ? 'record' : 'records'}`}</span></div>
      </section>
      <footer className="page-footer">AdosX Assignment <span>·</span> Ledger reconciliation</footer>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
