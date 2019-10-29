# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import falcon
import jsonschema

from osdpl_admission_controller import validators


_VALIDATORS = {}
for validator in validators.__all__:
    _VALIDATORS[validator.service] = validator()


class RootResource(object):
    def on_get(self, req, resp):
        pass


class ReviewResponse(object):
    def __init__(self):
        self.api_version = ''
        self.uid = ''
        self._allowed = True
        self._status_code = None
        self._status_message = None

    def set_error(self, code, message):
        self._allowed = False
        self._status_code = code
        self._status_message = message

    @property
    def is_allowed(self):
        return self._allowed

    def to_json(self):
        ret_json = {
            'kind': 'AdmissionReview', 'apiVersion': self.api_version,
            'response': {
                'allowed': self._allowed, 'uid': self.uid
            }
        }
        if not self._allowed:
            ret_json['response']['status'] = {
                'code': self._status_code, 'message': self._status_message}
        return ret_json


class ValidationResource(object):
    def on_post(self, req, resp):
        resp.content_type = 'application/json'
        response = ReviewResponse()
        try:
            body = json.loads(req.stream.read())
            # Try to get apiVersion and uid even if request doesn't comply to
            # schema
            response.api_version = body.get('apiVersion')
            review_request = body.get('request', {})
            response.uid = review_request.get('uid')
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   "schemas.json")) as f:
                schema_dict = json.load(f)
            # Validate admission request against schema
            jsonschema.Draft3Validator(schema_dict).validate(body)
        except Exception as e:
            response.set_error(
                400, f'Exception parsing the body of request: {e}.')
        else:
            features = review_request.get('object', {}).get('spec', {}).get(
                'features', {})
            if review_request.get('kind', {}).get(
                    'kind') == 'OpenStackDeployment':
                for service in features.get('services', []):
                    if service in _VALIDATORS:
                        # Validate all the enabled services, if there is a
                        # corresponding validator
                        _VALIDATORS[service].validate(
                            review_request, response)
                        if not response.is_allowed:
                            break
        resp.body = json.dumps(response.to_json())


def create_api():
    app = falcon.API()
    health_checker = RootResource()
    validator = ValidationResource()
    app.add_route('/', health_checker)
    app.add_route('/validate', validator)
    return app
