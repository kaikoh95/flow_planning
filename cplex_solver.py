"""
Course           : COSC 364 - Internet Technology and Engineering
Assignment 2 : Flow Planning
Authors          : Kai (64276083) and Eleasa (77307225)
Date Created : 18 May 2018

---Brief overview---
This program takes user input values and sets as the number of
Source, Transit and Destination nodes and generates a valid lp file
for the task mentioned in the assignment. Next, it processes the lp
file and prints out optimized results.
No vital results can be derived if Transit nodes < 3, ie Y < 3.
"""

import sys, subprocess, time

#Global variables
ERROR = ["ERROR 00: Incorrect number of parameters. Manual input set. . .", 
          "ERROR 01: Value must be an integer. Manual input set. . ."]
THREE_FLOW = 3 #for demand volume across 3 exact paths
ALL_NODES = [] #list to keep track of all nodes used
BIN_NODES = [] #list to keep track of binary nodes used

### Begin creating lp file ###

def is_integer(param):
    """
    Checks if the value given is an integer.
    Returns True if yes and False if not.
    """
    
    check = False
    
    try:
        param = int(param)
    except ValueError: #if not integer
        print(ERROR[1])
        check = False
    else:
        check = True
        
    return check


def check_default_params():
    """
    Checks for integer validity
    if user input is similar to 
    "python3 lp_generator.py X Y Z".
    X, Y and Z are parameters 
    for the Source, Transit and Destination nodes.
    True - is a valid integer
    False - is not a valid integer
    Returns True/False for checkers for X, Y and Z.
    """
    
    if len(sys.argv) == 4: 
        check_x = is_integer(sys.argv[1]) #prints error if not integer
        check_y = is_integer(sys.argv[2])
        check_z = is_integer(sys.argv[3])   
    else:
        print(ERROR[0]) #prints error if incorrect no. of params
        check_x = check_y = check_z = False
    
    return (check_x, check_y, check_z)
    
    
def user_input():
    """
    Checks if user runs program along with 3 integers for the parameters.
    Otherwise, program will prompt user for input.
    Gets user input for the values of X, Y and Z.
    and also checks if they are integers.
    X - Number of Source nodes.
    Y - Number of Transit nodes.
    Z - Number of Destination nodes.
    Returns given params as integer values if they are valid integers.
    """
    
    finished_checking = False #integer checker        
    check_x, check_y, check_z = check_default_params()
    
    if check_x == True and check_y == True and check_z == True: #if correct params
        src_x = int(sys.argv[1]) #set to integer values
        trs_y = int(sys.argv[2])
        dst_z = int(sys.argv[3])
    else:
        """
        Prompts user for input on the command line
        and checks for integer validity before user can continue.
        """
        while finished_checking == False:
            src_x = input("Number of Source nodes, X : ")
            finished_checking = is_integer(src_x)
        finished_checking = False #reset integer checker
        while finished_checking == False:
            trs_y = input("Number of Transit nodes, Y : ")
            finished_checking = is_integer(trs_y)         
        finished_checking = False #reset integer checker
        while finished_checking == False:
            dst_z = input("Number of Destination nodes, Z : ")
            finished_checking = is_integer(dst_z)
            
        src_x = int(src_x) #set to integer values
        trs_y = int(trs_y)
        dst_z = int(dst_z)
    
    return (src_x, trs_y, dst_z)


