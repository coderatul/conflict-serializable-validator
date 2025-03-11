# Conflict Serializable Validator [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

This Python script checks if a given schedule of transactions is conflict serializable by constructing a dependency graph and detecting cycles. If the graph has no cycles, the schedule is conflict serializable, and the script provides a topological order of transactions. The script also visualizes the dependency graph using `networkx` and `matplotlib`.

## usage
```
python css.py <schedule.xlsx> [--verbose]
```

## example
- operations corresponding to transactions of schedule are entered in a excle file for ease of use 
- more transaction can be added as columns

![image](https://github.com/user-attachments/assets/a56f6223-1667-47fb-a6b0-d69d63be46f6)

## output
```
No cycles detected. The given schedule is conflict serializable.
Order of serializability: ['T2', 'T3', 'T1']
```
> dependency graph

![example](https://github.com/user-attachments/assets/0a3cc712-2741-45b7-91c8-02aa7b2d8b65)




