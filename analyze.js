export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'الطريقة غير مسموحة' });
  }

  const { verse } = req.body || {};
  if (!verse || typeof verse !== 'string' || !verse.trim()) {
    return res.status(400).json({ error: 'لازم ترسل بيتاً شعرياً' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'مفتاح الـ API غير مضبوط على السيرفر' });
  }

  try {
    const upstream = await fetch('https://petite-signs-type.loca.lt/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        text: yourInputText,
        system:
          'أنت خبير عروض وشعر عربي. حلل البيت المُعطى وأرجع النتيجة كـJSON صِرف فقط، بدون أي نص أو علامات markdown حوله، بالضبط بهذا الشكل: {"meter":"اسم البحر الأقرب","meaning":"شرح موجز للمعنى بجملة أو جملتين","emotion":"المشاعر الأساسية بكلمة أو كلمتين","suggestion":"تعديل واحد مقترح يحافظ على فكرة البيت إن وجد خلل بالوزن، وإلا null"}',
        messages: [{ role: 'user', content: verse }]
      })
    });

    const data = await upstream.json();

    if (!upstream.ok) {
      return res.status(upstream.status).json({ error: 'رفض النموذج الطلب', detail: data });
    }

    const text = (data.content || []).map(b => b.text || '').join('');
    const cleaned = text.replace(/```json|```/g, '').trim();

    let parsed;
    try {
      parsed = JSON.parse(cleaned);
    } catch (e) {
      parsed = { meter: null, meaning: text, emotion: null, suggestion: null };
    }

    res.status(200).json(parsed);
  } catch (err) {
    res.status(500).json({ error: 'تعذّر الاتصال بالنموذج' });
  }
}
