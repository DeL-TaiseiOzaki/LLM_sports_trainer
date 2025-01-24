import json
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from agents.base import BaseAgent

class GoalSettingAgent(BaseAgent):
    """
    選手の情報と対話内容から、バッティング改善の大枠の目標を設定するエージェント。
    """

    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts.json")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def run(
        self,
        persona: Dict[str, Any],
        policy: Dict[str, Any],
        conversation_insights: List[Any]
    ) -> Dict[str, Any]:
        """
        ペルソナ情報、指導方針、対話内容から目標を設定。
        """
        try:
            prompt = self.prompts["goals_prompt"].format(
                persona=json.dumps(persona, ensure_ascii=False),
                policy=json.dumps(policy, ensure_ascii=False),
                insights=json.dumps(conversation_insights, ensure_ascii=False)
            )
            response = await self.llm.ainvoke(prompt)
            
            try:
                goal_data = json.loads(response.content)
            except json.JSONDecodeError:
                goal_data = {
                    "main_goal": "基本スイングの習得と安定化",
                    "focus_points": ["フォームの基礎固め", "バットコントロール向上"],
                    "timeframe": "3ヶ月"
                }

            return {
                "goals": goal_data
            }

        except Exception as e:
            self.logger.log_error_details(error=e, agent=self.agent_name)
            return {}