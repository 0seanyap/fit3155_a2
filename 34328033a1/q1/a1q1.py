# Yap Meng Hin (34328033)
#

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

def zalgo(inp_str: str):
    """
    Z Algorithm function to compute the z-array for the input pat.

    """
    # initialise z aray to be the size of input string
    # Time, Space comp: O(m), where m is the len of the inp_str
    zarr = [0 for i in range(len(inp_str))]
    
    # define the L, and R for the rightmost z-box
    # where R is the right most end of the rightmost z-box
    # L is the left end of the z-box that ends at R
    # at the start there are no z-boxes yet so both are initialised to 0
    L = 0 
    R = 0

    # Time comp: O(m) 
    for k in range(1, len(inp_str)):
        # case 1: k is out of the rightmost z-box, no info from the previous z-box to reuse
        if k > R:
            # perform explicit comparison from input_str[k....] vs input_str[1....] until a mismatch is found or we reach the end of the string
            # for each match, increment the z value of k by 1 and move on to compare the next corresponding char 
            j = 0 
            while k + zarr[k] < len(inp_str) and inp_str[k + zarr[k]] == inp_str[j]:
                zarr[k] += 1
                j += 1

            # only update L and R if a new Z-box is formed at k (z value of k > 0)
            # update L to k to represent the start of the z-box
            # update R to the right end of the z-box starting from k
            if zarr[k] > 0: 
                L = k
                R = L + zarr[k] - 1
        
        # case 2: k is within the rightmost z-box, reuse info from the previously computed z-values
        else:
            # case 2a: k is within z-box and z[k] < remaining 
            if zarr[k - L] < R - k + 1:
                # set z(k) to its mirror in the prev z-box: z(k - L)
                zarr[k] = zarr[k - L]

            # case 2b: k within z-box but z[k] >= remaining 
            elif zarr[k - L] >= R - k + 1:
                j = 1
                zarr[k] = R - k + 1
                # explicit comparison from R+1
                # while R + j < len(inp_str) and R - k + m < len(inp_str) and inp_str[R + j] == inp_str[R - k + j]:
                while R + j < len(inp_str) and inp_str[R + j] == inp_str[R - k + j]:
                    zarr[k] += 1
                    j += 1
                    # m += 1
                L = k
                R = L + zarr[k] - 1

    return zarr

def compute_sp_array(pat: str):
    """
    Function to preprocess the input string (pat) amd compute the SP(i) values for each char at index (i) in pat, 
    where 0 ≤ i ≤ len(pat)-1 (0-based perspective). 
    
    The SP(i) values represent the length of the longest substring in pat that ends at index SP(i)
    that matches with the prefix pat[0....SP(i)] such that pat[i+1] != pat[SP(i)+1]
    """
    # compute z array of the input pat to get the length of longest substrings in pat that matches the prefix for every index
    z_array = zalgo(pat)
    
    # initialise the sp_array to the size of the input pat, which stores the length of substring that matches a prefix and ends at index i 
    # for each index i in sp_array
    m = len(pat)
    # Time comp: O(m) 
    sp_array = [0 for _ in range(m)]

    # Since the sp value of i should store the length of the longest substring in pat that matches with a prefix 
    # And since thee z array already gives the length of longest substrings in pat that matches the prefix for every index j
    # for each z-value z_array[j], calculate the ending index (i) of the substring with the length of that z-value
    # Time comp: O(m) 
    for j in range(m - 1, 0, -1):
        # simply assign the z-value z_array[j] to index i in sp_array to represent the length of the longest suffix that matches the prefix 
        # that ends at index i to match the definition of the sp array
        i = j + z_array[j] - 1
        sp_array[i] = z_array[j]     

    return sp_array

def compute_reverse_sp_array(pat: str):
    # since we are doing right to left scanning in pat, we need to find the sp values with reference to the right end of pat
    # which means the prefix will be viewed as starting from the right end of pat and the sp values will be the length of longest 
    # substring from right to left that matches the prefix from the right end of pat 

    # To achive that, compute the sp array of the flipped input string, 
    # then flip the resultant SP array to yield the reverse (right to left) sp array with reference to the right end of pat
    return  compute_sp_array(pat[::-1])[::-1]

