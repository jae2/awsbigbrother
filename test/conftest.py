import pytest
import vcr
import sys
import re

PY3 = (sys.version_info[0] >= 3)

def scrub_string(string, replacement):
    def before_record_response(response):

        if PY3:
            response['body']['string'] = response['body']['string'].decode("utf8")
        if '<Content>' in response['body']['string']:
            f = open("fixtures/fake_cred_report_b64.txt", "r")
            response['body']['string'] = f.read()
        if PY3:
            response['body']['string'] = response['body']['string'].encode('utf-8')
        return response

    return before_record_response

def remove_group_data(string, replacement):
    def before_record_response(response):

        # Yeah it's horrible but I was having difficulty redacting the group response
        # The redacting is probably way over the top but better safe than sorry.
        decoded_body = response['body']['string'] = response['body']['string'].decode("utf8")
        decoded_body = re.sub(r"iam[:]{2}\d+:group", "iam::jaffa_cakes:group", decoded_body)
        decoded_body = re.sub(r"iam::\d+:", "arn:aws:iam::jaffacakes/", decoded_body)
        # Forgive me father for I have sinned.
        decoded_body = re.sub(r"<GroupId>\s*[A-Z0-9]+", "<GroupId>JAFFACAKES", decoded_body)
        response['body']['string'] = decoded_body
        response['body']['string'] = response['body']['string'].encode('utf-8')
        return response
    return before_record_response


@pytest.fixture(scope="module")
def vcr_test(request):

    my_vcr = vcr.VCR(filter_headers=['authorization'],
                     cassette_library_dir="fixtures/vcr_cassettes/python-{0}".format(sys.version_info[0]),
                     record_mode='once',
                     before_record_response=scrub_string('', ''),
                     decode_compressed_response=True

                     )
    yield my_vcr

@pytest.fixture(scope="module")
def group_vcr(request):

     group_vcr = vcr.VCR(
                     filter_headers=['authorization'],
                     cassette_library_dir="fixtures/vcr_cassettes/python-{0}".format(sys.version_info[0]),
                     record_mode='once',
                     before_record_response=remove_group_data('', ''),
                     decode_compressed_response=True
                     )
     yield group_vcr
