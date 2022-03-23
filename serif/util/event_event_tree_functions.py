import sys, os
script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, "..", ".."))
import serifxml3
from serifxml3 import PredType
from serifxml3 import MentionType 



def get_event_mention_maps(sentence, list_of_event_mentions):
    # Results caches
    event_mention_to_object_map = dict()
    object_to_event_mention_map = dict()
    mention_to_prop_map = dict()

    # Map mention heads to mentions, so we don't have to 
    # iterate over the mentions for every event mention
    mention_map = dict()
    for m in sentence.mention_set:
        if m.mention_type == MentionType.none:
            continue
        mention_head = m.syn_node.head_preterminal
        if mention_head not in mention_map:
            mention_map[mention_head] = set()
        #print("Mapping " + mention_head.pprint() + " to " + m.pprint())
        mention_map[mention_head].add(m)

        if mention_head not in mention_to_prop_map:
            mention_to_prop_map[mention_head] = set()

    # Align event mentions with mentions
    for em in list_of_event_mentions:
        event_head = None
        if em.anchor_node.is_terminal:
            event_head = em.anchor_node.parent
        else:
            event_head = em.anchor_node.head_preterminal
        # print ("Looking for mention match for: " + event_head.pprint())

        # only add stuff to object_to_event_mention_map and event_mention_to_object_map
        # that is directly related to target entities
        if event_head in mention_map:
            for m in mention_map[event_head]:
                # print ("Matched: " + m.pprint())
                if em not in event_mention_to_object_map:
                    event_mention_to_object_map[em] = set()
                event_mention_to_object_map[em].add(m)
                if m not in object_to_event_mention_map:
                    object_to_event_mention_map[m] = set()
                object_to_event_mention_map[m].add(em)

    # Map prop heads to props, so we don't have to 
    # iterate over the props for every event mention
    prop_map = dict()
    for p in sentence.proposition_set:
        if p.head is None:
            continue
        prop_head = p.head.head_preterminal
        # print ("Mapping " + prop_head.pprint() + " to " + p.pprint())
        if prop_head not in prop_map:
            prop_map[prop_head] = set()

        if prop_head not in mention_to_prop_map:
            mention_to_prop_map[prop_head] = set()
        mention_to_prop_map[prop_head].add(p)
        prop_map[prop_head].add(p)

    # Align propositions to with event mentions
    for em in list_of_event_mentions:
        event_head = None
        if em.anchor_node.is_terminal:
            event_head = em.anchor_node.parent
        else:
            event_head = em.anchor_node.head_preterminal   
        #print ("Looking for prop match for: " + event_head.pprint())
        if event_head in prop_map:
            for p in prop_map[event_head]:
                #print ("Matched: " + p.pprint())
                if em not in event_mention_to_object_map:
                    event_mention_to_object_map[em] = set()
                event_mention_to_object_map[em].add(p)
                if p not in object_to_event_mention_map:
                    object_to_event_mention_map[p] = set()
                object_to_event_mention_map[p].add(em)

    #print('Start of event mention to object map printing')
    #for key, val in event_mention_to_object_map.items():
    #    for prop in val:
    #        if isinstance(prop, serifxml3.Proposition):
    #            print(get_prop_pattern(prop))
    # print('event_mention_to_object_map', event_mention_to_object_map)
    # print('mention_to_prop_map', mention_to_prop_map)
    return event_mention_to_object_map, object_to_event_mention_map, mention_to_prop_map

def get_prop_map(sentence, object_to_event_mention_map, mention_to_prop_map):
    results = dict()
    starting_prop_to_depth = dict()

    for p in sentence.proposition_set:
        results[p] = set()
        starting_prop_to_depth[p] = 0
        #print ("Top level for " + p.pprint() + "\n")
        #print('Starting_prop', get_prop_pattern(p))
        traverse_event_props(p, p, object_to_event_mention_map, 0, results,
                 starting_prop_to_depth, mention_to_prop_map, set())
    return results, starting_prop_to_depth

