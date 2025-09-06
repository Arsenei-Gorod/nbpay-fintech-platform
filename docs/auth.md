# Авторизация

Сервис реализует авторизацию по схеме OAuth2 Password + JWT (access/refresh) и хранит `jti` токенов для отзыва в InMemory или Redis.

## Потоки
- Регистрация → Вход → Получение `access`/`refresh` → Доступ к защищённым эндпоинтам → Ротация `refresh` при обновлении → Выход (отзыв токенов)

## Эндпоинты

### POST /api/v1/auth/register
Регистрация пользователя.

Body (JSON):
```
{
  "email": "user@example.com",
  "full_name": "User Name",
  "password": "secret123"
}
```

Response: `200 OK` с данными пользователя.

### POST /api/v1/auth/login
Получение пары токенов (access/refresh).

Form (application/x-www-form-urlencoded):
```
username=<email>&password=<password>&grant_type=password
```

Response (JSON):
```
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### GET /api/v1/auth/me
Текущий пользователь (требуется Bearer access-token).

### POST /api/v1/auth/refresh
Обновление пары токенов; старый refresh помечается как отозванный.

Query:
```
refresh_token=<refresh>
```

### POST /api/v1/auth/logout
Отзыв access по `jti` и (опционально) refresh.

Query:
```
token=<access>&refresh_token=<refresh>
```

## Примечания по безопасности
- `access` — короткоживущий; `refresh` — более долгий, храните его аккуратно.
- Все `jti` записываются в стор (InMemory/Redis) и проверяются на каждом запросе.
- При `refresh` токены ротируются: старый refresh отзывается, создаётся новый.

## Роли и доступ
- Используйте `require_roles(Role.ADMIN)` для защиты эндпоинтов.
- `require_current_user()` — для получения текущего пользователя по access-токену.

