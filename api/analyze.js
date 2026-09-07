
// api/analyze.js
// نقطة API الإنتاجية: تستقبل بيتًا شعريًا وتُرجع تحليل الوزن/المعنى/المشاعر
// من نموذج Google Gemini (الحصة المجانية) عبر Generative Language API.
 
// يقرأ جسم الطلب بأمان بغض النظر إذا Vercel حلّله تلقائيًا لـ JSON
// أو تركه كنص خام — بعض الإعدادات لا تُحلّل الجسم تلقائيًا.
async function readJsonBody(req) {
  if (req.body && typeof req.body === 'object') {
    return req.body;
  }
  if (typeof req.body === 'string' && req.body.trim()) {
    try {
      return JSON.parse(req.body);
    } catch (e) {
      return {};
    }
  }
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (chunk) => { data += chunk; });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        resolve({});
      }
    });
    req.on('error', () => resolve({}));
  });
}
 
const SYSTEM_PROMPT =
  'أنت خبير عروض وشعر عربي. حلل البيت المُعطى وأرجع النتيجة كـJSON صِرف فقط، ' +
  'بدون أي نص أو علامات markdown حوله، بالضبط بهذا الشكل: ' +
  '{"meter":"اسم البحر الأقرب","meaning":"شرح موجز للمعنى بجملة أو جملتين",' +
  '"emotion":"المشاعر الأساسية بكلمة أو كلمتين",' +
  '"suggestion":"تعديل واحد مقترح يحافظ على فكرة البيت إن وجد خلل بالوزن، وإلا null"}';
 
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'الطريقة غير مسموحة' });
  }
 
  const body = await readJsonBody(req);
  const { verse } = body || {};
  if (!verse || typeof verse !== 'string' || !verse.trim()) {
    return res.status(400).json({ error: 'لازم ترسل بيتاً شعرياً' });
  }
 
  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: 'مفتاح الـ API غير مضبوط على السيرفر' });
  }
 
  try {
    const upstream = await fetch(
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' +
        process.env.GEMINI_API_KEY,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: verse }] }],
          systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
          generationConfig: {
            responseMimeType: 'application/json',
            temperature: 0.4,
            maxOutputTokens: 500,
          },
        }),
      }
    );
 
    const data = await upstream.json();
 
    if (!upstream.ok) {
      return res.status(upstream.status).json({ error: 'رفض النموذج الطلب', detail: data });
    }
 
    const text =
      (data.candidates &&
        data.candidates[0] &&
        data.candidates[0].content &&
        data.candidates[0].content.parts &&
        data.candidates[0].content.parts.map((p) => p.text || '').join('')) ||
      '';
    const cleaned = text.replace(/```json|```/g, '').trim();
 
    let parsed;
    try {
      parsed = JSON.parse(cleaned);
    } catch (e) {
      parsed = { meter: null, meaning: text, emotion: null, suggestion: null };
    }
 
    return res.status(200).json(parsed);
  } catch (err) {
    return res.status(500).json({ error: 'تعذّر الاتصال بالنموذج' });
  }
}
 
