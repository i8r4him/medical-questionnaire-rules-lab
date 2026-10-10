import argparse
import json
from pathlib import Path
import sys

from .engine import DEFAULT_RULES, load_rules, review


def main():
    parser = argparse.ArgumentParser(description='Synthetische Gesundheitsfragebögen regelbasiert prüfen.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--rules', type=Path, default=DEFAULT_RULES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output and args.output.resolve() in (args.input.resolve(), args.rules.resolve()):
            raise ValueError('Ausgabe darf Eingabe oder Regelbasis nicht überschreiben.')
        result = review(json.loads(args.input.read_text(encoding='utf-8')), load_rules(args.rules))
        text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding='utf-8')
        print(text, end='')
    except (ValueError, OSError) as error:
        print(f'Ungültige Eingabe: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
