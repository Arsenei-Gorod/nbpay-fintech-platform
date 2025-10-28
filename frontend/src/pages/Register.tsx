import { useState } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import { Box, Button, Card, CardContent, CardHeader, Alert, TextField, Stack, Link } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export default function Register() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await auth.register(email, fullName, password)
      navigate(`/login?email=${encodeURIComponent(email)}`)
    } catch {}
  }

  return (
    <Box display="flex" justifyContent="center">
      <Card sx={{ width: 480, maxWidth: '100%' }}>
        <CardHeader title="Регистрация" />
        <CardContent>
          {auth.error && <Alert severity="error" sx={{ mb: 2 }}>{auth.error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
              <TextField label="Полное имя" value={fullName} onChange={(e) => setFullName(e.target.value)} required fullWidth />
              <TextField label="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Button type="submit" variant="contained" disabled={auth.loading}>Создать аккаунт</Button>
                <Link component={RouterLink} to="/login">Уже есть аккаунт? Войти</Link>
              </Box>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

