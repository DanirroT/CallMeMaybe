_This project has been created as part of the 42 curriculum by dmota-ri._

• A “Description” section that clearly presents the project, including its goal and a
brief overview.

• An “Instructions” section containing any relevant information about compilation,
installation, and/or execution.

• A “Resources” section listing classic references related to the topic (documen-
tation, articles, tutorials, etc.), as well as a description of how AI was used —
specifying for which tasks and which parts of the project.

➠ Additional sections may be required depending on the project (e.g., usage
examples, feature list, technical choices, etc.).

Any required additions will be explicitly listed below.

For this project, the README.md must also include:
• Algorithm explanation: Describe your constrained decoding approach in detail
• Design decisions: Explain key choices in your implementation
• Performance analysis: Discuss accuracy, speed, and reliability of your solution
• Challenges faced: Document difficulties encountered and how you solved them
• Testing strategy: Describe how you validated your implementation
• Example usage: Provide clear examples of running your program




# Description

CallMeMaybe is designed to teach students how to Handle Small Large Language Models (LLMs) using Python.

The goal is to create an algurithm that takes in two input files, function_calling and functions_definition, takes in Prompts and Functions from each file and outputs a file with a

 of multiple **Coders** working together to **Compile**, **Debug** and **Refactor** Code into a central console by the means of a limited supply of **Dongles** that needs to be managed for the best possible efficiency and to try and evade **Burnout** at every turn.

During this Program, each `Coder` repeatedly:
- acquires two `Dongles`;
- Compiles (waits for `time_to_compile` ms);
- Debugs (waits for `time_to_debug` ms);
- Refactors (waits for `time_to_refactor` ms);

until the `number_of_compiles_required` has been met.

A Coder burns out if it fails to begin Compiling again within
`time_to_burnout` ms.

After use, `Dongles` become temporarily unavailable for `dongle_cooldown` ms.

The `Scheduler` can allocate Dongles using either First In, First Out (FIFO), meaning the `Dongle` is given to the **Coder** whose request arrived first; or Earliest Deadline First (EDF), meaning `Dongle` is given to the **Coder** whose deadline is sooner, deadline being defined as `last_compile_start + time_to_burnout`.

## Thread Synchronization Mechanisms

Threads cannot be left free to access shared memory and run without control, so we must implement those controls. This is made mainly in 3 forms: `Mutexes` (pthread_mutex_t), `Condition Variables` (pthread_cond_t), and `Shared State Variables`.

### Mutexes Used

`Mutexes` work like Locks. When you want to access some shared information or state, you must have the key. To do that, you use pthread_mutex_lock to take the key, and now you may look at and alter anything that is protected by that `Mutex`. To let go of the Key, you use pthread_mutex_unlock. If a second thread wants to use the key while it is taken by another, it will wait until the unlock happens, and the thread in waiting will immediately wake up and take it. Granted, there is not a data race between multiple threads all looking to get the same `Mutex`

Shared:
- `Print` - Protects the Console log from corruption
- `Burnout` - Protects the `Burnout State` Condition Variable

Used by Dongles
- `State` - Protects the `Lock State` of the `Dongle`, as well as all Condition Variables relating to the `Dongle`

### Condition Variables Used

`Condition Variables` work like Signals that can be broadcast from any thread and be detected by any other threads that are actively waiting for it. `Condition Variables` also must be protected by a `Mutex`, so it is impossible for multiple `Threads` to broadcast them as well as to make sure there are no data races between a broadcast and a receiving of said broadcast.

Shared:
- `Start Sim` - Serves as the Start Signal that makes all threads start working. Has a private `Mutex`.

Used by Coders
- `Compiling` - Serves to communicate between the `Main Coder Thread` and its `Coder Burnout Thread` to detect if a Burnout has occurred. Has a private `Mutex`.

Used by Dongles
- `Take` - Used to communicate between the `Main Coder Thread` and `Dongle Thread` to have the `Dongle` Lock itself
- `Free` - Used to Communicate Between `Main Coder Thread` and `Dongle Thread` to have the `Dongle` start it's Cooldown and free itself when Ready
- `Ready` - Used to Communicate Between `Dongle Thread` and `Main Coder Thread` to signal the `Dongle` has been freed and to allow the Coders to check if they are next in line to take it

### Shared State Variables Used

not to be confused with `Condition Variables`, these Variables are shared `Variables` that tell the `Threads` how to behave. Unlike `Condition Variables` that are instantaneous, `Variables` are lingering and can be detected at any time, so long as they are protected by a Designated `Mutex`.

Shared:
- `Burnout State` - set as **ACTIVE** for as long as there is no Burnout. as soon as a Burnout is detected, the `Burnout Thread` in question will change this variable to **DONE** which will be detected by all other parts of the code and start the death of all the threads and a successful closing of the program.
- `Complete State` - Similar to `Burnout State`, but this one will be changed to `Done` when all `Coder Functions` have returned successfully so we can have the Dongle threads return without touching `Burnout State`. Protected by `Burnout Mutex` as well

Used by Coders
- `Compilations Complete` - How many compilations a Coder has done. Protected by `Compiling Mutex`
- `Last Compile Time` - When was the last Compile. Used Mainly for EDF `Scheduler`. Protected by `Compiling Mutex`

Used by Dongles
- `Lock State` - set as **FREE** by default. when a `Take` Signal is received, it changes to **HELD**. It is freed after Cooldown again.

