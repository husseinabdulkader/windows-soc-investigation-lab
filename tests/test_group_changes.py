from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from group_changes import analyze, load_records, validate

ROOT = Path(__file__).resolve().parents[1]


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.events = load_records(ROOT/'data/group-events.json', 'events')
        self.approvals = load_records(ROOT/'data/group-approvals.json', 'approvals')

    def disposition(self, event, approvals=None):
        return analyze([event], self.approvals if approvals is None else approvals)['results'][0]

    def test_fixture_classification_and_evidence(self):
        result = analyze(self.events, self.approvals)
        self.assertEqual(result['counts'], {'expected_change':3, 'unexplained_change':3,
                                          'insufficient_evidence':1, 'out_of_scope':1})
        actual = {r['record_id']:r['disposition'] for r in result['results']}
        self.assertEqual(actual, {'G01':'unexplained_change','G02':'expected_change',
                                 'G03':'out_of_scope','G04':'expected_change',
                                 'G05':'expected_change','G06':'unexplained_change',
                                 'G07':'insufficient_evidence','G08':'unexplained_change'})
        approved = next(r for r in result['results'] if r['record_id']=='G02')
        self.assertEqual(approved['approval_ids'], ['CHG-001'])
        self.assertEqual(approved['member_sid'], self.events[1]['member_sid'])

    def test_exact_boundaries_and_one_second_outside(self):
        event = deepcopy(self.events[1])
        for time, expected in [('09:59:59','unexplained_change'),('10:00:00','expected_change'),
                               ('10:30:00','expected_change'),('10:30:01','unexplained_change')]:
            with self.subTest(time=time):
                event['timestamp'] = '2026-01-16T'+time+'Z'
                self.assertEqual(self.disposition(event)['disposition'],expected)

    def test_every_approval_key_must_match(self):
        for field, value in [('computer','LAB-PC02'),('actor_sid','S-1-5-21-111-222-333-2000'),
                             ('member_sid','S-1-5-21-111-222-333-2000'),('group_sid','S-1-5-32-545')]:
            with self.subTest(field=field):
                approvals = deepcopy(self.approvals)
                approvals[0][field] = value
                self.assertEqual(self.disposition(self.events[1], approvals)['disposition'],'unexplained_change')

    def test_display_names_do_not_authorize_or_select_group(self):
        event = deepcopy(self.events[1])
        event.update(actor_name='-', member_name='-',group_name='Administratoren',computer='lab-pc01')
        self.assertEqual(self.disposition(event)['disposition'],'expected_change')
        event['group_sid']='S-1-5-32-545'
        event['group_name']='Administrators'
        self.assertEqual(self.disposition(event)['disposition'],'out_of_scope')

    def test_non_addition_and_other_group_scopes_excluded(self):
        event = deepcopy(self.events[1])
        for event_id in ['4733','4728','4756']:
            with self.subTest(event_id=event_id):
                event['event_id']=event_id
                self.assertEqual(self.disposition(event)['disposition'],'out_of_scope')

    def test_missing_identity_never_matches_approval(self):
        for field in ['computer','actor_sid','member_sid','group_sid']:
            with self.subTest(field=field):
                event=deepcopy(self.events[1])
                event[field]='-'
                self.assertEqual(self.disposition(event)['disposition'],'insufficient_evidence')

    def test_empty_approval_list_and_empty_events(self):
        self.assertEqual(self.disposition(self.events[1],[])['disposition'],'unexplained_change')
        self.assertEqual(analyze([],[])['results'],[])

    def test_revoked_rejected_and_retrospective_approvals(self):
        for field,value in [('status','revoked'),('status','rejected'),('approved_at','2026-01-16T10:05:01Z')]:
            with self.subTest(field=field,value=value):
                approvals=deepcopy(self.approvals)
                approvals[0][field]=value
                self.assertEqual(self.disposition(self.events[1],approvals)['disposition'],'unexplained_change')

    def test_approval_issued_exactly_at_event_is_included(self):
        approvals=deepcopy(self.approvals)
        approvals[0]['approved_at']=self.events[1]['timestamp']
        self.assertEqual(self.disposition(self.events[1],approvals)['disposition'],'expected_change')

    def test_overlapping_approvals_require_review(self):
        approvals=deepcopy(self.approvals)
        extra=deepcopy(approvals[0])
        extra['approval_id']='CHG-003'
        approvals.append(extra)
        result=self.disposition(self.events[1],approvals)
        self.assertEqual(result['disposition'],'review_required')
        self.assertEqual(result['approval_ids'],['CHG-001','CHG-003'])

    def test_order_does_not_change_results(self):
        self.assertEqual(analyze(self.events,self.approvals),analyze(self.events[::-1],self.approvals[::-1]))

    def test_duplicate_identifiers_rejected(self):
        for rows,kind in [(self.events,'events'),(self.approvals,'approvals')]:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate(rows+[deepcopy(rows[0])],kind)

    def test_bad_inputs_rejected(self):
        for field,value in [('synthetic',False),('synthetic','true'),('event_id',4732),
                             ('event_id','9999'),('timestamp','2026-02-30T10:00:00Z'),
                             ('timestamp','2026-01-16T10:00:00'),('actor_sid','invalid'),
                             ('member_sid','S-1-5-4294967296'),('computer',' LAB-PC01')]:
            with self.subTest(field=field,value=value):
                event=deepcopy(self.events[0])
                event[field]=value
                with self.assertRaises(ValueError):
                    analyze([event],self.approvals)
        for rows in [{},[{}],[{'synthetic':True}],['invalid']]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                validate(rows,'events')

    def test_invalid_approval_is_not_treated_as_absent(self):
        for field,value in [('valid_until','2026-01-16T09:00:00Z'),('status','pending'),
                             ('member_sid','-'),('computer','-')]:
            with self.subTest(field=field):
                approvals=deepcopy(self.approvals)
                approvals[0][field]=value
                with self.assertRaises(ValueError):
                    analyze(self.events,approvals)

    def test_cli_and_malformed_file(self):
        command=[sys.executable,str(ROOT/'group_changes.py'),str(ROOT/'data/group-events.json'),str(ROOT/'data/group-approvals.json')]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(json.loads(result.stdout)['event_count'],8)
        with tempfile.TemporaryDirectory() as directory:
            invalid=Path(directory)/'invalid.json'
            invalid.write_text('{')
            command[-1]=str(invalid)
            result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Error:',result.stderr)
        self.assertEqual(result.stdout,'')


if __name__=='__main__':
    unittest.main()
