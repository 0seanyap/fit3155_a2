# Yap Meng Hin (34328033)
#

import sys
import random

def read_file(file_path: str) -> str:
    f = open(file_path, 'r')
    line = f.readlines()
    f.close()
    return line

def miller_rabin(n, k):
    """
    This function is an implementation of the Miller-Rabin randomised primality test used to test if a 
    input n is probably prime. Returns a single character 'c' if the input number n is a composite number,
    returns a single character 'p' if the input number n is probably a prime number. 

    This function is created by referencing the pseudocode provided in the class notes. 

    """

    #  handle special cases 
    if n == 2 or n == 3:
        return "p"
    
    # Handle cases where n is even as we only want to test odd integers 
    if n % 2 == 0:
        return "c"
    
    s = 0
    t = n-1
    while t % 2 == 0:
        s = s + 1
        # t // 2 here such that t is always updated is a whole number
        t = t // 2

    #  run k random tests
    for i in range(k):

        # select random witness w from the range 1 < a < n-1
        # since randint range is inclusive, we should use randint(2, n-2) to correctly reflect the range 
        w = random.randint(2, n-2)
        
        # check if n satisfies FLT for the witness w
        xs = mod_exponientiation(w, 2**s * t, n)
        if xs != 1:
            return 'c'

        # after FLT, also run the sequence test to avoid misclassifying pseudoprimes as prime
        for j in range(s):
            xj_min1 = mod_exponientiation(w, 2**j * t, n)
            xj = mod_exponientiation(xj_min1, 2, n)
            if xj == 1 and (xj_min1 != 1 and xj_min1 != n-1):
                return 'c'

    # if n has passed all tests, it is probably a prime number (there is a small chance that its incorrect)
    return 'p'

def convert_to_bin(inp_num):
    """
    Function to convert the input number, inp_num to its binary representation and returns a list with all digits 
    of the binary representation stored.
    """

    # list to store the binary representation of the inp_num 
    binary_val = []

    # Generate the binary representation of the inp_num starting from the least significant bit to the 
    # most significant bit by keep dividing the inp_str by 2 and getting the remainder, which represents a bit in the 
    # binary representation of inp_num. This would result in the binary_val storing the binary representation of inp_num
    # in reverse (from least significant bit to most significant bit ), thus in the end, we reverse the binary_val list to get the 
    # actual binary representation of inp_num before returning it. 
    while inp_num > 0:
        rem = inp_num % 2
        inp_num = inp_num // 2
        binary_val.append(rem)

    # get the binary representation in correct order
    binary_val.reverse()
    return binary_val

def mod_exponientiation(a, b, n):
    """
    Function to perform modular exponientiation a^b mod n based on the input params using repeated squaring and processes 
    the binary representation of the exponent b in the order of from the least significant bit to the most significant bit.

    This function is created by referencing the pseudocode provided in the applied 7 solution. 
    """
    r = 1

    # convert the exponent b to binary representation first
    b_binary_rep = convert_to_bin(b)

    for i in range(len(b_binary_rep)):
        r = (r*r) % n
        if b_binary_rep[i] == 1:
            r = (r*a) % n
    return r 

def r(inp_str, prime_num):
    """
    Function to map an input string to an integer (mod a prime number, prime_num), which is the r value of the input string.   
    
    """
    alphabet_start = 0
    alphabet_end = 127
    # use beta as the base which is 128 
    beta = 128 

    k = len(inp_str)
    z_inp_str = 0

    # Compute the z(inp_str) value using beta as the base, where for each character inp_str[i], 
    # compute: index(inp_str[i]) * beta ^ (k-1-i) and sum up the computed values for all characters in inp_str. 
    # Note that index(i) means the index of the character inp_str[i] in the alphabet. 
    for i in range(k):
        z_inp_str += ord(inp_str[i]) * beta ** ((k - 1) - i)

    # based on definition in specs sheet, compute r(inp_str) = z(inp_str) mod p and return it 
    r_inp_str = z_inp_str % prime_num

    return r_inp_str

