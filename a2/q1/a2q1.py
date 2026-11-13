# Yap Meng Hin (34328033)
#

import sys

# original alphabet ASCII range starts from 37 and ends at 126. But since we append '$' to the end of the input string,
# we also need to consider the special terminal character '$' with ASCII value 36, so we decrease the alphabet start by 1 
# to 36 to cover $ in the suffix tree construction later 
alphabet_start = 37-1
alphabet_end = 126
alphabet_range = alphabet_end - alphabet_start + 1

def read_file(file_path: str) -> str:
    """
    Function to read a file from the input file path 

    input: 
        file_path: the path to the input file
    output: 
        a string representing the content in the file

    """
    f = open(file_path, 'r')
    line = f.readlines()
    f.close()
    return line

class endpoint:
    """
    Class which represents the endpoint index (ep) of an edge leading to a node in the suffix tree in 0 base indexing. 
    
    Since in Ukkonen's Algorithm there is a need to update the ep of all leaf nodes simultaneosly, 
    for leaf nodes, this class basically serves as a mutable datatype storing the global endpoint index 
    such that all leaves can share a same global endpoint instance that can be updated globally. 

    To simplify code logic and avoid the need of handling cases such as storing ep as int for non leaf nodes 
    while storing ep using endpoint for leaf nodes, all edges leading to non leaf nodes also store their ep using 
    this endpoint class.
    """
    def __init__ (self, ep):
        self.ep = ep

    def update_global_ep(self, new_ep):
        # function to update the current ep value to the input new_ep value 
        # mainly used in Rule 1 extension to globally update the ep of the edge leading to leaf nodes
        self.ep = new_ep

    def __str__(self):
        # str function mainly used during debugging 
        return str(self.ep)

class node:
    """
    The node class represents a node in the suffix tree, with an ID to identify the node based on the order of creation of the node.
    
    To simplify the representation of the suffix tree, since each node can only have 1 incoming edge in a suffix tree, 
    the starting point (sp) and ending point (ep) of the edge leading to the node is also included in the node so there is no need to 
    create another edge class.  
    
    In the suffix tree, we apply Trick 1: Space-efficient representation of edge-labels/substrings, where each edge would represent a 
    substring of the string S[1...n-1], where the edge would represent the substring of string S starting from index sp to ep (S[sp, ep]) 
    in 0 base indexing. Thus, each edge is also represented by [sp, ep].
    
    """

    def __init__ (self, id: int, start: int, end: endpoint):
        self.id = id

        # Trick 1: Space-efficient representation of edge labels/substrings
        # Edge labels sp and ep represents the substring mod_txt[sp:ep] that forms the edge connecting from a parent node to this node, 
        # where the sp is the starting position index in the input string in 0 base, while 
        # ep is the ending position index in the input string in 0 base that forms the edge in the suffix tree. 
        self.sp = start
        self.ep = end
        self.parent = None

        self.suffix_link = None
        self.children = [None for _ in range(alphabet_range)]

    def get_edge_len(self):
        # calculate length of the edge, which is the length of the substring represented by the edge
        return self.ep.ep - self.sp + 1

    def __str__(self):
        return f"Node(id={self.id}, start={self.sp}, end={self.ep})" 

