from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
import json
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# ============================================================
# 模試マスターデータ
# ============================================================
EXAMS = {
    "共通テスト本番":              date(2026, 1, 17),
    "全統記述模試①(河合)":        date(2025, 6, 8),
    "全統共通テスト模試①(河合)":  date(2025, 6, 22),
    "全統記述模試②(河合)":        date(2025, 8, 24),
    "全統共通テスト模試②(河合)":  date(2025, 9, 28),
    "全統記述模試③(河合)":        date(2025, 10, 19),
    "全統共通テスト模試③(河合)":  date(2025, 11, 23),
    "駿台全国模試①":              date(2025, 6, 15),
    "駿台全国模試②":              date(2025, 8, 31),
    "駿台全国模試③":              date(2025, 11, 2),
    "駿台共通テスト模試①":        date(2025, 9, 7),
    "駿台共通テスト模試②":        date(2025, 11, 30),
    "東大オープン(河合)":          date(2025, 11, 3),
    "東大実戦(駿台)":              date(2025, 11, 9),
    "京大オープン(河合)":          date(2025, 11, 3),
    "京大実戦(駿台)":              date(2025, 11, 9),
    "阪大オープン(河合)":          date(2025, 11, 3),
    "阪大実戦(駿台)":              date(2025, 11, 9),
    "東北大オープン(河合)":        date(2025, 11, 3),
    "名大オープン(河合)":          date(2025, 11, 3),
    "九大オープン(河合)":          date(2025, 11, 3),
    "北大オープン(河合)":          date(2025, 11, 3),
    "一橋大オープン(河合)":        date(2025, 11, 3),
    "東工大オープン(河合)":        date(2025, 11, 3),
    "東工大実戦(駿台)":            date(2025, 11, 9),
    "医学部実戦模試(駿台)":        date(2025, 10, 5),
    "医進模試(河合)":              date(2025, 10, 12),
    "東京大学 前期":               date(2026, 2, 25),
    "京都大学 前期":               date(2026, 2, 25),
    "大阪大学 前期":               date(2026, 2, 25),
    "東北大学 前期":               date(2026, 2, 25),
    "名古屋大学 前期":             date(2026, 2, 25),
    "九州大学 前期":               date(2026, 2, 25),
    "北海道大学 前期":             date(2026, 2, 25),
    "一橋大学 前期":               date(2026, 2, 25),
    "東京工業大学 前期":           date(2026, 2, 25),
    "慶應義塾大学 入試":           date(2026, 2, 12),
    "早稲田大学 入試":             date(2026, 2, 15),
    "上智大学 入試":               date(2026, 2, 6),
    "明治大学 入試":               date(2026, 2, 5),
    "青山学院大学 入試":           date(2026, 2, 8),
    "立教大学 入試":               date(2026, 2, 7),
    "中央大学 入試":               date(2026, 2, 9),
    "法政大学 入試":               date(2026, 2, 10),
    "同志社大学 入試":             date(2026, 2, 6),
    "立命館大学 入試":             date(2026, 2, 3),
    "関西大学 入試":               date(2026, 2, 1),
    "関西学院大学 入試":           date(2026, 2, 2),
}

