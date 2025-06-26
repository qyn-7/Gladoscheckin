import requests
import json
import os

def send_telegram(title, context):
    bot_token = os.environ.get("TG_BOT_TOKEN", "")
    chat_id = os.environ.get("TG_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("❌ TG_BOT_TOKEN 或 TG_CHAT_ID 未设置，跳过 Telegram 推送")
        return

    message = f"*{title}*\n\n{context}"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
        print("Telegram 推送返回：", resp.json())
    except Exception as e:
        print("Telegram 推送失败：", e)

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # 推送内容
    title = ""
    success, fail, repeats = 0, 0, 0
    context = ""

    cookies = os.environ.get("COOKIES", "").split("&")
    if cookies[0] != "":

        check_in_url = "https://glados.space/api/user/checkin"
        status_url = "https://glados.space/api/user/status"

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {'token': 'glados.one'}

        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={
                'cookie': cookie,
                'referer': referer,
                'origin': origin,
                'user-agent': useragent,
                'content-type': 'application/json;charset=UTF-8'
            }, data=json.dumps(payload))

            state = requests.get(status_url, headers={
                'cookie': cookie,
                'referer': referer,
                'origin': origin,
                'user-agent': useragent
            })

            message_status = ""
            points = 0
            message_days = ""

            if checkin.status_code == 200:
                result = checkin.json()
                check_result = result.get('message')
                points = result.get('points')

                result = state.json()
                leftdays = int(float(result['data']['leftDays']))
                email = result['data']['email']

                print(check_result)
                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + str(points)
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                message_days = f"{leftdays} 天" if leftdays else "error"
            else:
                email = ""
                message_status = "签到请求失败，请检查..."
                message_days = "error"

            context += f"账号: {email}, P: {points}, 剩余: {message_days}, 状态: {message_status}\n"

        title = f'Glados 签到: ✅{success} ❌{fail} 🔁{repeats}'
        print("Send Content:\n", context)
    else:
        title = '❗ 未找到 cookies!'
        context = '请检查 COOKIES 环境变量是否配置正确。'

    send_telegram(title, context)
