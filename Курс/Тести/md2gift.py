#!/usr/bin/env python3
"""Конвертує тести з Markdown у формат Moodle GIFT.

Формат вхідного файлу:
    # Назва тесту
    ### 1. Текст питання
    - [ ] неправильний варіант
    - [x] правильний варіант

Якщо правильних варіантів кілька, питання стає множинним вибором
з рівномірним розподілом балів і -100% за кожну хибну відповідь.

Запуск:  python3 md2gift.py            -> створює Тести_GIFT.txt
"""
import glob
import os
import re

SPECIAL = '~=#{}:\\'


def esc(text):
    """Екранує спецсимволи GIFT."""
    return ''.join('\\' + c if c in SPECIAL else c for c in text)


def parse(path):
    """Повертає (назва_тесту, [(питання, [(текст, правильний)])])."""
    title, questions = os.path.basename(path), []
    current = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('### '):
                current = (re.sub(r'^\d+\.\s*', '', line[4:].strip()), [])
                questions.append(current)
            elif line.startswith('- [') and current is not None:
                correct = line[3].lower() == 'x'
                current[1].append((line[6:].strip(), correct))
    return title, questions


def to_gift(title, questions):
    out = ['$CATEGORY: $course$/%s' % title, '']
    for num, (text, options) in enumerate(questions, 1):
        right = [o for o in options if o[1]]
        wrong = [o for o in options if not o[1]]
        if not right:
            raise ValueError('%s, питання %d: немає правильної відповіді' % (title, num))
        out.append('::%s п.%d::%s {' % (esc(title), num, esc(text)))
        if len(right) == 1:
            out.append('    =%s' % esc(right[0][0]))
            out.extend('    ~%s' % esc(o[0]) for o in wrong)
        else:
            share = round(100 / len(right), 5)
            out.extend('    ~%%%s%%%s' % (share, esc(o[0])) for o in right)
            out.extend('    ~%%-100%%%s' % esc(o[0]) for o in wrong)
        out.extend(['}', ''])
    return '\n'.join(out)


def main():
    files = sorted(glob.glob('Тест_*.md'))
    if not files:
        raise SystemExit('Не знайдено жодного файлу Тест_*.md')
    blocks, total = [], 0
    for path in files:
        title, questions = parse(path)
        total += len(questions)
        blocks.append(to_gift(title, questions))
        print('%-12s %2d питань' % (os.path.basename(path), len(questions)))
    with open('Тести_GIFT.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(blocks))
    print('-' * 26)
    print('Разом: %d питань -> Тести_GIFT.txt' % total)


if __name__ == '__main__':
    main()
