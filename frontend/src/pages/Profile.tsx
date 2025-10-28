import { useEffect } from 'react'
import { Card, CardContent, CardHeader, List, ListItem, ListItemText } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export default function Profile() {
  const auth = useAuth()
  useEffect(() => { if (!auth.user) auth.fetchMe() }, [])
  const u = auth.user
  return (
    <Card>
      <CardHeader title="Профиль" />
      <CardContent>
        {u ? (
          <List>
            <ListItem><ListItemText primary="ID" secondary={u.id} /></ListItem>
            <ListItem><ListItemText primary="Email" secondary={u.email} /></ListItem>
            <ListItem><ListItemText primary="Полное имя" secondary={u.full_name} /></ListItem>
            <ListItem><ListItemText primary="Роль" secondary={u.role} /></ListItem>
            <ListItem><ListItemText primary="Активен" secondary={u.is_active ? 'Да' : 'Нет'} /></ListItem>
            <ListItem><ListItemText primary="Создан" secondary={new Date(u.created_at).toLocaleString()} /></ListItem>
            <ListItem><ListItemText primary="Обновлён" secondary={new Date(u.updated_at).toLocaleString()} /></ListItem>
          </List>
        ) : (
          <div>Загрузка…</div>
        )}
      </CardContent>
    </Card>
  )
}

