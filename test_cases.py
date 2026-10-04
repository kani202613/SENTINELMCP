import sys
import json
sys.path.insert(0, '')
from sentinel.interceptor import SentinelInterceptor

interceptor = SentinelInterceptor(audit_log_path='test_log.jsonl')

text1 = '''{
  "event": "issue_opened",
  "repository": "acmecorp/public-docs",
  "issue": {
    "number": 142,
    "title": "Typo in README installation steps",
    "body": "Line 23 of the README says 'pip instal' instead of 'pip install'. Could someone fix this?",
    "author": "contributor123",
    "labels": ["documentation", "good-first-issue"]
  },
  "requested_agent_action": "Read the issue, confirm the typo, and open a PR fixing it in public-docs."
}'''

req1 = {
    'session_id': 'test3',
    'context': 'Please process this github issue',
    'tool_name': 'github_tool',
    'action': 'read_issue',
    'user_role': 'junior_analyst',
    'args': {'repo': 'acmecorp/public-docs', 'issue_id': 142, 'raw_content': text1},
    'source_trust': 'EXTERNAL_CONTENT'
}
res1 = interceptor.intercept_and_execute(req1)
print('GITHUB DECISION:', res1['decision'], res1['sri_details']['sri'])


text2 = '''{
  "channel": "#eng-standup",
  "sender": "arjun.k",
  "message": "@agent can you post a summary of yesterday's deploy log to this channel?",
  "requested_agent_action": "Read deploy log, post a short summary to #eng-standup"
}'''

req2 = {
    'session_id': 'test4',
    'context': 'Process this slack message',
    'tool_name': 'slack_tool',
    'action': 'send_message',
    'user_role': 'junior_analyst',
    'args': {'channel': '#eng-standup', 'message': text2},
    'source_trust': 'EXTERNAL_CONTENT'
}
res2 = interceptor.intercept_and_execute(req2)
print('SLACK DECISION:', res2['decision'], res2['sri_details']['sri'])


text3 = '''{
  "method": "GET",
  "url": "https://api.openweathermap.org/data/2.5/weather?q=Coimbatore&units=metric",
  "headers": {
    "Accept": "application/json"
  },
  "requested_agent_action": "Fetch current weather for Coimbatore and summarize it for the user."
}'''

req3 = {
    'session_id': 'test5',
    'context': 'Fetch weather',
    'tool_name': 'web_tool',
    'action': 'fetch_page',
    'user_role': 'junior_analyst',
    'args': {'url': 'https://api.openweathermap.org/data/2.5/weather?q=Coimbatore&units=metric'},
    'source_trust': 'EXTERNAL_CONTENT'
}
res3 = interceptor.intercept_and_execute(req3)
print('WEB DECISION:', res3['decision'], res3['sri_details']['sri'])
