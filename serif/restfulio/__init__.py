import re
import select
import socket

from serif import Document
from serif.xmlio import ET

######################################################################
# { Serif HTTP Server
######################################################################

HOSTNAME = 'localhost'
PORT = 8000

PROCESS_DOCUMENT_TEMPLATE = r'''
<SerifXMLRequest>
  <ProcessDocument end_stage="%(end_stage)s" output_format="serifxml" input_type="%(input_type)s" %(date_string)s>
    %(document)s
  </ProcessDocument>
</SerifXMLRequest>
'''

PATTERN_MATCH_DOCUMENT_TEMPLATE = r'''
<SerifXMLRequest>
  <PatternMatch pattern_set_name="%(pattern_set_name)s" slot1_start_offset="%(slot1_start_offset)d" slot2_start_offset="%(slot2_start_offset)d" slot3_start_offset="%(slot3_start_offset)d">
    %(document)s
    %(slot1)s
    %(slot1_weights)s
    %(slot2)s
    %(slot2_weights)s
    %(slot3)s
    %(slot3_weights)s
    %(equiv_names)s
  </PatternMatch>
</SerifXMLRequest>
'''

DOCUMENT_TEMPLATE = r'''
<Document language="%(language)s" docid="%(docid)s">
  <OriginalText><Contents>%(content)s</Contents></OriginalText>
</Document>
'''


def send_serifxml_pd_request(document, hostname=HOSTNAME, port=PORT,
                             end_stage='output', input_type='auto',
                             verbose=False, timeout=0, num_tries=1,
                             document_date=None):
    """
    Send a SerifXML request to process the given document to the
    specified server.  If successful, then return a `Document` object
    containing the processed document.  If unsuccessful, then raise an
    exception with the response message from the server.

    @param document: A string containing an XML <Document> element.
    @param hostname: The hostname of the Serif HTTP server.
    @param port: The port on which the Serif HTTP server is listening.
    @param end_stage: The end stage for processing.
    """
    date_string = ""
    if document_date:
        date_string = "document_date=\"" + document_date + "\""
    request = PROCESS_DOCUMENT_TEMPLATE % dict(
        document=document, end_stage=end_stage, input_type=input_type,
        date_string=date_string)
    response = send_serif_request(
        'POST SerifXMLRequest', request,
        verbose=verbose, hostname=hostname, port=port, timeout=timeout, num_tries=num_tries)
    if re.match('HTTP/.* 200 OK', response):
        body = response.split('\r\n\r\n', 1)[1]
        return Document(ET.fromstring(body))
    else:
        raise ValueError(response)


def send_serifxml_pm_request(document, hostname=HOSTNAME, port=PORT,
                             pattern_set_name='test_patterns', slot1='', slot2='', slot3='',
                             slot1_weights='', slot2_weights='', slot3_weights='',
                             slot1_start_offset=-1, slot2_start_offset=-1, slot3_start_offset=-1, equiv_names='',
                             verbose=False, timeout=0, num_tries=1):
    """
    Send a SerifXML request to pattern match against the given document
    to the specified server.  If successful, return the output of the
    pattern match.  If unsuccessful, then raise an exception with the
    response message from the server.

    @param document: A string containing an XML <Document> element.
    @param hostname: The hostname of the Serif HTTP server.
    @param port: The port on which the Serif HTTP server is listening.
    """
    request = PATTERN_MATCH_DOCUMENT_TEMPLATE % dict(document=document, pattern_set_name=pattern_set_name, slot1=slot1,
                                                     slot2=slot2, slot3=slot3,
                                                     slot1_weights=slot1_weights, slot2_weights=slot2_weights,
                                                     slot3_weights=slot3_weights,
                                                     slot1_start_offset=slot1_start_offset,
                                                     slot2_start_offset=slot2_start_offset,
                                                     slot3_start_offset=slot3_start_offset, equiv_names=equiv_names)
    response = send_serif_request(
        'POST SerifXMLRequest', request,
        verbose=verbose, hostname=hostname, port=int(port), timeout=timeout, num_tries=num_tries)
    if re.match('HTTP/.* 200 OK', response):
        body = response.split('\r\n\r\n', 1)[1]
        return body
    else:
        raise ValueError(response)


