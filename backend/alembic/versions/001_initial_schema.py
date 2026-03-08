"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("oauth_provider", sa.String(50), nullable=True),
        sa.Column("oauth_id", sa.String(255), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_oauth_id", "users", ["oauth_id"], unique=True)

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)

    # --- tasks ---
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("source_id", sa.String(500), nullable=True),
        sa.Column("impact", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("urgency", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("energy_required", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("priority_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("is_big_rock", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sub_steps", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("snooze_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"])
    op.create_index("ix_tasks_source", "tasks", ["source"])
    op.create_index("ix_tasks_status", "tasks", ["status"])

    # --- task_metadata ---
    op.create_table(
        "task_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.Column("extracted_entities", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("llm_model_used", sa.String(100), nullable=True),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("task_id"),
    )
    op.create_index("ix_task_metadata_id", "task_metadata", ["id"])
    op.create_index("ix_task_metadata_task_id", "task_metadata", ["task_id"])

    # --- integrations ---
    op.create_table(
        "integrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "provider", name="uq_integration_user_provider"),
    )
    op.create_index("ix_integrations_id", "integrations", ["id"])
    op.create_index("ix_integrations_user_id", "integrations", ["user_id"])

    # --- sync_logs ---
    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_id", sa.Integer(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("items_imported", sa.Integer(), server_default=sa.text("0")),
        sa.Column("items_updated", sa.Integer(), server_default=sa.text("0")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'success'")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_sync_logs_id", "sync_logs", ["id"])
    op.create_index("ix_sync_logs_integration_id", "sync_logs", ["integration_id"])

    # --- energy_logs ---
    op.create_table(
        "energy_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_energy_logs_id", "energy_logs", ["id"])
    op.create_index("ix_energy_logs_user_id", "energy_logs", ["user_id"])

    # --- fresh_start_logs ---
    op.create_table(
        "fresh_start_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("tasks_archived_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("next_action_task_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_fresh_start_logs_id", "fresh_start_logs", ["id"])
    op.create_index("ix_fresh_start_logs_user_id", "fresh_start_logs", ["user_id"])

    # --- daily_stats ---
    op.create_table(
        "daily_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("avg_energy_level", sa.Float(), nullable=True),
        sa.Column("tasks_completed", sa.Integer(), server_default=sa.text("0")),
        sa.Column("tasks_archived", sa.Integer(), server_default=sa.text("0")),
        sa.Column("big_rocks_completed", sa.Integer(), server_default=sa.text("0")),
        sa.Column("easy_wins_completed", sa.Integer(), server_default=sa.text("0")),
        sa.Column("fresh_starts_triggered", sa.Integer(), server_default=sa.text("0")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),
    )
    op.create_index("ix_daily_stats_id", "daily_stats", ["id"])
    op.create_index("ix_daily_stats_user_id", "daily_stats", ["user_id"])
    op.create_index("ix_daily_stats_date", "daily_stats", ["date"])


def downgrade() -> None:
    op.drop_table("daily_stats")
    op.drop_table("fresh_start_logs")
    op.drop_table("energy_logs")
    op.drop_table("sync_logs")
    op.drop_table("integrations")
    op.drop_table("task_metadata")
    op.drop_table("tasks")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