class suffix_tree:
    """
    Class representing a suffix tree for the input string mod_txt, which is constructed using Ukkonen's Algorithm.

    """
    def __init__ (self, mod_txt):
        # function to initialise the suffix tree 

        # the input string mod_txt used to build the suffix tree 
        self.mod_txt = mod_txt

        # The root node of the suffix tree, which provides access to all other nodes in the suffix tree 
        # after construction of the suffix tree is done. 
        # Construct the suffix tree using Ukkonen's algorithm 
        self.root = self.ukn(mod_txt)
    
    def ukn(self, mod_txt):
        """
        Implementation of Ukkonen's algorithm to construct a suffix tree based on the given input string mod_txt in linear time.

        Takes in the param mod_txt, which is the input string used to construct the suffix tree that has the terminal character '$' appended to
        at the end and constructs the suffix tree for the input string. Returns the root node of the suffix tree after construction is done since 
        the whole suffix tree can be accessed under the root node. 

        """

        with open("runlog_a2q1.txt", "w") as log:

            # current_node_id_counter is the counter used to keep track of the number of nodes created (which is also the last assigned node ID). 
            # Initialised to 1 for the root node, such that the root node has ID 1 and increment it by 1 everytime before assigning to a newly created node.   
            # initialise root with ID 1, sp as -1 and ep as -1 and set its suffix link to itself
            current_node_id_counter = 1 
            root = node(current_node_id_counter, -1, endpoint(-1))
            root.suffix_link = root
            log.write('Root Node ' + str(root.id) + '\n')

            # Before any phase and extension starts:
            # initialise the global endpoint (GE) that is shared between all leaf nodes in the suffix tree to be used for rapid leaf extension trick 
            # set the current active node to the root node 
            global_end = endpoint(-1)
            active_node = root

            # initialise extension index j as 0 and initialise last j as None 
            # rem represents the remainder and is initialised as None 
            # pending_suflink_node stores the node with suffix link pending to be resolved
            j = 0
            last_j = None
            rem = None
            pending_suflink_node = None


            # phase loop, where i represents the current phase  
            for i in range(len(mod_txt)):
                
                # rule 1 extension with Trick 4: rapid leaf expansion trick, at the beggining of every phase i, extend global end (GE) by 1 
                # such that all edges leading to leaves add the ith character in mod_txt
                global_end.update_global_ep(global_end.ep + 1)
                log.write("\n") 
                log.write('Phase ' + str(i+1) + " starts from Extn " + str(j+1) + '\n')
                
                # extension loop for phase i, where j represents the current extension.
                # Note that in my approach, j is always updated in the previous extension such that it always starts from the last j value correctly. 
                # Since j needs to loop from last j to i+1, a while loop is used here instead of a for loop as j may or may not increment based on the extension case, 
                # thus the loop manually increment or not increment j based on the extension case and there is no need to maintain a last j, as j would already be 
                # updated to last j correctly before the next phase / extn  
                while j < i+1:

                    # Trick 2: Skip-Count trick
                    # extension point is the position index on an edge in the suffix tree to perform the extension case after performing the skip count trick 
                    # find the extension point before beggining extension j if there is a remainder 
                    extension_point = 0  
                    while rem != None:

                        # find the length of the remainder 
                        rem_len = rem[1] - rem[0] + 1

                        if active_node.children[ord(mod_txt[rem[0]]) - alphabet_start] is not None:
                            # find the length of the edge connecting the current active node to the respective child node
                            child_node = active_node.children[ord(mod_txt[rem[0]]) - alphabet_start]
                            edge_len = child_node.ep.ep - child_node.sp + 1

                            # if the edge length is > the remainder length, that means the extension point lies in the edge
                            # no need to jump to next node, just calculate how far is the extension point from the sp of the edge and stop skip counting  
                            if edge_len > rem_len:
                                extension_point = child_node.sp + rem_len
                                break
                            
                            # if the edge length is <= than the remainder length, that means the extension point will not be in the edge connecting the 
                            # current active node to its child node. So, we can just jump to the corresponding child node and set it as active node and 
                            # continue the skip count loop until we find the extension point and the edge it is on
                            elif edge_len <= rem_len:

                                # Update remainder based on the length of the edge jumped, as since we already jumped through the characters on the edge, 
                                # we can skip the need to compare them 1 by 1.
                                # Since the remainder stores the start and end index in the input string similar to the sp and ep of an edge,
                                # if we have skipped to the next node and jumped past an edge with edge_len, we just increment the start index of the remainder 
                                # by edge_len
                                if rem[0] + edge_len <= rem[1]:
                                    rem = [rem[0] + edge_len, rem[1]]
                                
                                elif rem[0] + edge_len > rem[1]:
                                    # if the full rem has been fully skipped past then reset the rem to None
                                    rem = None

                                # jump to the corresponding child node and set it as active node and continue skip count 
                                active_node = child_node

                    # if there is no remainder, the extension point is simply just at the position i (phase) in the the corresponding edge under the current active node 
                    if rem is None:
                        extension_point = i 


                    # Extension cases
                    # Check if theres any existing branch for the new character from the string mod_txt in this phase, mod_txt[i] or if there is a remainder.
                    # If there is already an existing edge under the current node starting with the character mod_txt[i] or starting with the first charcater of the 
                    # remainder (if the rem is not None), that means there is no need to create a new branch and we can perform extension under the corresponding edge 
                    if active_node.children[ord(mod_txt[i]) - alphabet_start] is not None or rem is not None:
                        
                        # find the corresponding edge and child node based on the starting character of the rem or the mod_txt[i] 
                        if rem is not None:
                            child_node = active_node.children[ord(mod_txt[rem[0]]) - alphabet_start]
                        else:
                            child_node = active_node.children[ord(mod_txt[i]) - alphabet_start]

                        # If at the extension point in the corresponding edge, the character we are trying to insert, mod_txt[i] does not exist, apply Rule 2 regular, 
                        # create a new internal node before the extension point on the edge between the current active node and the corresponding child node. 
                        # From the internal node, split out and create a new leaf node and insert mod_txt[i] to the edge connecting to the new leaf node  
                        if mod_txt[i] != mod_txt[extension_point]:

                            # write runlog
                            log.write("    Extn " + str(j+1) + ' applies Rule 2 (regular)\n')
                            rem_str = ''
                            if rem == None:
                                rem_str = 'EMPTY'
                            else:
                                rem_str = 'S[' + str(rem[0]+1) + '...' + str(rem[1]+1) + ']'
                            log.write("    Active Node = Node " + str(active_node.id) + ' (suffix link to Node ' + str(active_node.suffix_link.id) + "); " + "Remainder = " + rem_str + '\n') 
                            
                            # originally, the edge connecting the current active node to the original child node is [sp, ep]
                            # create a new internal node and connect the active node to the new internal node with the edge [sp, extension_point-1] (before the extn point)
                            # update the edge from the active node to connect to the new internal node instead of the original child node 
                            original_sp = child_node.sp
                            # update the ID before assigning to the new internal node 
                            current_node_id_counter += 1
                            internal_node = node(current_node_id_counter, original_sp, endpoint(extension_point-1))
                            active_node.children[ord(mod_txt[original_sp]) - alphabet_start] = internal_node
                            internal_node.parent = active_node
                            log.write("        Node " + str(internal_node.id) + ' created: Internal node!\n') 

                            # create new leaf node to insert the character mod_txt[i], so the edge connecting the internal node to this leaf node should be [i, GE], since it is 
                            # a leaf node, the edge connecting to the leaf node should end at the GE 
                            # update the ID before assigning to the new internal node 
                            current_node_id_counter += 1
                            new_leaf = node(current_node_id_counter, i, global_end)
                            internal_node.children[ord(mod_txt[i]) - alphabet_start] = new_leaf
                            new_leaf.parent = internal_node
                            log.write("        Node " + str(new_leaf.id) + ' created: Leaf node!\n') 

                            # Update the original child node, as the edge leading to the original child node is no longer from the active node, but from the new internal node. 
                            # Thus, the edge connecting the new internal node to the original child node should be [extension_point, ep], where the ep is unchanged. Connect the edge
                            # from the internal node to the original child node and now the child node's parent node is the internal node instead
                            child_node.sp = extension_point
                            child_node.parent = internal_node
                            internal_node.children[ord(mod_txt[extension_point]) - alphabet_start] = child_node
                            
                            last_j = j
                            
                            # resolve pending suffix link from prev extension, if a new internal node is created in this extn, set the node with pending suffix link to resolve to
                            # have a suffix link connecting to the newly created internal node 
                            if pending_suflink_node != None:
                                pending_suflink_node.suffix_link = internal_node
                                log.write("        Linking Node " + str(pending_suflink_node.id) + ' to Node ' + str(internal_node.id) + '\n') 
                                pending_suflink_node = None
                            # since a new internal node is created, save it as it is now pending to get its suffix link resolved 
                            pending_suflink_node = internal_node
                            
                            # Follow suffix link out of the active node and find the next active node
                            if active_node == root and active_node.suffix_link == root:
                                # if we are at the root, following the suffix link out would end up at the root again since the suffix link of root links to itself.
                                # reduce 1 character from rem if we are at the root node and following suffix link leads back to the root node
                                if rem != None:
                                    if rem[0] + 1 <= rem[1]:
                                        rem = [rem[0] + 1, rem[1]]
                                    else:
                                        rem = None
                            active_node = active_node.suffix_link

                        # If at the extension point, the character we are trying to insert, mod_txt[i] exists already, then there is no need to insert it. Apply Rule 3 
                        # do nothing.
                        elif mod_txt[i] == mod_txt[extension_point]:
                            # write runlog
                            log.write("    Extn " + str(j+1) + ' applies Rule 3\n')
                            rem_str = ''
                            if rem == None:
                                rem_str = 'EMPTY'
                            else:
                                rem_str = 'S[' + str(rem[0]+1) + '...' + str(rem[1]+1) + ']'
                            log.write("    Active Node = Node " + str(active_node.id) + ' (suffix link to Node ' + str(active_node.suffix_link.id) + "); " + "Remainder = " + rem_str +'\n') 

                            # for phase i, extend the remainder to add the character from mod_txt[i] to it 
                            if rem != None:
                                rem = [rem[0], rem[1] + 1]
                            else:
                                rem = [i, i]

                            # resolve pending suffix link 
                            # if in the previous extension there was newly created internal node, it would be saved in pending_suflink_node
                            # point its suffix link to the current active node to resolve it 
                            if pending_suflink_node != None:
                                pending_suflink_node.suffix_link = active_node
                                log.write("        Linking Node " + str(pending_suflink_node.id) + ' to Node ' + str(active_node.id) + '\n') 
                                # pending_suflink_node reset back to none after the suffix link of the node has been resolved
                                pending_suflink_node = None

                            # Trick 3: showstopper, early termination of current phase and move the next phase 
                            # note that once this phase is terminated through the showstopper trick in rule 3, the j would not be incremented and would automatically be the last j
                            # to be used as the start of extension in the next phase, which means the j would always start as the last j in each phase 
                            break
                    
                    # If theres no existing branch for the new character to be inserted in phase i, mod_txt[i], create a new branch with Rule 2 Alternate, where 
                    # we will create a new leaf node with an edge connecting the active node to the new leaf starting from index i and ending at GE since its a leaf.
                    elif active_node.children[ord(mod_txt[i]) - alphabet_start] is None:
                        
                        # write runlog 
                        rem_str = ''
                        if rem == None:
                            rem_str = 'EMPTY'
                        else:
                            rem_str = 'S[' + str(rem[0]+1) + '...' + str(rem[1]+1) + ']'

                        log.write("    Extn " + str(j+1) + ' applies Rule 2 (alternate)\n')
                        log.write("    Active Node = Node " + str(active_node.id) + ' (suffix link to Node ' + str(active_node.suffix_link.id) + "); " + "Remainder = " + rem_str + '\n') 

                        # create new leaf node to insert the character mod_txt[i], so the edge connecting the active node to this leaf node should be [i, GE], since it is 
                        # a leaf node, the edge connecting to the leaf node should end at the GE. Also, increment the ID before assigning to the new leaf node
                        current_node_id_counter += 1
                        new_leaf = node(current_node_id_counter, i, global_end)
                        active_node.children[ord(mod_txt[i]) - alphabet_start] = new_leaf
                        new_leaf.parent = active_node
                        log.write("        Node " + str(new_leaf.id) + ' created: Leaf node!\n') 

                        # update last j
                        last_j = j

                        # resolve pending suffix link from prev extn. Connect the node with unresolved suffix link to the current active node to resolve it 
                        if pending_suflink_node != None:
                            pending_suflink_node.suffix_link = active_node
                            log.write("        Linking Node " + str(pending_suflink_node.id) + ' to Node ' + str(active_node.id) + '\n') 
                            pending_suflink_node = None

                        # Follow suffix link out of the active node and find the next active node
                        active_node = active_node.suffix_link
                        if active_node == root:
                            # if we are at the root, following the suffix link out would end up at the root again since the suffix link of root links to itself.
                            # reduce 1 character from rem if we are at the root node and following suffix link leads back to the root node
                            if rem != None:
                                if rem[0] + rem_len <= rem[1]:
                                    rem = [rem[0] + rem_len, rem[1]]
                                else:
                                    rem = None
                    
                    # increment j to go to the next extension, note that only all rule 2 reg and alt will increment the j 
                    j += 1

            # return the root node such that the suffix tree could be accessed 
            return root
    
    def compute_lcp(self):
        with open("output_a2q1.txt", "w") as out:
            
            # Assume that SA[0...n-1] is the suffix array that stores the suffix that starts from the corresponding index i in the suffix,
            # for example, assume the string abc, the substring 'bc' that begins at index i = 1 would be store at position of index 1 in SA. 
            # lcp array is used to store the length of the longest common prefix (lcp_len) of the suffix that begins at index i-1 (SA[i−1]) and 
            # the suffix that begins at index i (SA[i]) at position index i in the lcp array.
            lcp_array = [None for _ in range(len(self.mod_txt))]

            # The idea is to simulate traversal through the suffix tree, where we will be using a stack for DFS traversal and maintain states during traversal. 
            # A state tuple takes the form of the (cur_node, cur_depth, cur_lcp_len), where
            # - cur_node is the current node visited during suffix tree traversal 
            # - cur_depth is the total depth taken to reach cur_node from the root node 
            # - cur_lcp_len is the length of the longest common prefix of the substring formed by the edges leading to the current node from root compared with 
            # the previous suffix formed by the leaf to the left of the current node in the suffix tree 
            # Since suffix tree traversal would start from the root node, initialise the starting state with the root node, where the depth of the 
            # root node in the tree is 0 and the lcp length of the root node is initialised as 0 (no lcp is possible so len is 0)
            stack = [] 
            suf_tree_root_node = self.root
            depth = 0
            lcp_len = 0 
            cur_state = (suf_tree_root_node, depth, lcp_len)
            stack.append(cur_state)

            # By observing a suffix tree, we can notice that all the leaf nodes in the suffix tree (from left to right) are in the same order as the suffix array
            # meaning that path from root to the leftmost leaf in the suffix tree would represent SA[0], the path to 2nd leaf would be SA[1] and so on. This is because the
            # suffix tree stores all suffixes lexicographically.
            # Since we use a stack and we push in all the states representing the children nodes of the current node lexicographically, we will actually traverse the tree in 
            # reverse lexicographical order and thus the first suffix that we explore should be the rightmost leaf (more details below)
            current_leaf_explored = len(self.mod_txt)
            
            while stack:
                current_state = stack.pop()
                current_node = current_state[0]
                current_depth = current_state[1]
                current_lcp_len = current_state[2]

                # if the current node has an incoming edge that ends at the last character of mod_txt (ep = len(mod_txt)-1), the current node is a leaf.
                # Since we traverse the leaves of the suffix tree in reverse lexicographocal order, we will explore all suffixes in reverse lexicographocal order too and thus
                # we will also write the values of the lcp_array in reverse order.
                # Since the current_leaf_explored is initialised as len(txt), by decrementing by 1 everytime, we will get the current 
                # suffix's index in reverse, corresponding to the reverse order traversal of the suffix tree.
                # At index i = current_leaf_explored, record the calculated lcp len to lcp_array[i] to store the lcp length between suffixes SA[i-1] and SA[i] 
                if current_node.ep.ep == len(self.mod_txt) - 1:
                    current_leaf_explored -= 1
                    lcp_array[current_leaf_explored] = current_lcp_len
                

                # if the current node is an internal node / root, push all their children into the stack in alphabetical order 
                # since it is a stack, and children nodes are pushed in alphabetical order, this would result in the suffix tree being
                # traversed in reverse lexicographical order due to the stack's LIFO property. 
                else:                    
                    # under_same_internal boolean flag represents whether the child node of the current internal node is under the same 
                    # same current internal node as the previous child node pushed in.
                    # Since the children nodes of the current node are pushed into the stack in alphabetical order, for the first children
                    # node to be pushed in, there will be no other nodes that are under the same parent as it, thus under_same_internal is initialised
                    # as false.
                    under_same_internal = False
                    
                    # iterate through all children in lexicographical order 
                    for child in current_state[0].children:
                        if child is not None:
                            edge_to_child = child

                            # for all existing child nodes of the current node, 
                            # calculate the depth of the child node, which is the total len of all edges needed to reach the child node from the root node  
                            child_node_depth = current_depth + edge_to_child.ep.ep - edge_to_child.sp + 1
                            
                            # if under_same_internal is True, meaning this is not the first (leftmost) child node of the subtree formed by the current internal node, 
                            # and there are other children nodes of this internal node before this current child node in the tree (at the left of this child node).
                            # Thus, the LCP len of this current child node and the previous child node would be the depth of their deepest common parent internal node 
                            # (which is the depth of the current internal node), as the fact that they share a parent internal node means they share a same path from root 
                            # to reach them means that they share the same substring before branching out as 2 different children nodes.
                            if under_same_internal:
                                new_lcp_len = current_depth
                                stack.append((edge_to_child, child_node_depth, new_lcp_len))
                            
                            # if under_same_internal is False, meaning this is the first (leftmost) child node of the subtree formed by the current internal node, 
                            # and there are no other children nodes before this first child node (to the left of this child node) under the current internal node.
                            # Thus, the lcp len of this child node and the previous child node before it from another subtree should be based on their deepest common parent 
                            # internal node, which is not the current parent node, but rather a shared ancestor node of the current parent node and the parent of the child node 
                            # to the left of the current parent node. 
                            # Therefore, the lcp length of this child node should inherit the LCP length of the current internal node. 
                            else:
                                stack.append((edge_to_child, child_node_depth, current_lcp_len))
                                under_same_internal = True

            # write out all computed lcp lengths to the output 
            for i in range(len(lcp_array)):
                lcp_val = lcp_array[i]
                if i != len(lcp_array)-1:
                    out.write(str(lcp_val) + '\n')
                else:
                    out.write(str(lcp_val))

        return lcp_array
            

if __name__ == '__main__':  
    _, filename1 = sys.argv

    file1content = read_file(filename1)

    # read the input string and append terminal '$' to its end
    txt = file1content[0].strip()
    mod_txt = txt + '$'

    suf_tree = suffix_tree(mod_txt)
    suf_tree.compute_lcp()

    
    