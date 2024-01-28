from openai import OpenAI
import openai
import os

# OpenAIのAPIキーを設定する
# 環境変数に「OPENAI_API_KEY」があるか、envなどの実行環境に設定されているかを確認してください

# Create an instance of OpenAI
client = OpenAI()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("現在の作業ディレクトリ: ", os.getcwd())

# ファイルを参照させたい場合はここで先にファイルをアップロードする
file = client.files.create(file=open("./file.txt", "rb"), purpose='assistants')

# assistantの作成
assistant = client.beta.assistants.create(
    name="数学チューター",
    instructions="数学の個人家庭教師です。数学の質問に答えるためにコードを書いて実行してください。",
    tools=[
        {
            "type": "code_interpreter"},
        {
            "type": "function",
            "function": {
            "name": "getCurrentWeather",
            "description": "Get the weather in location",
            "parameters": {
                "type": "object",
                "properties": {
                "location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"},
                "unit": {"type": "string", "enum": ["c", "f"]}
                },
                "required": ["location"]
            }
            }
        }, {
            "type": "function",
            "function": {
            "name": "getNickname",
            "description": "Get the nickname of a city",
            "parameters": {
                "type": "object",
                "properties": {
                "location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"},
                },
                "required": ["location"]
            }
            } 
        }
    ],
    model="gpt-4-turbo-preview",
    file_ids=[file.id]  # ファイルを参照させたい場合はここで指定する
    
)

# スレッドの作成
thread = client.beta.threads.create()

# スレッドにメッセージを追加
content = input("質問を入力してください：")
# ex: 方程式 `3x + 11 = 14` を解く必要があります。手伝ってもらえますか？
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=content
)

print(message)

# assistantを実行 => 引き同期になる
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="ユーザーをジェーン・ドウとして対応してください。ユーザーはプレミアムアカウントを持っています。"
)

# 実行結果を表示
run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)
import time

# runのstatusが"completed"になるまで待機
while run.status != "completed":
    #statusが"requires_action"の場合は、actionを実行する
    if run.status == "requires_action":
        #required_action内のtypeがsubmit_tool_outputsの場合
        call_ids = []
        if run.required_action.type == "submit_tool_outputs":
            #submit_tool_outputsから、tool_calls配列を取り出し、idを列挙する
            call_ids = [call.id for call in run.required_action.submit_tool_outputs.tool_calls]

        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[
            {
                "tool_call_id": call_ids[0],
                "output": "東京",
            },
            ]

        )


    time.sleep(1)  # 1秒ごとにstatusをチェック
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

### ここからFunctionCallingの埋め込み

###

# 応答を表示
messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

# メッセージは古い物から順番に入っているので、逆順にする
messages.data.reverse()

# 最後に見つかったuserのメッセージを開始点として、それより後のメッセージを表示
last_user_message_index = None

print("============================================")
# 最後のユーザーメッセージのインデックスを見つける
for i, message in enumerate(messages.data):
    if message.role == "user":
        last_user_message_index = i

# 最後のユーザーメッセージ以降のメッセージを表示
# 最後のユーザーメッセージは除外する
if last_user_message_index is not None:
    for message in messages.data[last_user_message_index+1:]:
        print(f"{message.role.title()}: {message.content}")





    