def set_generic_constraints(src_x, trs_y, dst_z, cst_symbol, exp_results):
    """
    Helper function for setting constraints with similar 
    methods to each other so as to make the source code cleaner.
    Uses values of src_x, trs_y, dst_z as the number of
    Source, Transit and Destination nodes.
    New params introduced here are:
    cst_symbol      - String containing symbol for constraints.
                      To be used in the equations.
    exp_results     - String containing expected results for the equations.
                      Vary between constraints
    """
    
    constraints = [] #temp storage for constraints equations
    string_final = "" #final string layout to be used for writing to lp file
    
    for x in range(1, src_x + 1):
        
        for z in range(1, dst_z + 1):
            temp_str = ""
            
            for y in range(1, trs_y + 1):
                """
                For example: "x111 + x121 + " for first iteration of 
                src_x and dst_z and second iteration of trs_y.
                The extra '+   ' part will be fixed after the iteration
                of trs_y is finished - for eg. "x111 + x121 = 2"
                """
                temp_var = "{0}{1}{2}{3} + ".format(cst_symbol, x, y, z)
                temp_str += temp_var   
                if cst_symbol == 'u':
                    BIN_NODES.append(temp_var[:4])
                
            temp_str = temp_str[:-3] #fixes the duplicate '+   ' part for second variable
            temp_str += " = {}".format(eval(str(exp_results))) #adds '= {results}' to the equation
            constraints.append(temp_str) #add to list for temp storage
            
    for string in constraints: #add to final string
        string_final += string
        string_final += '\n'
        
    string_final += '\n'
    
    return string_final
                

def set_demand_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for Demand Volume by
    using the values of X, Y, Z as the number of
    Source, Transit and Destination nodes.
    Denoted by x.
    """
    
    demand_string_final = set_generic_constraints(src_x, trs_y, dst_z, \
                                                  "x", "x + z")
    
    return demand_string_final


def set_three_path_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for Demand Volume split over 3 paths,
    using binary variables denoted u.
    Equations with 1 indicates path is used, 0 means not used.
    """
    
    path_string_final = set_generic_constraints(src_x, trs_y, dst_z, \
                                                "u", THREE_FLOW)
    
    return path_string_final


def set_generic_link_constraints(src_x, trs_y, dst_z, link_symbol, link_type):
    """
    Helper function for forming constraints used in
    equations for link capacity inequalities.
    Uses values from src_x, trs_y, dst_z inputs.
    New params introduced are:
    link_symbol  - String containing symbol for constraints.
                   To be used in the equations.
    link_type    - To check if setting source-transit or transit-destination
                   link constraints
    """
     
    link_constraints = [] #temp storage for link capacity equations
    link_string_final = "" #final string layout to be used for writing to lp file    
    
    for i in range(1, src_x + 1):
        
        for j in range(1, trs_y + 1):
            link_str = ""
            
            for k in range(1, dst_z + 1):
                
                """
                Forms variables for equation based on link type.
                i.e source-transit or transit-destination link capacities.
                """
                if link_type != 0: #cue for transit-destination link capacity
                    link_str += "x{0}{1}{2} + ".format(k, i, j) 
                else: #cue source-transit link capacity
                    link_str += "x{0}{1}{2} + ".format(i, j, k) 
            
            link_str = link_str[:-3] #remove additional + in last variable
            
            #forms inequality of =0 as specified in the report
            link_str += " - {0}{1}{2} = 0".format(link_symbol, i, j)
                
            link_constraints.append(link_str)
            
    for string in link_constraints:
        link_string_final += string
        link_string_final += '\n'
        
    link_string_final += '\n'
        
    return link_string_final 


def set_source_transit_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for link capacity between Source 
    and Transit nodes.
    Link capacity here is denoted by c.
    """
    
    src_trs_string_final = set_generic_link_constraints(src_x, trs_y, dst_z, \
                                                        "c", 0)
    
    return src_trs_string_final
           

def set_transit_destination_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for link capacity between Transit 
    and Destination nodes.
    Link capacity here is denoted by d.
    """
    
    trs_dst_string_final = set_generic_link_constraints(src_x, trs_y, dst_z, \
                                                        "d", 1)
    
    return trs_dst_string_final


