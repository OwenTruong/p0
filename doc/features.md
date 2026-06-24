User Story 1: Local System Diagnostics Feature
* CPU
  * Current Average Load
  * Current Users %
  * Current Systems %
  * Current Nice Values % (out of total processes)
  * Current Idle % (Percentage of CPU not used) 
  * Current Processes Waiting % (out of total processes)
  * Current Hardware Interrupt % (?)
  * Current Software Interrupt % (?)
  * Current Steal Time % (out of all requested CPU time?)
  * 1 Minute Load Average
  * 5 Minute Load Average
  * 15 Minute Load Average
* Memory
  * Memory Total
  * Memory Used
  * Memory Free
  * Memory Shared
  * Memory Buffer / Cache
  * Memory Available
  * Memory Swap Total
  * Memory Swap Used
  * Memory Swap Free
* Disk Utilization
  * Total Available
  * Total Used
  * Total Left
  * Filesystem Disk Allocated
  * Filesystem Disk Used from Allocation
  * Filesystem Disk Available from Allocation
  * Filesystem Disk Left from Allocation
  * Filesystem Mounted Directory
* Active Network Connection
  * Current IP Address
  * Sockets 
* Extra
  * System Uptime

Question
* What kind of CPU data would you like to track over time vs currently values?
* So user, system and idle %Cpu(s) from top makes sense. 
  * Nice Value is a representation of the percentage of all processes that have some nice value attached to them. 
  * Wait time is a representation of the percentage of all processes that are waiting for CPU.
  * SI (Steal Time) seems to be when the current VM share the same cores as one or more VM, and the other VM steal time from the current VM. I am assuming 0% means no CPU time was stolen by other VM.
  * What are hardware interrupt and software interrupt a percentage of? Processes that are hardware or software interrupted out of all processes?
* What data would you like us to display from all of the active sockets?
* What does the user stories mean by "error frequencies or trends"? Does it mean to analyze error logs from journeyctl and dmesg?


References
* CPU Load
  * https://superuser.com/questions/1402079/understanding-load-average-and-cpu-in-linux
* TOP
  * https://www.redhat.com/en/blog/interpret-top-output
* Shared Memory (tmp file & shared memory)
  * https://unix.stackexchange.com/questions/307015/what-is-the-meaning-of-shared-memory-in-the-free-command
* ESTAB from TCP (ss)
  * https://stackoverflow.com/questions/30947347/what-does-the-established-indicator-mean-after-running-lsof






Brainstorm
* Metrics
  * CPU
    * Average Load
    * 1 Minute Load
    * 5 Minute Load
    * 15 Minute Load
  * Memory
    * Memory Total
    * Memory Used
    * Memory Free
    * Memory Swap Total
    * Memory Swap Used
  * Disk
    * Disk-Partition Table
  * IP Addresses
    * [IPV4, Gateway, Submask]
  * Network
    * netstat