# complete_poetry_agent.py
# الوكيل الذكي الكامل مع جميع البحور

from all_bahoor import ALL_BAHOOR
import re

class CompletePoetryAgent:
    def __init__(self):
        self.bahoor = ALL_BAHOOR
        self.results = []
    
    def analyze(self, verse):
        """
        تحليل البيت الشعري ومقارنته مع جميع البحور
        """
        # تنظيف النص
        verse = self.clean_verse(verse)
        
        # استخراج النمط الإيقاعي
        pattern = self.extract_pattern(verse)
        
        # مقارنة مع جميع البحور
        matches = self.compare_all_bahoor(pattern)
        
        # ترتيب النتائج
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # إضافة معلومات إضافية
        for match in matches:
            if match['bahr'] in self.bahoor:
                match['description'] = self.bahoor[match['bahr']]['description']
                match['examples'] = self.bahoor[match['bahr']]['examples'][:2]
        
        return {
            'verse': verse,
            'pattern': pattern,
            'total_bahoor': len(matches),
            'matches': matches,
            'best_match': matches[0] if matches else None,
            'top_3': matches[:3] if matches else []
        }
    
    def clean_verse(self, verse):
        """تنظيف البيت من علامات الترقيم والتشكيل"""
        # إزالة علامات الترقيم
        verse = re.sub(r'[،؛؟!\.\-,]', '', verse)
        # إزالة التشكيل (مؤقتًا)
        verse = re.sub(r'[ًًٌٍَُِْ]', '', verse)
        return verse
    
    def extract_pattern(self, verse):
        """
        استخراج النمط الإيقاعي من البيت
        """
        # تقسيم إلى كلمات
        words = verse.split()
        pattern = []
        
        for word in words:
            # تحليل كل كلمة
            i = 0
            while i < len(word):
                if i + 1 < len(word):
                    # نأخذ حرفين (حرف متحرك + ساكن غالبًا)
                    pattern.append(1)  # الأول متحرك
                    pattern.append(0)  # الثاني ساكن (افتراضي)
                    i += 2
                else:
                    pattern.append(1)  # الحرف الأخير متحرك
                    i += 1
        
        return pattern
    
    def compare_all_bahoor(self, pattern):
        """
        مقارنة النمط مع جميع البحور
        """
        results = []
        
        for bahr_name, bahr_info in self.bahoor.items():
            # وزن البحر
            weight = bahr_info['weight'].replace(' ', '')
            
            # تحويل وزن البحر إلى نمط رقمي
            bahr_pattern = []
            for char in weight:
                # حروف متحركة
                if char in ['م', 'ف', 'ل', 'ا', 'أ', 'إ', 'آ']:
                    bahr_pattern.append(1)
                # حروف ساكنة
                elif char in ['ع', 'ن', 'ت', 'ك']:
                    bahr_pattern.append(0)
                # حروف المد
                elif char in ['ي', 'و']:
                    bahr_pattern.append(1)
                else:
                    bahr_pattern.append(1)  # افتراضيًا متحرك
            
            # حساب نسبة التطابق
            score = self.calculate_match_score(pattern, bahr_pattern)
            
            results.append({
                'bahr': bahr_name,
                'score': round(score, 2),
                'weight': bahr_info['weight'],
                'pattern': bahr_pattern
            })
        
        return results
    
    def calculate_match_score(self, pattern1, pattern2):
        """
        حساب نسبة التطابق بين نمطين
        مع مراعاة اختلاف الأطوال
        """
        # إذا كان النمط فارغًا
        if not pattern1 or not pattern2:
            return 0
        
        # نأخذ الأطول كمرجع
        if len(pattern1) > len(pattern2):
            # نحاول مطابقة مع إزاحة
            best_score = 0
            for offset in range(len(pattern1) - len(pattern2) + 1):
                matches = sum(1 for i in range(len(pattern2)) 
                            if pattern1[offset + i] == pattern2[i])
                score = (matches / len(pattern2)) * 100
                best_score = max(best_score, score)
            return best_score
        
        elif len(pattern2) > len(pattern1):
            # نحاول مطابقة مع إزاحة
            best_score = 0
            for offset in range(len(pattern2) - len(pattern1) + 1):
                matches = sum(1 for i in range(len(pattern1)) 
                            if pattern1[i] == pattern2[offset + i])
                score = (matches / len(pattern1)) * 100
                best_score = max(best_score, score)
            return best_score
        
        else:
            # نفس الطول - تطابق مباشر
            matches = sum(1 for i in range(len(pattern1)) 
                        if pattern1[i] == pattern2[i])
            return (matches / len(pattern1)) * 100

    def format_results(self, analysis):
        """
        تنسيق النتائج للعرض
        """
        output = []
        output.append("=" * 60)
        output.append(f"📝 البيت: {analysis['verse']}")
        output.append(f"📊 النمط الإيقاعي: {analysis['pattern']}")
        output.append(f"🔍 عدد البحور المحللة: {analysis['total_bahoor']}")
        output.append("")
        output.append("🏆 أفضل 3 بحور:")
        output.append("-" * 40)
        
        for i, match in enumerate(analysis['top_3'], 1):
            output.append(f"\n{i}. {match['bahr']}")
            output.append(f"   نسبة التطابق: {match['score']}%")
            output.append(f"   الوزن: {match['weight']}")
            output.append(f"   الوصف: {match.get('description', '')}")
            if match.get('examples'):
                output.append(f"   أمثلة: {', '.join(match['examples'])}")
        
        output.append("\n" + "=" * 60)
        
        # عرض جميع النتائج (اختياري)
        output.append("\n📊 جميع النتائج مرتبة:")
        for i, match in enumerate(analysis['matches'], 1):
            output.append(f"{i:2d}. {match['bahr']:10s} - {match['score']:6.2f}%")
        
        return "\n".join(output)

# اختبار الوكيل
if __name__ == "__main__":
    agent = CompletePoetryAgent()
    
    # قائمة اختبار من كل بحر
    test_verses = [
        "قفا نبك من ذكرى حبيب ومنزل",  # بسيط
        "ألا إنما الدنيا متاع وليست",  # طويل
        "كملت مكارم الأخلاق فيك",      # كامل
        "على قدر الكرام تكون نفسي",    # وافر
        "يا حبيبي هلم إن قلبي يهيم",   # متدارك
        "سأحمي حوزة الوطن",            # هزج
        "يا غزاة الحق ثابوا للوغى",    # سريع
    ]
    
    for verse in test_verses:
        result = agent.analyze(verse)
        print(agent.format_results(result))
        print("\n")