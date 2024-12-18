import asyncio
from typing import cast

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.contents import AuthorRole, ChatHistory, FunctionResultContent

from app.plugins.SafeCodeInterpreterPlugin.native_function import CodeInterpreterPlugin
from app.utils.config import configs

react_prompt: str = """
あなたはユーザーをサポートする AI Agent であり、指示された内容に基づきローカルのフォルダやファイルの確認、変更を行う事ができます。
ユーザーの指示に従って作業を進めなさい。

あなたは数回この処理を繰り返すことができる為、一度の作業ですべての要件を満たす必要はありません。
""".strip()


async def main(instructions: str) -> None:
    kernel = Kernel()
    chat_history = ChatHistory()
    chat_history.add_user_message(instructions)

    print("-" * 50)
    print(f"{chat_history.messages[-1].role}\n\n{chat_history.messages[-1].content}")

    service_id: str = "default"

    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            api_key=configs.AZURE_OPENAI_COMPLETION_API_KEY,
            deployment_name=configs.AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME,
            endpoint=configs.AZURE_OPENAI_COMPLETION_ENDPOINT,
            api_version=configs.AZURE_OPENAI_COMPLETION_API_VERSION,
        )
    )

    # 今回 function calling するプラグインを登録します
    kernel.add_plugin(CodeInterpreterPlugin("/Users/you/repos/github/yuichiromukaiyama/agent-study-content/exmaple"), "code_interpreter")
    service = cast(AzureChatCompletion, kernel.get_service(service_id=service_id, type=AzureChatCompletion))

    # 2回 function calling を実行します。
    for _ in range(2):
        settings = cast(
            AzureChatPromptExecutionSettings,
            kernel.get_prompt_execution_settings_from_service_id(service_id=service_id),
        )
        # SK の Auto Function Calling を有効化します
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True)

        # ReAct する為の Prompt を挿入します
        chat_history.add_system_message(react_prompt)

        # tool_call 履歴を出力する為に最新の位置を記録します
        last_message_height: int = len(chat_history.messages) - 1

        # 推論実行
        completion = await service.get_chat_message_contents(chat_history, settings, kernel=kernel)

        # tool call の実行履歴を出力します
        tool_msgs = [m for m in chat_history.messages[last_message_height:] if m.role == AuthorRole.TOOL]
        tool_results = [i for t in tool_msgs for i in t.items if isinstance(i, FunctionResultContent)]

        for result in tool_results:
            print("-" * 50)
            print(f"AuthorRole.TOOL\n\n{result.plugin_name}-{result.function_name} {result.result}")

        chat_history.add_message(completion[0])

        print("-" * 50)
        print(f"{chat_history.messages[-1].role}\n\n{chat_history.messages[-1].content}")


asyncio.run(
    main(
        """
現在のフォルダに README.md を作成しなさい。作成するプログラムは AI Agent の入門スクリプト集です。
作成ができたら最初のスクリプトを main.py として書きなさい。
""".strip()
    )
)