def compute_p_index_table(pat: str):
    """
    Function to preprocess pat, and return a table which stores which index of the pat should be aligned to under the assignment constraints 
    during right to left scanning in pat. Values can be accessed using the form p_table[k+1][char], when mismatch occured at index k of pat 
    and the mismatched char in txt is char. 
    """
    
    # compute the sp array with referring to the right end of pat for right to left scan
    sp_array = compute_reverse_sp_array(pat)
    
    m = len(pat)
    alphabet_start = 37
    alphabet_end = 126
    alphabet_range = alphabet_end - alphabet_start 

    # All values are initialised to m, which is the length of pat
    # In 0 base indexing, this would represent the position to the right of the rightmost char of pat at index m-1
    # This table supports O(1) lookup for which index is p (character preceding β in pat) located at in the pat when mismatch occurs at 
    # index k-1 by accessing p_table[k][char], where char is the mismatched character from txt.
    p_table = [[m for _ in range(alphabet_range)] for _ in range(m+1)]
    # Note that the table is initialised to have an extra mth row to handle the scenario where mismatch occurs at the rightmost pos of pat (index m -1)

    # Simulate right to left scan in pat
    for k in range(m-1, -1, -1):
        # For each k, we simulate the scenario where we have scanned up until position k-1 in pat and encountered a mismatch, which would define α.
        # Using the sp value with reference to the right end of pat, we can find the len of subtring that ends at k, and thus compute the 
        # index where β ends (position p), and obtain the char preceding β in pat, p_minus_1_char.
        spk = sp_array[k]
        p_minus_1_char_index = m - 1 - spk
        p_minus_1_char = pat[p_minus_1_char_index]

        # To support the lookup as mentioned, simply store the index of where the char preceding β in pat, p_minus_1_char in p_table[k][p_minus_1_char]. 
        index_to_store = ord(p_minus_1_char) - alphabet_start
        p_table[k][index_to_store] = p_minus_1_char_index
    
    return p_table
    