def match(txt, pat):
    """
    Function to perform exact pattern matching to find the index positions where the pat fully matches the txt
    and writes it to the runlog in 1 based indexing by first testing random candidates until a prime number p is 
    found. Then, the r value of the pat, r_pat is computed with the prime value p. 
    Next, we slide a window with a length of the pattern length through txt and compute the r value of the window, r_txt_window
    and see if it matches with r_pat. If it matches, we check the characters in the txt window and pat 1 by 1 and confirm if its 
    a full match found. 
    
    """
    with open("output_a2q2.txt", "w") as out:
        n = len(txt)
        m = len(pat)
        beta = 128
        # k represents the number of tests to be performed in Miller-Rabin algorithm, and is chosen as 
        # 64 based on slide 36/37 of the class slides 
        k = 64

        # randomly generate candidates from the range [2^(t-1), 2^t-1], where t=max(32, m) and test them for primality 
        # until a prime candidate is found
        chosen_candidate = 0
        is_prime = False 
        while not is_prime: 
            t=max(32,m)
            candidate = random.randint(2**(t-1), 2**t - 1)
            # test the generated candidate for primality with Miller-Rabin test, if the test reesult of Miller-Rabin
            # gives prime, then the candidate is probably a prime candidate and thus has been found and we can break the loop 
            test_res = miller_rabin(candidate, k)
            if test_res == 'p':
                is_prime = True
                chosen_candidate = candidate

        # Since now we know that the chosen_candidate is prime, we can map the pattern and the initial text window (txt[0:m]) to obtain 
        # their mapped r values. The mapped r values of the pattern and initial text window would then be compared and as part of the optimisation,
        # the mapped r value of the following text windows would be updated effectively as we slide the window across the text to try to find matches. 
        r_pat = r(pat, chosen_candidate)
        r_txt_window = r(txt[0:m], chosen_candidate)

        # Assume a text 'abcd', and pattern has a length of 3, this means the sliding window would also have a length of 3
        # First, the sliding window should start at 'abc', and if we work out the mapping on paper, it would be: ord(a)*beta^2 + ord(b)*beta^1 + ord(c)*beta^0
        # Now let's say we have done checking and we slide the window to the next position, which would align with 'bcd' in text. If we again work out the 
        # mapping on paper, it would be ord(b)*beta^2 + ord(c)*beta^1 + ord(d)*beta^0. 
        # Now by comparing them side by side:
        #           (ord(a)*beta^2 + ord(b)*beta^1 + ord(c)*beta^0)                 % p
        #                           (ord(b)*beta^2 + ord(c)*beta^1 + ord(d)*beta^0) % p 
        # we can see that they differ by removing the term wiith ord(a) and added the term ord(d)*beta^0 at the end, while all the other terms had their beta power
        # increased by 1.
        # Thus, to efficiently update the r value of the sliding window instead of recalculating it, we can simply minus the first (leftmost) term of it, multiply the remaining 
        # terms with beta and add the term at the end for the new character in the sliding window. Notice how the leftmost term will always have the same beta power, 
        # so save the first_term_beta_pow used in computing leftmost term to be used for calculations
        first_term_beta_pow_mod_p = mod_exponientiation(beta, m - 1, chosen_candidate)

        # slide the window through the text
        for j in range(n - m + 1):
            
            # if the mapped r value of the pattern matches the mapped r value of the text window, further check by comparing the text window and the pattern character 
            # by character
            if r_pat == r_txt_window:

                # check if the pattern matches the txt window char by char, if 1 mismatch occurs, break immediately as there is no way it can be a full match anymore 
                is_fully_match = True
                for i in range(m):
                    if pat[i] != txt[j+i]:
                        is_fully_match = False 
                        break
                
                # write to output if full match is found (in 1 based indexing)
                if is_fully_match:
                    out.write(str(j+1) + '\n')

            # Update the r value of the sliding window. First, minus the first term formed by the first char in the sliding window ord(first_char) * first_term_beta_pow mod p,
            # then multiply the remaining terms by beta and then add the term for the new_char_at_end and mod the result by chosen_candidate. This would 
            # give us the updated r value for the text window without the need of recomputing it from scratch every iteration
            if j < n - m:
                first_char = txt[j]
                new_char_at_end = txt[j + m]
                first_term = ord(first_char) * first_term_beta_pow_mod_p
                r_txt_window = ((r_txt_window - first_term) * beta + ord(new_char_at_end)) % chosen_candidate


if __name__ == '__main__':  
    _, filename1, filename2 = sys.argv

    file1content = read_file(filename1)
    file2content = read_file(filename2)

    txt = file1content[0]
    pat = file2content[0]

    match(txt, pat)