def escape_xml(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('\r', '&#xD;')
    return s


def send_serifxml_document(content, docid='anonymous', language='English',
                           hostname=HOSTNAME, port=PORT,
                           end_stage='output', input_type='auto', verbose=False,
                           timeout=0, num_tries=1, document_date=None):
    """
    Create a <Document> object from the given text content and docid,
    and use `send_serifxml_pd_request()` to send it to a Serif HTTP
    server.  If successful, then return a `Document` object containing
    the processed document.  If unsuccessful, then raise an exception
    with the response message from the server.

    @param content: The text content that should be processed by Serif.
    @param docid: The document identifier for the created <Document>.
    @param language: The language used by the document.
    @param hostname: The hostname of the Serif HTTP server.
    @param port: The port on which the Serif HTTP server is listening.
    @param end_stage: The end stage for processing.
    """
    xml_request = DOCUMENT_TEMPLATE % dict(
        docid=docid, content=escape_xml(content), language=language)
    return send_serifxml_pd_request(
        xml_request, end_stage=end_stage, input_type=input_type, verbose=verbose,
        hostname=hostname, port=port, timeout=timeout, num_tries=num_tries,
        document_date=document_date)


def send_serif_request(header, msg, hostname=HOSTNAME, port=PORT,
                       verbose=False, timeout=0, num_tries=1):
    """
    Send an HTTP request message to the serif server, and return
    the response message (as a string).
    """
    # Construct the HTTP request message.
    encoded_length = len(msg.encode('utf-8'))
    request = (header + ' HTTP/1.0\r\n' +
               'content-length: {}\r\n\r\n'.format(encoded_length) + msg)
    if verbose:
        DIV = '-' * 75
        print('%s\n%s%s' % (DIV, request.replace('\r\n', '\n'), DIV))

    for attempt in range(num_tries):
        if attempt > 0:
            print("send_serif_request() on attempt %d of %d" % (attempt + 1, num_tries))

        # Send the message.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        s.connect((hostname, int(port)))
        s.sendall(request.encode('utf-8'))
        s.setblocking(0)

        # Read and return the response.
        result = ''
        inputs = [s]
        data_bytes = bytes()
        problem_encountered = False
        while inputs and not problem_encountered:
            if timeout > 0:
                rlist, _, xlist = select.select(inputs, [], inputs, timeout)
            else:
                rlist, _, xlist = select.select(inputs, [], inputs)
            for s in rlist:
                data = s.recv(4096)
                # print "send_serif_request() received data of length %d" % len(data)
                if data:
                    data_bytes += data
                else:
                    result = data_bytes.decode('utf-8')
                    inputs.remove(s)
                    s.close()
            for s in xlist:
                print("send_serif_request() handling exceptional condition for %s" % s.getpeername())
                problem_encountered = True
                inputs.remove(s)
                s.close()
            if rlist == [] and xlist == []:
                print("send_serif_request() timed out while waiting for input from the socket!")
                problem_encountered = True
                inputs.remove(s)
                s.close()
        if problem_encountered:
            if result.endswith('</SerifXML>') or result.endswith('<SerifXML/>'):
                print("send_serif_request() encountered a problem but the result looks valid.")
                break  # Assume this means we got the result correctly
            else:
                continue  # Didn't get something we recognize, try again if attempt < num_tries
        else:
            break  # Success!  Break out of the num_tries loop

    if verbose: print('%s\n%s' % (result, DIV))
    return result


def send_shutdown_request(hostname=HOSTNAME, port=PORT):
    """
    Send a shutdown request to the serif server.

    @param hostname: The hostname of the Serif HTTP server.
    @param port: The port on which the Serif HTTP server is listening.
    """
    print("Sending shutdown request to %s:%d" % (hostname, int(port)))
    send_serif_request('POST Shutdown', '', hostname, port)
