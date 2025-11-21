#!/bin/bash
# Usage: ./crawl_dependencies.sh <ROOT_JOB>
# Output:
#   deps_all.txt      → list of all jobs in tree
#   deps_map.txt      → job: parent1 parent2 ...
#   deps_edges.txt    → parent → child edges

ROOT="$1"
OUTDIR="deps_$ROOT"
mkdir -p "$OUTDIR"

DEPS_ALL="$OUTDIR/deps_all.txt"
DEPS_MAP="$OUTDIR/deps_map.txt"
DEPS_EDGES="$OUTDIR/deps_edges.txt"

# init
> "$DEPS_ALL"
> "$DEPS_MAP"
> "$DEPS_EDGES"

queue="$ROOT"

while [ -n "$queue" ]; do
    CURRENT="$queue"
    queue=""

    for JOB in $CURRENT; do
        # Skip if already processed
        grep -q "^$JOB$" "$DEPS_ALL" && continue

        echo "$JOB" >> "$DEPS_ALL"

        # Pull job definition
        DEF=$(autorep -j "$JOB" -q 2>/dev/null)

        # Extract parent jobs from condition lines
        PARENTS=$(echo "$DEF" | grep -i "condition:" | \
                  sed 's/(/\n/g' | grep -E "s|f" | sed 's/).*//' | awk -F")" '{print $1}' | sed 's/^s//;s/^f//;s/[()]//g' | tr -d ' ' )

        echo -n "$JOB:" >> "$DEPS_MAP"
        for P in $PARENTS; do
            echo -n " $P" >> "$DEPS_MAP"
            echo "$P $JOB" >> "$DEPS_EDGES"
            # Queue for next iteration
            if ! grep -q "^$P$" "$DEPS_ALL"; then
                queue="$queue $P"
            fi
        done
        echo "" >> "$DEPS_MAP"

    done
done

echo "Dependency extraction complete."
echo "Files created in $OUTDIR:"
echo "  deps_all.txt   → all jobs in the chain"
echo "  deps_map.txt   → job : parents"
echo "  deps_edges.txt → parent → child edges"
