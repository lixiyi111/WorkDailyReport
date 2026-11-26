-- 智能日报生成器 v1 · MySQL 8 建表脚本
-- 用法（在 v1-sdd/backend 目录下）：
--   mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql
-- 说明：与 app/models/entities.py 保持一致；应用启动不自动建表（AUTO_CREATE_TABLES=false）。

CREATE DATABASE IF NOT EXISTS daily_report
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE daily_report;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS members (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL,
  role ENUM('member','leader','mentor') NOT NULL DEFAULT 'member',
  status ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_members_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS member_identities (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  member_id BIGINT UNSIGNED NOT NULL,
  provider ENUM('github','feishu') NOT NULL,
  external_id VARCHAR(128) NOT NULL,
  external_username VARCHAR(128) NULL,
  verified TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_provider_external (provider, external_id),
  KEY idx_identity_member (member_id),
  CONSTRAINT fk_identity_member FOREIGN KEY (member_id) REFERENCES members(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repositories (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  owner VARCHAR(128) NOT NULL,
  name VARCHAR(128) NOT NULL,
  default_branch VARCHAR(128) NOT NULL DEFAULT 'main',
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_repo (owner, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS raw_commits (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  repo_id BIGINT UNSIGNED NOT NULL,
  sha CHAR(40) NOT NULL,
  author_identity_id BIGINT UNSIGNED NULL,
  author_name VARCHAR(128) NOT NULL,
  author_email VARCHAR(255) NULL,
  committed_at DATETIME NOT NULL,
  message TEXT NOT NULL,
  branch VARCHAR(128) NULL,
  url VARCHAR(512) NULL,
  pr_number INT NULL,
  collected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_repo_sha (repo_id, sha),
  KEY idx_commit_time (committed_at),
  KEY idx_commit_author (author_identity_id),
  CONSTRAINT fk_commit_repo FOREIGN KEY (repo_id) REFERENCES repositories(id),
  CONSTRAINT fk_commit_identity FOREIGN KEY (author_identity_id) REFERENCES member_identities(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS raw_tasks (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  task_id VARCHAR(128) NOT NULL,
  title VARCHAR(512) NOT NULL,
  owner_identity_id BIGINT UNSIGNED NULL,
  participants_json JSON NULL,
  status VARCHAR(64) NOT NULL DEFAULT 'open',
  status_changed_at DATETIME NULL,
  created_at_source DATETIME NULL,
  updated_at_source DATETIME NULL,
  collected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_task_id (task_id),
  KEY idx_task_owner (owner_identity_id),
  KEY idx_task_time (status_changed_at),
  CONSTRAINT fk_task_owner FOREIGN KEY (owner_identity_id) REFERENCES member_identities(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS raw_messages (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  message_id VARCHAR(128) NOT NULL,
  chat_id VARCHAR(128) NOT NULL,
  sender_identity_id BIGINT UNSIGNED NULL,
  sender_name VARCHAR(128) NULL,
  sent_at DATETIME NOT NULL,
  content_excerpt TEXT NULL,
  content_hash CHAR(64) NULL,
  collected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_message_id (message_id),
  KEY idx_chat_sent (chat_id, sent_at),
  KEY idx_message_sender (sender_identity_id),
  CONSTRAINT fk_message_sender FOREIGN KEY (sender_identity_id) REFERENCES member_identities(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS identity_unmatched (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  provider ENUM('github','feishu') NOT NULL,
  external_id VARCHAR(128) NOT NULL,
  external_name VARCHAR(128) NULL,
  source_type VARCHAR(32) NOT NULL,
  source_id VARCHAR(128) NOT NULL,
  resolved_member_id BIGINT UNSIGNED NULL,
  resolved_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_unmatched (provider, external_id, source_type, source_id),
  CONSTRAINT fk_unmatched_member FOREIGN KEY (resolved_member_id) REFERENCES members(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_reports (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  report_date DATE NOT NULL,
  report_type ENUM('personal','team') NOT NULL,
  scope_key VARCHAR(64) NOT NULL,
  member_id BIGINT UNSIGNED NULL,
  status ENUM('draft','generated','published') NOT NULL DEFAULT 'generated',
  current_version INT NOT NULL DEFAULT 1,
  content_md MEDIUMTEXT NOT NULL,
  summary_json JSON NULL,
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_report_scope (report_date, report_type, scope_key),
  KEY idx_report_date (report_date),
  KEY idx_report_member (member_id),
  CONSTRAINT fk_report_member FOREIGN KEY (member_id) REFERENCES members(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_items (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  report_id BIGINT UNSIGNED NOT NULL,
  category ENUM('commit','task','message','collaboration','manual') NOT NULL,
  title VARCHAR(512) NOT NULL,
  detail TEXT NULL,
  source_type VARCHAR(32) NULL,
  source_id VARCHAR(128) NULL,
  attribution_role ENUM('author','reviewer','assignee','participant','owner') NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_item_report (report_id),
  KEY idx_item_source (source_type, source_id),
  CONSTRAINT fk_item_report FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_versions (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  report_id BIGINT UNSIGNED NOT NULL,
  version INT NOT NULL,
  content_md MEDIUMTEXT NOT NULL,
  editor VARCHAR(64) NOT NULL,
  change_note VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_report_version (report_id, version),
  CONSTRAINT fk_version_report FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS push_logs (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  report_id BIGINT UNSIGNED NOT NULL,
  channel ENUM('email','feishu','console') NOT NULL,
  target VARCHAR(255) NOT NULL,
  status ENUM('success','failed') NOT NULL,
  attempt INT NOT NULL DEFAULT 1,
  error_message VARCHAR(1024) NULL,
  sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_push_report (report_id),
  KEY idx_push_status (status, sent_at),
  CONSTRAINT fk_push_report FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS source_sync_state (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  source ENUM('github','feishu_tasks','feishu_messages') NOT NULL,
  resource_key VARCHAR(191) NOT NULL,
  last_cursor VARCHAR(255) NULL,
  last_synced_at DATETIME NULL,
  status ENUM('idle','running','success','partial','failed') NOT NULL DEFAULT 'idle',
  error_message VARCHAR(1024) NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_source_resource (source, resource_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
