# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, execute, Aer, QuantumRegister, ClassicalRegister

# Useful imports
def find_pairs(entries, n):
    """
    Creates a circuit that, given a list of entries, marks the input qubits
    that form a valid pair-combination present in that list.
    For example, for entries=['01', '11'], the possible pair combinations are:
    
    ('01','11')
    
    So for the input qubits, only '0111' will be marked:
    
    '0000 0', '0001 0', ..., '0111 1', ..., '1111 0'
    
    Input is expected as:
    - n qubits as input1
    - n qubits as input2 (which will be combined with input1)
    - 1 qubit to be marked with 1 if input1+input2 is a valid combination
    - ancilla qubits that must be of length 2*n - 2

    Args
    --------------------
    entries: list of entires to combine. Each entry must be of length n
    n: length (in bits) of each entry
    """
    d0 = QuantumRegister(n,name="digits0")
    d1 = QuantumRegister(n,name="digits1")
    is_valid = QuantumRegister(1,name="is_valid")
    ancilla = QuantumRegister(2*n-2,name="anc")
    qc = QuantumCircuit(d0, d1, is_valid, ancilla, name="PairFinder")
    # Mark the pairs that are found in the possible pair-combinations of entries
    import itertools
    for i,j in itertools.combinations(entries, 2):
        # Init condition to identify i in d0 and j in d1
        if i.count('1') != n:
            qc.x([ d0[k] for k,digit in enumerate(i) if digit=='0' ])
        if j.count('1') != n:
            qc.x([ d1[k] for k,digit in enumerate(j) if digit=='0' ])
        # Mark the registers that form a pair present in the generated combinations
        qc.mct( d0[:] + d1[:], is_valid, ancilla, mode="basic" )
        # Uncompute condition
        if i.count('1') != n:
            qc.x([ d0[k] for k,digit in enumerate(i) if digit=='0' ])
        if j.count('1') != n:
            qc.x([ d1[k] for k,digit in enumerate(j) if digit=='0' ])
        qc.barrier()
    return qc

def diffuser(qbits, ancilla_amount=0):
    """
    Creates a circuit that performs a diffusion algorithm to the given qubits.
    The input is expected as: qbits qubits to diffuse, ancilla_amount qubits

    Args
    --------------------
    qbits: the amount of qbits to diffuse
    ancilla_amount: the amount of ancilla qubits to use by the MCT with mode=basic
    """
    qc = QuantumCircuit(qbits + ancilla_amount, name="diffuser")
    qlist = [i for i in range(0,qbits)]
    ancilla = [i for i in range(qbits, qbits+ancilla_amount)]
    # Apply transformation |s> -> |00..0> (H-gates)
    qc.h(qlist)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    qc.x(qlist)
    # Do multi-controlled-Z gate
    qc.h(qlist[-1])
    if ancilla_amount > 0:
        qc.mct(qlist[:-1], qlist[-1], ancilla, mode="basic")  # multi-controlled-toffoli
    else:
        qc.mct(qlist[:-1], qlist[-1])
    qc.h(qlist[-1])
    # Apply transformation |11..1> -> |00..0>
    qc.x(qlist)
    # Apply transformation |00..0> -> |s>
    qc.h(qlist)
    return qc

def one_counter(n):
    """
    Counts the amount of ones in an n qubit register.
    Qubits are expected as: n input, log2(n+1) output, log2(n+1)-2 ancilla
    The result is in the shape:
        count[4] ... count[0]
          LSB    ...   MSB
    i.e. 4 = '0010'
    
    Args
    --------------------
    n: size of the register whose 1s are going to be counted
    """
    import math
    c = math.ceil(math.log2(n+1))
    q = QuantumRegister(n,name="q")
    count = QuantumRegister(c,name="count")
    ancilla = QuantumRegister(c-2, name="ancilla")
    qc = QuantumCircuit(q,count,ancilla,name="OneCounter")
    # Count the amount of ones in 'q' bit by bit and store the result in 'count'
    for i in range(n):
        for j in range(len(count)):
            qc.mct( [q[i]] + count[j+1:], count[j], ancilla, mode="basic")
        qc.barrier()
    return qc

