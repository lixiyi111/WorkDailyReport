-- v2 演示成员与飞书 Mock 身份（可重复执行）
USE daily_report_v2;

INSERT IGNORE INTO members (name, email, role, status, created_at, updated_at) VALUES
  ('王芳', 'wangfang@example.com', 'member', 'active', NOW(), NOW()),
  ('李四', 'lisi@example.com', 'member', 'active', NOW(), NOW()),
  ('赵敏', 'zhaomin@example.com', 'leader', 'active', NOW(), NOW());

INSERT IGNORE INTO repositories
  (owner, name, default_branch, enabled, created_at)
VALUES ('lixiyi111', 'WorkDailyReport', 'master', 1, NOW());

INSERT IGNORE INTO member_identities
  (member_id, provider, external_id, external_username, verified, created_at)
SELECT id, 'feishu', 'mock-wangfang', '王芳', 1, NOW()
FROM members WHERE email = 'wangfang@example.com';

INSERT IGNORE INTO member_identities
  (member_id, provider, external_id, external_username, verified, created_at)
SELECT id, 'feishu', 'mock-lisi', '李四', 1, NOW()
FROM members WHERE email = 'lisi@example.com';

INSERT IGNORE INTO member_identities
  (member_id, provider, external_id, external_username, verified, created_at)
SELECT id, 'feishu', 'mock-zhaomin', '赵敏', 1, NOW()
FROM members WHERE email = 'zhaomin@example.com';