def traverse_event_props(starting_prop, reachable_prop,
             object_to_event_mention_map, depth, results, 
             starting_prop_to_depth, mention_to_prop_map, visited):
    # print('reachable_prop', get_prop_pattern(reachable_prop))
    visited.add(reachable_prop)
    if reachable_prop in object_to_event_mention_map:
        #print ("PROP " + str(depth))
        event_event_add_all(results[starting_prop],
                object_to_event_mention_map[reachable_prop])
        if depth > starting_prop_to_depth[starting_prop]:
             starting_prop_to_depth[starting_prop] = depth

    for a in reachable_prop.arguments:
        if a.proposition is not None:
            if a.proposition not in visited:
                traverse_event_props(starting_prop, a.proposition,
                         object_to_event_mention_map, depth + 1,
                         results, starting_prop_to_depth, mention_to_prop_map, visited)
        if a.mention is not None:
            if a.mention in object_to_event_mention_map:
                #print ("MENTION " + str(depth+1))
                event_event_add_all(results[starting_prop],
                        object_to_event_mention_map[a.mention])
                if depth + 1 > starting_prop_to_depth[starting_prop]:
                    starting_prop_to_depth[starting_prop] = depth + 1

            mention_head = a.mention.syn_node.head_preterminal
            for p in mention_to_prop_map[mention_head]:
                # print('in here')
                if p not in visited:
                    traverse_event_props(starting_prop, p,
                             object_to_event_mention_map, depth + 1,
                             results, starting_prop_to_depth, mention_to_prop_map, visited)

def event_event_add_all(s, lst):
    #print ("Found these event mentions:")
    for em in lst:
        #print(em.anchor_node.pprint())
        s.add(em)

def get_best_proposition(prop_list, prop_to_depth):
    min_depth = None
    shallowest_prop = None
    for p in prop_list:
        if shallowest_prop is None:
            shallowest_prop = p
            min_depth = prop_to_depth[p]
            continue
        if prop_to_depth[p] < min_depth:
            shallowest_prop = p
            min_depth = prop_to_depth[p]
            continue
    #print ("Depth: " + str(min_depth))
    return shallowest_prop

def get_prop_patterns_between_pairs(sentence, list_of_event_mentions, event_mention_to_object_map, object_to_event_mention_map, mention_to_prop_map):
    # print('list_of_event_mentions', list_of_event_mentions)
    results = dict()

    # "Starting" Proposition to set of EventMentions
    # that can be reached by walking down from the starting
    # Proposition.
    starting_prop_to_child_map, prop_to_depth = get_prop_map(
        sentence, object_to_event_mention_map, mention_to_prop_map)

    em1 = list_of_event_mentions[0]
    em2 = list_of_event_mentions[1]
    #print('em1', em1)
    #print('em2', em2)

    candidate_props = []
    for (starting_prop, reachable_event_mentions) in\
            starting_prop_to_child_map.items():
        # print(get_prop_pattern(starting_prop))
        # print('reachable_event_mentions', reachable_event_mentions)
        if (em1 in reachable_event_mentions and
            em2 in reachable_event_mentions):
            candidate_props.append(starting_prop)

    # print('candidate_props', candidate_props)

    if len(candidate_props) > 0:
        best_prop = get_best_proposition(candidate_props, prop_to_depth)
        results[(em1, em2)] = best_prop
    #else:
    #    print("This pair has no connection: " +
    #          em1.anchor_node.pprint() + " " +
    #          em2.anchor_node.pprint() + "\n")

    # print(results)
    return results

def get_prop_pattern(prop):
    pattern_string = "("
    if prop.pred_type == PredType.verb:
        pattern_string += "vprop"
    elif prop.pred_type == PredType.copula:
        pattern_string += "vprop"
    elif prop.pred_type == PredType.modifier:
        pattern_string += "mprop"
    elif prop.pred_type == PredType.noun:
        pattern_string += "nprop"
    elif prop.pred_type == PredType.set:
        pattern_string += "sprop"
    elif prop.pred_type == PredType.comp:
        pattern_string += "cprop"
    else:
        pattern_string += "prop"

    if prop.head:
        pattern_string += " (predicate " + prop.head.head_terminal.tag + ")"
    
    if len(prop.arguments) > 0:
        pattern_string += " (args"
        for arg in prop.arguments:
            pattern_string += " (argument (role " + arg.role + ")"
            if arg.mention is not None:
                pattern_string += " " + get_mention_pattern(arg.mention)
            elif arg.proposition is not None:
                pattern_string += " " + get_prop_pattern(arg.proposition)
            pattern_string += ")"
        pattern_string += ")" # closes args

    pattern_string += ")"

    return pattern_string

