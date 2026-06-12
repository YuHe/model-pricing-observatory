"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-12 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('provider',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('country', sa.String(10)),
        sa.Column('official_url', sa.Text),
        sa.Column('logo_url', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('model',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('provider.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('family', sa.String(100)),
        sa.Column('release_date', sa.Date),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('provider_id', 'name'),
    )

    op.create_table('model_capability',
        sa.Column('model_id', UUID(as_uuid=True), sa.ForeignKey('model.id'), primary_key=True),
        sa.Column('context_window', sa.Integer),
        sa.Column('max_output_tokens', sa.Integer),
        sa.Column('vision', sa.Boolean, server_default='false'),
        sa.Column('reasoning', sa.Boolean, server_default='false'),
        sa.Column('tool_calling', sa.Boolean, server_default='false'),
        sa.Column('structured_output', sa.Boolean, server_default='false'),
        sa.Column('json_mode', sa.Boolean, server_default='false'),
        sa.Column('batch_api', sa.Boolean, server_default='false'),
        sa.Column('fine_tuning', sa.Boolean, server_default='false'),
        sa.Column('prompt_caching', sa.Boolean, server_default='false'),
    )

    op.create_table('model_alias',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('model_id', UUID(as_uuid=True), sa.ForeignKey('model.id'), nullable=False),
        sa.Column('alias_name', sa.String(300), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.UniqueConstraint('alias_name', 'source'),
    )

    op.create_table('price_snapshot',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('model_id', UUID(as_uuid=True), sa.ForeignKey('model.id'), nullable=False),
        sa.Column('channel_id', UUID(as_uuid=True), sa.ForeignKey('provider.id'), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('input_price_per_m', sa.Numeric(12, 6)),
        sa.Column('output_price_per_m', sa.Numeric(12, 6)),
        sa.Column('input_price_cny', sa.Numeric(12, 6)),
        sa.Column('output_price_cny', sa.Numeric(12, 6)),
        sa.Column('exchange_rate', sa.Numeric(10, 4)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('date', 'model_id', 'channel_id'),
    )

    op.create_table('subscription_plan',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('plan_name', sa.String(200), nullable=False),
        sa.Column('monthly_price', sa.Numeric(10, 2)),
        sa.Column('annual_price', sa.Numeric(10, 2)),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('monthly_price_cny', sa.Numeric(10, 2)),
        sa.Column('features', JSONB),
        sa.Column('source_url', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('provider', 'plan_name'),
    )

    op.create_table('subscription_snapshot',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('plan_id', UUID(as_uuid=True), sa.ForeignKey('subscription_plan.id'), nullable=False),
        sa.Column('monthly_price', sa.Numeric(10, 2)),
        sa.Column('monthly_price_cny', sa.Numeric(10, 2)),
        sa.Column('exchange_rate', sa.Numeric(10, 4)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('date', 'plan_id'),
    )

    op.create_table('exchange_rate',
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('usd_cny', sa.Numeric(10, 4), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('crawl_job',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('models_synced', sa.Integer, server_default='0'),
        sa.Column('error_message', sa.Text),
        sa.Column('stack_trace', sa.Text),
        sa.Column('retry_count', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('alert_config',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('endpoint', sa.Text, nullable=False),
        sa.Column('enabled', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('alert_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('alert_config_id', UUID(as_uuid=True), sa.ForeignKey('alert_config.id')),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('crawl_job.id')),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(20)),
        sa.Column('error_message', sa.Text),
    )


def downgrade() -> None:
    op.drop_table('alert_log')
    op.drop_table('alert_config')
    op.drop_table('crawl_job')
    op.drop_table('exchange_rate')
    op.drop_table('subscription_snapshot')
    op.drop_table('subscription_plan')
    op.drop_table('price_snapshot')
    op.drop_table('model_alias')
    op.drop_table('model_capability')
    op.drop_table('model')
    op.drop_table('provider')
