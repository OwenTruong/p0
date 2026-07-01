1. Setup a watch program to monitor systems, and insert system stats to DB.
   1. metric db class
      2. cpu_average (based on 15 minute Exponential Moving Average) [1]
         1. Load average is the is a measurement of how many tasks are waiting in a kernel run queue. If load average falls below 100%, it means there are idle cpu time left for the amount of tasks running.
         2. Load average scales with the amount of logical cores you have. So if you have 10 logical cores, you load average will be out of 10, and if you have 4 logical cores, your load average will be out of 4. (load_average / logical_cores) * 100 to get cpu utilization as a percentage.
      3. memory_total
      4. memory_used
      7. created_on

2. Fetch metric data from DB + check /var/log/auth.log and journalctl for logs.
3. Then display those data to web with an option to download report as pdf.
4. Add the relevant data to database so that we can view them another time.



[1] https://superuser.com/questions/1402079/understanding-load-average-and-cpu-in-linux