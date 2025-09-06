from __future__ import annotations

import argparse
import sys
from getpass import getpass

from app.core.config import get_settings
from app.domain.user.models import Role
from app.domain.user.schemas import UserRegisterDTO
from app.domain.user.services import UserService
from app.infrastructure.db.session import get_session, create_all
from app.infrastructure.repositories.user_sqlalchemy import SQLUserRepository


def cmd_create_superuser(args: argparse.Namespace) -> int:
    settings = get_settings()
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL is not configured. Configure a database to create persistent users.", file=sys.stderr)
        return 2

    email: str = args.email
    full_name: str = args.full_name
    password: str | None = args.password
    if not password:
        # prompt interactively
        pw1 = getpass("Password: ")
        pw2 = getpass("Confirm password: ")
        if pw1 != pw2:
            print("ERROR: Passwords do not match", file=sys.stderr)
            return 3
        password = pw1

    assert password is not None

    # Ensure tables exist
    create_all()

    with get_session() as session:
        repo = SQLUserRepository(session)
        svc = UserService(user_repo=repo)
        existing = repo.get_by_email(email)
        if existing:
            if args.upgrade_if_exists:
                dto = svc.set_role(str(existing.id), Role.ADMIN)
                print(f"User already exists. Promoted to admin: {dto.id} <{dto.email}>")
                return 0
            else:
                print("ERROR: User with this email already exists. Use --upgrade-if-exists to promote.", file=sys.stderr)
                return 1
        dto = UserRegisterDTO(email=email, full_name=full_name, password=password)
        created = svc.register(dto)
        created_admin = svc.set_role(str(created.id), Role.ADMIN)
        print(f"Superuser created: {created_admin.id} <{created_admin.email}>")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="manage", description="Management commands")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cs = sub.add_parser("create-superuser", help="Create a superuser (admin)")
    p_cs.add_argument("--email", required=True, help="Email of the superuser")
    p_cs.add_argument("--full-name", required=True, help="Full name of the superuser")
    p_cs.add_argument("--password", help="Password (omit to be prompted)")
    p_cs.add_argument(
        "--upgrade-if-exists",
        action="store_true",
        help="If a user with this email exists, set role=admin",
    )
    p_cs.set_defaults(func=cmd_create_superuser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if not func:
        parser.print_help()
        return 1
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())

