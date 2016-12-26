import json
from base64 import b64decode

from config import settings
from limesurveyrc2api import LimeSurveyRemoteControl2API

# Make a session.
api = LimeSurveyRemoteControl2API(settings.rpc_url)
session_req = api.sessions.get_session_key(settings.username, settings.password)
session_key = session_req.get('result')

surveys_req = api.surveys.list_surveys(session_key, settings.username)
surveys = surveys_req.get('result')
for survey in surveys:
    if survey.get('surveyls_title') == 'yunity Contributors page':
        sid = survey.get('sid')
        responses_req = api.surveys.export_responses(session_key, sid)
        response_b64 = responses_req.get('result')
        responses = json.loads(b64decode(response_b64).decode())
        picture_list = []
        for _ in responses['responses']:
            for rid, response in _.items():
                if response['picture']:
                    pic_dict = json.loads(response['picture'])[0]
                    picture_list.append({'name': pic_dict['name'], 'rid': rid, 'sid': sid})


from requests import session
with session() as s:
    response = s.get(settings.login_url)
    csrf = response.cookies['YII_CSRF_TOKEN']
    response = s.post(settings.login_url,
                      {'YII_CSRF_TOKEN': csrf,
                        'authMethod': 'Authdb',
                        'user': settings.username,
                        'password': settings.password,
                        'loginlang': 'default',
                        'action': 'login',
                        'login_submit': 'login'}
                      )
    for p in picture_list:
        response = s.get(settings.response_url,
                         params={
                             'sa': 'actionDownloadfile',
                             'sFileName': p['name'],
                             'iResponseId': p['rid'],
                             'surveyid': p['sid']})
        with open('{}{}'.format(p['rid'], p['name']), 'bw') as f:
            f.write(response.content)