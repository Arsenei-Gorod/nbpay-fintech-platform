import { useState } from 'react'
import { useNavigate, useSearchParams, Link as RouterLink } from 'react-router-dom'
import { Box, Button, Card, CardContent, CardHeader, Alert, TextField, Stack, Link } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [username, setUsername] = useState(params.get('email') || '')
  const [password, setPassword] = useState('')

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await auth.login(username, password)
      const redirect = params.get('redirect') || '/profile'
      navigate(redirect, { replace: true })
    } catch {}
  }

  return (
    <Box display="flex" justifyContent="center">
      <Card sx={{ width: 420, maxWidth: '100%' }}>
        <CardHeader title="Вход" />
        <CardContent>
          {auth.error && <Alert severity="error" sx={{ mb: 2 }}>{auth.error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField label="Email" type="email" value={username} onChange={(e) => setUsername(e.target.value)} required fullWidth />
              <TextField label="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Button type="submit" variant="contained" disabled={auth.loading}>Войти</Button>
                <Link component={RouterLink} to="/register">Нет аккаунта? Регистрация</Link>
              </Box>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

