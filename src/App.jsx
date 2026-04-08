import { useState, useEffect } from 'react'
import './App.css'
import Summary from './Summary'
import TransactionForm from './TransactionForm'
import TransactionList from './TransactionList'
import AuthForm from './AuthForm'

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  const authHeaders = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }

  const fetchTransactions = () => {
    fetch('/api/transactions', { headers: authHeaders })
      .then(res => {
        if (res.status === 401) { handleLogout(); return null }
        return res.json()
      })
      .then(data => {
        if (data) setTransactions(data)
        setLoading(false)
      })
  }

  useEffect(() => {
    if (token) fetchTransactions()
  }, [token])

  const handleAuth = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
    setLoading(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setTransactions([])
  }

  const handleAdd = (transaction) => {
    fetch('/api/transactions', {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify(transaction),
    }).then(() => fetchTransactions())
  }

  const handleDelete = (id) => {
    fetch(`/api/transactions/${id}`, {
      method: 'DELETE',
      headers: authHeaders,
    }).then(() => fetchTransactions())
  }

  if (!token) {
    return <AuthForm onAuth={handleAuth} />
  }

  if (loading) {
    return (
      <div className="app">
        <h1>Finance Tracker</h1>
        <p className="subtitle">Loading…</p>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="app-header">
        <div>
          <h1>Finance Tracker</h1>
          <p className="subtitle">Track your income and expenses</p>
        </div>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </div>

      <Summary transactions={transactions} />
      <TransactionForm onAdd={handleAdd} />
      <TransactionList transactions={transactions} onDelete={handleDelete} />
    </div>
  )
}

export default App
