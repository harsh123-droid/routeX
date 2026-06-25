\# Benchmark Results



\## Configuration



Distance Budget: 50

Category Threshold: 2

Beam Width: 10

Population Size: 30

Generations: 50



\## Results



| Size | Greedy | Beam Search | Genetic |

|------|---------|---------|---------|

| 10 | 14.55 | 14.58 | 14.62 |

| 20 | 21.20 | 20.55 | 21.33 |

| 50 | 24.48 | 22.67 | 21.98 |

| 100 | 45.92 | 41.71 | 37.55 |



\## Conclusion



Greedy achieved the best score/runtime tradeoff.

Beam Search improved when beam width increased from 3 to 10.

Genetic Algorithm produced competitive results but required higher computation time.