## Blocking Cases Handled

Certain problems are baked into the project, and they must be addressed by the student. Here are some of them and the way I prevent them from occurring

### Deadlock prevention

A deadlock is when a `Mutex` is held by one thread and needs a second mutex to continue; however, a second thread has that second `Mutex` locked and requires the first `Mutex` to work. in this case, nothing can happen, as both threads are waiting for the other and none will advance.

to prevent this, I make it so the first dongle that a coder is looking for depends on its index. Odd `Coders` always look for the right `Dongle` first, while even `Coders` always look for the left `Dongle` first.

In an example with 2 coders, this means `Coder 1` will be looking for `Dongle 1` on its right, while `Coder 2` will also be looking for `Dongle 1` on its left. They cannot both grab one and need the other; only one can grab the first, and from the first they will be free to grab the second. As extra Insurance i also make even `Coders` Wait some time before looking for dongles.

### Burnout prevention

The `Schedulers` will be the ones preventing burnouts in the case that the cooldown of the Dongles is long enough that both Coders will be expecting it. This is because the `Schedulers` will determine how the Queue of the Dongles will be ordered. From there, before a `Coder` locks a `Dongle`, it must first check if it is the first on the Queue to take it. if not, it must wait for the next time the `Dongle` is available to check again.

### Cooldown handling

`Dongles`, after being freed, must enter a Cooldown State; this is done by the dedicated `Dongle` Thread. this thread monitors others' access to it. this thread waits for a take signal (`condition`) to lock itself, then it will wait for a Free signal to start Cooldown. after `dongle_cooldown` ms, it will unlock itself and send out a Ready signal that can be detected by any `Coder` waiting for the `Dongle`.

### Burnout detection

If a `Coder` doesn't compile in `time_to_burnout`, it will burn out and must send a signal to stop all of the simulation and any console logs from being displayed. Since the `Main Coder Thread` is busy in the Compilation Loop, I use a `Coder Burnout Thread` to control each `Coder`. when a `Coder` starts compiling, it sends a Compiling Signal (`Condition`) that is detected by the `Coder Burnout Thread`. So long as the `Coder Burnout Thread` keeps detecting the Compiling Signal in intervals of `time_to_burnout`, nothing will go wrong. However, if a Signal is not detected, Burnout is activated. We change an internal Variable that is checked before any sleep or print functions, and that will make all the threads return as fast as possible so we can exit with no memory issues.

### Log serialization

To prevent two threads from trying to write at the same time, Console output is protected by a dedicated mutex. This prevents corruption of the displayed message and makes sure the events are logged in the correct order that they happen, not the thread that gets a slight priority on printing


# Instructions

For compilation, a Makefile is provided. Running the command `make` on a shell console will compile the program.

The output of this compilation will be a `codexion` executable.

To use it as intended, run it with a set of arguments in the following order:

- `number_of_coders` - Number of **Coders** and **Dongles** present for the Simulation.
- `time_to_burnout` - if a **Coder** does not start **compiling** after this amount of time, starting from the moment they started **compiling** for the last time, the **Coder** will burnout.
- `time_to_compile` - Time needed to **Compile** code. Requite **Dongles**.
- `time_to_debug` - Time needed to **Debug** code. Does not requite **Dongles**.
- `time_to_refactor` - Time needed to **Refactor** code. Does not requite **Dongles**.
- `number_of_compiles_required` - the number of **Compilations** each `Coder` has to complete for the **Simulation** to end in a Success.
- `dongle_cooldown` - Time a dongle needs to cooldown after use.
- `scheduler` - The decision mechanism used by **Dongles** to decide who gets one
when multiple `Coders` request them. The value must be exactly one of: `fifo` or `edf`.

- Example:

    `./codexion 4 400 200 200 200 3 100 fifo`

when running, a live log will be displayed with all the actions taken by each **Coder**. the listed actions are formatted as follows:

- `<timestamp> <Coder> <Action>`
  - `timestamp` is the time in milliseconds since the start of the Simulation
  - `Coder` will be the ID of the `Coder` in question, ranging from 1 to `number_of_coders`
  - `Action` will be the Action taken. 5 Actions are possible
    - `has taken a dongle` - **Coder** takes one of the **Dongles**
    - `is compiling` - **Coder** starts **Compiling**
    - `is debugging` - **Coder** starts **Debugging**
    - `is refactoring` - **Coder** starts **Refactoring**
    - `burned out` - **Coder** declares **Burned Out**, meaning it has failed to start **Compiling** in `time_to_burnout`

# Resources

Most of the core concepts I learned from evaluating others and through pure experimentation; I needed only to look up how the Thread functions were called properly, and not much other research was necessary beyond understanding how threads fundamentally worked.

For further explanation of particular aspects of internal Thread Logic or strange errors I was not able to find elsewhere, I sometimes checked in with AI with mixed results. I also used it as a tool to sift through the lengthy error messages I was not yet familiar with (my own in-built debugging outputs while in development and Valgrind memory testing output, for example).

## Sources:
Thread Functions list and explanation:
- https://www.geeksforgeeks.org/c/thread-functions-in-c-c/

Time Functions Help:
- https://man7.org/linux/man-pages/man3/usleep.3.html
- https://man7.org/linux/man-pages/man2/settimeofday.2.html
- https://man7.org/linux/man-pages/man3/timeval.3type.html
- https://man7.org/linux/man-pages/man3/timespec.3type.html