def get_mention_pattern(mention):
    pattern_string = "(mention"
    pattern_string += " (headword " + mention.head.head_terminal.tag + ")"

    pattern_string += ")"

    return pattern_string

class PropNode(object):
    def __init__(self, prop_type=None, mention_head=None, role=None, color=-1):
        self.prop_type = prop_type # this will be None if it's a Mention leaf node
        self.mention_head = mention_head # this should always be populated
        self.role = role # the parent of current node wiht 'role' is the governor of the argument (which could be a Prop or Mention)
        self.color = color # -1 if it is neither event_0 neither event_1, 0 if event_0, 1 if event_1
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

def get_tree_from_prop(event_seen_0, event_seen_1, visited, mention_to_prop_map, obj, role=None):
    try_to_compute = False
    for mention in event_seen_0:
        if not event_seen_0[mention]:
            try_to_compute = True
            break
    for mention in event_seen_1:
        if not event_seen_1[mention]:
            try_to_compute = True
            break

    if not try_to_compute:
        return None
    else:
        color = -1
        if isinstance(obj, serifxml3.Proposition):
            visited.add(obj)
            prop = obj

            if prop.pred_type == PredType.verb:
                prop_type = "vprop"
            elif prop.pred_type == PredType.copula:
                prop_type = "vprop"
            elif prop.pred_type == PredType.modifier:
                prop_type = "mprop"
            elif prop.pred_type == PredType.noun:
                prop_type = "nprop"
            elif prop.pred_type == PredType.set:
                prop_type = "sprop"
            elif prop.pred_type == PredType.comp:
                prop_type = "cprop"
            else:
                prop_type = "prop"

            mention_head = None
            if prop.head:
                mention_head = prop.head.head_terminal.tag
                mention_key = prop.head.head_preterminal
                # print('mention_key', mention_key)
                if mention_key in event_seen_0:
                    # print('mention_key', mention_key)
                    event_seen_0[mention_key] = True
                    color = 0
                if mention_key in event_seen_1:
                    # print('mention_key', mention_key)
                    event_seen_1[mention_key] = True
                    color = 1
            node = PropNode(prop_type=prop_type, mention_head=mention_head, role=role, color=color)

            if len(prop.arguments) > 0:
                for arg in prop.arguments:
                    child_node = None
                    role = arg.role
                    if arg.mention is not None:
                        child_node = get_tree_from_prop(event_seen_0, event_seen_1, visited, mention_to_prop_map, arg.mention, role=role)
                    elif arg.proposition is not None:
                        if arg.proposition not in visited:
                            child_node = get_tree_from_prop(event_seen_0, event_seen_1, visited, mention_to_prop_map, arg.proposition, role=role)
                    if child_node is not None:
                        node.add_child(child_node)

            return node
        elif isinstance(obj, serifxml3.Mention):
            mention_head = obj.head.head_terminal.tag
            mention_key = obj.syn_node.head_preterminal

            if len(mention_to_prop_map[mention_key]) > 0:
                assert(len(mention_to_prop_map[mention_key]) == 1) # might not be true, I hope it is...
                next_prop = next(iter(mention_to_prop_map[mention_key]))

                if next_prop not in visited:
                    node = get_tree_from_prop(event_seen_0, event_seen_1, visited, mention_to_prop_map, next_prop, role=role)
                    if node is not None:
                        return node
                    else:
                        return None
            else:
                if mention_key in event_seen_0:
                    # print('mention_key', mention_key)
                    event_seen_0[mention_key] = True
                    color = 0
                if mention_key in event_seen_1:
                    # print('mention_key', mention_key)
                    event_seen_1[mention_key] = True
                    color = 1
                return PropNode(prop_type=None, mention_head=mention_head, role=role, color=color)
        else:
            print(type(obj))
            raise Exception('obj must be of type Proposition or Mention')