# ============================================================
# 志望校ごとのスケジュール
# ============================================================
SCHOOL_SCHEDULES = {
    "東京大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)", "駿台全国模試①",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)", "駿台全国模試②",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "東大オープン(河合)", "東大実戦(駿台)",
        "駿台全国模試③", "駿台共通テスト模試②",
        "共通テスト本番", "東京大学 前期",
    ],
    "京都大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)", "駿台全国模試①",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)", "駿台全国模試②",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "京大オープン(河合)", "京大実戦(駿台)",
        "駿台共通テスト模試②", "共通テスト本番", "京都大学 前期",
    ],
    "大阪大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)", "駿台全国模試①",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "阪大オープン(河合)", "阪大実戦(駿台)",
        "共通テスト本番", "大阪大学 前期",
    ],
    "東北大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "東北大オープン(河合)", "共通テスト本番", "東北大学 前期",
    ],
    "名古屋大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "名大オープン(河合)", "共通テスト本番", "名古屋大学 前期",
    ],
    "九州大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "九大オープン(河合)", "共通テスト本番", "九州大学 前期",
    ],
    "北海道大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "北大オープン(河合)", "共通テスト本番", "北海道大学 前期",
    ],
    "一橋大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "一橋大オープン(河合)", "共通テスト本番", "一橋大学 前期",
    ],
    "東京工業大学": [
        "全統記述模試①(河合)", "駿台全国模試①",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)", "駿台全国模試②",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "東工大オープン(河合)", "東工大実戦(駿台)",
        "共通テスト本番", "東京工業大学 前期",
    ],
    "医学部(国立)": [
        "全統記述模試①(河合)", "駿台全国模試①",
        "全統記述模試②(河合)", "駿台全国模試②",
        "医進模試(河合)", "医学部実戦模試(駿台)",
        "全統記述模試③(河合)", "駿台全国模試③",
        "共通テスト本番",
    ],
    "早稲田大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "駿台共通テスト模試②", "共通テスト本番", "早稲田大学 入試",
    ],
    "慶應義塾大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統記述模試③(河合)", "全統共通テスト模試③(河合)",
        "共通テスト本番", "慶應義塾大学 入試",
    ],
    "上智大学": [
        "全統記述模試①(河合)", "全統共通テスト模試①(河合)",
        "全統記述模試②(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "上智大学 入試",
    ],
    "明治大学": [
        "全統共通テスト模試①(河合)", "全統記述模試②(河合)",
        "全統共通テスト模試②(河合)", "全統共通テスト模試③(河合)",
        "共通テスト本番", "明治大学 入試",
    ],
    "青山学院大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "青山学院大学 入試",
    ],
    "立教大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "立教大学 入試",
    ],
    "中央大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "中央大学 入試",
    ],
    "法政大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "法政大学 入試",
    ],
    "同志社大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "同志社大学 入試",
    ],
    "立命館大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "立命館大学 入試",
    ],
    "関西大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "関西大学 入試",
    ],
    "関西学院大学": [
        "全統共通テスト模試①(河合)", "全統共通テスト模試②(河合)",
        "全統共通テスト模試③(河合)", "共通テスト本番", "関西学院大学 入試",
    ],
}

SCHOOL_ALIASES = {
    "東大": "東京大学", "京大": "京都大学", "阪大": "大阪大学",
    "東北大": "東北大学", "名大": "名古屋大学", "九大": "九州大学",
    "北大": "北海道大学", "一橋": "一橋大学", "東工大": "東京工業大学",
    "医学部": "医学部(国立)", "医学部国立": "医学部(国立)",
    "早稲田": "早稲田大学", "早大": "早稲田大学",
    "慶應": "慶應義塾大学", "慶大": "慶應義塾大学",
    "上智": "上智大学", "明治": "明治大学", "青学": "青山学院大学",
    "立教": "立教大学", "中央": "中央大学", "法政": "法政大学",
    "同志社": "同志社大学", "立命館": "立命館大学",
    "関大": "関西大学", "関学": "関西学院大学",
}

EXAM_KEYS = {
    "東京大学 前期", "京都大学 前期", "大阪大学 前期",
    "東北大学 前期", "名古屋大学 前期", "九州大学 前期",
    "北海道大学 前期", "一橋大学 前期", "東京工業大学 前期",
    "慶應義塾大学 入試", "早稲田大学 入試", "上智大学 入試",
    "明治大学 入試", "青山学院大学 入試", "立教大学 入試",
    "中央大学 入試", "法政大学 入試", "同志社大学 入試",
    "立命館大学 入試", "関西大学 入試", "関西学院大学 入試",
}
KYOTSU_KEY = "共通テスト本番"

