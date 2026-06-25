\# Beam Search Design



Goal:

Find higher-scoring routes than Greedy.



Beam Width:

3



Algorithm:



1\. Start with an empty route.

2\. Expand all possible next locations.

3\. Score each partial route.

4\. Keep only the top 3 routes.

5\. Repeat until no route can be expanded.



Constraints:

\- Respect distance budget.

\- No duplicate visits.

\- Use score\_route() for evaluation.



Output:

\- route

\- total\_score

\- total\_distance

\- penalty\_count

