"""
Gemini無料検索枠APIを使用した検索機能付きAIチャットボット
最新のテックニュースなど、リアルタイム情報に答えることができます
"""
import os
import json
import sys
import time
from google.genai import Client
from google.genai.errors import APIError
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig


class MiniGemini:
    """Gemini無料検索枠APIを使用した検索機能付きAIチャットボット"""
    
    def __init__(self, api_key=None, model_name=None, config_file='minigemini.json'):
        """
        MiniGeminiを初期化
        
        Args:
            api_key: Gemini APIキー（Noneの場合はminigemini.jsonから読み込み）
            model_name: 使用するモデル名（Noneの場合はminigemini.jsonから読み込み）
            config_file: 設定ファイルのパス（デフォルト: minigemini.json）
        """
        # 設定ファイルのパスをPythonファイルと同じディレクトリに設定
        if not os.path.isabs(config_file):
            # 相対パスの場合、Pythonファイルと同じディレクトリからのパスにする
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(script_dir, config_file)
        
        # デフォルト値（現在のjsonの値）
        default_api_key = "AIzaSyAkIKuvYomu9BY53iyObL0SKLy7i1D9gp4"
        default_model_name = "gemini-2.5-flash-lite"
        default_prompt_rule = "出典を含む50字以内"
        
        # minigemini.jsonから設定を読み込み
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = api_key or config.get('api_key') or default_api_key
                    self.model_name = model_name or config.get('model_name', default_model_name)
                    self.prompt_rule = config.get('prompt_rule', default_prompt_rule)
            except Exception as e:
                raise ValueError(f"設定ファイルの読み込みエラー: {e}")
        else:
            # jsonファイルがない場合は自動生成
            self.api_key = api_key or default_api_key
            self.model_name = model_name or default_model_name
            self.prompt_rule = default_prompt_rule
            
            # デフォルト値でJSONファイルを自動生成
            config = {
                "api_key": self.api_key,
                "model_name": self.model_name,
                "prompt_rule": self.prompt_rule
            }
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"警告: 設定ファイルの生成に失敗しました: {e}")
        
        if not self.api_key:
            raise ValueError("APIキーが設定されていません。minigemini.jsonに設定するか、引数で指定してください。")
        self.config_file = config_file
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Gemini APIクライアントを初期化"""
        try:
            self.client = Client(api_key=self.api_key)
        except Exception as e:
            print(f"エラー: {e}")
            raise
    
    def _check_cooldown(self):
        """クールダウンをチェックし、1分未経過の場合は残り秒数を返す（経過している場合はNone）"""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                last_used = config.get('last_used')
                if last_used:
                    elapsed = time.time() - last_used
                    if elapsed < 60:  # 1分 = 60秒
                        remaining = int(60 - elapsed) + 1  # 切り上げ
                        return remaining
        except Exception as e:
            print(f"エラー: クールダウンチェック失敗: {e}")
        return None
    
    def _update_last_used(self):
        """JSONファイルに前回の利用時刻を記録"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['last_used'] = time.time()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"エラー: 利用時刻更新失敗: {e}")
    
    def ask(self, question, temperature=0.7):
        """
        質問をして回答を得る
        
        Args:
            question: 質問内容（文字列）
            temperature: 生成の温度パラメータ（0.0-1.0、デフォルト: 0.7）
        
        Returns:
            回答テキスト（文字列）、またはNone（エラー時）
        """
        if not self.client:
            return None
        
        # クールダウンチェック
        remaining = self._check_cooldown()
        if remaining is not None:
            print(f"エラー: クールダウン中（残{remaining}秒）")
            return None
        
        # プロンプトルールを追加
        if self.prompt_rule:
            question = f"{question}\n\n{self.prompt_rule}"
        
        try:
            # 検索機能（Google Search）を有効化
            # 無料検索枠APIを使用するため、Toolオブジェクトを作成
            search_tool = Tool(google_search=GoogleSearch())
            
            # コンテンツ生成設定を作成
            config = GenerateContentConfig(
                tools=[search_tool],
                temperature=temperature
            )
            
            # コンテンツを生成
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=question,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                # 成功したら利用時刻を更新
                self._update_last_used()
                return response.text
            else:
                return None
                
        except APIError as e:
            error_str = str(e)
            error_lower = error_str.lower()
            
            # ステータスコードを確認
            status_code = None
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            elif hasattr(e, 'code'):
                status_code = e.code
            
            # 429 TooManyRequests - クォータ超過
            if status_code == 429 or '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_lower or 'too many requests' in error_lower:
                print("エラー: クォータ超過")
            # 403 Forbidden - 無効なキー
            elif status_code == 403 or \
                 (hasattr(e, 'code') and str(e.code) in ['PERMISSION_DENIED', 'UNAUTHENTICATED']) or \
                 'PERMISSION_DENIED' in error_str or 'UNAUTHENTICATED' in error_str or \
                 ('invalid api key' in error_lower) or \
                 ('api key not valid' in error_lower) or \
                 ('invalid key' in error_lower and 'api' in error_lower) or \
                 ('unauthorized' in error_lower and 'api key' in error_lower) or \
                 ('permission denied' in error_lower and ('api key' in error_lower or 'key' in error_lower)) or \
                 ('api key was reported' in error_lower) or \
                 ('leaked' in error_lower and 'api key' in error_lower) or \
                 'forbidden' in error_lower:
                print("エラー: 無効なキー")
            # 400 BadRequest - リクエストエラー
            elif status_code == 400 or '400' in error_str or 'bad request' in error_lower or 'INVALID_ARGUMENT' in error_str:
                print("エラー: リクエストエラー")
            else:
                # その他のエラーは詳細を表示
                print(f"エラー: APIエラー: {e}")
            return None
        except Exception as e:
            print(f"エラー: {e}")
            return None
    
    def chat(self, message, temperature=0.7):
        """
        チャット形式で会話する（簡易版、履歴なし）
        
        Args:
            message: メッセージ内容（文字列）
            temperature: 生成の温度パラメータ（0.0-1.0、デフォルト: 0.7）
        
        Returns:
            回答テキスト（文字列）、またはNone（エラー時）
        """
        return self.ask(message, temperature)


def main():
    """対話型メイン関数"""
    try:
        # MiniGeminiインスタンスを作成
        mini_gemini = MiniGemini()
        
        # 起動時引数でプロンプトが渡された場合
        if len(sys.argv) > 1:
            # 引数を結合してプロンプトとして使用（UTF-8）
            question = ' '.join(sys.argv[1:])
            
            # 質問を送信して回答を取得
            answer = mini_gemini.ask(question)
            
            # 回答を表示
            if answer:
                print(answer)
            
            # プログラム終了
            return
        
        # 対話ループ
        while True:
            try:
                # プロンプト入力
                question = input().strip()
                
                # 終了コマンド
                if question.lower() in ['exit', 'quit', 'q']:
                    break
                
                # 空の入力はスキップ
                if not question:
                    continue
                
                # 質問を送信して回答を取得
                answer = mini_gemini.ask(question)
                
                # 回答を表示
                if answer:
                    print(answer)
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                print(f"エラー: {e}")
                break
    
    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()
