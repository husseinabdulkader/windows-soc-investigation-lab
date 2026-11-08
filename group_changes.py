"""Classify synthetic local Administrators additions against approval records."""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sys

ADMIN_SID = 'S-1-5-32-544'
EVENT_FIELDS = {'synthetic', 'record_id', 'timestamp', 'event_id', 'computer',
                'actor_sid', 'actor_name', 'member_sid', 'member_name',
                'group_sid', 'group_name'}
APPROVAL_FIELDS = {'synthetic', 'approval_id', 'computer', 'actor_sid', 'member_sid',
                   'group_sid', 'status', 'approved_at', 'valid_from', 'valid_until'}
MATCH_FIELDS = ('computer', 'actor_sid', 'member_sid', 'group_sid')


def timestamp(value):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise ValueError('timestamps must use YYYY-MM-DDTHH:MM:SSZ')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def validate(rows, kind):
    fields = EVENT_FIELDS if kind == 'events' else APPROVAL_FIELDS
    id_field = 'record_id' if kind == 'events' else 'approval_id'
    if not isinstance(rows, list):
        raise ValueError(f'{kind} must be a JSON array')
    seen = set()
    for index, row in enumerate(rows, 1):
        try:
            if not isinstance(row, dict) or set(row) != fields:
                raise ValueError('fields must exactly match the documented schema')
            if row['synthetic'] is not True:
                raise ValueError('only explicitly synthetic records are accepted')
            for name, value in row.items():
                if name != 'synthetic' and (not isinstance(value, str) or not value or value != value.strip()):
                    raise ValueError(f'{name} must be a nonempty trimmed string')
            if row[id_field] == '-' or row[id_field] in seen:
                raise ValueError('record identifiers must be unique and nonmissing')
            seen.add(row[id_field])
            for name in ('actor_sid', 'member_sid', 'group_sid'):
                value = row[name]
                if value == '-' and kind == 'events':
                    continue
                if not re.fullmatch(r'S-1-(?:0|[1-9]\d*)(?:-(?:0|[1-9]\d*)){1,15}', value):
                    raise ValueError(f'{name} must be SID-shaped text')
                parts = value.split('-')
                if int(parts[2]) >= 2**48 or any(int(p) >= 2**32 for p in parts[3:]):
                    raise ValueError('SID numeric component out of range')
            if kind == 'events':
                timestamp(row['timestamp'])
                if row['event_id'] not in {'4732', '4733', '4728', '4756'}:
                    raise ValueError('unsupported event_id')
            else:
                if row['computer'] == '-':
                    raise ValueError('approval computer cannot be missing')
                if row['status'] not in {'approved', 'revoked', 'rejected'}:
                    raise ValueError('invalid approval status')
                issued, start, end = [timestamp(row[f]) for f in ('approved_at', 'valid_from', 'valid_until')]
                if start > end:
                    raise ValueError('approval interval is reversed')
        except ValueError as exc:
            raise ValueError(f'{kind} row {index}: {exc}') from exc
    return rows


def load_records(path, kind):
    return validate(json.loads(Path(path).read_text(encoding='utf-8-sig')), kind)


def analyze(events, approvals):
    validate(events, 'events')
    validate(approvals, 'approvals')
    results = []
    for event in sorted(events, key=lambda e: (e['timestamp'], e['record_id'])):
        matches = []
        if event['event_id'] != '4732':
            disposition, reason = 'out_of_scope', 'event_is_not_local_group_addition'
        elif event['group_sid'] == '-':
            disposition, reason = 'insufficient_evidence', 'missing_group_sid'
        elif event['group_sid'] != ADMIN_SID:
            disposition, reason = 'out_of_scope', 'group_is_not_builtin_administrators'
        elif any(event[f] == '-' for f in MATCH_FIELDS):
            disposition, reason = 'insufficient_evidence', 'missing_correlation_identity'
        else:
            when = timestamp(event['timestamp'])
            matches = sorted(a['approval_id'] for a in approvals
                             if all(a[f].casefold() == event[f].casefold() for f in MATCH_FIELDS)
                             and a['status'] == 'approved'
                             and timestamp(a['approved_at']) <= when
                             and timestamp(a['valid_from']) <= when <= timestamp(a['valid_until']))
            if len(matches) == 1:
                disposition, reason = 'expected_change', 'matching_approval'
            elif len(matches) > 1:
                disposition, reason = 'review_required', 'ambiguous_approvals'
            else:
                disposition, reason = 'unexplained_change', 'no_matching_approval'
        results.append({'rule': 'GROUP-001', 'synthetic': True, 'record_id': event['record_id'],
                        'timestamp': event['timestamp'], 'computer': event['computer'],
                        'actor_sid': event['actor_sid'], 'actor_name': event['actor_name'],
                        'member_sid': event['member_sid'], 'member_name': event['member_name'],
                        'group_sid': event['group_sid'], 'group_name': event['group_name'],
                        'disposition': disposition, 'reason': reason, 'approval_ids': matches})
    return {'event_count': len(events), 'approval_count': len(approvals),
            'counts': dict(sorted(Counter(r['disposition'] for r in results).items())),
            'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('events', type=Path)
    parser.add_argument('approvals', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    try:
        events = load_records(args.events, 'events')
        approvals = load_records(args.approvals, 'approvals')
        result = analyze(events, approvals)
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2
    if args.validate_only:
        print(f'Validated {len(events)} synthetic events and {len(approvals)} synthetic approvals.')
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
