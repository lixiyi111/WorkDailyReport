-- 智能日报生成器 · 演示数据（只含 INSERT）
-- 前置：已执行 sql/schema.sql
-- 用法：mysql -h 127.0.0.1 -P 3305 -u root -p daily_report < sql/demo_data.sql
-- 警告：本脚本会先清空业务表，再写入演示数据；请勿在生产库执行。
USE daily_report;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE report_items;
TRUNCATE TABLE report_versions;
TRUNCATE TABLE push_logs;
TRUNCATE TABLE daily_reports;
TRUNCATE TABLE raw_messages;
TRUNCATE TABLE raw_tasks;
TRUNCATE TABLE raw_commits;
TRUNCATE TABLE identity_unmatched;
TRUNCATE TABLE member_identities;
TRUNCATE TABLE repositories;
TRUNCATE TABLE members;
TRUNCATE TABLE source_sync_state;
SET FOREIGN_KEY_CHECKS = 1;
START TRANSACTION;
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (1, '李明', 'liming@example.com', 'leader', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (2, '王芳', 'wangfang@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (3, '张伟', 'zhangwei@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (4, '刘洋', 'liuyang@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (5, '陈静', 'chenjing@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (6, '赵磊', 'zhaolei@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (7, '孙悦', 'sunyue@example.com', 'member', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO members (id, name, email, role, status, created_at, updated_at) VALUES (8, '周老师', 'zhou@example.com', 'mentor', 'active', '2026-11-01 09:00:00', '2026-11-01 09:00:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (1, 1, 'github', 'gh_m1', 'user_m1', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (2, 1, 'feishu', 'ou_m1', 'user_m1', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (3, 2, 'github', 'gh_m2', 'user_m2', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (4, 2, 'feishu', 'ou_m2', 'user_m2', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (5, 3, 'github', 'gh_m3', 'user_m3', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (6, 3, 'feishu', 'ou_m3', 'user_m3', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (7, 4, 'github', 'gh_m4', 'user_m4', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (8, 4, 'feishu', 'ou_m4', 'user_m4', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (9, 5, 'github', 'gh_m5', 'user_m5', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (10, 5, 'feishu', 'ou_m5', 'user_m5', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (11, 6, 'github', 'gh_m6', 'user_m6', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (12, 6, 'feishu', 'ou_m6', 'user_m6', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (13, 7, 'github', 'gh_m7', 'user_m7', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (14, 7, 'feishu', 'ou_m7', 'user_m7', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (15, 8, 'github', 'gh_m8', 'user_m8', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO member_identities (id, member_id, provider, external_id, external_username, verified, created_at) VALUES (16, 8, 'feishu', 'ou_m8', 'user_m8', 1, '2026-11-01 09:05:00');
INSERT IGNORE INTO repositories (id, owner, name, default_branch, enabled, created_at) VALUES (1, 'team', 'daily-report', 'main', 1, '2026-11-01 09:00:00');
INSERT IGNORE INTO repositories (id, owner, name, default_branch, enabled, created_at) VALUES (2, 'team', 'web-console', 'main', 1, '2026-11-01 09:00:00');
INSERT IGNORE INTO repositories (id, owner, name, default_branch, enabled, created_at) VALUES (3, 'team', 'api-gateway', 'main', 1, '2026-11-01 09:00:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (1, 1, '61121720406dbe0283bcc2dc7efbeb8bd42e3c8b', 3, '王芳', 'wangfang@example.com', '2026-11-20 03:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/daily-report/commit/61121720406dbe0283bcc2dc7efbeb8bd42e3c8b', NULL, '2026-11-20 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (2, 2, 'bea3e1c4a8271b0390b2f7427affecd1cbd8316a', 3, '王芳', 'wangfang@example.com', '2026-11-20 05:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/web-console/commit/bea3e1c4a8271b0390b2f7427affecd1cbd8316a', 1002, '2026-11-20 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (3, 3, '34d29103335944f8d4037e5cff75662b222c909a', 5, '张伟', 'zhangwei@example.com', '2026-11-20 01:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/api-gateway/commit/34d29103335944f8d4037e5cff75662b222c909a', NULL, '2026-11-20 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (4, 1, 'd76bf9cc86eab5e3282086b67dcba34864bbc095', 5, '张伟', 'zhangwei@example.com', '2026-11-20 03:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/daily-report/commit/d76bf9cc86eab5e3282086b67dcba34864bbc095', 1004, '2026-11-20 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (5, 2, '71a010772bb69ad8d88d9c37ef636c068e0a5d09', 7, '刘洋', 'liuyang@example.com', '2026-11-20 02:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/web-console/commit/71a010772bb69ad8d88d9c37ef636c068e0a5d09', NULL, '2026-11-20 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (6, 3, '30db47aaf7f9b66c6cee168fe5d3c89cda63a6e1', 7, '刘洋', 'liuyang@example.com', '2026-11-20 04:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/api-gateway/commit/30db47aaf7f9b66c6cee168fe5d3c89cda63a6e1', 1006, '2026-11-20 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (7, 1, 'be1c2a519f9c2a821c58d8fa460566b715458405', 9, '陈静', 'chenjing@example.com', '2026-11-20 03:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/daily-report/commit/be1c2a519f9c2a821c58d8fa460566b715458405', NULL, '2026-11-20 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (8, 2, 'b168e5c30358c4f9ae471bf71bb41159243e73ee', 9, '陈静', 'chenjing@example.com', '2026-11-20 05:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/web-console/commit/b168e5c30358c4f9ae471bf71bb41159243e73ee', 1008, '2026-11-20 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (9, 3, 'b56137799f75f91aacc4653887002813dbe61453', 11, '赵磊', 'zhaolei@example.com', '2026-11-20 01:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/api-gateway/commit/b56137799f75f91aacc4653887002813dbe61453', NULL, '2026-11-20 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (10, 1, '77385cfab65d14907dc409de34db9841c219bd91', 11, '赵磊', 'zhaolei@example.com', '2026-11-20 03:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/daily-report/commit/77385cfab65d14907dc409de34db9841c219bd91', 1010, '2026-11-20 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (11, 2, '54f217cf5e4880aff180af963bc5bf206479a1ea', 13, '孙悦', 'sunyue@example.com', '2026-11-20 02:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/web-console/commit/54f217cf5e4880aff180af963bc5bf206479a1ea', NULL, '2026-11-20 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (12, 3, '5876dc8a3179ddda9d52910ff2a54220f5c75743', 13, '孙悦', 'sunyue@example.com', '2026-11-20 04:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/api-gateway/commit/5876dc8a3179ddda9d52910ff2a54220f5c75743', 1012, '2026-11-20 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (13, 1, '73a74da7d3fc9c3805f3e21ac0a8166c68f84e45', 3, '王芳', 'wangfang@example.com', '2026-11-21 03:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/daily-report/commit/73a74da7d3fc9c3805f3e21ac0a8166c68f84e45', NULL, '2026-11-21 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (14, 2, 'c9b165631f39f5ee29f6f15184ec3925879cef7f', 5, '张伟', 'zhangwei@example.com', '2026-11-21 01:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/web-console/commit/c9b165631f39f5ee29f6f15184ec3925879cef7f', NULL, '2026-11-21 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (15, 3, '51e7ff9e1e5b14e257ef512164084654aea30846', 7, '刘洋', 'liuyang@example.com', '2026-11-21 02:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/api-gateway/commit/51e7ff9e1e5b14e257ef512164084654aea30846', NULL, '2026-11-21 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (16, 1, 'f9bbe40b602cc5917247ce9066d322d7f52f813e', 9, '陈静', 'chenjing@example.com', '2026-11-21 03:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/daily-report/commit/f9bbe40b602cc5917247ce9066d322d7f52f813e', NULL, '2026-11-21 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (17, 2, '781d2c7fbd6eaab000c5c254ea2222a61ef9e455', 11, '赵磊', 'zhaolei@example.com', '2026-11-21 01:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/web-console/commit/781d2c7fbd6eaab000c5c254ea2222a61ef9e455', NULL, '2026-11-21 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (18, 3, 'c6e900eed821d5f0b3897d24eda65de4a8820909', 13, '孙悦', 'sunyue@example.com', '2026-11-21 02:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/api-gateway/commit/c6e900eed821d5f0b3897d24eda65de4a8820909', NULL, '2026-11-21 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (19, 1, 'c78ef350d796fa46b4922c087ec83b622330308f', 3, '王芳', 'wangfang@example.com', '2026-11-22 03:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/daily-report/commit/c78ef350d796fa46b4922c087ec83b622330308f', NULL, '2026-11-22 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (20, 2, 'b7e0337baa2be8532ba0aa8f01b8362b03d5812b', 5, '张伟', 'zhangwei@example.com', '2026-11-22 01:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/web-console/commit/b7e0337baa2be8532ba0aa8f01b8362b03d5812b', NULL, '2026-11-22 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (21, 3, '25c3f03c3320268ff4fa9c66e232bdf4d538f670', 7, '刘洋', 'liuyang@example.com', '2026-11-22 02:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/api-gateway/commit/25c3f03c3320268ff4fa9c66e232bdf4d538f670', NULL, '2026-11-22 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (22, 1, '918e1fa17eab86183762900d6c4b2e49b5bba24b', 9, '陈静', 'chenjing@example.com', '2026-11-22 03:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/daily-report/commit/918e1fa17eab86183762900d6c4b2e49b5bba24b', NULL, '2026-11-22 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (23, 2, '4f7e52a8236afd1d780491416d0e08ab70c8d3db', 11, '赵磊', 'zhaolei@example.com', '2026-11-22 01:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/web-console/commit/4f7e52a8236afd1d780491416d0e08ab70c8d3db', NULL, '2026-11-22 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (24, 3, 'b497295babde27a7db036a447c7b5b17a24057e8', 13, '孙悦', 'sunyue@example.com', '2026-11-22 02:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/api-gateway/commit/b497295babde27a7db036a447c7b5b17a24057e8', NULL, '2026-11-22 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (25, 1, '5920d02a1754125c46619e99463d4cdde5410f3a', 3, '王芳', 'wangfang@example.com', '2026-11-23 03:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/daily-report/commit/5920d02a1754125c46619e99463d4cdde5410f3a', NULL, '2026-11-23 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (26, 2, '343d7b31e708371158f8299f5640fe9435142082', 3, '王芳', 'wangfang@example.com', '2026-11-23 05:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/web-console/commit/343d7b31e708371158f8299f5640fe9435142082', 1026, '2026-11-23 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (27, 3, 'd15ecf948bef2eb04ea052bc1107ffa0488edea7', 5, '张伟', 'zhangwei@example.com', '2026-11-23 01:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/api-gateway/commit/d15ecf948bef2eb04ea052bc1107ffa0488edea7', NULL, '2026-11-23 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (28, 1, '0537f4b161c33de0530a7e51d6e58fa06b5cebc5', 5, '张伟', 'zhangwei@example.com', '2026-11-23 03:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/daily-report/commit/0537f4b161c33de0530a7e51d6e58fa06b5cebc5', 1028, '2026-11-23 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (29, 2, 'ce7199c47432ba582c01e47f2a3f0dbdb106b5ef', 7, '刘洋', 'liuyang@example.com', '2026-11-23 02:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/web-console/commit/ce7199c47432ba582c01e47f2a3f0dbdb106b5ef', NULL, '2026-11-23 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (30, 3, '0a008234994031bafb0902d6ab1b1ac07c877eb8', 7, '刘洋', 'liuyang@example.com', '2026-11-23 04:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/api-gateway/commit/0a008234994031bafb0902d6ab1b1ac07c877eb8', 1030, '2026-11-23 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (31, 1, '24480efb3a88a83c320c40f7df2d7e92eb6f9d3a', 9, '陈静', 'chenjing@example.com', '2026-11-23 03:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/daily-report/commit/24480efb3a88a83c320c40f7df2d7e92eb6f9d3a', NULL, '2026-11-23 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (32, 2, '5198e85e147af8551b4038ccf4f953e5d6eccb19', 9, '陈静', 'chenjing@example.com', '2026-11-23 05:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/web-console/commit/5198e85e147af8551b4038ccf4f953e5d6eccb19', 1032, '2026-11-23 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (33, 3, 'ece510dda9e3d760e2d35f047fc869fda52067d0', 11, '赵磊', 'zhaolei@example.com', '2026-11-23 01:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/api-gateway/commit/ece510dda9e3d760e2d35f047fc869fda52067d0', NULL, '2026-11-23 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (34, 1, 'abed9b7b8cad9fa427250a1f53b33f0a3a3d5ca2', 11, '赵磊', 'zhaolei@example.com', '2026-11-23 03:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/daily-report/commit/abed9b7b8cad9fa427250a1f53b33f0a3a3d5ca2', 1034, '2026-11-23 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (35, 2, '7df9ab9ecd21c574d9d4504d5d8e5481fe605495', 13, '孙悦', 'sunyue@example.com', '2026-11-23 02:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/web-console/commit/7df9ab9ecd21c574d9d4504d5d8e5481fe605495', NULL, '2026-11-23 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (36, 3, '543682faba7caccadeddcea98ab708a98f6fd05c', 13, '孙悦', 'sunyue@example.com', '2026-11-23 04:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/api-gateway/commit/543682faba7caccadeddcea98ab708a98f6fd05c', 1036, '2026-11-23 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (37, 1, '701bb1529dcc7925ff56bf5fc7d0bde5185a3e3f', 3, '王芳', 'wangfang@example.com', '2026-11-24 03:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/daily-report/commit/701bb1529dcc7925ff56bf5fc7d0bde5185a3e3f', NULL, '2026-11-24 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (38, 2, '06333660e0aadb58c477744fbfa9f5a1d2f994ef', 3, '王芳', 'wangfang@example.com', '2026-11-24 05:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/web-console/commit/06333660e0aadb58c477744fbfa9f5a1d2f994ef', 1038, '2026-11-24 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (39, 3, '525fca2b5a1e0de2a611561408672dfa7af4144e', 5, '张伟', 'zhangwei@example.com', '2026-11-24 01:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/api-gateway/commit/525fca2b5a1e0de2a611561408672dfa7af4144e', NULL, '2026-11-24 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (40, 1, '3eb07169492a779152a6d5f2988e9db78a832261', 5, '张伟', 'zhangwei@example.com', '2026-11-24 03:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/daily-report/commit/3eb07169492a779152a6d5f2988e9db78a832261', 1040, '2026-11-24 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (41, 2, 'e1eeebec5a1217cbf069702bd00cf3514c654b2e', 7, '刘洋', 'liuyang@example.com', '2026-11-24 02:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/web-console/commit/e1eeebec5a1217cbf069702bd00cf3514c654b2e', NULL, '2026-11-24 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (42, 3, '3533f72722bc16ca411ad7e4bea0363ae1b721d7', 7, '刘洋', 'liuyang@example.com', '2026-11-24 04:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/api-gateway/commit/3533f72722bc16ca411ad7e4bea0363ae1b721d7', 1042, '2026-11-24 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (43, 1, 'dcef3096bb8f25b38db34ead3ce9a62de68b41c9', 9, '陈静', 'chenjing@example.com', '2026-11-24 03:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/daily-report/commit/dcef3096bb8f25b38db34ead3ce9a62de68b41c9', NULL, '2026-11-24 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (44, 2, 'd512b94fbc7059bf74d02b3ad76bec783db026e8', 9, '陈静', 'chenjing@example.com', '2026-11-24 05:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/web-console/commit/d512b94fbc7059bf74d02b3ad76bec783db026e8', 1044, '2026-11-24 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (45, 3, '105a71160b0c07cbd52370162ea66f6cb80ba814', 11, '赵磊', 'zhaolei@example.com', '2026-11-24 01:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/api-gateway/commit/105a71160b0c07cbd52370162ea66f6cb80ba814', NULL, '2026-11-24 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (46, 1, '61b17410e0a065e2e73d219b0c9bd0da00192ec1', 11, '赵磊', 'zhaolei@example.com', '2026-11-24 03:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/daily-report/commit/61b17410e0a065e2e73d219b0c9bd0da00192ec1', 1046, '2026-11-24 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (47, 2, 'acc2c39ce8f7497a518ea0fe3e946904395d6fcc', 13, '孙悦', 'sunyue@example.com', '2026-11-24 02:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/web-console/commit/acc2c39ce8f7497a518ea0fe3e946904395d6fcc', NULL, '2026-11-24 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (48, 3, '25cc3ad17e030762e0c076819bbe4d83a4d3d6e5', 13, '孙悦', 'sunyue@example.com', '2026-11-24 04:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/api-gateway/commit/25cc3ad17e030762e0c076819bbe4d83a4d3d6e5', 1048, '2026-11-24 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (49, 1, '90e66848a26dd47463a6afa9f2d8390ea35b34d6', 3, '王芳', 'wangfang@example.com', '2026-11-25 03:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/daily-report/commit/90e66848a26dd47463a6afa9f2d8390ea35b34d6', NULL, '2026-11-25 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (50, 2, 'd3f3063c08828f10f05ad9e35ad117a867cc0170', 3, '王芳', 'wangfang@example.com', '2026-11-25 05:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/web-console/commit/d3f3063c08828f10f05ad9e35ad117a867cc0170', 1050, '2026-11-25 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (51, 3, 'ed4b7eee2ab5a47401830a2b5e809d9475102a2a', 5, '张伟', 'zhangwei@example.com', '2026-11-25 01:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/api-gateway/commit/ed4b7eee2ab5a47401830a2b5e809d9475102a2a', NULL, '2026-11-25 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (52, 1, 'cf7cba9f228d7da64345b9e1da83bbe211789a5e', 5, '张伟', 'zhangwei@example.com', '2026-11-25 03:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/daily-report/commit/cf7cba9f228d7da64345b9e1da83bbe211789a5e', 1052, '2026-11-25 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (53, 2, '653b2479704ded7229f288f58da624abdd387e52', 7, '刘洋', 'liuyang@example.com', '2026-11-25 02:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/web-console/commit/653b2479704ded7229f288f58da624abdd387e52', NULL, '2026-11-25 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (54, 3, 'ec0f020e83b78cf1de5cc293e1f86c2eed2d2302', 7, '刘洋', 'liuyang@example.com', '2026-11-25 04:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/api-gateway/commit/ec0f020e83b78cf1de5cc293e1f86c2eed2d2302', 1054, '2026-11-25 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (55, 1, 'c94681cca47dc36c68bedf97fbc8b48d28478b61', 9, '陈静', 'chenjing@example.com', '2026-11-25 03:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/daily-report/commit/c94681cca47dc36c68bedf97fbc8b48d28478b61', NULL, '2026-11-25 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (56, 2, 'ac11f739dbe425c8d56ff5fd7748ef45ed66bede', 9, '陈静', 'chenjing@example.com', '2026-11-25 05:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/web-console/commit/ac11f739dbe425c8d56ff5fd7748ef45ed66bede', 1056, '2026-11-25 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (57, 3, 'aa55c4227909f4e380754bf00b798481558f0ab5', 11, '赵磊', 'zhaolei@example.com', '2026-11-25 01:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/api-gateway/commit/aa55c4227909f4e380754bf00b798481558f0ab5', NULL, '2026-11-25 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (58, 1, '408cf27ae25013ed81aa921cf831ac2ffdb980cb', 11, '赵磊', 'zhaolei@example.com', '2026-11-25 03:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/daily-report/commit/408cf27ae25013ed81aa921cf831ac2ffdb980cb', 1058, '2026-11-25 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (59, 2, 'a14cb2db2764778d1c197eac6ea390622033acfd', 13, '孙悦', 'sunyue@example.com', '2026-11-25 02:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/web-console/commit/a14cb2db2764778d1c197eac6ea390622033acfd', NULL, '2026-11-25 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (60, 3, '04cc6c11ef195918b6542a06d8d7d57991652368', 13, '孙悦', 'sunyue@example.com', '2026-11-25 04:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/api-gateway/commit/04cc6c11ef195918b6542a06d8d7d57991652368', 1060, '2026-11-25 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (61, 1, '64954eea99c82c7cae76e032103c516e6ca95f68', 3, '王芳', 'wangfang@example.com', '2026-11-26 03:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/daily-report/commit/64954eea99c82c7cae76e032103c516e6ca95f68', NULL, '2026-11-26 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (62, 2, 'a53588b856a43e10a1bcefdbf897a75ed9db55f1', 3, '王芳', 'wangfang@example.com', '2026-11-26 05:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/web-console/commit/a53588b856a43e10a1bcefdbf897a75ed9db55f1', 1062, '2026-11-26 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (63, 3, '2d14d0a06c8a02752b4b72454804cca8474e2e53', 5, '张伟', 'zhangwei@example.com', '2026-11-26 01:15:00', 'docs: 补充接口契约说明', 'main', 'https://github.com/team/api-gateway/commit/2d14d0a06c8a02752b4b72454804cca8474e2e53', NULL, '2026-11-26 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (64, 1, 'dc3fa114ee4cc478081500894d7be17705fa73b5', 5, '张伟', 'zhangwei@example.com', '2026-11-26 03:15:00', 'refactor: 拆分采集器与推送器', 'main', 'https://github.com/team/daily-report/commit/dc3fa114ee4cc478081500894d7be17705fa73b5', 1064, '2026-11-26 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (65, 2, 'dd72928cd2a110c3223e31b738305c76b4f3000a', 7, '刘洋', 'liuyang@example.com', '2026-11-26 02:15:00', 'test: 增加日报生成用例', 'main', 'https://github.com/team/web-console/commit/dd72928cd2a110c3223e31b738305c76b4f3000a', NULL, '2026-11-26 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (66, 3, 'c6adb63aa9a458adf39122cda78a84e73ad6279f', 7, '刘洋', 'liuyang@example.com', '2026-11-26 04:15:00', 'feat: 支持成员身份绑定', 'main', 'https://github.com/team/api-gateway/commit/c6adb63aa9a458adf39122cda78a84e73ad6279f', 1066, '2026-11-26 05:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (67, 1, '95b415d8c68d1d1adeace6635dff32a83852277e', 9, '陈静', 'chenjing@example.com', '2026-11-26 03:15:00', 'fix: 处理飞书限流重试', 'main', 'https://github.com/team/daily-report/commit/95b415d8c68d1d1adeace6635dff32a83852277e', NULL, '2026-11-26 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (68, 2, 'd0212f42319d082bd269e11112e4f35a2cfe479a', 9, '陈静', 'chenjing@example.com', '2026-11-26 05:15:00', 'chore: 调整前端状态页间距', 'main', 'https://github.com/team/web-console/commit/d0212f42319d082bd269e11112e4f35a2cfe479a', 1068, '2026-11-26 06:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (69, 3, 'a99a29734a731de64839a7248446b36fbb7643af', 11, '赵磊', 'zhaolei@example.com', '2026-11-26 01:15:00', 'feat: 增加团队日报汇总', 'main', 'https://github.com/team/api-gateway/commit/a99a29734a731de64839a7248446b36fbb7643af', NULL, '2026-11-26 02:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (70, 1, '1b1dd7a7f3fb1972ae85a9b0951686b1fd6fbde6', 11, '赵磊', 'zhaolei@example.com', '2026-11-26 03:15:00', 'fix: 修正时区转换边界', 'main', 'https://github.com/team/daily-report/commit/1b1dd7a7f3fb1972ae85a9b0951686b1fd6fbde6', 1070, '2026-11-26 04:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (71, 2, '36529ba25f8b102818c940a4628829a29c124767', 13, '孙悦', 'sunyue@example.com', '2026-11-26 02:15:00', 'feat: 实现日报模板渲染', 'main', 'https://github.com/team/web-console/commit/36529ba25f8b102818c940a4628829a29c124767', NULL, '2026-11-26 03:15:00');
INSERT IGNORE INTO raw_commits (id, repo_id, sha, author_identity_id, author_name, author_email, committed_at, message, branch, url, pr_number, collected_at) VALUES (72, 3, '087a0a8c780ba1bfb4a4086402d362540e4b26d1', 13, '孙悦', 'sunyue@example.com', '2026-11-26 04:15:00', 'fix: 修复跨零点归属问题', 'main', 'https://github.com/team/api-gateway/commit/087a0a8c780ba1bfb4a4086402d362540e4b26d1', 1072, '2026-11-26 05:15:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (1, 'T-2-1', '完成日报模板设计', 4, '["ou_m3"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (2, 'T-2-2', '联调飞书任务接口', 4, '["ou_m3"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (3, 'T-2-3', '修复身份映射', 4, '["ou_m3"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (4, 'T-2-4', '补充集成测试', 4, '["ou_m3"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (5, 'T-3-1', '整理接口契约', 6, '["ou_m4"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (6, 'T-3-2', '优化前端状态页', 6, '["ou_m4"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (7, 'T-3-3', '接入 MySQL 表结构', 6, '["ou_m4"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (8, 'T-3-4', '编写验收核对表', 6, '["ou_m4"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (9, 'T-4-1', '完成日报模板设计', 8, '["ou_m5"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (10, 'T-4-2', '联调飞书任务接口', 8, '["ou_m5"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (11, 'T-4-3', '修复身份映射', 8, '["ou_m5"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (12, 'T-4-4', '补充集成测试', 8, '["ou_m5"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (13, 'T-5-1', '整理接口契约', 10, '["ou_m6"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (14, 'T-5-2', '优化前端状态页', 10, '["ou_m6"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (15, 'T-5-3', '接入 MySQL 表结构', 10, '["ou_m6"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (16, 'T-5-4', '编写验收核对表', 10, '["ou_m6"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (17, 'T-6-1', '完成日报模板设计', 12, '["ou_m7"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (18, 'T-6-2', '联调飞书任务接口', 12, '["ou_m7"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (19, 'T-6-3', '修复身份映射', 12, '["ou_m7"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (20, 'T-6-4', '补充集成测试', 12, '["ou_m7"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (21, 'T-7-1', '整理接口契约', 14, '["ou_m2"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (22, 'T-7-2', '优化前端状态页', 14, '["ou_m2"]', 'in_progress', '2026-11-25 07:30:00', '2026-11-25 02:00:00', '2026-11-25 07:30:00', '2026-11-25 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (23, 'T-7-3', '接入 MySQL 表结构', 14, '["ou_m2"]', 'blocked', '2026-11-26 07:30:00', '2026-11-26 02:00:00', '2026-11-26 07:30:00', '2026-11-26 08:00:00');
INSERT IGNORE INTO raw_tasks (id, task_id, title, owner_identity_id, participants_json, status, status_changed_at, created_at_source, updated_at_source, collected_at) VALUES (24, 'T-7-4', '编写验收核对表', 14, '["ou_m2"]', 'done', '2026-11-24 07:30:00', '2026-11-24 02:00:00', '2026-11-24 07:30:00', '2026-11-24 08:00:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (1, 'M-2026-11-20-2', 'oc_daily_team', 4, '王芳', '2026-11-20 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (2, 'M-2026-11-20-3', 'oc_daily_team', 6, '张伟', '2026-11-20 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (3, 'M-2026-11-20-4', 'oc_daily_team', 8, '刘洋', '2026-11-20 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (4, 'M-2026-11-20-5', 'oc_daily_team', 10, '陈静', '2026-11-20 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (5, 'M-2026-11-20-6', 'oc_daily_team', 12, '赵磊', '2026-11-20 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (6, 'M-2026-11-20-7', 'oc_daily_team', 14, '孙悦', '2026-11-20 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-20 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (7, 'M-2026-11-21-2', 'oc_daily_team', 4, '王芳', '2026-11-21 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (8, 'M-2026-11-21-3', 'oc_daily_team', 6, '张伟', '2026-11-21 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (9, 'M-2026-11-21-4', 'oc_daily_team', 8, '刘洋', '2026-11-21 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (10, 'M-2026-11-21-5', 'oc_daily_team', 10, '陈静', '2026-11-21 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (11, 'M-2026-11-21-6', 'oc_daily_team', 12, '赵磊', '2026-11-21 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (12, 'M-2026-11-21-7', 'oc_daily_team', 14, '孙悦', '2026-11-21 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-21 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (13, 'M-2026-11-22-2', 'oc_daily_team', 4, '王芳', '2026-11-22 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (14, 'M-2026-11-22-3', 'oc_daily_team', 6, '张伟', '2026-11-22 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (15, 'M-2026-11-22-4', 'oc_daily_team', 8, '刘洋', '2026-11-22 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (16, 'M-2026-11-22-5', 'oc_daily_team', 10, '陈静', '2026-11-22 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (17, 'M-2026-11-22-6', 'oc_daily_team', 12, '赵磊', '2026-11-22 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (18, 'M-2026-11-22-7', 'oc_daily_team', 14, '孙悦', '2026-11-22 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-22 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (19, 'M-2026-11-23-2', 'oc_daily_team', 4, '王芳', '2026-11-23 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (20, 'M-2026-11-23-3', 'oc_daily_team', 6, '张伟', '2026-11-23 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (21, 'M-2026-11-23-4', 'oc_daily_team', 8, '刘洋', '2026-11-23 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (22, 'M-2026-11-23-5', 'oc_daily_team', 10, '陈静', '2026-11-23 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (23, 'M-2026-11-23-6', 'oc_daily_team', 12, '赵磊', '2026-11-23 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (24, 'M-2026-11-23-7', 'oc_daily_team', 14, '孙悦', '2026-11-23 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-23 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (25, 'M-2026-11-24-2', 'oc_daily_team', 4, '王芳', '2026-11-24 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (26, 'M-2026-11-24-3', 'oc_daily_team', 6, '张伟', '2026-11-24 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (27, 'M-2026-11-24-4', 'oc_daily_team', 8, '刘洋', '2026-11-24 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (28, 'M-2026-11-24-5', 'oc_daily_team', 10, '陈静', '2026-11-24 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (29, 'M-2026-11-24-6', 'oc_daily_team', 12, '赵磊', '2026-11-24 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (30, 'M-2026-11-24-7', 'oc_daily_team', 14, '孙悦', '2026-11-24 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-24 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (31, 'M-2026-11-25-2', 'oc_daily_team', 4, '王芳', '2026-11-25 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (32, 'M-2026-11-25-3', 'oc_daily_team', 6, '张伟', '2026-11-25 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (33, 'M-2026-11-25-4', 'oc_daily_team', 8, '刘洋', '2026-11-25 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (34, 'M-2026-11-25-5', 'oc_daily_team', 10, '陈静', '2026-11-25 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (35, 'M-2026-11-25-6', 'oc_daily_team', 12, '赵磊', '2026-11-25 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (36, 'M-2026-11-25-7', 'oc_daily_team', 14, '孙悦', '2026-11-25 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-25 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (37, 'M-2026-11-26-2', 'oc_daily_team', 4, '王芳', '2026-11-26 09:30:00', '已完成后端接口联调，明天继续前端。', '06ce7829583bbca3928a5852a1d5bc53771cdf1b827449f13ab6dcefa68502fe', '2026-11-26 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (38, 'M-2026-11-26-3', 'oc_daily_team', 6, '张伟', '2026-11-26 09:30:00', '帮忙 review 了日报汇总的逻辑。', '237c84658b919936c5901bb7fae1a5593f09d940e6107f9aed514ef1a8e3bbdf', '2026-11-26 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (39, 'M-2026-11-26-4', 'oc_daily_team', 8, '刘洋', '2026-11-26 09:30:00', '今天阻塞在飞书权限，先切 Mock 继续。', '55f700aa6a74ee1754c6f9c5feb0f645df1dc6d558358b29ce6fa6b794be6432', '2026-11-26 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (40, 'M-2026-11-26-5', 'oc_daily_team', 10, '陈静', '2026-11-26 09:30:00', 'MySQL 建表已完成，可以开始接真实数据。', '857b061b984ebbc91ddd38f352d357283f88438d05038346e95a5fd38976de46', '2026-11-26 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (41, 'M-2026-11-26-6', 'oc_daily_team', 12, '赵磊', '2026-11-26 09:30:00', '首页状态页已经按 unslop 重新排版。', '191938438f7011db770f314c8e6f9a81be6c0c445b13b80f1b9cc436071d128e', '2026-11-26 10:30:00');
INSERT IGNORE INTO raw_messages (id, message_id, chat_id, sender_identity_id, sender_name, sent_at, content_excerpt, content_hash, collected_at) VALUES (42, 'M-2026-11-26-7', 'oc_daily_team', 14, '孙悦', '2026-11-26 09:30:00', '提交了身份回填和分页修复，麻烦看一下。', '7b31f59eb6a2c0b24424cb7641651a8facb6fd21265fffe1681b240882389d54', '2026-11-26 10:30:00');
INSERT IGNORE INTO identity_unmatched (id, provider, external_id, external_name, source_type, source_id, resolved_member_id, resolved_at, created_at) VALUES (1, 'github', 'gh_unknown_1', 'unknown-dev', 'commit', '61121720406dbe0283bcc2dc7efbeb8bd42e3c8b', NULL, NULL, '2026-11-26 03:00:00');
INSERT IGNORE INTO identity_unmatched (id, provider, external_id, external_name, source_type, source_id, resolved_member_id, resolved_at, created_at) VALUES (2, 'feishu', 'ou_unknown_2', '外部协作者', 'task', 'T-2-1', NULL, NULL, '2026-11-26 04:00:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (1, '2026-11-24', 'personal', 'member:2', 2, 'generated', 1, '# 王芳 的个人日报（2026-11-24）

## 今日完成
- [提交] fix: 处理飞书限流重试（team/daily-report@701bb15）
- [提交] chore: 调整前端状态页间距（team/web-console@0633366）
- [任务] 完成日报模板设计（状态：done）
- [任务] 补充集成测试（状态：done）

## 协作贡献
- 群消息（已完成后端接口联调，明天继续前端。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 2, "member_name": "王芳", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (2, '2026-11-24', 'personal', 'member:3', 3, 'generated', 1, '# 张伟 的个人日报（2026-11-24）

## 今日完成
- [提交] feat: 增加团队日报汇总（team/api-gateway@525fca2）
- [提交] fix: 修正时区转换边界（team/daily-report@3eb0716）
- [任务] 整理接口契约（状态：done）
- [任务] 编写验收核对表（状态：done）

## 协作贡献
- 群消息（帮忙 review 了日报汇总的逻辑。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 3, "member_name": "张伟", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (3, '2026-11-24', 'personal', 'member:4', 4, 'generated', 1, '# 刘洋 的个人日报（2026-11-24）

## 今日完成
- [提交] feat: 实现日报模板渲染（team/web-console@e1eeebe）
- [提交] fix: 修复跨零点归属问题（team/api-gateway@3533f72）
- [任务] 完成日报模板设计（状态：done）
- [任务] 补充集成测试（状态：done）

## 协作贡献
- 群消息（今天阻塞在飞书权限，先切 Mock 继续。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 4, "member_name": "刘洋", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (4, '2026-11-24', 'personal', 'member:5', 5, 'generated', 1, '# 陈静 的个人日报（2026-11-24）

## 今日完成
- [提交] docs: 补充接口契约说明（team/daily-report@dcef309）
- [提交] refactor: 拆分采集器与推送器（team/web-console@d512b94）
- [任务] 整理接口契约（状态：done）
- [任务] 编写验收核对表（状态：done）

## 协作贡献
- 群消息（MySQL 建表已完成，可以开始接真实数据。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 5, "member_name": "陈静", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (5, '2026-11-24', 'personal', 'member:6', 6, 'generated', 1, '# 赵磊 的个人日报（2026-11-24）

## 今日完成
- [提交] test: 增加日报生成用例（team/api-gateway@105a711）
- [提交] feat: 支持成员身份绑定（team/daily-report@61b1741）
- [任务] 完成日报模板设计（状态：done）
- [任务] 补充集成测试（状态：done）

## 协作贡献
- 群消息（首页状态页已经按 unslop 重新排版。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 6, "member_name": "赵磊", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (6, '2026-11-24', 'personal', 'member:7', 7, 'generated', 1, '# 孙悦 的个人日报（2026-11-24）

## 今日完成
- [提交] fix: 处理飞书限流重试（team/web-console@acc2c39）
- [提交] chore: 调整前端状态页间距（team/api-gateway@25cc3ad）
- [任务] 整理接口契约（状态：done）
- [任务] 编写验收核对表（状态：done）

## 协作贡献
- 群消息（提交了身份回填和分页修复，麻烦看一下。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 7, "member_name": "孙悦", "commits": 2, "tasks": 2, "messages": 1, "total": 5, "no_output": false}', '2026-11-24 10:00:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (7, '2026-11-24', 'team', 'team', NULL, 'published', 1, '# 团队日报（2026-11-24）

## 团队概览
- 参与成员：6 人
- 提交数：12
- 任务数：12
- 群消息：6
- 无产出成员：0 人

## 成员摘要
- 王芳：提交 2，任务 2，消息 1
- 张伟：提交 2，任务 2，消息 1
- 刘洋：提交 2，任务 2，消息 1
- 陈静：提交 2，任务 2，消息 1
- 赵磊：提交 2，任务 2，消息 1
- 孙悦：提交 2，任务 2，消息 1

## 协作成果
- 王芳：群消息（已完成后端接口联调，明天继续前端。）
- 张伟：群消息（帮忙 review 了日报汇总的逻辑。）
- 刘洋：群消息（今天阻塞在飞书权限，先切 Mock 继续。）
- 陈静：群消息（MySQL 建表已完成，可以开始接真实数据。）
- 赵磊：群消息（首页状态页已经按 unslop 重新排版。）
- 孙悦：群消息（提交了身份回填和分页修复，麻烦看一下。）

## 风险与阻塞
- 王芳：任务阻塞：修复身份映射
- 张伟：任务阻塞：接入 MySQL 表结构
- 刘洋：任务阻塞：修复身份映射
- 陈静：任务阻塞：接入 MySQL 表结构
- 赵磊：任务阻塞：修复身份映射
- 孙悦：任务阻塞：接入 MySQL 表结构', '{"members": 6, "commits": 12, "tasks": 12, "messages": 6, "no_output": 0}', '2026-11-24 10:30:00', '2026-11-24 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (8, '2026-11-25', 'personal', 'member:2', 2, 'generated', 1, '# 王芳 的个人日报（2026-11-25）

## 今日完成
- [提交] feat: 增加团队日报汇总（team/daily-report@90e6684）
- [提交] fix: 修正时区转换边界（team/web-console@d3f3063）
- [任务] 联调飞书任务接口（状态：in_progress）

## 协作贡献
- 群消息（已完成后端接口联调，明天继续前端。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 2, "member_name": "王芳", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (9, '2026-11-25', 'personal', 'member:3', 3, 'generated', 1, '# 张伟 的个人日报（2026-11-25）

## 今日完成
- [提交] feat: 实现日报模板渲染（team/api-gateway@ed4b7ee）
- [提交] fix: 修复跨零点归属问题（team/daily-report@cf7cba9）
- [任务] 优化前端状态页（状态：in_progress）

## 协作贡献
- 群消息（帮忙 review 了日报汇总的逻辑。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 3, "member_name": "张伟", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (10, '2026-11-25', 'personal', 'member:4', 4, 'generated', 1, '# 刘洋 的个人日报（2026-11-25）

## 今日完成
- [提交] docs: 补充接口契约说明（team/web-console@653b247）
- [提交] refactor: 拆分采集器与推送器（team/api-gateway@ec0f020）
- [任务] 联调飞书任务接口（状态：in_progress）

## 协作贡献
- 群消息（今天阻塞在飞书权限，先切 Mock 继续。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 4, "member_name": "刘洋", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (11, '2026-11-25', 'personal', 'member:5', 5, 'generated', 1, '# 陈静 的个人日报（2026-11-25）

## 今日完成
- [提交] test: 增加日报生成用例（team/daily-report@c94681c）
- [提交] feat: 支持成员身份绑定（team/web-console@ac11f73）
- [任务] 优化前端状态页（状态：in_progress）

## 协作贡献
- 群消息（MySQL 建表已完成，可以开始接真实数据。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 5, "member_name": "陈静", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (12, '2026-11-25', 'personal', 'member:6', 6, 'generated', 1, '# 赵磊 的个人日报（2026-11-25）

## 今日完成
- [提交] fix: 处理飞书限流重试（team/api-gateway@aa55c42）
- [提交] chore: 调整前端状态页间距（team/daily-report@408cf27）
- [任务] 联调飞书任务接口（状态：in_progress）

## 协作贡献
- 群消息（首页状态页已经按 unslop 重新排版。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 6, "member_name": "赵磊", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (13, '2026-11-25', 'personal', 'member:7', 7, 'generated', 1, '# 孙悦 的个人日报（2026-11-25）

## 今日完成
- [提交] feat: 增加团队日报汇总（team/web-console@a14cb2d）
- [提交] fix: 修正时区转换边界（team/api-gateway@04cc6c1）
- [任务] 优化前端状态页（状态：in_progress）

## 协作贡献
- 群消息（提交了身份回填和分页修复，麻烦看一下。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 7, "member_name": "孙悦", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-25 10:00:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (14, '2026-11-25', 'team', 'team', NULL, 'published', 1, '# 团队日报（2026-11-25）

## 团队概览
- 参与成员：6 人
- 提交数：12
- 任务数：6
- 群消息：6
- 无产出成员：0 人

## 成员摘要
- 王芳：提交 2，任务 1，消息 1
- 张伟：提交 2，任务 1，消息 1
- 刘洋：提交 2，任务 1，消息 1
- 陈静：提交 2，任务 1，消息 1
- 赵磊：提交 2，任务 1，消息 1
- 孙悦：提交 2，任务 1，消息 1

## 协作成果
- 王芳：群消息（已完成后端接口联调，明天继续前端。）
- 张伟：群消息（帮忙 review 了日报汇总的逻辑。）
- 刘洋：群消息（今天阻塞在飞书权限，先切 Mock 继续。）
- 陈静：群消息（MySQL 建表已完成，可以开始接真实数据。）
- 赵磊：群消息（首页状态页已经按 unslop 重新排版。）
- 孙悦：群消息（提交了身份回填和分页修复，麻烦看一下。）

## 风险与阻塞
- 王芳：任务阻塞：修复身份映射
- 张伟：任务阻塞：接入 MySQL 表结构
- 刘洋：任务阻塞：修复身份映射
- 陈静：任务阻塞：接入 MySQL 表结构
- 赵磊：任务阻塞：修复身份映射
- 孙悦：任务阻塞：接入 MySQL 表结构', '{"members": 6, "commits": 12, "tasks": 6, "messages": 6, "no_output": 0}', '2026-11-25 10:30:00', '2026-11-25 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (15, '2026-11-26', 'personal', 'member:2', 2, 'draft', 2, '# 王芳 的个人日报（2026-11-26）

## 今日完成
- [提交] feat: 实现日报模板渲染（team/daily-report@64954ee）
- [提交] fix: 修复跨零点归属问题（team/web-console@a53588b）
- [任务] 修复身份映射（状态：blocked）

## 协作贡献
- 群消息（已完成后端接口联调，明天继续前端。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射

> 已补充：明日计划已与组长确认。', '{"member_id": 2, "member_name": "王芳", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (16, '2026-11-26', 'personal', 'member:3', 3, 'published', 1, '# 张伟 的个人日报（2026-11-26）

## 今日完成
- [提交] docs: 补充接口契约说明（team/api-gateway@2d14d0a）
- [提交] refactor: 拆分采集器与推送器（team/daily-report@dc3fa11）
- [任务] 接入 MySQL 表结构（状态：blocked）

## 协作贡献
- 群消息（帮忙 review 了日报汇总的逻辑。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 3, "member_name": "张伟", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (17, '2026-11-26', 'personal', 'member:4', 4, 'published', 1, '# 刘洋 的个人日报（2026-11-26）

## 今日完成
- [提交] test: 增加日报生成用例（team/web-console@dd72928）
- [提交] feat: 支持成员身份绑定（team/api-gateway@c6adb63）
- [任务] 修复身份映射（状态：blocked）

## 协作贡献
- 群消息（今天阻塞在飞书权限，先切 Mock 继续。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 4, "member_name": "刘洋", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (18, '2026-11-26', 'personal', 'member:5', 5, 'published', 1, '# 陈静 的个人日报（2026-11-26）

## 今日完成
- [提交] fix: 处理飞书限流重试（team/daily-report@95b415d）
- [提交] chore: 调整前端状态页间距（team/web-console@d0212f4）
- [任务] 接入 MySQL 表结构（状态：blocked）

## 协作贡献
- 群消息（MySQL 建表已完成，可以开始接真实数据。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 5, "member_name": "陈静", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (19, '2026-11-26', 'personal', 'member:6', 6, 'published', 1, '# 赵磊 的个人日报（2026-11-26）

## 今日完成
- [提交] feat: 增加团队日报汇总（team/api-gateway@a99a297）
- [提交] fix: 修正时区转换边界（team/daily-report@1b1dd7a）
- [任务] 修复身份映射（状态：blocked）

## 协作贡献
- 群消息（首页状态页已经按 unslop 重新排版。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射', '{"member_id": 6, "member_name": "赵磊", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (20, '2026-11-26', 'personal', 'member:7', 7, 'published', 1, '# 孙悦 的个人日报（2026-11-26）

## 今日完成
- [提交] feat: 实现日报模板渲染（team/web-console@36529ba）
- [提交] fix: 修复跨零点归属问题（team/api-gateway@087a0a8）
- [任务] 接入 MySQL 表结构（状态：blocked）

## 协作贡献
- 群消息（提交了身份回填和分页修复，麻烦看一下。）

## 问题与阻塞
- 暂无

## 明日计划
- 优化前端状态页
- 接入 MySQL 表结构', '{"member_id": 7, "member_name": "孙悦", "commits": 2, "tasks": 1, "messages": 1, "total": 4, "no_output": false}', '2026-11-26 10:00:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO daily_reports (id, report_date, report_type, scope_key, member_id, status, current_version, content_md, summary_json, generated_at, updated_at) VALUES (21, '2026-11-26', 'team', 'team', NULL, 'published', 1, '# 团队日报（2026-11-26）

## 团队概览
- 参与成员：6 人
- 提交数：12
- 任务数：6
- 群消息：6
- 无产出成员：0 人

## 成员摘要
- 王芳：提交 2，任务 1，消息 1
- 张伟：提交 2，任务 1，消息 1
- 刘洋：提交 2，任务 1，消息 1
- 陈静：提交 2，任务 1，消息 1
- 赵磊：提交 2，任务 1，消息 1
- 孙悦：提交 2，任务 1，消息 1

## 协作成果
- 王芳：群消息（已完成后端接口联调，明天继续前端。）
- 张伟：群消息（帮忙 review 了日报汇总的逻辑。）
- 刘洋：群消息（今天阻塞在飞书权限，先切 Mock 继续。）
- 陈静：群消息（MySQL 建表已完成，可以开始接真实数据。）
- 赵磊：群消息（首页状态页已经按 unslop 重新排版。）
- 孙悦：群消息（提交了身份回填和分页修复，麻烦看一下。）

## 风险与阻塞
- 王芳：任务阻塞：修复身份映射
- 张伟：任务阻塞：接入 MySQL 表结构
- 刘洋：任务阻塞：修复身份映射
- 陈静：任务阻塞：接入 MySQL 表结构
- 赵磊：任务阻塞：修复身份映射
- 孙悦：任务阻塞：接入 MySQL 表结构', '{"members": 6, "commits": 12, "tasks": 6, "messages": 6, "no_output": 0}', '2026-11-26 10:30:00', '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (1, 1, 'commit', 'fix: 处理飞书限流重试', 'team/daily-report@701bb15', 'commit', '701bb1529dcc7925ff56bf5fc7d0bde5185a3e3f', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (2, 1, 'commit', 'chore: 调整前端状态页间距', 'team/web-console@0633366', 'commit', '06333660e0aadb58c477744fbfa9f5a1d2f994ef', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (3, 1, 'task', '完成日报模板设计', '状态：done', 'task', 'T-2-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (4, 1, 'task', '补充集成测试', '状态：done', 'task', 'T-2-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (5, 1, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-24-2', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (6, 2, 'commit', 'feat: 增加团队日报汇总', 'team/api-gateway@525fca2', 'commit', '525fca2b5a1e0de2a611561408672dfa7af4144e', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (7, 2, 'commit', 'fix: 修正时区转换边界', 'team/daily-report@3eb0716', 'commit', '3eb07169492a779152a6d5f2988e9db78a832261', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (8, 2, 'task', '整理接口契约', '状态：done', 'task', 'T-3-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (9, 2, 'task', '编写验收核对表', '状态：done', 'task', 'T-3-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (10, 2, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-24-3', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (11, 3, 'commit', 'feat: 实现日报模板渲染', 'team/web-console@e1eeebe', 'commit', 'e1eeebec5a1217cbf069702bd00cf3514c654b2e', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (12, 3, 'commit', 'fix: 修复跨零点归属问题', 'team/api-gateway@3533f72', 'commit', '3533f72722bc16ca411ad7e4bea0363ae1b721d7', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (13, 3, 'task', '完成日报模板设计', '状态：done', 'task', 'T-4-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (14, 3, 'task', '补充集成测试', '状态：done', 'task', 'T-4-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (15, 3, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-24-4', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (16, 4, 'commit', 'docs: 补充接口契约说明', 'team/daily-report@dcef309', 'commit', 'dcef3096bb8f25b38db34ead3ce9a62de68b41c9', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (17, 4, 'commit', 'refactor: 拆分采集器与推送器', 'team/web-console@d512b94', 'commit', 'd512b94fbc7059bf74d02b3ad76bec783db026e8', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (18, 4, 'task', '整理接口契约', '状态：done', 'task', 'T-5-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (19, 4, 'task', '编写验收核对表', '状态：done', 'task', 'T-5-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (20, 4, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-24-5', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (21, 5, 'commit', 'test: 增加日报生成用例', 'team/api-gateway@105a711', 'commit', '105a71160b0c07cbd52370162ea66f6cb80ba814', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (22, 5, 'commit', 'feat: 支持成员身份绑定', 'team/daily-report@61b1741', 'commit', '61b17410e0a065e2e73d219b0c9bd0da00192ec1', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (23, 5, 'task', '完成日报模板设计', '状态：done', 'task', 'T-6-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (24, 5, 'task', '补充集成测试', '状态：done', 'task', 'T-6-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (25, 5, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-24-6', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (26, 6, 'commit', 'fix: 处理飞书限流重试', 'team/web-console@acc2c39', 'commit', 'acc2c39ce8f7497a518ea0fe3e946904395d6fcc', 'author', 0, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (27, 6, 'commit', 'chore: 调整前端状态页间距', 'team/api-gateway@25cc3ad', 'commit', '25cc3ad17e030762e0c076819bbe4d83a4d3d6e5', 'author', 1, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (28, 6, 'task', '整理接口契约', '状态：done', 'task', 'T-7-1', 'owner', 2, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (29, 6, 'task', '编写验收核对表', '状态：done', 'task', 'T-7-4', 'owner', 3, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (30, 6, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-24-7', 'participant', 4, '2026-11-24 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (31, 7, 'commit', 'fix: 处理飞书限流重试', 'team/daily-report@701bb15', 'commit', '701bb1529dcc7925ff56bf5fc7d0bde5185a3e3f', 'author', 0, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (32, 7, 'commit', 'chore: 调整前端状态页间距', 'team/web-console@0633366', 'commit', '06333660e0aadb58c477744fbfa9f5a1d2f994ef', 'author', 1, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (33, 7, 'task', '完成日报模板设计', '状态：done', 'task', 'T-2-1', 'owner', 2, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (34, 7, 'task', '补充集成测试', '状态：done', 'task', 'T-2-4', 'owner', 3, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (35, 7, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-24-2', 'participant', 4, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (36, 7, 'commit', 'feat: 增加团队日报汇总', 'team/api-gateway@525fca2', 'commit', '525fca2b5a1e0de2a611561408672dfa7af4144e', 'author', 5, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (37, 7, 'commit', 'fix: 修正时区转换边界', 'team/daily-report@3eb0716', 'commit', '3eb07169492a779152a6d5f2988e9db78a832261', 'author', 6, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (38, 7, 'task', '整理接口契约', '状态：done', 'task', 'T-3-1', 'owner', 7, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (39, 7, 'task', '编写验收核对表', '状态：done', 'task', 'T-3-4', 'owner', 8, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (40, 7, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-24-3', 'participant', 9, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (41, 7, 'commit', 'feat: 实现日报模板渲染', 'team/web-console@e1eeebe', 'commit', 'e1eeebec5a1217cbf069702bd00cf3514c654b2e', 'author', 10, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (42, 7, 'commit', 'fix: 修复跨零点归属问题', 'team/api-gateway@3533f72', 'commit', '3533f72722bc16ca411ad7e4bea0363ae1b721d7', 'author', 11, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (43, 7, 'task', '完成日报模板设计', '状态：done', 'task', 'T-4-1', 'owner', 12, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (44, 7, 'task', '补充集成测试', '状态：done', 'task', 'T-4-4', 'owner', 13, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (45, 7, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-24-4', 'participant', 14, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (46, 7, 'commit', 'docs: 补充接口契约说明', 'team/daily-report@dcef309', 'commit', 'dcef3096bb8f25b38db34ead3ce9a62de68b41c9', 'author', 15, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (47, 7, 'commit', 'refactor: 拆分采集器与推送器', 'team/web-console@d512b94', 'commit', 'd512b94fbc7059bf74d02b3ad76bec783db026e8', 'author', 16, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (48, 7, 'task', '整理接口契约', '状态：done', 'task', 'T-5-1', 'owner', 17, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (49, 7, 'task', '编写验收核对表', '状态：done', 'task', 'T-5-4', 'owner', 18, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (50, 7, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-24-5', 'participant', 19, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (51, 7, 'commit', 'test: 增加日报生成用例', 'team/api-gateway@105a711', 'commit', '105a71160b0c07cbd52370162ea66f6cb80ba814', 'author', 20, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (52, 7, 'commit', 'feat: 支持成员身份绑定', 'team/daily-report@61b1741', 'commit', '61b17410e0a065e2e73d219b0c9bd0da00192ec1', 'author', 21, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (53, 7, 'task', '完成日报模板设计', '状态：done', 'task', 'T-6-1', 'owner', 22, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (54, 7, 'task', '补充集成测试', '状态：done', 'task', 'T-6-4', 'owner', 23, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (55, 7, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-24-6', 'participant', 24, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (56, 7, 'commit', 'fix: 处理飞书限流重试', 'team/web-console@acc2c39', 'commit', 'acc2c39ce8f7497a518ea0fe3e946904395d6fcc', 'author', 25, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (57, 7, 'commit', 'chore: 调整前端状态页间距', 'team/api-gateway@25cc3ad', 'commit', '25cc3ad17e030762e0c076819bbe4d83a4d3d6e5', 'author', 26, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (58, 7, 'task', '整理接口契约', '状态：done', 'task', 'T-7-1', 'owner', 27, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (59, 7, 'task', '编写验收核对表', '状态：done', 'task', 'T-7-4', 'owner', 28, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (60, 7, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-24-7', 'participant', 29, '2026-11-24 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (61, 8, 'commit', 'feat: 增加团队日报汇总', 'team/daily-report@90e6684', 'commit', '90e66848a26dd47463a6afa9f2d8390ea35b34d6', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (62, 8, 'commit', 'fix: 修正时区转换边界', 'team/web-console@d3f3063', 'commit', 'd3f3063c08828f10f05ad9e35ad117a867cc0170', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (63, 8, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-2-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (64, 8, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-25-2', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (65, 9, 'commit', 'feat: 实现日报模板渲染', 'team/api-gateway@ed4b7ee', 'commit', 'ed4b7eee2ab5a47401830a2b5e809d9475102a2a', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (66, 9, 'commit', 'fix: 修复跨零点归属问题', 'team/daily-report@cf7cba9', 'commit', 'cf7cba9f228d7da64345b9e1da83bbe211789a5e', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (67, 9, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-3-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (68, 9, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-25-3', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (69, 10, 'commit', 'docs: 补充接口契约说明', 'team/web-console@653b247', 'commit', '653b2479704ded7229f288f58da624abdd387e52', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (70, 10, 'commit', 'refactor: 拆分采集器与推送器', 'team/api-gateway@ec0f020', 'commit', 'ec0f020e83b78cf1de5cc293e1f86c2eed2d2302', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (71, 10, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-4-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (72, 10, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-25-4', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (73, 11, 'commit', 'test: 增加日报生成用例', 'team/daily-report@c94681c', 'commit', 'c94681cca47dc36c68bedf97fbc8b48d28478b61', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (74, 11, 'commit', 'feat: 支持成员身份绑定', 'team/web-console@ac11f73', 'commit', 'ac11f739dbe425c8d56ff5fd7748ef45ed66bede', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (75, 11, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-5-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (76, 11, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-25-5', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (77, 12, 'commit', 'fix: 处理飞书限流重试', 'team/api-gateway@aa55c42', 'commit', 'aa55c4227909f4e380754bf00b798481558f0ab5', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (78, 12, 'commit', 'chore: 调整前端状态页间距', 'team/daily-report@408cf27', 'commit', '408cf27ae25013ed81aa921cf831ac2ffdb980cb', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (79, 12, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-6-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (80, 12, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-25-6', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (81, 13, 'commit', 'feat: 增加团队日报汇总', 'team/web-console@a14cb2d', 'commit', 'a14cb2db2764778d1c197eac6ea390622033acfd', 'author', 0, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (82, 13, 'commit', 'fix: 修正时区转换边界', 'team/api-gateway@04cc6c1', 'commit', '04cc6c11ef195918b6542a06d8d7d57991652368', 'author', 1, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (83, 13, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-7-2', 'owner', 2, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (84, 13, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-25-7', 'participant', 3, '2026-11-25 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (85, 14, 'commit', 'feat: 增加团队日报汇总', 'team/daily-report@90e6684', 'commit', '90e66848a26dd47463a6afa9f2d8390ea35b34d6', 'author', 0, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (86, 14, 'commit', 'fix: 修正时区转换边界', 'team/web-console@d3f3063', 'commit', 'd3f3063c08828f10f05ad9e35ad117a867cc0170', 'author', 1, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (87, 14, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-2-2', 'owner', 2, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (88, 14, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-25-2', 'participant', 3, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (89, 14, 'commit', 'feat: 实现日报模板渲染', 'team/api-gateway@ed4b7ee', 'commit', 'ed4b7eee2ab5a47401830a2b5e809d9475102a2a', 'author', 4, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (90, 14, 'commit', 'fix: 修复跨零点归属问题', 'team/daily-report@cf7cba9', 'commit', 'cf7cba9f228d7da64345b9e1da83bbe211789a5e', 'author', 5, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (91, 14, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-3-2', 'owner', 6, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (92, 14, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-25-3', 'participant', 7, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (93, 14, 'commit', 'docs: 补充接口契约说明', 'team/web-console@653b247', 'commit', '653b2479704ded7229f288f58da624abdd387e52', 'author', 8, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (94, 14, 'commit', 'refactor: 拆分采集器与推送器', 'team/api-gateway@ec0f020', 'commit', 'ec0f020e83b78cf1de5cc293e1f86c2eed2d2302', 'author', 9, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (95, 14, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-4-2', 'owner', 10, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (96, 14, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-25-4', 'participant', 11, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (97, 14, 'commit', 'test: 增加日报生成用例', 'team/daily-report@c94681c', 'commit', 'c94681cca47dc36c68bedf97fbc8b48d28478b61', 'author', 12, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (98, 14, 'commit', 'feat: 支持成员身份绑定', 'team/web-console@ac11f73', 'commit', 'ac11f739dbe425c8d56ff5fd7748ef45ed66bede', 'author', 13, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (99, 14, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-5-2', 'owner', 14, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (100, 14, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-25-5', 'participant', 15, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (101, 14, 'commit', 'fix: 处理飞书限流重试', 'team/api-gateway@aa55c42', 'commit', 'aa55c4227909f4e380754bf00b798481558f0ab5', 'author', 16, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (102, 14, 'commit', 'chore: 调整前端状态页间距', 'team/daily-report@408cf27', 'commit', '408cf27ae25013ed81aa921cf831ac2ffdb980cb', 'author', 17, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (103, 14, 'task', '联调飞书任务接口', '状态：in_progress', 'task', 'T-6-2', 'owner', 18, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (104, 14, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-25-6', 'participant', 19, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (105, 14, 'commit', 'feat: 增加团队日报汇总', 'team/web-console@a14cb2d', 'commit', 'a14cb2db2764778d1c197eac6ea390622033acfd', 'author', 20, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (106, 14, 'commit', 'fix: 修正时区转换边界', 'team/api-gateway@04cc6c1', 'commit', '04cc6c11ef195918b6542a06d8d7d57991652368', 'author', 21, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (107, 14, 'task', '优化前端状态页', '状态：in_progress', 'task', 'T-7-2', 'owner', 22, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (108, 14, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-25-7', 'participant', 23, '2026-11-25 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (109, 15, 'commit', 'feat: 实现日报模板渲染', 'team/daily-report@64954ee', 'commit', '64954eea99c82c7cae76e032103c516e6ca95f68', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (110, 15, 'commit', 'fix: 修复跨零点归属问题', 'team/web-console@a53588b', 'commit', 'a53588b856a43e10a1bcefdbf897a75ed9db55f1', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (111, 15, 'task', '修复身份映射', '状态：blocked', 'task', 'T-2-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (112, 15, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-26-2', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (113, 16, 'commit', 'docs: 补充接口契约说明', 'team/api-gateway@2d14d0a', 'commit', '2d14d0a06c8a02752b4b72454804cca8474e2e53', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (114, 16, 'commit', 'refactor: 拆分采集器与推送器', 'team/daily-report@dc3fa11', 'commit', 'dc3fa114ee4cc478081500894d7be17705fa73b5', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (115, 16, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-3-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (116, 16, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-26-3', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (117, 17, 'commit', 'test: 增加日报生成用例', 'team/web-console@dd72928', 'commit', 'dd72928cd2a110c3223e31b738305c76b4f3000a', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (118, 17, 'commit', 'feat: 支持成员身份绑定', 'team/api-gateway@c6adb63', 'commit', 'c6adb63aa9a458adf39122cda78a84e73ad6279f', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (119, 17, 'task', '修复身份映射', '状态：blocked', 'task', 'T-4-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (120, 17, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-26-4', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (121, 18, 'commit', 'fix: 处理飞书限流重试', 'team/daily-report@95b415d', 'commit', '95b415d8c68d1d1adeace6635dff32a83852277e', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (122, 18, 'commit', 'chore: 调整前端状态页间距', 'team/web-console@d0212f4', 'commit', 'd0212f42319d082bd269e11112e4f35a2cfe479a', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (123, 18, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-5-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (124, 18, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-26-5', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (125, 19, 'commit', 'feat: 增加团队日报汇总', 'team/api-gateway@a99a297', 'commit', 'a99a29734a731de64839a7248446b36fbb7643af', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (126, 19, 'commit', 'fix: 修正时区转换边界', 'team/daily-report@1b1dd7a', 'commit', '1b1dd7a7f3fb1972ae85a9b0951686b1fd6fbde6', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (127, 19, 'task', '修复身份映射', '状态：blocked', 'task', 'T-6-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (128, 19, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-26-6', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (129, 20, 'commit', 'feat: 实现日报模板渲染', 'team/web-console@36529ba', 'commit', '36529ba25f8b102818c940a4628829a29c124767', 'author', 0, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (130, 20, 'commit', 'fix: 修复跨零点归属问题', 'team/api-gateway@087a0a8', 'commit', '087a0a8c780ba1bfb4a4086402d362540e4b26d1', 'author', 1, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (131, 20, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-7-3', 'owner', 2, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (132, 20, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-26-7', 'participant', 3, '2026-11-26 10:00:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (133, 21, 'commit', 'feat: 实现日报模板渲染', 'team/daily-report@64954ee', 'commit', '64954eea99c82c7cae76e032103c516e6ca95f68', 'author', 0, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (134, 21, 'commit', 'fix: 修复跨零点归属问题', 'team/web-console@a53588b', 'commit', 'a53588b856a43e10a1bcefdbf897a75ed9db55f1', 'author', 1, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (135, 21, 'task', '修复身份映射', '状态：blocked', 'task', 'T-2-3', 'owner', 2, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (136, 21, 'message', '群消息', '已完成后端接口联调，明天继续前端。', 'message', 'M-2026-11-26-2', 'participant', 3, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (137, 21, 'commit', 'docs: 补充接口契约说明', 'team/api-gateway@2d14d0a', 'commit', '2d14d0a06c8a02752b4b72454804cca8474e2e53', 'author', 4, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (138, 21, 'commit', 'refactor: 拆分采集器与推送器', 'team/daily-report@dc3fa11', 'commit', 'dc3fa114ee4cc478081500894d7be17705fa73b5', 'author', 5, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (139, 21, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-3-3', 'owner', 6, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (140, 21, 'message', '群消息', '帮忙 review 了日报汇总的逻辑。', 'message', 'M-2026-11-26-3', 'participant', 7, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (141, 21, 'commit', 'test: 增加日报生成用例', 'team/web-console@dd72928', 'commit', 'dd72928cd2a110c3223e31b738305c76b4f3000a', 'author', 8, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (142, 21, 'commit', 'feat: 支持成员身份绑定', 'team/api-gateway@c6adb63', 'commit', 'c6adb63aa9a458adf39122cda78a84e73ad6279f', 'author', 9, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (143, 21, 'task', '修复身份映射', '状态：blocked', 'task', 'T-4-3', 'owner', 10, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (144, 21, 'message', '群消息', '今天阻塞在飞书权限，先切 Mock 继续。', 'message', 'M-2026-11-26-4', 'participant', 11, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (145, 21, 'commit', 'fix: 处理飞书限流重试', 'team/daily-report@95b415d', 'commit', '95b415d8c68d1d1adeace6635dff32a83852277e', 'author', 12, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (146, 21, 'commit', 'chore: 调整前端状态页间距', 'team/web-console@d0212f4', 'commit', 'd0212f42319d082bd269e11112e4f35a2cfe479a', 'author', 13, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (147, 21, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-5-3', 'owner', 14, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (148, 21, 'message', '群消息', 'MySQL 建表已完成，可以开始接真实数据。', 'message', 'M-2026-11-26-5', 'participant', 15, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (149, 21, 'commit', 'feat: 增加团队日报汇总', 'team/api-gateway@a99a297', 'commit', 'a99a29734a731de64839a7248446b36fbb7643af', 'author', 16, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (150, 21, 'commit', 'fix: 修正时区转换边界', 'team/daily-report@1b1dd7a', 'commit', '1b1dd7a7f3fb1972ae85a9b0951686b1fd6fbde6', 'author', 17, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (151, 21, 'task', '修复身份映射', '状态：blocked', 'task', 'T-6-3', 'owner', 18, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (152, 21, 'message', '群消息', '首页状态页已经按 unslop 重新排版。', 'message', 'M-2026-11-26-6', 'participant', 19, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (153, 21, 'commit', 'feat: 实现日报模板渲染', 'team/web-console@36529ba', 'commit', '36529ba25f8b102818c940a4628829a29c124767', 'author', 20, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (154, 21, 'commit', 'fix: 修复跨零点归属问题', 'team/api-gateway@087a0a8', 'commit', '087a0a8c780ba1bfb4a4086402d362540e4b26d1', 'author', 21, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (155, 21, 'task', '接入 MySQL 表结构', '状态：blocked', 'task', 'T-7-3', 'owner', 22, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_items (id, report_id, category, title, detail, source_type, source_id, attribution_role, sort_order, created_at) VALUES (156, 21, 'message', '群消息', '提交了身份回填和分页修复，麻烦看一下。', 'message', 'M-2026-11-26-7', 'participant', 23, '2026-11-26 10:30:00');
INSERT IGNORE INTO report_versions (id, report_id, version, content_md, editor, change_note, created_at) VALUES (1, 15, 2, '# 王芳 的个人日报（2026-11-26）

## 今日完成
- [提交] feat: 实现日报模板渲染（team/daily-report@64954ee）
- [提交] fix: 修复跨零点归属问题（team/web-console@a53588b）
- [任务] 修复身份映射（状态：blocked）

## 协作贡献
- 群消息（已完成后端接口联调，明天继续前端。）

## 问题与阻塞
- 暂无

## 明日计划
- 联调飞书任务接口
- 修复身份映射

> 已补充：明日计划已与组长确认。', 'wangfang', '补充明日计划', '2026-11-26 10:30:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (1, 7, 'email', 'team@example.com', 'success', 1, NULL, '2026-11-24 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (2, 7, 'feishu', 'oc_daily_team', 'success', 1, NULL, '2026-11-24 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (3, 7, 'console', 'stdout', 'success', 1, NULL, '2026-11-24 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (4, 14, 'email', 'team@example.com', 'success', 1, NULL, '2026-11-25 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (5, 14, 'feishu', 'oc_daily_team', 'success', 1, NULL, '2026-11-25 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (6, 14, 'console', 'stdout', 'success', 1, NULL, '2026-11-25 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (7, 14, 'email', 'team@example.com', 'failed', 3, 'SMTP timeout', '2026-11-25 10:40:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (8, 21, 'email', 'team@example.com', 'success', 1, NULL, '2026-11-26 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (9, 21, 'feishu', 'oc_daily_team', 'success', 1, NULL, '2026-11-26 10:35:00');
INSERT IGNORE INTO push_logs (id, report_id, channel, target, status, attempt, error_message, sent_at) VALUES (10, 21, 'console', 'stdout', 'success', 1, NULL, '2026-11-26 10:35:00');
INSERT IGNORE INTO source_sync_state (id, source, resource_key, last_cursor, last_synced_at, status, error_message, updated_at) VALUES (1, 'github', 'team/daily-report', 'cursor-gh-1', '2026-11-26 01:00:00', 'success', NULL, '2026-11-26 01:00:00');
INSERT IGNORE INTO source_sync_state (id, source, resource_key, last_cursor, last_synced_at, status, error_message, updated_at) VALUES (2, 'feishu_tasks', 'task-center', 'cursor-task-1', '2026-11-26 01:05:00', 'success', NULL, '2026-11-26 01:05:00');
INSERT IGNORE INTO source_sync_state (id, source, resource_key, last_cursor, last_synced_at, status, error_message, updated_at) VALUES (3, 'feishu_messages', 'oc_daily_team', 'cursor-msg-1', '2026-11-26 01:10:00', 'success', NULL, '2026-11-26 01:10:00');
COMMIT;

-- 数据量：members=8, repositories=3, commits=72, tasks=24, messages=42, reports=21, report_items=156, push_logs=10