-- v2 智能日报生成器 · MySQL 建表脚本（由 ORM 元数据生成）
-- 使用：mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql

CREATE DATABASE IF NOT EXISTS daily_report_v2
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE daily_report_v2;

CREATE TABLE IF NOT EXISTS members (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(64) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	`role` VARCHAR(16) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_members_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS repositories (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	owner VARCHAR(128) NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	default_branch VARCHAR(128) NOT NULL, 
	enabled BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_repo UNIQUE (owner, name)
);

CREATE TABLE IF NOT EXISTS source_sync_state (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	source VARCHAR(32) NOT NULL, 
	resource_key VARCHAR(191) NOT NULL, 
	last_cursor VARCHAR(255), 
	last_synced_at DATETIME, 
	status VARCHAR(16) NOT NULL, 
	error_message VARCHAR(1024), 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_source_resource UNIQUE (source, resource_key)
);

CREATE TABLE IF NOT EXISTS app_users (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	username VARCHAR(64) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(16) NOT NULL, 
	member_id BIGINT, 
	active BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_app_users_username UNIQUE (username), 
	FOREIGN KEY(member_id) REFERENCES members (id)
);

CREATE TABLE IF NOT EXISTS daily_reports (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	report_date DATE NOT NULL, 
	report_type VARCHAR(16) NOT NULL, 
	scope_key VARCHAR(64) NOT NULL, 
	member_id BIGINT, 
	status VARCHAR(16) NOT NULL, 
	current_version INTEGER NOT NULL, 
	content_md MEDIUMTEXT NOT NULL, 
	summary_json JSON, 
	generated_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_report_scope UNIQUE (report_date, report_type, scope_key), 
	FOREIGN KEY(member_id) REFERENCES members (id)
);

CREATE TABLE IF NOT EXISTS identity_unmatched (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	provider VARCHAR(16) NOT NULL, 
	external_id VARCHAR(128) NOT NULL, 
	external_name VARCHAR(128), 
	source_type VARCHAR(32) NOT NULL, 
	source_id VARCHAR(128) NOT NULL, 
	resolved_member_id BIGINT, 
	resolved_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_unmatched UNIQUE (provider, external_id, source_type, source_id), 
	FOREIGN KEY(resolved_member_id) REFERENCES members (id)
);

CREATE TABLE IF NOT EXISTS member_identities (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	member_id BIGINT NOT NULL, 
	provider VARCHAR(16) NOT NULL, 
	external_id VARCHAR(128) NOT NULL, 
	external_username VARCHAR(128), 
	verified BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_provider_external UNIQUE (provider, external_id), 
	FOREIGN KEY(member_id) REFERENCES members (id)
);

CREATE TABLE IF NOT EXISTS push_logs (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	report_id BIGINT NOT NULL, 
	channel VARCHAR(16) NOT NULL, 
	target VARCHAR(255) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	attempt INTEGER NOT NULL, 
	error_message VARCHAR(1024), 
	sent_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(report_id) REFERENCES daily_reports (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS raw_commits (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	repo_id BIGINT NOT NULL, 
	sha VARCHAR(40) NOT NULL, 
	author_identity_id BIGINT, 
	author_name VARCHAR(128) NOT NULL, 
	author_email VARCHAR(255), 
	committed_at DATETIME NOT NULL, 
	message TEXT NOT NULL, 
	branch VARCHAR(128), 
	url VARCHAR(512), 
	pr_number INTEGER, 
	collected_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_repo_sha UNIQUE (repo_id, sha), 
	FOREIGN KEY(repo_id) REFERENCES repositories (id), 
	FOREIGN KEY(author_identity_id) REFERENCES member_identities (id)
);

CREATE TABLE IF NOT EXISTS raw_messages (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	message_id VARCHAR(128) NOT NULL, 
	chat_id VARCHAR(128) NOT NULL, 
	sender_identity_id BIGINT, 
	sender_name VARCHAR(128), 
	sent_at DATETIME NOT NULL, 
	content_excerpt TEXT, 
	content_hash VARCHAR(64), 
	collected_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_message_id UNIQUE (message_id), 
	FOREIGN KEY(sender_identity_id) REFERENCES member_identities (id)
);

CREATE TABLE IF NOT EXISTS raw_tasks (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	task_id VARCHAR(128) NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	owner_identity_id BIGINT, 
	participants_json JSON, 
	status VARCHAR(64) NOT NULL, 
	status_changed_at DATETIME, 
	created_at_source DATETIME, 
	updated_at_source DATETIME, 
	collected_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_task_id UNIQUE (task_id), 
	FOREIGN KEY(owner_identity_id) REFERENCES member_identities (id)
);

CREATE TABLE IF NOT EXISTS report_items (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	report_id BIGINT NOT NULL, 
	category VARCHAR(32) NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	detail TEXT, 
	source_type VARCHAR(32), 
	source_id VARCHAR(128), 
	attribution_role VARCHAR(32), 
	sort_order INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(report_id) REFERENCES daily_reports (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS report_versions (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	report_id BIGINT NOT NULL, 
	version INTEGER NOT NULL, 
	content_md MEDIUMTEXT NOT NULL, 
	editor VARCHAR(64) NOT NULL, 
	change_note VARCHAR(255), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_report_version UNIQUE (report_id, version), 
	FOREIGN KEY(report_id) REFERENCES daily_reports (id) ON DELETE CASCADE
);
