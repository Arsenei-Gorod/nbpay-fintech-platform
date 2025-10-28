import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Card, CardContent, CardHeader, Stack, TextField, Typography } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export default function ForgotPassword() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [token, setToken] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(false)
    setToken(null)
    try {
      const issued = await auth.requestPasswordReset(email)
      setToken(issued)
      setSuccess(true)
    } catch {}
  }

  return (
    <Box display="flex" justifyContent="center">
      <Card sx={{ width: 480, maxWidth: '100%' }}>
        <CardHeader title="Восстановление пароля" />
        <CardContent>
          {auth.error && <Alert severity="error" sx={{ mb: 2 }}>{auth.error}</Alert>}
          {success && (
            <Alert severity={token ? 'success' : 'info'} sx={{ mb: 2 }}>
              {token
                ? (
                  <>
                    <Typography variant="body2" component="div">
                      Ссылка на почту пока не отправляется. Используйте этот токен, чтобы задать новый пароль:
                    </Typography>
                    <Typography variant="subtitle2" sx={{ mt: 1, wordBreak: 'break-all' }}>{token}</Typography>
                  </>
                )
                : 'Если такой email зарегистрирован, инструкцию отправим на почту.'}
            </Alert>
          )}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
              <Stack direction="row" spacing={1} justifyContent="space-between">
                <Button type="submit" variant="contained" disabled={auth.loading}>Получить токен</Button>
                <Button variant="text" onClick={() => navigate('/login')}>Отмена</Button>
              </Stack>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
