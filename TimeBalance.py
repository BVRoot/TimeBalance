from itertools import izip, count
from operator import itemgetter
from datetime import timedelta
import numpy as np

# given an iterable of pairs return the key corresponding to the greatest value
def argmax(pairs):
    return max(pairs, key=itemgetter(1))[0]

# given an iterable of values return the index of the greatest value
def argmax_index(values):
    return argmax(izip(count(), values))

def argfind_index(item, values) :
    for index, aVal in enumerate(values) :
        if item is aVal :
            return index

    raise ValueError("Could not find item in list of values")


class TBScheduler(object) :
    def __init__(self, surveil_task) :
        self.tasks = []
        self.T_B = []

        self.surveil_task = surveil_task

        # The T_B value threshold for action
        self.actionTB = timedelta()

    def add_tasks(self, tasks) :
        # Initialize the T_B for each task
        self.T_B.extend([timedelta()] * len(tasks))
        self.tasks.extend(tasks)

    def rm_tasks(self, tasks) :
        findargs = [argfind_index(aTask, self.tasks) for aTask in tasks]

        args = np.argsort(findargs)[::-1]

        for anItem in args :
            del self.tasks[findargs[anItem]]
            del self.T_B[findargs[anItem]]

    def next_task(self) :
        # -1 shall indicate to use the fallback task of surveillance.
        doTask = -1

        # Determine the next task to execute
        if len(self.tasks) > 0 :
            availTask = argmax_index(self.T_B)

            if self.T_B[availTask] >= self.actionTB :
                doTask = availTask
                # decrement the T_B of the task by the update time.
                self.T_B[availTask] -= self.tasks[availTask].U

        theTask = self.tasks[doTask] if doTask >= 0 else self.surveil_task
        
        # Decrement the T_B of all tasks by the selected task time
        # NOTE: can't do `tb += theTask.T` because += operator on
        #       a timedelta object isn't in-place. Go figure...
        for index in range(len(self.T_B)) :
            self.T_B[index] += theTask.T

        return theTask



if __name__ == '__main__' :
    import ScanRadSim.task as task

    #import matplotlib.pyplot as plt

    # Just a quick test...
    surveillance = task.Task(timedelta(seconds=1),
                             timedelta(seconds=1),
                             range(10))
    tasks = [task.Task(update, time, radials) for update, time, radials
             in zip((timedelta(seconds=20), timedelta(seconds=35)),
                    (timedelta(seconds=10), timedelta(seconds=14)),
                    (range(30), range(14)))]
    sched = TBScheduler(surveillance)
    
    print sched.next_task()

    timer = timedelta(seconds=0)
    sched.add_tasks(tasks)
    """
    tb1 = []
    tb2 = []
    times1 = []
    times2 = []
    tb1.append(sched.T_B[0])
    tb2.append(sched.T_B[1])
    times1.append(timer)
    times2.append(timer)
    """
    while timer.seconds < 110 :
        theTask = sched.next_task()
        print "%.3d %.2d %.2d" % (timer.seconds, theTask.T.seconds, theTask.U.seconds)

        """
        if theTask.name == 'foo' :
            times1.extend([timer, timer])
            tb1.extend([tb1[-1], sched.T_B[0]])

            times2.append(timer + theTask.T)
            tb2.append(sched.T_B[1])
        elif theTask.name == 'bar' :
            times2.extend([timer, timer])
            tb2.extend([tb2[-1], sched.T_B[1]])

            times1.append(timer + theTask.T)
            tb1.append(sched.T_B[0])
        """

        timer += theTask.T



    """
    plt.plot(times1, tb1, 'r', label='task 1')
    plt.plot(times2, tb2, 'g', label='task 2') 
    plt.legend()
    plt.show()
    """
