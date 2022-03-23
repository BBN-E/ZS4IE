# Ported from CSerif -- Core/SERIF/English/trainers/en_HeadFinder.cpp


# priority_scan searches go through the tags in "set" one by one to see if
#		they match the elements in right[]
# scan searches go through the elements of right[] one by one to see if
#		they match any of the tags in "set"
#
# i.e. in priority_scan, the order of the tags in the set matters,
#   and in scan it doesn't
#
# left_to_right / right_to_left obviously refers to the order in which it
#   searches through the elements of right[], a.k.a. the children 
#   of the node whose head we're trying to find

def priority_scan_from_left_to_right(syn_node, tags):
    for j in range(len(tags)):
        for k in range(len(syn_node)):
            if syn_node[k] == tags[j]:
                return k;
    return 0

def priority_scan_from_right_to_left(syn_node, tags):
    for j in range(len(tags)):
        for k in reversed(range(len(syn_node))):
            if syn_node[k] == tags[j]:
                return k
    return len(syn_node) - 1


def scan_from_left_to_right(syn_node, tags):
    for j in range(len(syn_node)):
        for k in range(len(tags)):
            if syn_node[j] == tags[k]:
                return j;	
    return -1;

def scan_from_right_to_left(syn_node, tags):
    for j in reversed(range(len(syn_node))):
        for k in range(len(tags)):
            if syn_node[j] == tags[k]:
                return j	
    return -1;


def findHeadADJP(syn_node):
    tags = ['NNS', 'QP', 'NN', 'DOLLAR', 'ADVP', 
            'JJ', 'VBN', 'VBG', 'ADJP', 'JJR', 
            'NP', 'NPA', 'DATE', 'NPP', 'NPPOS', 
            'JJS', 'DT', 'FW', 'RBR', 'RBS', 
            'SBAR', 'RB']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadADVP(syn_node):
    tags = ['RB', 'RBR', 'RBS', 'FW', 'ADVP', 
            'TO', 'CD', 'JJR', 'JJ', 'IN', 
            'NP', 'NPA', 'DATE', 'NPP', 'NPPOS', 
            'JJS', 'NN']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadCONJP(syn_node):
    tags = ['CC', 'RB', 'IN']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadFRAG(syn_node): 
    return len(syn_node) - 1

def findHeadINTJ(syn_node):
    return 0;

def findHeadLST(syn_node):
    tags = ['LS', 'COLON']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadNAC(syn_node):
    tags = ['NN', 'NNS', 'NNP', 'NPP', 'NNPS', 
            'NP', 'NPA', 'DATE', 'NPP', 'NPPOS', 
            'NAC', 'EX', 'DOLLAR', 'CD', 'QP', 
            'PRP', 'VBG', 'JJ', 'JJS', 'JJR',
            'ADJP', 'FW']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadPP(syn_node):
    tags = ['IN', 'TO', 'VBG', 'VBN', 'RP', 'FW']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadPRN(syn_node):
    return 0;

def findHeadPRT(syn_node):
    tags = ['RP']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadQP(syn_node):
    tags = ['DOLLAR', 'IN', 'NNS', 'NN', 'NPP', 
            'DATE', 'JJ', 'RB', 'DT', 'CD',
            'NCD', 'QP', 'JJR', 'JJS']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadRRC(syn_node):
    tags = ['VP', 'NP', 'NPA', 'DATE', 'NPP',
            'NPPOS', 'ADVP', 'ADJP', 'PP']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadS(syn_node):
    tags = ['TO', 'IN', 'VP', 'S', 'SBAR', 
            'ADJP', 'UCP', 'NP', 'NPA', 'NPP',
            'DATE', 'NPPOS']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadSBAR(syn_node):
    tags = ['WHNP', 'WHPP', 'WHADVP', 'WHADJP', 'IN',
            'DT', 'S', 'SQ', 'SINV', 'SBAR', 
            'FRAG']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadSBARQ(syn_node):
    tags = ['SQ', 'S', 'SINV', 'SBARQ', 'FRAG']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadSINV(syn_node):
    tags = ['VBZ', 'VBD', 'VBP', 'VB', 'MD', 
            'VP', 'S', 'SINV', 'ADJP', 'NP', 
            'NPA', 'DATE', 'NPP', 'NPPOS']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadSQ(syn_node):
    tags = ['VBZ', 'VBD', 'VBP', 'VB', 'MD', 
            'VP', 'SQ']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadUCP(syn_node): 
    return len(syn_node) -1

