import contextlib
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hermes_reader as r

URL='https://hermes-agent.nousresearch.com/docs/getting-started/installation'
PAGE='# Installation\n\n## Quick Install\n\nDesktop packages include supported dependencies.\n\n## Prerequisites\n\nChoose the correct platform and configure a working model provider.\n'
ANSWER='# Documentation checklist\n\n## Source\n'+URL+'\n\n## Checklist\n\n1. Choose the correct platform.\n2. Configure a working model provider.\n'

def envelope(page=PAGE):
    return json.dumps({'result':'Response:\n\n'+json.dumps(page)})

def events():
    return [
        {'type':'tool_use','name':r.TOOL,'input':{'url':URL}},
        {'type':'tool_result','name':r.TOOL,'output':'intentionally truncated preview...','is_error':False},
        {'type':'result','exit_code':0,'text':ANSWER,'session_id':'test-session'}]

class ReaderTests(unittest.TestCase):
    def test_public_target(self): self.assertEqual(r.target_url(URL),URL)
    def test_private_targets_rejected(self):
        for value in ['http://example.com','https://localhost','https://10.0.0.1','https://[::1]/','https://u:p@example.com','https://example.com/?token=x']:
            with self.subTest(value=value),self.assertRaises(r.ReaderError):r.target_url(value)
    def test_config_changed_target_clears_markers(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'config.json';p.write_text(json.dumps({'url':URL,'expected_text':['Old marker']}))
            self.assertEqual(r.load_config(p,'https://example.com')['expected_text'],[])
    def test_bad_config_marker_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'config.json';p.write_text(json.dumps({'url':URL,'expected_text':'wrong'}))
            with self.assertRaises(r.ReaderError):r.load_config(p)
    def test_real_envelope_shape(self):self.assertEqual(r.unwrap_page(envelope()),PAGE.strip())
    def test_error_envelope_rejected(self):
        for raw in [json.dumps({'error':'failure'}),json.dumps({'result':''}),json.dumps({'result':'Insufficient credits to perform this request. '*3}),'bad json']:
            with self.subTest(raw=raw),self.assertRaises(r.ReaderError):r.unwrap_page(raw)
    def test_events_success(self):self.assertEqual(r.validate_events(events(),URL),(ANSWER,'test-session'))
    def test_wrong_url_rejected(self):
        e=events();e[0]['input']['url']='https://example.com'
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_repeated_extraction_rejected(self):
        e=events();e.insert(1,e[0].copy())
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_unexpected_tool_rejected(self):
        e=events();e.insert(0,{'type':'tool_use','name':'terminal'})
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_transport_error_rejected(self):
        e=events();e[1]['is_error']=True
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_failed_final_rejected(self):
        e=events();e[-1]['exit_code']=1
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_missing_source_rejected(self):
        e=events();e[-1]['text']='A very long answer without the required source. '*8
        with self.assertRaises(r.ReaderError):r.validate_events(e,URL)
    def test_markers_rejected(self):
        with self.assertRaises(r.ReaderError):r.validate_page(PAGE,['Missing expected phrase'])
    def test_nonempty_validation_is_labeled(self):self.assertEqual(r.validate_page(PAGE,[]),'nonempty_text_only')
    def test_bad_stream_rejected(self):
        with self.assertRaises(r.ReaderError):r.parse_events('not json')
    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);(d/'keep.txt').write_text('keep')
            with self.assertRaises(r.ReaderError):r.prepare_output(d)
            self.assertEqual((d/'keep.txt').read_text(),'keep')
    def test_read_only_full_result_not_stream_excerpt(self):
        with tempfile.TemporaryDirectory() as t:
            db=Path(t)/'state.db'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE messages (id INTEGER, session_id TEXT, role TEXT, tool_name TEXT, content TEXT)')
                c.execute('INSERT INTO messages VALUES (1,?,?,?,?)',('test-session','tool',r.TOOL,envelope()))
            self.assertEqual(r.read_session_page(db,'test-session'),PAGE.strip())
            with self.assertRaises(r.ReaderError):r.read_session_page(db,'other-session')
    def test_subprocess_contract_and_business_artifacts(self):
        with tempfile.TemporaryDirectory() as t:
            output=Path(t)/'out';args=type('Args',(),{'hermes':'hermes','output':output,'timeout':180,'state_db':Path(t)/'state.db'})()
            result=subprocess.CompletedProcess([],0,'\n'.join(json.dumps(e) for e in events()),'private stderr')
            with patch.object(r.shutil,'which',return_value='/test/hermes'),patch.object(r.subprocess,'run',return_value=result) as call,patch.object(r,'preflight',return_value={'hermes_version':'0.22.5'}),patch.object(r,'read_session_page',return_value=PAGE),patch.object(r,'secret_values',return_value=[]):
                r.run_live(args,{'url':URL,'expected_text':['Quick Install']})
            command=call.call_args.args[0]
            self.assertIn('--query-file',command);self.assertIn('mcp-scrapeless',command)
            self.assertNotIn('shell',call.call_args.kwargs)
            self.assertEqual((output/'page.md').read_text(),PAGE+'\n')
            report=json.loads((output/'report.json').read_text())
            self.assertEqual(report['tool_invocations_observed'],1);self.assertNotIn('session_id',report)
    def test_timeout_does_not_retry(self):
        with tempfile.TemporaryDirectory() as t:
            args=type('Args',(),{'hermes':'hermes','output':Path(t)/'out','timeout':30,'state_db':Path(t)/'state.db'})()
            with patch.object(r.shutil,'which',return_value='/test/hermes'),patch.object(r.subprocess,'run',side_effect=subprocess.TimeoutExpired('hermes',30)) as call,patch.object(r,'preflight',return_value={}):
                with self.assertRaises(r.ReaderError):r.run_live(args,{'url':URL,'expected_text':[]})
            self.assertEqual(call.call_count,1)
    def test_redaction(self):
        self.assertEqual(r.redact('secretvalue me@example.com',['secretvalue']),'[REDACTED] [EMAIL REDACTED]')
    def test_demo_is_offline(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(r.subprocess,'run',side_effect=AssertionError('Network command forbidden')),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(r.main(['demo','--output',str(Path(t)/'demo')]),0)
            report=json.loads((Path(t)/'demo/report.json').read_text())
            self.assertEqual(report['network_requests'],0);self.assertEqual(report['mode'],'offline_demo')

    def test_preflight_rejects_version_before_request(self):
        with patch.object(r,'local_command',return_value='Hermes Agent v0.23.0') as call:
            with self.assertRaises(r.ReaderError):r.preflight('hermes',Path('unused'))
        self.assertEqual(call.call_count,1)
    def test_preflight_rejects_unrestricted_tools(self):
        values=['Hermes Agent v0.22.5','--query-file --format --ignore-rules --toolsets --max-turns','["*"]','true']
        with patch.object(r,'local_command',side_effect=values),patch.object(r,'validate_database_schema') as schema:
            with self.assertRaises(r.ReaderError):r.preflight('hermes',Path('unused'))
            schema.assert_not_called()
    def test_preflight_rejects_incomplete_cli(self):
        with patch.object(r,'local_command',side_effect=['Hermes Agent v0.22.5','--query-file']):
            with self.assertRaises(r.ReaderError):r.preflight('hermes',Path('unused'))
    def test_preflight_valid_local_contract(self):
        values=['Hermes Agent v0.22.5','--query-file --format --ignore-rules --toolsets --max-turns','["scrape_markdown"]','true']
        with patch.object(r,'local_command',side_effect=values),patch.object(r,'validate_database_schema'):
            result=r.preflight('hermes',Path('unused'))
        self.assertEqual(result['extraction_requests'],0);self.assertEqual(result['model_requests'],0)
    def test_schema_drift_rejected_read_only(self):
        with tempfile.TemporaryDirectory() as t:
            db=Path(t)/'state.db'
            with sqlite3.connect(db) as c:c.execute('CREATE TABLE messages (id INTEGER, body TEXT)')
            before=db.read_bytes()
            with self.assertRaises(r.ReaderError):r.validate_database_schema(db)
            self.assertEqual(before,db.read_bytes())
    def test_preflight_failure_stops_chat(self):
        with tempfile.TemporaryDirectory() as t:
            args=type('Args',(),{'hermes':'hermes','output':Path(t)/'out','state_db':Path(t)/'state.db'})()
            with patch.object(r.shutil,'which',return_value='/test/hermes'),patch.object(r,'preflight',side_effect=r.ReaderError('unsupported')),patch.object(r.subprocess,'run') as call:
                with self.assertRaises(r.ReaderError):r.run_live(args,{'url':URL,'expected_text':[]})
                call.assert_not_called()


    def test_topic_prompt_preserves_single_tool_and_source(self):
        topic='Create and activate a Python virtual environment'
        prompt=r.build_prompt(URL,topic)
        self.assertIn(topic,prompt);self.assertIn(URL,prompt)
        self.assertIn('exactly once',prompt);self.assertIn('Do not execute them',prompt)
    def test_topic_override_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'config.json';p.write_text(json.dumps({'url':URL,'topic':'Old topic'}))
            self.assertEqual(r.load_config(p,topic_override=' New topic ')['topic'],'New topic')
            for topic in ['', 'x'*201, 'topic\nwith newline',42]:
                with self.subTest(topic=topic),self.assertRaises(r.ReaderError):r.load_config(p,topic_override=topic)
    def test_topic_flows_through_prompt_report_and_saved_answer(self):
        topic='Create and activate a Python virtual environment'
        e=events();e[-1]['text']=ANSWER+'\n## Topic\n'+topic+'\n'
        result=subprocess.CompletedProcess([],0,'\n'.join(json.dumps(x) for x in e),'')
        with tempfile.TemporaryDirectory() as t:
            output=Path(t)/'out';args=type('Args',(),{'hermes':'hermes','output':output,'timeout':180,'state_db':Path(t)/'state.db'})()
            seen=[]
            def execute(command,**kwargs):
                seen.append(Path(command[command.index('--query-file')+1]).read_text());return result
            with patch.object(r.shutil,'which',return_value='/test/hermes'),patch.object(r.subprocess,'run',side_effect=execute),patch.object(r,'preflight',return_value={}),patch.object(r,'read_session_page',return_value=PAGE),patch.object(r,'secret_values',return_value=[]):
                r.run_live(args,{'url':URL,'expected_text':['Quick Install'],'topic':topic})
            self.assertIn(topic,seen[0]);self.assertIn(topic,(output/'checklist.md').read_text())
            self.assertEqual(json.loads((output/'report.json').read_text())['topic'],topic)
    def test_missing_topic_stops_export_without_retry(self):
        result=subprocess.CompletedProcess([],0,'\n'.join(json.dumps(x) for x in events()),'')
        with tempfile.TemporaryDirectory() as t:
            output=Path(t)/'out';args=type('Args',(),{'hermes':'hermes','output':output,'timeout':180,'state_db':Path(t)/'state.db'})()
            with patch.object(r.shutil,'which',return_value='/test/hermes'),patch.object(r.subprocess,'run',return_value=result) as call,patch.object(r,'preflight',return_value={}):
                with self.assertRaises(r.ReaderError):r.run_live(args,{'url':URL,'expected_text':[],'topic':'Missing topic'})
                self.assertEqual(call.call_count,1)
            self.assertFalse((output/'checklist.md').exists())

if __name__=='__main__':unittest.main()
