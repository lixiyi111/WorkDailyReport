"""控制台推送：用于本地演示与测试，不依赖外部服务。"""

from app.services.pushers.base import PushResult


class ConsolePusher:
    channel = "console"

    async def push(self, subject: str, content: str, target: str) -> PushResult:
        print(f"\n===== [{self.channel}] {subject} → {target} =====\n{content}\n")
        return PushResult(channel=self.channel, target=target, success=True)
