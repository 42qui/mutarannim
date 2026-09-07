# complete_poetry_agent.py
# الوكيل المحلي (fallback) لتحليل البحر الشعري تقريبيًا بدون تشكيل.
#
# ملاحظة مهمة: هذا تحليل تقريبي محلي فقط (بدون تشكيل حقيقي للنص)، وليس
# تحليلاً عروضيًا دقيقًا. المرجع الأدق في المشروع هو نموذج الذكاء الاصطناعي
# عبر analyze.js / api/analyze — هذا الملف يُستخدم فقط كـ fallback سريع لما
# ما يكون في اتصال بالنموذج، بنفس الفكرة المطبّقة بالضبط بالواجهة الأمامية
# (poet-and-machine.html) حتى تكون النتائج متسقة بين الطرفين.

import re
from all_bahoor import ALL_BAHOOR

LONG_VOWELS = {'ا', 'و', 'ي'}


class CompletePoetryAgent:
    def __init__(self):
        self.bahoor = ALL_BAHOOR

    def clean_verse(self, verse):
        """إزالة علامات الترقيم والتشكيل من البيت."""
        verse = re.sub(r'[،؛؟!.\-,]', '', verse)
        verse = re.sub(r'[\u064B-\u0652]', '', verse)  # التشكيل
        verse = re.sub(r'[^\u0600-\u06FF\s]', '', verse)  # إبقاء الحروف العربية فقط
        return verse.strip()

    def extract_pattern(self, verse):
        """
        استخراج نمط تقريبي (متحرك=1 / ساكن=0) من نص غير مُشكّل:
        أي حرف مدّ طويل (ا و ي) يأتي بعد حرف ساكن سابق يُعتبر امتدادًا
        ساكنًا لما قبله (يشكّلان مقطعًا طويلاً)، وما عدا ذلك متحرك.
        هذا تخمين تقريبي وليس تحليلاً عروضيًا حقيقيًا يعتمد التشكيل.
        """
        words = verse.split()
        pattern = []
        for word in words:
            prev_was_letter = False
            for ch in word:
                if ch in LONG_VOWELS and prev_was_letter:
                    pattern.append(0)
                    prev_was_letter = False
                else:
                    pattern.append(1)
                    prev_was_letter = True
        return pattern

    def calculate_match_score(self, pattern, ref_pattern):
        """
        نسبة تطابق النمط مع مرجع البحر، بتجربة كل الإزاحات الممكنة
        (لأن البيت نادرًا ما يبدأ بالضبط من أول تفعيلة بالمرجع).
        """
        if not pattern or not ref_pattern:
            return 0.0

        best = 0.0
        ref_len = len(ref_pattern)
        for offset in range(ref_len):
            tiled = [ref_pattern[(i + offset) % ref_len] for i in range(len(pattern))]
            matches = sum(1 for a, b in zip(pattern, tiled) if a == b)
            score = (matches / len(pattern)) * 100
            best = max(best, score)
        return best

    def compare_all_bahoor(self, pattern):
        results = []
        for bahr_name, bahr_info in self.bahoor.items():
            ref_pattern = bahr_info['pattern']
            score = self.calculate_match_score(pattern, ref_pattern)
            results.append({
                'bahr': bahr_name,
                'score': round(score, 2),
                'weight': bahr_info['weight'],
                'description': bahr_info.get('description', ''),
                'examples': bahr_info.get('verses', [])[:2],
            })
        return results

    def analyze(self, verse):
        """تحليل تقريبي محلي لبيت شعري ومقارنته بكل البحور الـ16."""
        cleaned = self.clean_verse(verse)
        pattern = self.extract_pattern(cleaned)
        matches = self.compare_all_bahoor(pattern)
        matches.sort(key=lambda x: x['score'], reverse=True)

        return {
            'verse': cleaned,
            'pattern': pattern,
            'total_bahoor': len(matches),
            'matches': matches,
            'best_match': matches[0] if matches else None,
            'top_3': matches[:3] if matches else [],
            'disclaimer': 'هذا تخمين محلي تقريبي بدون تشكيل، وليس تحليلاً عروضيًا نهائيًا.',
        }

    def format_results(self, analysis):
        output = []
        output.append("=" * 60)
        output.append(f"📝 البيت: {analysis['verse']}")
        output.append(f"📊 النمط التقريبي: {''.join(map(str, analysis['pattern']))}")
        output.append(f"🔍 عدد البحور المقارَنة: {analysis['total_bahoor']}")
        output.append(f"⚠️  {analysis['disclaimer']}")
        output.append("")
        output.append("🏆 أقرب 3 بحور:")
        output.append("-" * 40)

        for i, match in enumerate(analysis['top_3'], 1):
            output.append(f"\n{i}. {match['bahr']}")
            output.append(f"   نسبة التقارب: {match['score']}%")
            output.append(f"   الوزن: {match['weight']}")
            output.append(f"   الوصف: {match.get('description', '')}")
            if match.get('examples'):
                output.append(f"   أمثلة: {', '.join(match['examples'])}")

        output.append("\n" + "=" * 60)
        output.append("\n📊 كل النتائج مرتبة:")
        for i, match in enumerate(analysis['matches'], 1):
            output.append(f"{i:2d}. {match['bahr']:10s} - {match['score']:6.2f}%")

        return "\n".join(output)


if __name__ == "__main__":
    agent = CompletePoetryAgent()

    test_verses = [
        "قفا نبك من ذكرى حبيب ومنزل",   # بسيط
        "ألا إنما الدنيا متاع وليست",    # طويل
        "كملت مكارم الأخلاق فيك",        # كامل
        "على قدر الكرام تكون نفسي",      # وافر
        "يا حبيبي هلم إن قلبي يهيم",     # متدارك
        "سأحمي حوزة الوطن",              # هزج
        "يا غزاة الحق ثابوا للوغى",      # سريع
    ]

    for verse in test_verses:
        result = agent.analyze(verse)
        print(agent.format_results(result))
        print("\n")