def set_load_balancing_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for load balancing.
    """
    
    load_constraints = [] #temp storage for load balancing equations
    load_string_final = "" #final string layout to be used for writing to lp file    
    
    for y in range(1, trs_y + 1):
        load_str = ""
        
        for x in range(1, src_x + 1):
            
            for z in range(1, dst_z + 1):
                load_str += "x{0}{1}{2} + ".format(x, y, z) #form variables
                
        load_str = load_str[:-3] #remove + from final variable
        load_str += " - r <= 0" #<=0 for load balancing as required
        load_constraints.append(load_str)
    
    for string in load_constraints:
        load_string_final += string
        load_string_final += '\n'
        
    load_string_final += '\n'
        
    return load_string_final


def set_equal_demand_constraints(src_x, trs_y, dst_z):
    """
    Sets constraints for Demand Volume that is equally split.
    """
    
    equal_string_final = ""
    
    for x in range(1, src_x + 1):
        
        for z in range(1, dst_z + 1):
            
            for y in range(1, trs_y + 1):
                h = x + z #param for demand vol from src to dst node
                equal_str = "3 x{0}{1}{2} - {3} u{0}{1}{2} = 0".format(x, y, z, h)
                equal_string_final += equal_str
                equal_string_final += '\n'
    
    equal_string_final += '\n'
                
    return equal_string_final


def set_variables_constraints(src_x, trs_y, dst_z):
    """
    Sets bounds for ALL solution variables.
    """
    
    vars_constraints = []
    vars_string_final = "Bounds\n"
    
    #Iteration for Demand Volume variables
    #from Source to Destination via Transit
    for x in range(1, src_x + 1):
        
        for y in range(1, trs_y + 1):
            
            for z in range(1, dst_z + 1):
                vars_str = "x{}{}{} >= 0".format(x, y, z)
                vars_constraints.append(vars_str)
                
    #Iteration for link capacity variables 
    #from Source to Transit
    for x in range(1, src_x + 1):
        
        for y in range(1, trs_y + 1):
            vars_str = "c{}{} >= 0".format(x, y)
            vars_constraints.append(vars_str)
            
    #Iteration for link capacity variables
    #from Transit to Destination
    for z in range(1, dst_z + 1):
        
        for y in range(1, trs_y + 1):
            vars_str = "d{}{} >= 0".format(y, z)
            vars_constraints.append(vars_str)
    
    vars_constraints.append("r >= 0")   
    
    for string in vars_constraints:
        vars_string_final += string
        vars_string_final += '\n'
    
    vars_string_final += '\n'
    
    return vars_string_final


def set_binary_variables(src_x, trs_y, dst_z):
    """
    Sets all possible binary variables processed
    from the user inputs for Source, Transit
    and Destination nodes.
    """
    
    bin_constraints = []
    bin_string_final = "Binaries\n"

    for string in list(set(BIN_NODES)): #remove duplicates
    #for string in bin_constraints:
        bin_string_final += string
        bin_string_final += '\n'
    
    bin_string_final += '\n'    
    
    return bin_string_final
    
    
def set_header(src_x, trs_y, dst_z):
    """
    Sets header of the file according to
    the values as well as the name of file 
    for the constraints to be written to.
    """
    
    header = """----------------------
Source nodes      - X 
{0}
Transit nodes     - Y 
{1}
Destination nodes - Z 
{2}
----------------------
Filename                   
cplex_{0}{1}{2}.lp     
----------------------
Minimize       
r

Subject to

