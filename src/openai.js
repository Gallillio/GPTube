// import OpenAI from 'openai';
import { OpenAIClient } from "@azure/openai";
import { AzureKeyCredential } from "@azure/openai";


// const OpenAIClient = require("@azure/openai");
const apiKey = process.env.REACT_APP_OPENAI_API_KEY;
const apiBase = process.env.REACT_APP_OPENAI_API_BASE;
const apiDeployment = process.env.REACT_APP_OPENAI_API_DEPLOYMENT;
export async function sendMessageToOpenAI(message) {

    const client = new OpenAIClient(
        apiBase,
        new AzureKeyCredential(apiKey)
    );

    const response = await client.getChatCompletions(
        apiDeployment,
        [{ 'role': 'user', 'content': message }],
    );

    //this is the messsage on its own, remove .message.content to get the  { 'role': 'user', 'content': message }
    console.log(response.choices[0].message.content)
    return response.choices[0].message.content
}

// const openai = new OpenAI({
//     // apiKey: process.env.OPENAI_API_KEY
//     apiKey: "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",
//     dangerouslyAllowBrowser: true
// });


// export async function sendMessageToOpenAI(message) {
//     const response = await openai.chat.completions.create({
//         model: 'gpt-3.5-turbo',
//         messages: [{ 'role': 'user', 'content': message }],
//         temperature: 0.7,
//         max_tokens: 256,
//     });
//     return response.choices[0].message.content;
// }