// functions/api/send-to-telegram.js
//
// Cloudflare Pages Function.
// Принимает данные формы с сайта и пересылает их в Telegram через Bot API.
// Токен бота и chat_id берутся из переменных окружения (Settings → Environment variables
// в панели Cloudflare Pages), а не хранятся в коде страницы — так они не видны
// в исходном коде сайта и не попадают в публичный репозиторий на GitHub.

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    const data = await request.json();
    const { name, contact, format, request: userRequest } = data;

    if (!name || !contact) {
      return new Response(
        JSON.stringify({ error: "Заполните имя и контакт" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    let text = `<b>🔔 Новая заявка!</b>\n`;
    text += `<b>Имя:</b> ${escapeHtml(name)}\n`;
    text += `<b>Контакт:</b> ${escapeHtml(contact)}\n`;
    text += `<b>Формат:</b> ${escapeHtml(format || "Не указан")}\n`;
    text += `<b>Проблема:</b> ${escapeHtml(userRequest || "Не заполнено")}`;

    const tgResponse = await fetch(
      `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          parse_mode: "html",
          text,
        }),
      }
    );

    if (!tgResponse.ok) {
      const errText = await tgResponse.text();
      console.error("Telegram API error:", errText);
      throw new Error("Telegram API error");
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("send-to-telegram error:", err);
    return new Response(JSON.stringify({ error: "Ошибка сервера" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

// Экранируем спецсимволы HTML, чтобы данные из формы (например, если кто-то
// введёт "<b>" или "<script>") не ломали разметку сообщения в Telegram
// и не могли повлиять на его отображение.
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