""".format(src_x, trs_y, dst_z)

    return header


def form_cplex_content(src_x, trs_y, dst_z):
    """
    Forms file contents for cplex to process.
    """
    
    header = set_header(src_x, trs_y, dst_z)
    
    #Form strings for all constraints, bounds and binaries
    demand_string_final = set_demand_constraints(src_x, trs_y, dst_z)
    path_string_final = set_three_path_constraints(src_x, trs_y, dst_z)
    
    src_trs_string_final = set_source_transit_constraints(src_x, trs_y, dst_z)
    trs_dst_string_final = set_transit_destination_constraints(trs_y, dst_z, src_x)
    
    load_string_final = set_load_balancing_constraints(src_x, trs_y, dst_z)
    equal_string_final = set_equal_demand_constraints(src_x, trs_y, dst_z)
    
    vars_string_final = set_variables_constraints(src_x, trs_y, dst_z)
    bin_string_final  = set_binary_variables(src_x, trs_y, dst_z)    
    
    #The great combine
    cplex_data = header + demand_string_final + path_string_final + \
                 src_trs_string_final + trs_dst_string_final + \
                 load_string_final + equal_string_final + \
                 vars_string_final + bin_string_final + 'End'
    
    print(cplex_data) #for assignment specifications
    
    return cplex_data

def create_lp_file(src_x, trs_y, dst_z, cplex_data):
    """
    Creates and names lp file for CPLEX
    to process.
    An example of a filename would be:
    "cplex_XYZ.lp" where
    X - src_x, number of Source nodes
    Y - trs_y, number of Transit nodes
    Z - dst_z, number of Destination nodes
    Does nothing if filename already exists.
    Proceeds to write contents into the file.
    """
    
    lp_file = open("cplex_{0}{1}{2}.lp".format(src_x, trs_y, dst_z), "w+")
    lp_file.write(cplex_data)
    lp_file.close()

### End of creating lp file ###
    
### Begin processing lp file ###

def process_cplex(filename):
    """"
    Process input lp file using CPLEX.
    If filename given on terminal, use that,
    if not prompts user for filename.
    If invalid filename given, program stops.
    """    
    
    #Must be where CPLEX is installed
    cplex_dir = "/home/cosc/student/hkk18/cplex/cplex/bin/x86-64_linux/cplex"
    
    #2nd element of list must be read + dir of lp file
    cplex_command = ["-c", "read /home/cosc/student/hkk18/cplex/" + filename, 
                     "optimize", "display solution variables -"]
    
    output = subprocess.Popen([cplex_dir] + cplex_command, stdout=subprocess.PIPE)
    out, err = output.communicate()
    results = out.decode("utf-8") #obtain readable results
    
    return results


def get_run_time(filename):
    """
    Track execution time for each lp files.
    Returns run_time and results to be reused for later on.
    """
    
    start_time = time.time()
    results = process_cplex(filename)
    end_time = time.time()
    run_time = (end_time - start_time) * 1000 #convert to milliseconds
    
    return run_time, results


def parse_results(results):
    """
    Helper function to parse results and returns
    a list containing variable names and solution values.
    """
    
    #remove unecessary lines
    data = results.split("Variable Name           Solution Value\n")[-1] 
    
    dataset = [] #store data
    
    for line in data.split('\n'): #break up each line
        line = line.split(" ") #remove unnecessary spaces between each var name and sol value
        dataset.append(line)
        
    return dataset
    

def get_information(filename, run_time, results):
    """
    Gets information for maximum load across transit nodes,
    highest capacity links, highest link and number
    of links with non-zero capacities.
    """
    
    max_load = 0
    highest_cap = 0
    num_links = 0
    highest_link = "" #to be set from results    
    
    dataset = parse_results(results)
    
    for stuff in dataset:
        var_name, sol_val = stuff[0], stuff[-1]
        
        #stop once it reaches non-variable-solution value pair
        try:
            sol_val = float(sol_val)
        except ValueError: #move on to optimized results
            break
        else:
            sol_val = float(sol_val)
        
        if var_name == 'r':
            max_load = sol_val
        
        #check if they are link nodes
        if var_name.startswith('c') or var_name.startswith('d'):
            num_links += 1
            
            if highest_cap < sol_val:
                highest_cap = sol_val
                highest_link = var_name
    
    string = """---Optimized Results---
Filename: {}
Execution Time: {}
Maximum Load: {}
Highest Capacity: {}
Number of non-zero links: {}
Highest Link: {}""".format(filename, run_time, max_load, highest_cap, \
                           num_links, highest_link)
    
    return string

### End of processing lp file ###

def main():
    """Main Program integrating helper functions"""
    
    src_x, trs_y, dst_z = user_input() #gets user input
    
    filename = "cplex_{}{}{}.lp".format(src_x, trs_y, dst_z)
    
    cplex_data = form_cplex_content(src_x, trs_y, dst_z) #create data
    create_lp_file(src_x, trs_y, dst_z, cplex_data) #create and write into lp file
    print("\n{} file created. Processing file. . .\n".format(filename))
    
    run_time, results = get_run_time(filename)
    string = get_information(filename, run_time, results)
    print(string)    
    
    
if __name__ == "__main__":
    main()