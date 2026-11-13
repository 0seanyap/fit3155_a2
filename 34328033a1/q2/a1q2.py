# Yap Meng Hin (34328033)

import sys

def read_file(file_path: str) -> str:
    """
    Function to read a file from the specified input file path 

    input: 
        file_path - a string representing the path to the input file
    output: 
        a string representing the content in the file

    """
    f = open(file_path, 'r')
    line = f.readlines()
    f.close()
    return line

def compute_suffix_array(mod_txt: str):
    """
    Function to compute the suffix array for the input txt (assumed to be terminated by $).
    Where the suffix array stores the suffix ID which is the index i of suffixes starting at index i towards 
    the end of the input txt, [i...n-1] for all index i in txt. 
    """
    n = len(mod_txt)

    # Generate all suffixes of input mod_txt starting at index i  
    suffixes = ["" for _ in range(n)]
    for i in range(n):
        current_suffix = mod_txt[i:]
        suffixes[i] = current_suffix

    # Sort the generated suffixes lexicographically
    suffixes.sort()
    suffix_array = [0 for _ in range(n)]

    # Store the index of the starting character of the suffix (suffix ID) by simply subtracting the 
    # len of the suffixes with the total len of the string to get its starting char index in mod_txt
    for j in range(len(suffixes)):
        suffix_pos = n - len(suffixes[j])
        suffix_array[j] = suffix_pos

    return suffix_array

def compute_bwt(mod_txt: str):
    """
    Function to compute the bwt string of the input string (assumed to be terminated by $), which corresponds
    to the last column (L) of the cyclic permutation matrix of the input string
    """
    # compute the suffix array for the input string mod_txt
    sa = compute_suffix_array(mod_txt)
    n = len(sa)

    bwt = ["" for _ in range(n)]

    for i in range(n):
        # for each suffix ID from suffix array, compute (suffix ID - 1) to get the bwt index which is the 
        # character preceding the suffix due to the cyclic property 
        suffix_index = sa[i]
        bwt_index = suffix_index - 1

        if bwt_index >= 0:
            bwt[i] = mod_txt[bwt_index]

        # wrap the index due to cyclic property when the computed bwt index is negative
        elif bwt_index < 0:
            bwt[i] = mod_txt[n + bwt_index]
    
    # join the list of chars and return the bwt string 
    return "".join(bwt)

def build_rank_table(mod_txt):
    """
    Builds the rank table data structure which corresponds to the first column (F) of the cyclic permutation 
    matrix of the input text
    """
    terminal = 36       # ASCII value for the terminal character $
    alphabet_start = 37
    alphabet_end = 126
    alphabet_range = alphabet_end - terminal + 1

    n = len(mod_txt)

    counts = [0 for _ in range(alphabet_range)]
    # Note that rank starts from 0 for 0 based implementation 
    rank = [0 for _ in range(alphabet_range)]

    # count frequency of each character in the input text
    for i in range(n):
        txt_char = mod_txt[i]
        char_rank_index = ord(txt_char) - terminal
        counts[char_rank_index] += 1

    # build rank table such that at index i of the table, we can know the sum of count for all lexicographical 
    # smaller characters 
    rank[0] = 0
    # note that we start from 1 here to skip counting the rank of the terminal char (default as 0)
    for i in range(1, alphabet_range):
        rank[i] = rank[i-1] + counts[i-1]
    
    return rank 

def build_nOccurences(bwt: str):
    """
    Build the nOcc data structure, which stores the number of occurences for any character at any range i. 
    Where nOcc[i][c] stores the number of occurrences of character c before index i in the bwt (exclusive) 
    """
    terminal = 36
    alphabet_start = 37
    alphabet_end = 126
    n = len(bwt)

    # each row i in in nOcc would store the number of occurrences of character c before index i (exclusive) 
    # in the bwt
    nOcc = [[0 for _ in range(alphabet_end - terminal + 1)] for _ in range(n+1)]
    # helper array to store the running counts of each character 
    runC = [0 for _ in range(alphabet_end - terminal + 1)]

    # store the number of occurences for each character before each index i 
    for i in range(n):
        nOcc[i] = runC.copy()
        # update running count afterwards to update the count for the current char at i
        runC[ord(bwt[i])-terminal] += 1

    # construct the nth row to handle inclusion case for the char at the last index, which js stores 
    # counts for all characters for the full bwt string 
    nOcc[n] = runC.copy()
    return nOcc

