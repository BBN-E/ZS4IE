# Copyright 2015 by Raytheon BBN Technologies Corp.
# All Rights Reserved.

"""
Python API for Accessing SerifXML Files.

    >>> import serifxml3
    >>> document_text = '''
    ...     John talked to his sister Mary.
    ...     The president of Iran, Joe Smith, said he wanted to resume talks.
    ...     I saw peacemaker Bob at the mall.'''
    >>> serif_doc = serifxml3.send_serifxml_document(document_text)
    >>> print serif_doc
    Document:
      docid = u'anonymous'
      language = u'English'
      source_type = u'UNKNOWN'
      ...

or, to load a document from a file:

    >>> serif_doc = serifxml3.Document(filename)

to save a document to a file:

    >>> serif_doc.save(output_filename)

For a list of attributes that any serif theory object takes, use the
'help' method on the theory object (or its class).  E.g.:

    >>> serif_doc.sentences[0].help()
    >>> MentionSet.help()
"""

from serif.theory.document import *
from serif.util.event_event_tree_functions import construct_joint_prop_between_events, prune_bad_patterns_from_joint_prop_tree