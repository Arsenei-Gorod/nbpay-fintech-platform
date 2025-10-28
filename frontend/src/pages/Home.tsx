import { Card, CardContent, CardHeader, Typography } from '@mui/material'

export default function Home() {
  return (
    <Card>
      <CardHeader title="Добро пожаловать" />
      <CardContent>
        <Typography gutterBottom>
          Это фронтенд‑сервис (React + MUI), который обращается к вашему FastAPI бэкенду.
        </Typography>
        <Typography>Используйте шапку, чтобы войти, зарегистрироваться или открыть профиль.</Typography>
      </CardContent>
    </Card>
  )
}

