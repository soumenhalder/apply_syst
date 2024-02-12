
# **If you have a 2d systematics table, and want to calculate weight factor of each events according to systematics table,  yes! you have chosen the right code.**
  
## How it works?
  1. Calculate the bin edge of two variables from systematics table
  2. Calculate the bin_id of those two variables both in systematics table and the desired ntuple of events
  3. Merge two entity (systematics table and our ntuple) base on the bin_id calculated in (2)


  Example:
  
 Systematic table
 
 p_low | p_high | theta_low | theta_high |  weight
 ------|---------|-----------|-----------|-----------
   0.5 |  1.5      |  17          |  90    |  0.10
   1.5 |  3.5      |  17          |  90    |  0.20
   0.5 |  1.5      |  90          | 150    | 0.14
   1.5 |  3.5      |  90          | 150    | 0.19
 
 
 
 Our ntuple
    
p    |    theta | < other variables >
-----|----------|----------------------
   1.2  |     40   |  -- 
   1.7  |    135   |   --

## 1. find bin edge,  p = [0.5,1.5,3.5], theta = [17,90,150]

## 2. calculating bin_id

syatematics table:
  
 p_low  | p_high  |theta_low  | theta_high|  weight |  p_binid  | theta_binid
 --------|---------|-----------|-----------|----------|------------|-------------
   0.5  |1.5      |    17     |    90     | 0.10     |   1        |      1
   1.5  |3.5      |    17     |    90     | 0.20     |   2        |      1
   0.5  |1.5      |    90     |   150     | 0.14     |   1        |      2
   1.5  |3.5      |    90     |   150     | 0.19     |   2        |      2

Our ntuple

p   |  theta  | <other variables>  |   p_binid  | theta_binid
 ----|----------|----------------------|-----------|-----------
 1.2 |      40 |     --            |           1 |             1
 1.7 |     135 |     --            |           2 |            2
   
## 3. Merge two entity

Our ntuple

 p  |  theta  | other variables  |   p_binid  | theta_binid | p_low | p_high  |theta_low  | theta_high|  weight 
----|----------|-------------------|------------|-------------|------|-----------|-----------|----------|--------
 1.2 |      40 |     --            |          1 |         1   | 0.5  |    1.5    |      17   |      90  |    0.10
 1.7 |     135 |     --            |          2 |         2   | 1.5  |    3.5    |       90  |     150   |  0.19

## Cross check

* How many candidates are out of scope to assign weight
* Check whether var1low < var1 < var1high and same for var2

## How you will use?

* Find the systematics table, provided by performance group. For this particular case there are two files. So give their path to `systematics_table()` function. However sometimes systematic table has a different format. For this case the entries are separated by comma, but for other format investigate [`read_csv`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) function a little to fix.
* Assuming the systematics table having a standard form like above explained, having a bin edge variable (p_low, p_high..), put their name to following variables `var1min`, `var1max`, `var2min`, `var2max`.
* Check which columns of the systematics table are not numeric, taking the number of precision at highest prority, we will avoid those columns. Put their name in `ignore` list.
* Input your ntuple having this two target variable, put their name to `var1_Ntuple`, `var2_Ntuple`, and input file path with the ntuple to pick (`tree` for our case) to `analysis_ntuple()` function
* execute by `basf2 estimate.py`
* If there are charge inclusive table provided (do the exercise), then there should be only one systematic table. So change `systematics_table()` fun and the Step 3, accordingly 