def findHeadVP(syn_node):
    tags = ['TO', 'VBD', 'VBN', 'MD', 'VBZ', 
            'VB', 'VBG', 'VBP', 'VP', 'ADJP',
            'NN', 'NNS', 'NP', 'NPA', 'NPP',
            'DATE', 'NPPOS']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadWHADJP(syn_node):
    tags = ['CC', 'WRB', 'JJ', 'ADJP']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadWHADVP(syn_node):
    tags = ['CC', 'WRB']
    return priority_scan_from_right_to_left(syn_node, tags)

def findHeadWHNP(syn_node):
    tags = ['WDT', 'WP', 'WPDOLLAR', 'WHADJP', 'WHPP',
            'WHNP']
    return priority_scan_from_left_to_right(syn_node, tags)

def findHeadWHPP(syn_node):
     tags = ['IN', 'TO', 'FW']
     return priority_scan_from_right_to_left(syn_node, tags)

def findHeadNP(syn_node):
    result = None

    if syn_node[-1] == 'POS':
        return len(syn_node) - 1

    tags1 = ['NN', 'NNP', 'NPP', 'NNPS', 'NPP',
             'DATE', 'NNS', 'NX', 'POS', 'JJR']
    result = scan_from_right_to_left(syn_node, tags1)
    if result >= 0:
        return result

    tags2 = ['NP', 'NPA', 'NPPOS']
    result = scan_from_left_to_right(syn_node, tags2)
    if result >= 0:
        return result

    tags3 = ['DOLLAR', 'ADJP', 'PRN']
    result = scan_from_right_to_left(syn_node, tags3)
    if result >= 0:
        return result

    tags4 = ['CD']
    result = scan_from_right_to_left(syn_node, tags4)
    if result >= 0:
        return result

    tags5 = ['JJ', 'JJS', 'RB', 'QP']
    result = scan_from_right_to_left(syn_node, tags5)
    if result >= 0:
        return result

    return len(syn_node) - 1


def find_head_index(syn_node):
    if syn_node.is_terminal:
        return None
    
    tag = syn_node.tag

    if tag == 'ADJP':
        return findHeadADJP(syn_node)
    elif tag == 'ADVP':
        return findHeadADVP(syn_node)
    elif tag == 'CONJP':
        return findHeadCONJP(syn_node)
    elif tag == 'FRAG':
        return findHeadFRAG(syn_node);
    elif tag == 'INTJ':
        return findHeadINTJ(syn_node)
    elif tag == 'LST':
        return findHeadLST(syn_node)
    elif tag == 'NAC':
        return findHeadNAC(syn_node)
    elif tag == 'NP':
        return findHeadNP(syn_node)
    elif tag == 'NPA':
        return findHeadNP(syn_node)
    elif tag == 'NPP':
        return findHeadNP(syn_node)
    elif tag == 'NPPOS':
        return findHeadNP(syn_node)
    elif tag == 'PP':
        return findHeadPP(syn_node)
    elif tag == 'PRN':
        return findHeadPRN(syn_node)
    elif tag == 'PRT':
        return findHeadPRT(syn_node)
    elif tag == 'QP':
        return findHeadQP(syn_node)
    elif tag == 'RRC':
        return findHeadRRC(syn_node)
    elif tag == 'S':
        return findHeadS(syn_node)
    elif tag == 'SBAR':
        return findHeadSBAR(syn_node)
    elif tag == 'SBARQ':
        return findHeadSBARQ(syn_node)
    elif tag == 'SINV':
        return findHeadSINV(syn_node)
    elif tag == 'SQ':
        return findHeadSQ(syn_node)
    elif tag == 'UCP':
        return findHeadUCP(syn_node)
    elif tag == 'VP':
        return findHeadVP(syn_node)
    elif tag == 'WHADJP':
        return findHeadWHADJP(syn_node)
    elif tag == 'WHADVP':
        return findHeadWHADVP(syn_node)
    elif tag == 'WHNP':
        return findHeadWHNP(syn_node)
    elif tag == 'WHPP':
        return findHeadWHPP(syn_node)
    else:
        return 0


