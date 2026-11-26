# Q4 (Optional): Optimal Binary Search Tree
#
# Usage:
#   python optimal_bst.py

# Keys k1..k5 with search probabilities p, dummy keys d0..d5 with probabilities q
P = [None, 0.15, 0.10, 0.05, 0.10, 0.20]        # p[1..n]
Q = [0.05, 0.10, 0.05, 0.05, 0.05, 0.10]        # q[0..n]


# ---------------------------------------------------------------------------
# Bottom-up DP (CLRS OPTIMAL-BST), O(n^3)
#   e[i][j]    = expected search cost of an optimal tree on k_i..k_j
#   w[i][j]    = total probability of k_i..k_j and d_{i-1}..d_j
#   root[i][j] = index of the root of that optimal tree
# ---------------------------------------------------------------------------
def optimal_bst(p, q, n):
    e = [[0.0] * (n + 1) for _ in range(n + 2)]
    w = [[0.0] * (n + 1) for _ in range(n + 2)]
    root = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 2):
        e[i][i - 1] = q[i - 1]                  # empty tree: only dummy d_{i-1}
        w[i][i - 1] = q[i - 1]
    for length in range(1, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            e[i][j] = float("inf")
            w[i][j] = w[i][j - 1] + p[j] + q[j]
            for r in range(i, j + 1):
                t = e[i][r - 1] + e[r + 1][j] + w[i][j]
                if t < e[i][j]:
                    e[i][j] = t
                    root[i][j] = r
    return e, w, root


# ---------------------------------------------------------------------------
# Print the structure of the tree
# ---------------------------------------------------------------------------
def print_structure(root, i, j, parent=None, side=None):
    if i > j:                                   # dummy key d_j
        print(f"d{j} is the {side} child of k{parent}")
        return
    r = root[i][j]
    if parent is None:
        print(f"k{r} is the root")
    else:
        print(f"k{r} is the {side} child of k{parent}")
    print_structure(root, i, r - 1, r, "left")
    print_structure(root, r + 1, j, r, "right")


def draw_tree(root, i, j, prefix="", is_left=None):
    # Sideways drawing: right subtree on top, left subtree below
    if i > j:
        label, r = f"d{j}", None
    else:
        r = root[i][j]
        label = f"k{r}"
    if r is not None:
        draw_tree(root, r + 1, j, prefix + ("        " if is_left is False or is_left is None else "|       "), False)
    connector = "" if is_left is None else ("/--- " if is_left is False else "\\--- ")
    print(prefix + connector + label)
    if r is not None:
        draw_tree(root, i, r - 1, prefix + ("        " if is_left is True or is_left is None else "|       "), True)


def depth_cost(root, i, j, depth=0):
    # Independent check: sum of (depth + 1) * probability over all nodes
    if i > j:
        return (depth + 1) * Q[j]
    r = root[i][j]
    return ((depth + 1) * P[r]
            + depth_cost(root, i, r - 1, depth + 1)
            + depth_cost(root, r + 1, j, depth + 1))


if __name__ == "__main__":
    n = 5
    e, w, root = optimal_bst(P, Q, n)
    print("=== Optimal binary search tree ===")
    print("i :   " + "".join(f"{i:>6}" for i in range(n + 1)))
    print("p :   " + "".join(f"{'':>6}" if i == 0 else f"{P[i]:>6.2f}" for i in range(n + 1)))
    print("q :   " + "".join(f"{Q[i]:>6.2f}" for i in range(n + 1)))

    print("\nRoot table root[i][j]:")
    print("      " + "".join(f"j={j:<4}" for j in range(1, n + 1)))
    for i in range(1, n + 1):
        print(f"i={i}   " + "".join(f"{('k' + str(root[i][j])) if j >= i else '':<6}" for j in range(1, n + 1)))

    print(f"\nExpected search cost: {e[1][n]:.2f}   (expected 2.75)")
    print(f"Check by summing depth x probability over the tree: {depth_cost(root, 1, n):.2f}")

    print("\nStructure of the optimal tree:")
    print_structure(root, 1, n)

    print("\nTree drawing (rotated: right children above, left children below):")
    draw_tree(root, 1, n)


# Analysis / Conclusion:
# The DP tries every key k_r as the root of every sub-range k_i..k_j. Making
# a subtree one level deeper adds its total probability w[i][j] to the cost,
# so e[i][j] = min over r of e[i][r-1] + e[r+1][j] + w[i][j]. Filling the
# tables by increasing range length takes O(n^3) time.
#
# For the given probabilities the minimum expected search cost is 2.75, with
# k2 at the root, k1 on its left and k5 on its right, k4 under k5 and k3
# under k4. Note that k5, the most likely key (p = 0.20), is not the root:
# putting it at the top would push the other keys deeper and cost more
# overall, so a greedy "most frequent key first" rule does not give the
# optimal tree.
