import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Dashboard } from '@/pages/Dashboard'
import { Newsstand } from '@/pages/Newsstand'
import { Bookmarks } from '@/pages/Bookmarks'
import { Settings } from '@/pages/Settings'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Toaster } from 'sonner'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/newsstand"
          element={
            <ProtectedRoute>
              <Newsstand />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bookmarks"
          element={
            <ProtectedRoute>
              <Bookmarks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
