import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Box, Container, Menu, MenuItem, IconButton } from '@mui/material'
import AccountCircle from '@mui/icons-material/AccountCircle'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import { AuthProvider, useAuth } from './auth/AuthContext'

function RequireAuth({ children }: { children: JSX.Element }) {
  const auth = useAuth()
  const location = useLocation()
  if (!auth.isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`} replace />
  }
  return children
}

function NavBar() {
  const auth = useAuth()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const open = Boolean(anchorEl)
  const handleMenu = (event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget)
  const handleClose = () => setAnchorEl(null)

  return (
    <AppBar position="static" color="primary" elevation={1}>
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            color: 'inherit',
            textDecoration: 'none',
            fontWeight: 600,
            letterSpacing: 0.3,
          }}
        >
          FastAPI
        </Typography>
        {!auth.isAuthenticated && (
          <Button color="inherit" component={RouterLink} to="/login" sx={{ fontWeight: 500 }}>
            Войти
          </Button>
        )}
        {auth.isAuthenticated && (
          <>
            <IconButton size="large" color="inherit" onClick={handleMenu}>
              <AccountCircle />
            </IconButton>
            <Menu anchorEl={anchorEl} open={open} onClose={handleClose} keepMounted>
              <MenuItem component={RouterLink} to="/profile" onClick={handleClose}>Профиль</MenuItem>
              <MenuItem onClick={() => { handleClose(); auth.logout() }}>Выход</MenuItem>
            </Menu>
          </>
        )}
      </Toolbar>
    </AppBar>
  )
}


function Shell() {
  const auth = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  useEffect(() => {
    auth.initFromStorage()
    if (auth.isAuthenticated && !auth.user) auth.fetchMe()
  }, [])
  useEffect(() => {
    // If user becomes unauthenticated, redirect to login (except when already on auth pages)
    const isAuthPage = location.pathname.startsWith('/login') || location.pathname.startsWith('/register')
    if (!auth.isAuthenticated && !isAuthPage) {
      const redirect = encodeURIComponent(location.pathname + location.search)
      navigate(`/login?redirect=${redirect}`, { replace: true })
    }
  }, [auth.isAuthenticated, location.pathname, location.search, navigate])
  return (
    <Box>
      <NavBar />
      <Container sx={{ py: 4 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}
