import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analyze import FIELDS, detect, load_events

ROOT = Path(__file__).resolve().parents[1]


def event(number, seconds, event_id='4625', **changes):
    stamp = datetime(2026, 1, 15, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    row = dict(zip(FIELDS, ['true', str(number), stamp.isoformat().replace('+00:00', 'Z'),
                           event_id, 'LAB-FS01', 'LAB', 'user01', '192.0.2.10', '3']))
    row.update(changes)
    row['time'] = stamp
    return row


def sequence(offsets=(0, 60, 120, 180, 240), success=300):
    return [event(i, t) for i, t in enumerate(offsets)] + [event('S', success, '4624')]


class DetectionTests(unittest.TestCase):
    def test_positive_evidence_and_unsorted_input(self):
        alerts = detect(list(reversed(sequence())))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['failure_record_ids'], ['0','1','2','3','4'])
        self.assertEqual(alerts[0]['success_record_id'], 'S')

    def test_below_threshold(self):
        self.assertEqual(detect(sequence((0,60,120,180))), [])

    def test_inclusive_both_time_boundaries(self):
        self.assertEqual(len(detect(sequence((0,60,120,180,300), 600))), 1)

    def test_failure_span_one_second_too_long(self):
        self.assertEqual(detect(sequence((0,60,120,180,301), 400)), [])

    def test_success_one_second_too_late(self):
        self.assertEqual(detect(sequence(success=541)), [])

    def test_same_timestamp_is_not_followed_by(self):
        self.assertEqual(detect(sequence((0,0,0,0,0), 0)), [])

    def test_success_before_failures(self):
        self.assertEqual(detect(sequence(success=-1)), [])

    def test_no_success_no_alert(self):
        self.assertEqual(detect(sequence()[:-1]), [])

    def test_each_identity_component_is_required(self):
        for field, value in [('target_user','other'), ('target_domain','OTHER'),
                             ('computer','LAB-FS02'), ('source_ip','192.0.2.11'),
                             ('logon_type','10')]:
            with self.subTest(field=field):
                rows = sequence()
                rows[-1][field] = value
                self.assertEqual(detect(rows), [])

    def test_case_insensitive_names(self):
        rows = sequence()
        rows[-1].update(computer='lab-fs01', target_domain='lab', target_user='USER01')
        self.assertEqual(len(detect(rows)), 1)

    def test_missing_ip_and_other_logon_type_excluded(self):
        for field, value in [('source_ip','-'), ('logon_type','2')]:
            rows = sequence()
            for row in rows:
                row[field] = value
            self.assertEqual(detect(rows), [])

    def test_success_resets_failure_history(self):
        rows = sequence() + [event('S2', 310, '4624')]
        self.assertEqual(len(detect(rows)), 1)
        rows = sequence()
        rows.append(event('intermediate', 150, '4624'))
        self.assertEqual(detect(rows), [])

    def test_tied_failure_not_reused_after_success(self):
        rows = [event('A',0,'4624')] + [event('Z'+str(i),0) for i in range(5)]
        rows.append(event('next', 60, '4624'))
        self.assertEqual(detect(rows), [])

    def test_repository_fixture_and_golden_output(self):
        events = load_events(ROOT/'data/authentication.csv')
        actual = {'event_count':len(events), 'alerts':detect(events)}
        expected = json.loads((ROOT/'reports/expected-alerts.json').read_text())
        self.assertEqual(actual, expected)
        self.assertEqual([a['success_record_id'] for a in actual['alerts']], ['P06','A06','E06'])
        self.assertEqual(actual['event_count'], 32)


class InputTests(unittest.TestCase):
    def write_csv(self, directory, rows, fields=FIELDS):
        path=Path(directory)/'input.csv'
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer=csv.DictWriter(handle,fieldnames=fields,extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_valid_csv_and_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path=self.write_csv(directory, sequence())
            path.write_text('\ufeff'+path.read_text(), encoding='utf-8')
            self.assertEqual(len(detect(load_events(path))),1)

    def test_rejects_invalid_values(self):
        for field, value in [('synthetic','false'),('timestamp','2026-01-15T00:00:00'),
                             ('timestamp','nonsenseZ'),('source_ip','not-an-ip'),
                             ('event_id','9999'),('logon_type','99'),
                             ('target_domain',''),('target_user',' user'),('record_id','')]:
            with self.subTest(field=field,value=value), tempfile.TemporaryDirectory() as directory:
                rows=sequence()
                rows[0][field]=value
                with self.assertRaises(ValueError):
                    load_events(self.write_csv(directory,rows))

    def test_duplicate_record_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            rows=sequence()
            rows.append(rows[0])
            with self.assertRaises(ValueError):
                load_events(self.write_csv(directory,rows))

    def test_empty_and_wrong_header_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            for rows, fields in [([],FIELDS), (sequence(),FIELDS[:-1])]:
                with self.assertRaises(ValueError):
                    load_events(self.write_csv(directory,rows,fields))

    def test_bad_column_count_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=self.write_csv(directory,sequence())
            with path.open('a') as handle:
                handle.write('true,short\n')
            with self.assertRaisesRegex(ValueError, 'column count'):
                load_events(path)

    def test_cli_success(self):
        result=subprocess.run([sys.executable,str(ROOT/'analyze.py'),str(ROOT/'data/authentication.csv')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(len(json.loads(result.stdout)['alerts']),3)

    def test_cli_missing_file_is_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result=subprocess.run([sys.executable,str(ROOT/'analyze.py'),str(Path(directory)/'missing.csv')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Error:',result.stderr)
        self.assertNotIn('Traceback',result.stderr)


if __name__ == '__main__':
    unittest.main()