def hamming_calculator(n):
    """
    Calculates the Hamming distance between two n-size registers
    Qubits are expected as: n input1, n input2, log2(n+1) output/hamming distance, nh-2 ancilla
    
    Args
    --------------------
    n: size of the registers whose Hamming distance is going to be calculated
    """
    # Amount of qubits to store hamming distance
    import math
    nh = math.ceil(math.log2(n+1))
    # Create circuit
    in0 = QuantumRegister(n,name="in0")
    in1 = QuantumRegister(n,name="in1")
    distance = QuantumRegister(nh,name="distance")
    ancilla = QuantumRegister(nh-2, name="ancilla")
    qc = QuantumCircuit(in0,in1,distance,ancilla, name="CalcHamming")
    # Calculate the hamming distance between in0 and in1 and store in in1
    for i,j in zip(in0,in1):
        qc.cx(i,j)
    # Count the amount of ones in in1 and store the amount in distance as the result
    qc.append( one_counter(n), in1[:] + distance[:] + ancilla[:] )
    # Uncompute Hamming distance to restore in1
    for i,j in zip(in0,in1):
        qc.cx(i,j)
    # Return
    return qc


def calculate_ideal_amount_of_iterations(n, k=1):
    """
    Calculates the ideal amount of Grover's iterations required for n qubits
    (assuming k solutions). See:
    https://en.wikipedia.org/wiki/Grover%27s_algorithm#Extension_to_space_with_multiple_targets
    
    If there are no solutions, no iterations are needed (but actually those iterations wouldn't
    matter as they would just scramble the states)

    Args
    --------------------
    n: amount of qubits to be diffused
    k: amount of solutions
    """
    import math
    # return closest integer to the ideal amount of calculations
    return round((math.pi/4)*( math.sqrt(2**n/k) )) if k>0 else 0

def challenge02(entries, solutions):
    """
    Args
    --------------------
    entries: list of binary strings
    solutions: list with the amount of solutions to expect for each Hamming distance 0,1,2,...,len(entries[0]-1)
    """
    # Get number of qubits required to represent the entries
    n = len(entries[0])
    # Get the number of qubits required to store the hamming distances
    import math
    nh = math.ceil(math.log2(n+1))
    # Create quantum circuit
    d0 = QuantumRegister(n,name="digits0")
    d1 = QuantumRegister(n,name="digits1")
    is_pair = QuantumRegister(1,name="is_pair")
    hamming = QuantumRegister(nh,name="hamming")
    oracle = QuantumRegister(1,name="oracle")
    ancilla = QuantumRegister(n+n-2,name="anc")
    bits = ClassicalRegister(2*n, name='bits')
    qc = QuantumCircuit(d0, d1, is_pair, hamming, oracle, ancilla, bits)
    # Init oracle
    qc.x(oracle)
    # Create all possible combinations of pairs of numbers
    qc.h( d0[:] + d1[:] )
    qc.barrier()

    # Amplify the pair(s) with the minimum Hamming distance using Grover's algorithm
    distances = [bin(i)[2:].zfill(nh) for i in range(0,n)]
    # Perform Grover's algorithm
    for d, distance in enumerate(distances):
        # Calculate the ideal amount of iterations required for Grover's Algorithm given
        # the amount of solutions.
        # TODO: how to extend this to the case where we don't know the amount of solutions
        # to look for? See Wikipedia for some suggestions
        iterations = calculate_ideal_amount_of_iterations(2*n, solutions[d])
        print(f"Iterating {iterations} times for distance {distance}")
        for i in range(iterations):
            # Mark the pairs that are in the input
            qc.append( find_pairs(entries,n), d0[:] + d1[:] + is_pair[:] + ancilla[:] )
            # Calculate the hamming distances between each pair
            qc.append( hamming_calculator(n), d0[:] + d1[:] + hamming[:] + ancilla[:nh-2] )

            # Mark the states that are a valid pair AND have the minimum amount of ones
            qc.x([ hamming[k] for k,digit in enumerate(distance) if digit=='0' ])
            qc.h(oracle)
            qc.mct(is_pair[:] + hamming[:], oracle, ancilla, mode="basic" )
            qc.h(oracle)
            qc.x([ hamming[k] for k,digit in enumerate(distance) if digit=='0' ])

            # Uncompute distances
            qc.append( hamming_calculator(n).inverse(), d0[:] + d1[:] + hamming[:] + ancilla[:nh-2] )
            # Uncompute pairing mark
            qc.append( find_pairs(entries,n).inverse(), d0[:] + d1[:] + is_pair[:] + ancilla[:] )

            # diffuse
            qc.append( diffuser(2*n, 2*n-2), d0[:] + d1[:] + ancilla[:] )
            qc.barrier()

    # Measure
    qc.measure(d0[:] + d1[:], bits)
    return qc

if __name__ == '__main__':
    # Create circuit with the ideal amount of iterations
    # ['00000','00001','11000','11010']
    entries = ['0000','1001','1100','1101']
    circuit = challenge02(entries, solutions=[0,2,3,1])
    circuit.draw()
    # Get backend and run job
    backend = Aer.get_backend('qasm_simulator')
    print("Executing job...")
    job = execute(circuit, backend, shots=1000)
    print(job.result().get_counts())