def q2_search(txt, pat, bwt):
    with open("output_a1q2.txt", "w") as out:

        # unique terminal char is set as '$' 
        terminal_char = '$'
        terminal_char_index = ord(terminal_char)

        # define start, end and range of alphabet  
        alphabet_start = 37
        alphabet_end = 126
        alphabet_range = alphabet_end - alphabet_start + 1
        
        # n is defined as the length of text, m is defined as length of pattern
        n = len(txt)
        m = len(pat)

        # initialise the result_edit_distant list, where each index i corresponds to the same index in txt and would 
        # store the edit distance for matches found starting at index i in the txt. Initialise all positions to 
        # be -1 at the start 
        result_edit_distant = [-1 for _ in range(n)]

        # compute the suffix array, rank table and nOcc data structure to be used in pattern matching 
        sa = compute_suffix_array(txt)
        rank = build_rank_table(txt)
        nOcc = build_nOccurences(bwt)
         

        # To handle the cases with edit distance of 1, we would need to try to match different combinations of the 
        # pattern with the text to explore all possible ways the pattern can be editted to match with parts of the text 
        # This would form a search tree with branches from each position in the pattern as we use BWT as a search index during 
        # backwards search of the pattern. 
        # Therefore, the idea is to represent each iteration as states, which would be allow us to fully explore a branch before 
        # moving on to another branch of another combination and explore all possible combinations of edit distance <= 1 for 
        # each case using a stack due to its LIFO property 
        stack = []
        
        # A state tuple takes the form of the(index, sp, ep, edit_dist), where 
        #  -index is the current index in the pattern during backward search
        #  -sp is the lower bound of the search range up until this state
        #  -ep is the upper bound of the search range up until this state
        #  -edit_dist is the accumulated number of edit distance up until this point 
        # initialise the initial state tuple, start backwards search from the last index of pattern 
        # with the initial values of the search range in bwt, sp being 0 and ep being n-1 
        # and edit distance = 0 at the start 
        initial_pat_index = m-1
        sp = 0
        ep = n-1
        edit_dist = 0
        stack.append((initial_pat_index, sp, ep, edit_dist))

        # search through all possible valid states 
        while stack:
            current_state = stack.pop()
            curr_pat_index = current_state[0]
            sp = current_state[1]
            ep = current_state[2]
            edit_dist = current_state[3]

            # prune and ignore branches with an edit distance > 1 as they are invalid already 
            if edit_dist > 1:
                continue

            # base case: if the index reached < 0 in backwards search, it means the branch leading 
            # to this state has fully searched through the pattern, ensure that the branch leading to 
            # this state has at most edit distance of 1 and the sp, ep range is valid 
            if curr_pat_index < 0 and edit_dist <= 1 and sp <= ep:
                # loop through the search range defined by sp and ep to get all the index of suffixes
                # that matched the combination leading to this state 
                for i in range(sp, ep+1):
                    suffix_start_index = sa[i]
                    if suffix_start_index < n-1: 
                        # sa[i] would give us the index of where the suffix starts in txt, so to record where
                        # a match occured, we simply set the corresponding index suffix_start_index in result_edit_distant array to
                        # the edit distance. Note that if theres already an existing record at index suffix_start_index, the  
                        # edit distance 0 would take precedence, meaning dont overwrite existing result_edit_distant[suffix_start_index] 
                        # that has an edit distance of 0
                        if result_edit_distant[suffix_start_index] == -1:
                            result_edit_distant[suffix_start_index] = edit_dist

                        # handles case where edit distance is 0, overwrite existing as 0 would take precedence
                        elif result_edit_distant[suffix_start_index] != -1 and edit_dist == 0:
                            result_edit_distant[suffix_start_index] = edit_dist
                            # whenever a full match is found, as long as the suffix forming the full match
                            # does not start at index 0 of the text, any character to the left of the full match
                            # would also satisfy the insertion case with edit distance of 1
                            # example: 
                            # txt = abcd, pat = bcd, if we find a full match at the suffix starting from index 1
                            # in txt, index 0 would also satisfy the insertion case (insert 'a' in front of pat) and
                            # should have edit distance set to 1
                            if result_edit_distant[suffix_start_index] == 0 and suffix_start_index !=0:
                                result_edit_distant[suffix_start_index-1] = 1


            # case where the pattern has not been fully searched through in backwards search
            elif curr_pat_index >= 0:

                # only handle valid states with edit_dist <= 1 and prune invalid branches
                if edit_dist <= 1:
                    current_pat_char = pat[curr_pat_index]

                    # 1. Handle Edit-distance += 0 case: handle normal full match
                    # simply update the sp_normal and ep_normal using normal backward search L-F mapping rules
                    # note that since the nOcc for updating ep_normal needs to be inclusive of ep, while the nOcc data structure is exclusive
                    # we will access nOcc[ep+1] to include ep, same for all below cases
                    sp_normal = rank[ord(current_pat_char)-terminal_char_index] + nOcc[sp][ord(current_pat_char)-terminal_char_index]
                    ep_normal = rank[ord(current_pat_char)-terminal_char_index] + nOcc[ep+1][ord(current_pat_char)-terminal_char_index] - 1 
                    # if the sp_normal and ep_normal search range is valid, push the next state with:
                    #  - index reduced by 1 (move on to the next character leftwards)
                    #  - the updated sp_normal index value
                    #  - the updated ep_normal index value
                    #  - edit_dist remains same (no edit operations performed)
                    if sp_normal <= ep_normal:
                        stack.append((curr_pat_index-1, sp_normal, ep_normal, edit_dist))

                    # 2. Handle Edit-distance += 1 cases:
                    # Only states with edit distance of 0 are allowed to simulate Edit-Distance 1 cases as the edit distance must be <= 1
                    # States with edit distance of 1 will not be allowed to perform edit operations as it would result in states with > 1 edit distance
                    if edit_dist == 0:

                        # 2.1 Substitution case, edit distance +=1
                        # Branch out and substitute in all possible characters from the alphabet to the curr index in pattern and run backwards search 
                        # with the substituted character for each branch 
                        for alpha_c in range(alphabet_range):
                            cur_alpha_char = chr(alpha_c + alphabet_start)
                            # Apply LF-mapping for each possible alphabet character starting from the curr_pat_index
                            # update the sp_sub and ep_sub search range index values with the substituted alphabet character 
                            if cur_alpha_char != current_pat_char:
                                sp_sub = rank[ord(cur_alpha_char)-terminal_char_index] + nOcc[sp][ord(cur_alpha_char)-terminal_char_index]
                                ep_sub = rank[ord(cur_alpha_char)-terminal_char_index] + nOcc[ep+1][ord(cur_alpha_char)-terminal_char_index] - 1

                                # for each substituted alphabet char, if the sp_sub and ep_sub search range is valid, push the next state with:
                                #  - index reduced by 1 (move on to the next character leftwards)
                                #  - the updated sp_sub index values
                                #  - the updated ep_sub index values
                                #  - edit_dist + 1 
                                if sp_sub <= ep_sub:
                                    stack.append((curr_pat_index-1, sp_sub, ep_sub, edit_dist+1))

                        # 2.2 Transposition case, edit distance+= 1
                        # To simulate transposition, for each possible index i in pattern, where i > 0 (we cant swap with any char to the left anymore if i = 0),
                        # swap the position of character at i and with the character to its left at i - 1.
                        if curr_pat_index > 0:
                            # we get the current_pat_char at curr_pat_index and the next_pat_char at the left of it 
                            current_pat_char = pat[curr_pat_index]
                            next_pat_char = pat[curr_pat_index-1]

                            # To simulate transposition, we treat the pattern as if we first encountered next_pat_char before current_pat_char and perform L-F mapping
                            # to update the search range sp_trans and ep_trans value
                            # For example, pat = "abcd", if transposition between c and d, we would first perform handle d first then followed by c to simulate transposition. 
                            sp_trans = rank[ord(next_pat_char)-terminal_char_index] + nOcc[sp][ord(next_pat_char)-terminal_char_index]
                            ep_trans = rank[ord(next_pat_char)-terminal_char_index] + nOcc[ep+1][ord(next_pat_char)-terminal_char_index] - 1 
                            
                            # Then, followed by that, apply L-F mapping on the current_pat_char and update the search range sp_trans_final and ep_trans_final value based on
                            # the sp_trans and ep_trans of the transpositioned next_pat_char (if the search range produced by the transpositioned next_pat_char is valid)
                            if sp_trans <= ep_trans:
                                sp_trans_final = rank[ord(current_pat_char)-terminal_char_index] + nOcc[sp_trans][ord(current_pat_char)-terminal_char_index]
                                ep_trans_final = rank[ord(current_pat_char)-terminal_char_index] + nOcc[ep_trans+1][ord(current_pat_char)-terminal_char_index] - 1 
                                
                                # if the final search range after transposition is valid 
                                #  - reduce index by 2, as we have went through 2 characters consecutively 
                                #  - the updated search range sp index value, sp_trans_final
                                #  - the updated search range ep index value, ep_trans_final
                                #  - edit_dist + 1 
                                if sp_trans_final <= ep_trans_final:
                                    stack.append((curr_pat_index-2, sp_trans_final, ep_trans_final, edit_dist+1))

                        # 2.3 Insertion case, edit distance+= 1, 
                        # Branch out and simulate a character insertion for each possible alphabet character by performing an extra backwards search step on the 
                        # inserted character instead of the original character at curr_pat_index in pattern. 
                        for alpha_c in range(alphabet_range):
                            cur_alpha_char = chr(alpha_c + alphabet_start)

                            # To simulate inserting each of the alphabet_char, perform L-F mapping for all of the inserted alphabet_char
                            # and update the search range values sp_ins and ep_ins
                            sp_ins = rank[ord(cur_alpha_char) - terminal_char_index] + nOcc[sp][ord(cur_alpha_char) - terminal_char_index]
                            ep_ins = rank[ord(cur_alpha_char) - terminal_char_index] + nOcc[ep + 1][ord(cur_alpha_char) - terminal_char_index] - 1
                            
                            # Then, for each inserted alphabet_char, if the search range is valid, push the next state with:
                                #  - curr_pat_index unchanged, as adding a character would mean that we dont compare the actual character at 
                                #    curr_pat_index yet and instead compare the inserted alphabet char first. Thus, in the next iteration, the backwards
                                #    search should continue at the original character at curr_pat_index.  
                                #  - the updated sp_ins index values
                                #  - the updated ep_ins index values
                                #  - edit_dist + 1 
                            if sp_ins <= ep_ins:
                                stack.append((curr_pat_index, sp_ins, ep_ins, edit_dist +1))
                        
                        # 2.4 Deletion case, edit distance+= 1
                        # Simulate that the character at curr_pat_index is deleted, just ignore the curr index char in pat 
                        # and move on to the next curr_pat_index at curr_pat_index-1 without updating the search range formed by sp and ep 
                        sp_del = sp
                        ep_del = ep
                        # if the search range is valid 
                            #  - reduce index by 1 (move on to the next character leftwards)
                            #  - remain sp index value
                            #  - remain ep index value 
                            #  - edit_dist + 1 
                        if sp_del <= ep_del:
                            stack.append((curr_pat_index-1, sp_del, ep_del, edit_dist+1))
        
        # write all outputs from the result_edit_distant (non -1 values)
        # for each index i representing where a match with edit distance <= 1starts, add 1 to index i to represent in 1 based indexing
        for i in range(len(result_edit_distant)):
            if result_edit_distant[i] != -1:
                out.write(str(i+1) + " " + str(result_edit_distant[i]) + "\n")


if __name__ == '__main__':  
    _, filename1, filename2 = sys.argv

    file1content = read_file(filename1)
    file2content = read_file(filename2)

    txt = file1content[0]
    pat = file2content[0]
    
    # append $ to txt, where $ is lexicographocally smaller (36) than Σ with ASCII range [37,126]
    mod_txt = txt + '$'

    # since it is mentioned in the spec sheet that the method of bwt construction will not be assessed for 
    # complexity (and considering that my bwt implementation has quadratic complexity) I decided to split the 
    # bwt construction from the q2_match algorithm 
    bwt = compute_bwt(mod_txt)
    
    q2_search(mod_txt, pat, bwt)