# Note: i am aware that this function has some slight code repetition and could be further simplified, but due to me being late for submission already
# i believe it would be best that i leave it be first... (very unfortunate)
def right_to_left_search(txt, pat):
    with open("output_a1q1.txt", "w") as out, open("runlog_a1q1.txt", "w") as log:
        n = len(txt)
        m = len(pat)
        alphabet_start = 37

        # preprocess the pat 
        p_index_table = compute_p_index_table(pat)

        # Define important positions according to Question 1 (all in 0 based indexing)
        # j is defined as the index in txt that corresponds to index 0 of pat, used to keep track where pat is with reference to txt
        j = n - m

        # k is the pointer used during the right to left scan in pat, where it represents the current index the scan is at
        # j_plus_k_minus_1 represents the current index in txt that corresponds to the index of pointer k in pat during right to left scan of pat
        # Notice that k and j_plus_k_minus_1 are initialised outside of pat and txt respectively in 0 base
        # The pointers will be shifted leftwards when the search loop starts, which will automatically align to the rightmost position of pat and txt in the 
        # 1st iteration
        k = m
        j_plus_k_minus_1 = j + k 
        

        # Search loop
        # Continue shifting pattern leftwards as long as pat does not exceed the txt at the left 
        # If pat exceeds txt at the left, no more possible matches can be found, exit the search loop
        while j >=0:
            
            # shift k and j_plus_k_minus_1 leftwards by 1 in each iteration to simulate right to left search of txt with pat
            k -= 1
            j_plus_k_minus_1 = j + k


            # Case 1: char at index k in pat matches with char at index j_plus_k_minus_1 in txt
            # Continue right to left scan for pat against txt until a mismatch is found or the whole pat has been scanned through
            while k >= 0 and pat[k] == txt[j_plus_k_minus_1]:
                # shift k left by 1 and update j_plus_k_minus_1 accordingly  
                k -= 1
                j_plus_k_minus_1 = j + k

            # Either whole pat has been scanned through (full match) or mismatch is encountered while still scanning within pat 
            
            # Case 2: Mismatch encountered at index k of pat and j + k -1 of txt, α is defined. 
            # Get the char at position j + k -1 in txt when mismatch occured. 
            j_plus_k_minus_1_char = txt[j_plus_k_minus_1]
            # Lookup the p_index_table using index k + 1 and the char to obtain the index of position p-1 (character preceding prefix β)
            # Compute position p, which marks the leftmost index defining the prefix β
            p_minus_1 = p_index_table[k+1][ord(j_plus_k_minus_1_char) - alphabet_start]

            # write runlog <j> <k+1> <p>  
            # handle special case where if the pattern matches the txt at index 0 of txt, 
            # the next iteration should techically safely shift and align to the end of pat and skip by 1 pos 
            if j == 0:
                log.write(str(j) + " " + str(k + 1) + " " + str(m) + "\n")
            
            else:
                # handles case where:
                # 1. after match, we need to shift through the whole pat
                # Since my table would return m by default if mismatch at first, there is no need to modify the value already.
                if p_minus_1 == m:
                    log.write(str(j) + " " + str(k + 1) + " " + str(m) + "\n")

                # handles normal case, where:
                # after match, the mismatch char at j+k-1 position j+k-1 in txt == char at p-1 in pat (char preceding β)
                # both conditions are satisfied, calculate p by adding 1 tp p_minus_1
                elif p_minus_1 < m:
                    p = p_minus_1 + 1
                    log.write(str(j) + " " + str(k + 1) + " " + str(p) + "\n")


            # Case 2.1: Pattern matched and found in text When mismatch occur after scanning through the whole pat
            # when pattern is matched, the mismatch would occur at index -1 of pat (we have gone thorugh the whole pat)
            if k < 0:
                # write matched position in txt in 1 based indexing to output
                matched_j_index_1_based = j + 1
                out.write(str(matched_j_index_1_based) + "\n") 

                # Since the table already tells us where is p_minus_1
                # shift the pattern leftwards by p - 1- k
                shift = p_minus_1 - k
                j -= shift

                # shift and align k to the p_minus_1 index obtained from the table and continue the next iteration in the next position
                k = p_minus_1 

            # Case 2.2: Mismatch found when still scanning within pat
            elif k >= 0:
                if p_minus_1 == m:                   
                    # handles case where:
                    # 1. if the scan mismatches at the rightmost character in pat, 
                    # 2. if the scan mismatches at position j+k-1 in txt, and the char at j+k-1 != char at p-1 in pat (char preceding β)
                    # These cases results in α and β being empty and p = m + 1 as defined by the assignment spec (1 based indexing)
                    # For 0-based indexing approach, this would mean when mismatch at first, index p = (m-1) + 1 = m 
                    # Since my table would return m by default if mismatch at first, there is no need to modify the value already.

                    # shift the pattern leftwards by p - 1- k
                    shift = p_minus_1 - k
                    j -= shift
                    
                    # shift and align k in pat to the p_minus_1 position, which is m in this case
                    # therefore, in next iteration, we will start scanning right to left from index m-1 in pat again 
                    k = p_minus_1 
                           
                elif p_minus_1 < m:
                    # handles case where:
                    # 1. if the scan mismatches at position j+k-1 in txt, and the char at j+k-1 == char at p-1 in pat (char preceding β)
                    # shift and align accordingly to the p_minus_1 index provided from the table. 
                    p = p_minus_1 + 1
                    
                    # shift the pattern leftwards by p - 1- k
                    shift = p_minus_1 - k
                    j -= shift

                    # shift and align k to the p_minus_1 index obtained from the table and continue the next iteration in the next position
                    k = p_minus_1 
    return 
            
if __name__ == '__main__':  
    _, filename1, filename2 = sys.argv

    # print("Number of arguments passed : ", len(sys.argv))

    # since we know the program takes two arguments
    # print("First argument : ", filename1)
    # print("Second argument : ", filename2)

    file1content = read_file(filename1)
    # print("\nContent of first file : ", file1content)
    file2content = read_file(filename2)
    # print("\nContent of second file : ", file2content)

    txt = file1content[0]
    pat = file2content[0]

    right_to_left_search(txt, pat)
