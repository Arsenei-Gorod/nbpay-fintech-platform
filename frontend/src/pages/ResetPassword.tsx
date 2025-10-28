import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Alert, Box, Button, Card, CardContent, CardHeader, Stack, TextField, Typography } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export default function ResetPassword() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [token, setToken] = useState(params.get('token') || '')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [success, setSuccess] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) {
      return
    }
    setSuccess(false)
    try {
      await auth.confirmPasswordReset(token, password)
      setSuccess(true)
      setTimeout(() => navigate('/login'), 1500)
    } catch {}
  }

  const passwordMismatch = password !== confirm && confirm.length > 0

  return (
    <Box display="flex" justifyContent="center">
      <Card sx={{ width: 480, maxWidth: '100%' }}>
        <CardHeader title="Смена пароля" />
        <CardContent>
          {auth.error && <Alert severity="error" sx={{ mb: 2 }}>{auth.error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>Пароль успешно обновлён. Сейчас перенаправим на страницу входа…</Alert>}
          <Typography variant="body2" sx={{ mb: 2 }}>
            Введите токен сброса и придумайте новый пароль. Токен вы получили на предыдущем шаге.
          </Typography>
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField label="Токен" value={token} onChange={(e) => setToken(e.target.value)} required fullWidth />
              <TextField label="Новый пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
              <TextField label="Повторите пароль" type="password" value={confirm} error={passwordMismatch} helperText={passwordMismatch ? 'Пароли не совпадают' : ''} onChange={(e) => setConfirm(e.target.value)} required fullWidth />
              <Stack direction="row" spacing={1} justifyContent="space-between">
                <Button type="submit" variant="contained" disabled={auth.loading || passwordMismatch}>Сменить пароль</Button>
                <Button variant="text" onClick={() => navigate('/login')}>Назад</Button>
              </Stack>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
