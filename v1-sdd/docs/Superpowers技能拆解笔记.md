# Superpowers 技能拆解笔记（brainstorming）

我拆的是 `brainstorming`。触发描述写得很强硬：任何新建功能、组件、修改行为或做新计划前都必须先加载。正文步骤是：先判断已知信息是否足够；不足就一次问一个开放问题，让用户自己描述；理解后先摆出 2–3 个方案并说明取舍；再写 design doc（小改动写短版，项目写完整版）；用户批准后才允许实现，最后调用 `superpowers:writing-plans`，中间有明确的 HARD-GATE。

配套文件分工清楚：`builder-check-prompt.md` 用于让子代理预审设计文档，`visual-companion.md` 说明可视化伴侣，`scripts/` 下的 `server.cjs`、`start-server.sh`、`stop-server.sh`、`helper.js`、`frame-template.html` 负责起一个本地浏览器标签页展示 mockup。

SKILL.md 只保留触发、步骤和边界，细节放到 references 与 scripts 按需加载，这正是 5.1.1 说的渐进披露。第 3 周我会用它先澄清需求，再交给 writing-plans。
