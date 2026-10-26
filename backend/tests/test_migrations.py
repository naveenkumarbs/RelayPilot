import os
from pathlib import Path
import subprocess
import sys

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL


BACKEND_DIR = Path(__file__).resolve().parents[1]


def run_alembic(arguments, environment):
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"Alembic failed: {arguments}\n"
        f"{result.stdout}\n"
        f"{result.stderr}"
    )

    return result


def test_migrations_build_fresh_database(test_settings, tmp_path):
    database_path = tmp_path / "migration-test.db"

    environment = os.environ.copy()
    environment["RELAYPILOT_ENVIRONMENT"] = "test"
    environment["RELAYPILOT_DATABASE_PATH"] = str(database_path)

    # This subprocess inherits the synthetic JWT settings
    # supplied by the test_settings fixture.
    run_alembic(["upgrade", "head"], environment)

    assert database_path.is_file()

    migration_engine = create_engine(
        URL.create(
            "sqlite+pysqlite",
            database=str(database_path),
        )
    )

    try:
        inspector = inspect(migration_engine)

        assert set(inspector.get_table_names()) == {
            "alembic_version",
            "tenants",
            "users",
            "tenant_memberships",
        }

        foreign_keys = inspector.get_foreign_keys(
            "tenant_memberships"
        )

        assert {
            foreign_key["referred_table"]
            for foreign_key in foreign_keys
        } == {"tenants", "users"}

        unique_constraints = inspector.get_unique_constraints(
            "tenant_memberships"
        )

        assert any(
            set(constraint["column_names"]) == {"tenant_id", "user_id"}
            for constraint in unique_constraints
        )

        role_constraints = inspector.get_check_constraints(
            "tenant_memberships"
        )

        assert any(
            constraint["name"]
            == "ck_tenant_memberships_valid_role"
            for constraint in role_constraints
        )

    finally:
        migration_engine.dispose()

    # Reapplying the latest revision should succeed.
    run_alembic(["upgrade", "head"], environment)

    # Detect supported differences between migrated schema and models.
    run_alembic(["check"], environment)