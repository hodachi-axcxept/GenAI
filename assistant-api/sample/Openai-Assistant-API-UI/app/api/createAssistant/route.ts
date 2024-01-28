/**
 * API Route - Create Assistant
 *
 * This route handles the creation of a new OpenAI assistant. It accepts POST requests
 * with necessary data such as assistant name, model, description, and an optional file ID.
 * This data is used to configure and create an assistant via the OpenAI API. The route
 * returns the ID of the newly created assistant, allowing for further operations involving
 * this assistant. It's designed to provide a seamless process for setting up customized
 * OpenAI assistants as per user requirements.
 *
 * Path: /api/createAssistant
 */
import { NextRequest, NextResponse } from 'next/server'
import { OpenAI } from 'openai';

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });



  export async function POST(req: NextRequest) {
    debugger;
    if (req.method === 'POST') {
        try {
            // リクエストから必要な情報を取得します
            const { assistantName, assistantModel, assistantDescription, fileId } = await req.json();

            console.log("入っている")
            // 必要な情報が不足している場合はエラーをスローします
            if (!assistantName || !assistantModel || !assistantDescription) {
                throw new Error('必要なアシスタントのパラメータが不足しています');
            }

            // アシスタントのオプションを設定します
            const assistantOptions: any = {
                name: assistantName,
                instructions: assistantDescription,
                model: assistantModel,
                tools: [{ "type": "retrieval" }],
            };
            // ファイルIDが存在する場合は、それをオプションに追加します
            if (fileId) {
                assistantOptions.file_ids = [fileId];
            }

            // OpenAI APIを使用して新しいアシスタントを作成します
            const assistant = await openai.beta.assistants.create(assistantOptions);
            const assistantId = assistant.id;

            // アシスタントの作成が成功したことと、そのIDをレスポンスとして返します
            return NextResponse.json({ 
                message: 'アシスタントが正常に作成されました', 
                assistantId: assistantId 
            });
        } catch (error) {
            if (error instanceof Error) {
                console.error('Error:', error);
                return NextResponse.json({ error: error.message });
            } else {
                console.error('Unknown error:', error);
                return NextResponse.json({ error: 'An unknown error occurred' });
            }
        }
    } else {
        return NextResponse.json({ error: 'Method Not Allowed' });
    }
};