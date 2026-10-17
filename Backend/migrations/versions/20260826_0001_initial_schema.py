"""Create the initial academic schema."""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260826_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _common_columns() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    enrollment_status = postgresql.ENUM(
    "ACTIVE",
    "CANCELLED",
    "COMPLETED",
    name="enrollment_status",
    create_type=False,
    )
    enrollment_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "roles",
        *_common_columns(),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)
    op.create_table(
        "users",
        *_common_columns(),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "academic_periods",
        *_common_columns(),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("enrollment_start", sa.Date(), nullable=False),
        sa.Column("enrollment_end", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint("end_date >= start_date", name="ck_period_date_order"),
    )
    op.create_table(
        "subjects",
        *_common_columns(),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint("credits > 0", name="ck_subject_credits_positive"),
    )
    op.create_index("ix_subjects_code", "subjects", ["code"], unique=True)
    op.create_index("ix_subjects_teacher_id", "subjects", ["teacher_id"])
    op.create_table(
        "enrollments",
        *_common_columns(),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("academic_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("academic_periods.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", enrollment_status, server_default="ACTIVE", nullable=False),
        sa.UniqueConstraint("student_id", "subject_id", "academic_period_id", name="uq_enrollment_context"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_subject_id", "enrollments", ["subject_id"])
    op.create_index("ix_enrollments_academic_period_id", "enrollments", ["academic_period_id"])
    op.create_table(
        "grades",
        *_common_columns(),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("score", sa.Numeric(3, 2), nullable=False),
        sa.Column("weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("observations", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 5", name="ck_grade_score_range"),
        sa.CheckConstraint("weight > 0 AND weight <= 100", name="ck_grade_weight_range"),
    )
    op.create_index("ix_grades_enrollment_id", "grades", ["enrollment_id"])

    roles = sa.table("roles", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("name"), sa.column("description"))
    op.bulk_insert(
        roles,
        [
            {"id": uuid4(), "name": "administrator", "description": "Full system administration"},
            {"id": uuid4(), "name": "teacher", "description": "Assigned academic instruction"},
            {"id": uuid4(), "name": "student", "description": "Student self-service"},
        ],
    )


def downgrade() -> None:
    op.drop_table("grades")
    op.drop_table("enrollments")
    op.drop_table("subjects")
    op.drop_table("academic_periods")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
    sa.Enum(name="enrollment_status").drop(op.get_bind(), checkfirst=True)