def pprint_tree(node, _prefix="", _last=True):
    print(_prefix, "`- " if _last else "|- ", (node.prop_type, node.mention_head, node.role, node.color), sep="")
    _prefix += "   " if _last else "|  "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        pprint_tree(child, _prefix, _last)

def add_event_seen(d, event):
    if event.anchor_node.is_terminal:
        event_head = event.anchor_node.parent
    else:
        event_head = event.anchor_node.head_preterminal
    d[event_head] = False

def construct_prop_event_pair_features(prop, event_pair, mention_to_prop_map):
    # collect targets
    event_seen_0 = dict()
    event_seen_1 = dict()

    add_event_seen(event_seen_0, event_pair[0])
    add_event_seen(event_seen_1, event_pair[1])
    tree = get_tree_from_prop(event_seen_0, event_seen_1, set(), mention_to_prop_map, prop)
    # print('event_seen_0', event_seen_0)
    # print('event_seen_1', event_seen_1)
    # pprint_tree(tree)
    return tree

def construct_joint_prop_between_events(serif_sentence, serif_event_0, serif_event_1):
    tree = None
    e_to_o_map = None
    #print(serif_sentence.text)
    #print('serif_event_0', serif_event_0.anchor_node.head_preterminal)
    #print('serif_event_1', serif_event_1.anchor_node.head_preterminal)

    try:
        # EventMention to list of Propositions and Mentions whose head
        # overlaps with EventMention trigger
        event_mention_to_object_map, object_to_event_mention_map, mention_to_prop_map\
            = get_event_mention_maps(serif_sentence, [serif_event_0, serif_event_1])
        for event_pair, best_prop in get_prop_patterns_between_pairs(
                serif_sentence, [serif_event_0, serif_event_1], event_mention_to_object_map, object_to_event_mention_map, mention_to_prop_map).items():
            tree = construct_prop_event_pair_features(best_prop, event_pair, mention_to_prop_map)
            break

        e_to_o_map = event_mention_to_object_map
    except:
        pass
    return tree, e_to_o_map

def lca(a, b, root, event_dict):
    """
    least common ancestor for n-ary tree
    :param a: 0 or 1
    :param b: 0 or 1
    :param root: root of tree
    :return:
    """
    if (root.color == a) or (root.color == b):
        if root.color == a:
            event_dict[a] = root
        if root.color == b:
            event_dict[b] = root
        return root

    count = 0
    temp = None

    for child in root.children:
        res = lca(a,b,child, event_dict)
        if res is not None:
            count += 1
            temp = res

    if count == 2:
        return root

    return temp

def prune_bad_patterns_from_joint_prop_tree(tree, e_to_o_map):
    if tree is not None:
        # Check if lca is either 1 or 0, which means one event is the ancestor of the other event
        event_dict = dict()
        ancestor = lca(0,1,tree, event_dict)

        common_ancestor = False

        if ancestor.color == 0 or ancestor.color == 1:
            common_ancestor = True

        if common_ancestor:
            # Check if event is one hop away
            for child in ancestor.children:
                if child.color == 0 or child.color == 1:
                    return True
        else:
            # Check if conjunction or sprop; different branches mean they are unlikely to be related
            if (tree.prop_type is not None) and (tree.prop_type == 'cprop' or tree.prop_type == 'sprop'):
                return True

    if e_to_o_map is not None:
        for e in e_to_o_map:
            for v in e_to_o_map[e]:
                if isinstance(v, serifxml3.Proposition):
                    if v.pred_type == PredType.modifier:
                        return True

    return False

if __name__ == "__main__":
    doc = serifxml3.Document(
        "/nfs/raid88/u10/users/jcai/code/ldc-utils/ida_annotation/outputs/4.xml")

    for sentence in doc.sentences:
        print('sentence', sentence.text)
        print('sentence', [em.anchor_node.head_preterminal for em in sentence.event_mention_set])
        for event_pair, triplet in get_prop_patterns_between_pairs(
            sentence, sentence.event_mention_set).items():
            print('event_pair', event_pair)
            best_prop, object_to_event_map, mention_to_prop_map = triplet
            print('best_prop', best_prop)
            construct_prop_event_pair_features(best_prop, event_pair, mention_to_prop_map)
