import os
import re
import sys
import time
from optparse import OptionParser

from serif.restfulio import send_serifxml_document, send_shutdown_request

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", '--input_batch_file', dest='input_batch_file', help="Path to input batch file", default="")
    parser.add_option("-o", '--output_dir', dest='output_dir', help="Path to output directory", default="")
    parser.add_option("-l", '--language', dest='language', help="Document language", default="English")
    parser.add_option("-m", '--max_lines', dest='max_lines',
                      help="Maximum number of lines to process (lines in excess of max_lines will be discarded)",
                      default="")
    opts, args = parser.parse_args()

    if len(args) == 2 and args[0] in ('process_batch_file', 'shutdown'):
        ip_address_regex = re.compile('[^:]+:\d+$')
        if ip_address_regex.match(args[1]):
            hostname, port = args[1].split(':')
        else:
            server_info_file = args[1]
            seconds_to_sleep = 5
            total_seconds_slept = 0
            if not os.path.exists(server_info_file):
                sys.stdout.write('Waiting for {} to exist'.format(server_info_file))
                sys.stdout.flush()
            while not os.path.exists(server_info_file):
                time.sleep(seconds_to_sleep)
                total_seconds_slept += seconds_to_sleep
                sys.stdout.write('.')
                sys.stdout.flush()
                if total_seconds_slept == 600:
                    raise RuntimeError("Timed out while waiting for {} to exist".format(server_info_file))
            hostname, port = open(server_info_file).read().strip().split(':')
    else:
        sys.exit(
            "Usage is %s process_batch_file|shutdown server_info_file|host:port (-i <input_batch_file> -o <output_dir>)" %
            sys.argv[0])

    if args[0] == 'process_batch_file':
        if opts.output_dir != "" and not os.path.exists(opts.output_dir):
            os.makedirs(opts.output_dir)  # Create our output dir if it doesn't exist
        lines = [x.strip() for x in open(opts.input_batch_file, 'r', encoding='utf-8').readlines()]
        for index, line in enumerate(lines):
            # Allow for an optional tab-delimited format: path\tdocument_date
            if len(line.split('\t')) == 2:
                input_file, document_date = line.split('\t')
                if document_date == 'n/a':
                    document_date = None
            else:
                input_file = line
                document_date = None
            filename = os.path.basename(input_file)
            print("Processing file (%d of %d): %s" % (index, len(lines), filename))
            sys.stdout.flush()
            data = open(input_file, 'r', encoding='utf-8').read()
            if opts.max_lines != "" and int(opts.max_lines) > 0:
                lines = data.split('\n')
                data = '\n'.join(lines[0:int(opts.max_lines)])
            doc = send_serifxml_document(data, docid=filename, hostname=hostname, port=port,
                                         document_date=document_date, language=opts.language)
            doc.save(os.path.join(opts.output_dir, "%s.xml" % filename))
    elif args[0] == 'shutdown':
        send_shutdown_request(hostname, port)

#     if 0:
#         send_serifxml_document('foo', hostname='language-01')
#     if 0:
#         print 'sending doc to serif...'
#         e = send_serifxml_document('''
#         John talked to his sister Mary.
#         The president of Iran, Joe Smith, said he wanted to resume talks.
#         I saw peacemaker Bob at the mall.
#         ''', 'anonymous', 'English', 'localhost', 8081)
#         print 'serif is done!'
#         print e
#
#     if 0:
#         f = ('c:/TextGroup/Core/arabia/output-local0-x86_64/'
#              'actor/output/actor00.txt.xml')
#         #f = '/home/eloper/code/text/Core/SERIF/build/expts/arabic_translit_new/output/DIGRESSING_20050102.0130.sgm.xml'
#         #f = '/home/eloper/code/textDoc/Core/SERIF/build/expts/arabic_translit_new/output/DIGRESSING_20050102.0130.sgm.xml'
#         #f = '/home/eloper/tmp/serifxml_out/XIN_ENG_20030405.0080.sgm.xml'
#
#     if 0:
#         apf = send_serif_request('POST sgm2apf', '<DOC><DOCID>1</DOCID><TEXT>Bob and Mary went to the store. The store was called Safeway.</TEXT></DOC>', 'azamania11desk', 8081, True)
#         print apf
#     if 0:
#         doctheory = Document("icews.xml")
#         print doctheory.icews_actor_mention_set.pprint(depth=10)
#         print doctheory.icews_event_mention_set.pprint(depth=10)
#     if 0:
#         doctheory = send_serifxml_pm_request('<SerifXML version="18"><Document href="file://C:/temp/sample-doc.xml"></Document></SerifXML>', 'localhost', 8081)
#         print doctheory


# Load a document.
# etree = ET.parse(f).getroot()

# Set some "unknown" attributes
# etree.attrib['foo'] = 'bar'
# etree[0].attrib['baz'] = 'bap'

# d = Document(etree)
# s = d.sentences[0]
# print s.text
# s.save_text()
# print d
# print d.sentences[0]
# del d
# print s.text
# print s.mention_set[1]
# Modify the document.
# d.sentences[0].parse.root = d.sentences[0].parse.root[0]
# del d.sentences._children[1:]
# Save the document.
# d.save('foo.xml')
