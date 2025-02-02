import re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def main(file_path, verbose=False):  # Add verbose as a parameter with a default value
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it exists in the specified directory.")
        exit()
    except ValueError as e:
        print(f"Error: Unable to read the file. Make sure it's a valid Excel file. Details: {e}")
        exit()

    # Check if the DataFrame is empty
    if df.empty:
        print("Error: The provided Excel file is empty.")
        exit()

    if df.isnull().all().all():
        print("Error: The Excel file contains no valid data.")
        exit()

    # Ensure columns have valid names
    if df.columns.duplicated().any():
        print("Error: The Excel file contains duplicate transaction names in columns.")
        exit()

    if any(col == '' for col in df.columns):
        print("Error: One or more column names in the Excel file are empty.")
        exit()

    index = 0
    temp = 0

    # transaction : other transactions
    other = dict()
    transactions = [trnsc_name for trnsc_name in df]
    n_transactions = len(transactions)

    for transaction in transactions:
        other[transaction] = []

    for transaction in transactions:
        for othr in range(n_transactions - 1):
            other[transaction].append(transactions[((temp + 1) % n_transactions)])
            temp += 1
        index += 1
        temp = index

    # Serial schedule corresponding to each transaction
    column_wise_tnrcs = {}
    for l in range(0, n_transactions):
        column_wise_tnrcs[transactions[l]] = []

    temp = 0
    for l in range(0, n_transactions):
        column_wise_tnrcs[transactions[l]].extend(list(filter(lambda x: x != '', df[transactions[temp]].dropna().tolist())))
        temp += 1

    # Nodes of dependency graph
    nodes = []
    # Pairs of transactions having conflict
    conflicting_nodes = []
    conflicting_pairs = {'r': ['w'],
                         'w': ['w', 'r']}

    # Finding conflicting pairs
    for index, row in df.iterrows():
        for col_name, operation in row.items():
            if pd.notna(operation):
                match = re.match(r'([rw])\((\w+)\)', operation)
                if not match:
                    print(f"Error: Invalid operation format '{operation}' in column '{col_name}'. Expected 'r(var)' or 'w(var)'.")
                    exit()
                op = match.group(1)  # operation
                var = match.group(2)  # variable
                if op == 'r':
                    conflict_rw = conflicting_pairs[op][0] + '(' + var + ')'
                    if verbose:  # Use the verbose flag to control output
                        print(f"Transaction {col_name}'s conflicting pair for operation {operation} is {conflict_rw}")
                    for other_transactions in range(n_transactions - 1):
                        if conflict_rw in column_wise_tnrcs[other[col_name][other_transactions]]:
                            nodes.append(col_name)
                            conflicting_nodes.append(tuple([col_name, other[col_name][other_transactions]]))
                    column_wise_tnrcs[col_name].remove(operation)
                else:
                    conflict_ww = conflicting_pairs[op][0] + '(' + var + ')'
                    conflict_wr = conflicting_pairs[op][1] + '(' + var + ')'
                    if verbose:  # Use the verbose flag to control output
                        print(f"Transaction {col_name}'s conflicting pair for operation {operation} is {conflict_ww} and {conflict_wr}")

                    for other_transactions in range(n_transactions - 1):
                        if conflict_ww in column_wise_tnrcs[other[col_name][other_transactions]]:
                            nodes.append(col_name)
                            conflicting_nodes.append(tuple([col_name, other[col_name][other_transactions]]))
                    column_wise_tnrcs[col_name].remove(operation)

                    for other_transactions in range(n_transactions - 1):
                        if conflict_wr in column_wise_tnrcs[other[col_name][other_transactions]]:
                            nodes.append(col_name)
                            conflicting_nodes.append(tuple([col_name, other[col_name][other_transactions]]))

    # Building dependency graph
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(conflicting_nodes)

    # Detect if the graph has cycles
    try:
        cycles = list(nx.simple_cycles(G))
        if cycles:
            print("Detected cycles:", cycles)
            print("Therefore, the given schedule is not conflict serializable.")
        else:
            print("No cycles detected. The given schedule is conflict serializable.")
            try:
                topological_order = list(nx.topological_sort(G))
                print("Order of serializability:", topological_order)
            except nx.NetworkXUnfeasible:
                print("Error: Topological sorting failed despite no cycles detected.")
    except Exception as e:
        print(f"Unexpected error during cycle detection or topological sorting: {e}")

    # Draw the graph
    if not G.nodes or not G.edges:
        print("Warning: The dependency graph is empty; nothing to plot.")
    else:
        pos = nx.spring_layout(G)  # positions for all nodes
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold', arrowsize=20)

        # Add text on the plot to indicate if a cycle exists
        cycle_text = "Cycle Exists, NOT CSS" if cycles else "No Cycle, CSS"
        text_color = 'red' if cycles else 'green'

        # Determine the center of the graph to place the text dynamically
        x_center = sum(p[0] for p in pos.values()) / len(pos)
        y_center = sum(p[1] for p in pos.values()) / len(pos)

        plt.text(x_center, y_center - 0.1, cycle_text, horizontalalignment='center',
                 fontsize=14, color=text_color, bbox=dict(facecolor='white', alpha=0.7))

        plt.title('Dependency Graph')
        plt.show()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Check if a schedule is conflict serializable.")
    parser.add_argument("file", type=str, help="Path to the Excel file containing the schedule.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for debugging.")  # Add verbose flag
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the main function with the file path and verbose flag
    main(args.file, args.verbose)