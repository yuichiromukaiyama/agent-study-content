import os
import subprocess
from typing import Annotated, Self

from semantic_kernel.functions import kernel_function


class CodeInterpreterPlugin:
    def __init__(self, allow_dir: str) -> None:
        self.__allow_dir: str = allow_dir

    @kernel_function(description="指定されたパスへフォルダを作成")
    async def mkdir(self: Self, folder_path: Annotated[str, "フォルダの相対パス"]) -> str:
        try:
            os.makedirs(name=os.path.join(self.__allow_dir, folder_path), exist_ok=False)
            return "書き込みに成功しました"
        except Exception as err:
            return f"書き込みに失敗しました: {str(err)}"

    @kernel_function(description="指定されたパスへテキストファイルを作成")
    async def create_file(self: Self, file_path: Annotated[str, "ファイルの相対パス"], text: Annotated[str, "書き込むテキスト"]) -> str:
        """Open を用いてファイルを書き込みます"""
        try:
            # subprocess.run で結果をキャプチャし、文字列として返却
            with open(file=os.path.join(self.__allow_dir, file_path), mode="w") as f:
                f.write(text)
            return "書き込みに成功しました"
        except Exception as err:
            return f"書き込みに失敗しました: {str(err)}"

    @kernel_function(description="/bin/sh ls -l を実行します")
    async def exec_list(self: Self) -> str:
        """ローカルのシェルを用いて ls コマンドを実行"""
        try:
            # subprocess.run で結果をキャプチャし、文字列として返却
            result = subprocess.run(args=["/bin/ls", "-l"], cwd=self.__allow_dir, check=True, capture_output=True, text=True)
            return result.stdout
        except Exception as err:
            return f"失敗しました: {str(err)}"