# ============================================================
# データの保存・読み込み
# ============================================================
DATA_FILE = "user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("user_school", {}), data.get("user_state", {})
    return {}, {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_school": user_school, "user_state": user_state},
                  f, ensure_ascii=False, indent=2)

# 起動時に読み込む
user_school, user_state = load_data()

# ============================================================
# スケジュール・通知
# ============================================================
def get_schedule_text(school_name):
    keys = SCHOOL_SCHEDULES.get(school_name, [])
    today = date.today()
    lines = [f"📋 {school_name} のスケジュール\n"]
    for key in keys:
        d = EXAMS[key]
        days_left = (d - today).days
        if days_left > 0:
            lines.append(f"📌 {key}\n　{d}（あと {days_left} 日）\n")
        elif days_left == 0:
            lines.append(f"🔥 {key}\n　今日！\n")
        else:
            lines.append(f"✅ {key}\n　{d}（終了）\n")
    return "\n".join(lines)


def build_notification(user_id):
    school = user_school.get(user_id)
    if not school:
        return None
    today = date.today()
    keys = SCHOOL_SCHEDULES.get(school, [])
    next_mock = None
    next_mock_days = None
    kyotsu_days = None
    exam_days = None

    for key in keys:
        d = EXAMS[key]
        days_left = (d - today).days
        if days_left < 0:
            continue
        if key == KYOTSU_KEY:
            kyotsu_days = days_left
        elif key in EXAM_KEYS:
            exam_days = days_left
        else:
            if next_mock_days is None or days_left < next_mock_days:
                next_mock = key
                next_mock_days = days_left

    lines = [f"☀️ {today} の受験カウントダウン\n志望校：{school}\n"]
    lines.append(f"📝 次の模試\n　{next_mock}\n　あと {next_mock_days} 日\n" if next_mock
                 else "📝 次の模試\n　予定なし\n")
    lines.append(f"📖 共通テスト本番\n　あと {kyotsu_days} 日\n" if kyotsu_days is not None
                 else "📖 共通テスト\n　終了 ✅\n")
    lines.append(f"🏫 {school} 入試\n　あと {exam_days} 日\n" if exam_days is not None
                 else f"🏫 {school} 入試\n　終了 ✅\n")
    lines.append("💪 今日も全力で頑張ろう！")
    return "\n".join(lines)


def send_daily_notifications():
    for user_id in list(user_school.keys()):
        message = build_notification(user_id)
        if message:
            line_bot_api.push_message(user_id, TextSendMessage(text=message))


scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
scheduler.add_job(send_daily_notifications, 'cron', hour=12, minute=0)
scheduler.start()

# ============================================================
# メッセージハンドラ
# ============================================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text == "志望校設定":
        user_state[user_id] = "waiting_school"
        save_data()
        school_list = "\n".join(f"・{s}" for s in SCHOOL_SCHEDULES.keys())
        reply = f"志望校を入力してください🏫\n（略称もOK: 東大、京大、早稲田など）\n\n{school_list}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if user_state.get(user_id) == "waiting_school":
        school_name = SCHOOL_ALIASES.get(text, text)
        if school_name in SCHOOL_SCHEDULES:
            user_school[user_id] = school_name
            user_state[user_id] = None
            save_data()
            reply = f"✅ 志望校を「{school_name}」に設定しました！\n\n"
            reply += get_schedule_text(school_name)
        else:
            reply = f"「{text}」は未登録です😥\n「志望校設定」と送り直してください。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text == "カレンダー":
        school = user_school.get(user_id)
        reply = get_schedule_text(school) if school else "まず「志望校設定」と送って登録してください！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text == "今日の確認":
        reply = build_notification(user_id) or "まず「志望校設定」と送って登録してください！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    handler.handle(body, signature)
    return "OK"

if __name__ == "__main__":
    app.run(port=5000)
