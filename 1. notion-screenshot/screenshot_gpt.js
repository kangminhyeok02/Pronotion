const express = require('express');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const base64 = require('base64-js');
const axios = require('axios');
const bodyParser = require('body-parser');
const { exec } = require('child_process');

const app = express();
const API_KEY = 'sk-None-RBABrRpY6QTyj87O2Pb4T3BlbkFJaud6a8XmRdr9WdMmTMIk';

app.use(bodyParser.urlencoded({ extended: true }));

// 정적 파일 경로 설정
app.use('/static', express.static(path.join(__dirname, 'static')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/start', async (req, res) => {
    const startUrl = req.body.url;
    const maxScreenshots = 8;

    const visitedUrls = new Set();
    const queue = [startUrl];
    let screenshots = 0;
    const screenshotPaths = [];

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    while (queue.length > 0 && screenshots < maxScreenshots) {
        const url = queue.shift();
        if (visitedUrls.has(url)) {
            continue;
        }

        await page.goto(url, { waitUntil: 'networkidle2' });

        // 페이지 높이 계산
        const bodyHandle = await page.$('body');
        const { height } = await bodyHandle.boundingBox();
        await bodyHandle.dispose();

        // 페이지 높이를 설정
        await page.setViewport({ width: 1920, height: Math.ceil(height) });

        // 전체 페이지 스크린샷 찍기
        const screenshotPath = path.join('static', `screenshot_${screenshots + 1}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Saved screenshot: ${screenshotPath}`);
        screenshots++;
        screenshotPaths.push(screenshotPath);

        visitedUrls.add(url);

        // 내부 링크 찾기
        const links = await page.evaluate(() => {
            const anchors = [];
            const elements = document.querySelectorAll('a');

            elements.forEach(element => {
                const href = element.href;
                if (href && (href.includes('notion.site') || href.includes('notion.so')) && !anchors.includes(href)) {
                    anchors.push(href);
                }
            });

            return anchors;
        });

        for (const link of links) {
            if (!visitedUrls.has(link)) {
                queue.push(link);
            }
        }
    }

    await browser.close();

    // 이미지 인코딩
    function encodeImage(imagePath) {
        const imageBuffer = fs.readFileSync(imagePath);
        return base64.fromByteArray(imageBuffer);
    }

    const base64Images = screenshotPaths.map(encodeImage);

    const headersForVision = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${API_KEY}`
    };

    const payloadForVision = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Evaluate the Notion page content available at these images based on these criteria: Provide a score out of 20 for each criterion with a brief justification for each score."
                    },
                    {
                        "type": "text",
                        "text": "1. Page Structure and Layout.(20 points), 2. Depth and Quality of Content.(20 points), 3. Usage of Notion Features.(20 points), 4. Visual Elements (20 points), 5. Readability and Accessibility (20 points)"
                    },
                    {
                        "type": "text",
                        "text": "Please do the final output format as follows. You must follow formats strictly. Give at least 14 points for (2. Depth and quality of the content) Eg) 1. Criteria (17/20): Reason \n 2. Criteria (16/20): Reason \n 3. Criteria (18/20): Reason \n 4. Criteria (14/20): Reason \n 5. Criteria (15/20): Reason \n Total score: [17,16,18,14,15] \n Key Areas of Interest: Computer Science"
                    },
                    {
                        "type": "text",
                        "text": "Each Reason should be just one sentence. And the Key Areas of Interest should be one, either. (Eg: Artificial intelligence)"
                    },
                    ...base64Images.map(img => ({
                        "type": "image_url",
                        "image_url": { "url": `data:image/png;base64,${img}`, "detail": "high" }
                    }))
                ]
            }
        ],
        "max_tokens": 1000
    };

    async function gptVision() {
        try {
            const response = await axios.post('https://api.openai.com/v1/chat/completions', payloadForVision, { headers: headersForVision });
            if (response.status !== 200) {
                throw new Error(`API request failed with status code ${response.status}: ${response.data}`);
            }

            const gptVisionAnswer = response.data;

            if (!gptVisionAnswer.choices) {
                throw new Error(`'choices' key not found in the API response: ${JSON.stringify(gptVisionAnswer)}`);
            }

            const gptVisionAnswers = gptVisionAnswer.choices.map(choice => choice.message.content.split('\n').map(item => item.trim()));

            // 결과를 JSON 파일로 저장
            fs.writeFileSync('gpt_vision_result.json', JSON.stringify(gptVisionAnswers, null, 2));
            
            return gptVisionAnswers;
        } catch (error) {
            console.error(`An error occurred: ${error.message}`);
            return null;
        }
    }

    // GPT 평가 결과를 JSON 파일로 저장하고, Python 스크립트를 실행하여 추가 작업 수행
    const gptVisionAnswers = await gptVision();
    console.log(gptVisionAnswers);

    // 통합 Python 스크립트 실행
    exec('python3 process_results.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            res.send(`<h1>Error during process_results.py execution</h1><pre>${error.message}</pre>`);
            return;
        }
        console.log(`stdout: ${stdout}`);
        if (stderr) {
            console.error(`stderr: ${stderr}`);
        }

        res.send(`
            <h1>GPT 평가 결과</h1>
            <pre>${stdout}</pre>
            ${stderr ? `<h2>stderr:</h2><pre>${stderr}</pre>` : ''}
            <img src="/static/output_image.jpeg" alt="Generated Image">
        `);
    });
});

// /report 경로 추가
app.get('/report', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'report.html'));
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
