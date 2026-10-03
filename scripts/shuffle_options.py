"""
scripts/shuffle_options.py
確定性選項洗牌協議 (Deterministic Option Shuffling & Balancing Protocol)
用於消除 LLM 在生成四選一選擇題時的天生位置偏誤 (Position Bias)。
"""

import random
from typing import List, Dict, Tuple

def shuffle_question_options(
    question_text: str,
    options: Dict[str, str],
    correct_key: str
) -> Tuple[Dict[str, str], str]:
    """
    對單一題目的選項進行隨機洗牌，並計算洗牌後的新正解代碼。
    
    :param question_text: 題幹文字
    :param options: 原始選項字典，例如 {'A': '...', 'B': '...', 'C': '...', 'D': '...'}
    :param correct_key: 原始正確答案代碼，例如 'A'
    :return: (洗牌後選項字典, 洗牌後正確代碼)
    """
    items = list(options.items())
    correct_content = options[correct_key]
    
    # 隨機打亂
    random.shuffle(items)
    
    letters = ['A', 'B', 'C', 'D']
    new_options = {}
    new_correct_key = ''
    
    for i, (_, content) in enumerate(items):
        target_letter = letters[i]
        new_options[target_letter] = content
        if content == correct_content:
            new_correct_key = target_letter
            
    return new_options, new_correct_key

def balance_quiz_options(questions: List[Dict], max_attempts: int = 1000) -> List[Dict]:
    """
    對全卷題目進行多次洗牌嘗試，直到正解完全符合均勻分佈且無連續 3 題相同選項。
    
    分佈規範：
    - 10 題：A, B, C, D 各佔 2~3 題
    - 40 題：各佔 10 題
    - 50 題：各佔 12~13 題
    - 硬性防重複：全卷禁止連續 3 題相同選項
    """
    total = len(questions)
    
    for _ in range(max_attempts):
        shuffled_quiz = []
        answer_keys = []
        
        for q in questions:
            shuffled_opts, new_ans = shuffle_question_options(
                q['stem'], q['options'], q['correct_answer']
            )
            shuffled_quiz.append({
                'id': q.get('id', len(shuffled_quiz) + 1),
                'stem': q['stem'],
                'options': shuffled_opts,
                'correct_answer': new_ans,
                'explanation': q.get('explanation', '')
            })
            answer_keys.append(new_ans)
            
        # 1. 檢查是否有連續 3 題相同選項
        has_three_in_a_row = False
        for i in range(len(answer_keys) - 2):
            if answer_keys[i] == answer_keys[i+1] == answer_keys[i+2]:
                has_three_in_a_row = True
                break
        if has_three_in_a_row:
            continue
            
        # 2. 檢查均勻分佈
        counts = {k: answer_keys.count(k) for k in ['A', 'B', 'C', 'D']}
        
        if total == 10:
            if all(2 <= counts[k] <= 3 for k in ['A', 'B', 'C', 'D']):
                return shuffled_quiz
        elif total == 40:
            if all(counts[k] == 10 for k in ['A', 'B', 'C', 'D']):
                return shuffled_quiz
        elif total == 50:
            if all(12 <= counts[k] <= 13 for k in ['A', 'B', 'C', 'D']):
                return shuffled_quiz
        else:
            # 一般題數：容許最大與最小出現次數差 <= 1
            if max(counts.values()) - min(counts.values()) <= 1:
                return shuffled_quiz
                
    raise ValueError(f"無法在 {max_attempts} 次嘗試內達成均勻分佈與防重複條件，請確認題目數量。")

if __name__ == '__main__':
    # 測試示範
    sample_questions = [
        {
            'stem': f'第 {i+1} 題題幹範例',
            'options': {'A': '選項一', 'B': '選項二', 'C': '選項三', 'D': '選項四'},
            'correct_answer': 'A'
        }
        for i in range(10)
    ]
    balanced = balance_quiz_options(sample_questions)
    print("洗牌完成！全卷正解順序：", [q['correct_answer'] for q in balanced])
