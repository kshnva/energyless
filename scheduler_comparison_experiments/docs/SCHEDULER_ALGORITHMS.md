# Scheduler Algorithms Documentation

This document provides detailed pseudocode and algorithm descriptions for the custom schedulers implemented in this project.

## Table of Contents

1. [Overview](#overview)
2. [Workflow-Aware Scheduler](#workflow-aware-scheduler)
3. [Carbon-Aware Workflow Scheduler](#carbon-aware-workflow-scheduler)
4. [Algorithm Comparison](#algorithm-comparison)

---

## Overview

This project implements two advanced schedulers that extend OpenDC's base `FilterScheduler`:

- **Workflow-Aware Scheduler**: Prioritizes tasks based on deadline urgency, critical path analysis, and parallelism potential
- **Carbon-Aware Workflow Scheduler**: Delays deferrable tasks during high-carbon periods while respecting workflow deadlines

Both schedulers maintain workflow dependencies and task deadlines while optimizing for their respective objectives.

---

## Workflow-Aware Scheduler

### Purpose

The Workflow-Aware Scheduler optimizes task scheduling by considering:
- **Deadline urgency**: Prioritizes tasks close to their deadlines
- **Critical path**: Favors tasks on the longest dependency chain
- **Parallelism potential**: Optionally prioritizes tasks that unlock parallel execution

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `taskDeadlineScore` | Boolean | required | Enable/disable deadline-based urgency scoring |
| `weightUrgency` | Double | 0.2 | Weight for urgency score component |
| `weightCriticalDependencyChain` | Double | 0.2 | Weight for critical path length |
| `enableParallelismScore` | Boolean | false | Enable parallelism-aware scoring |
| `weightParallelism` | Double | 0.0 | Weight for parallelism score component |
| `parallelismDecayRate` | Double | 0.15 | Decay rate for parallelism score calculation |
| `taskLookaheadThreshold` | Int | 1000 | Max tasks to evaluate in each scheduling round |

### Algorithm Pseudocode

```
CLASS WorkflowAwareScheduler EXTENDS FilterScheduler:
    
    ATTRIBUTES:
        taskDeadlineScore: Boolean
        weightUrgency: Double
        weightCriticalDependencyChain: Double
        enableParallelismScore: Boolean
        weightParallelism: Double
        parallelismDecayRate: Double
        taskLookaheadThreshold: Integer
        initTime: Long  // Scheduler initialization time
    
    INITIALIZE:
        initTime ← current_clock_time()
    
    FUNCTION selectTask(taskIterator):
        """
        Selects the highest-priority task from the ready queue using
        multi-criteria scoring with configurable weights.
        """
        currentTime ← current_clock_time()
        simulationOffsetTime ← NULL
        
        // Count ready (non-cancelled) tasks for parallelism scoring
        readyTaskCount ← 0
        FOR EACH task IN taskIterator:
            IF NOT task.isCancelled:
                readyTaskCount ← readyTaskCount + 1
        
        // Reset iterator to beginning
        RESET taskIterator TO START
        
        highestPriorityIndex ← -1
        highestPriorityScore ← -∞
        tasksEvaluated ← 0
        
        // --- LOOKAHEAD PHASE: Evaluate up to taskLookaheadThreshold tasks ---
        WHILE taskIterator.hasNext() AND tasksEvaluated < taskLookaheadThreshold:
            currentIndex ← taskIterator.currentIndex()
            request ← taskIterator.next()
            
            // Initialize simulation time offset from first task submission
            IF simulationOffsetTime IS NULL:
                firstSubmitTime ← request.task.service.firstTaskSubmittedAt
                simulationOffset ← firstSubmitTime - initTime
                simulationOffsetTime ← currentTime + simulationOffset
            
            // Skip cancelled tasks
            IF request.isCancelled:
                CONTINUE
            
            // Calculate priority score for this task
            score ← calculatePriorityScore(request, simulationOffsetTime, readyTaskCount)
            
            // Track highest scoring task
            IF score > highestPriorityScore:
                highestPriorityScore ← score
                highestPriorityIndex ← currentIndex
            
            tasksEvaluated ← tasksEvaluated + 1
        
        // Reset iterator to beginning
        RESET taskIterator TO START
        
        IF highestPriorityIndex == -1:
            RETURN NULL  // No valid task found
        
        // --- NAVIGATION PHASE: Move to highest priority task ---
        WHILE taskIterator.currentIndex() < highestPriorityIndex:
            taskIterator.next()
        
        selectedTask ← taskIterator.next()
        RETURN selectedTask
    
    FUNCTION calculatePriorityScore(request, currentTime, readyTaskCount):
        """
        Computes a weighted priority score combining urgency, critical path,
        and optional parallelism metrics.
        """
        task ← request.task
        
        // --- URGENCY SCORE: Based on deadline proximity ---
        IF taskDeadlineScore IS TRUE:
            slack ← task.deadline - currentTime
            
            IF slack < 0:
                // Overdue tasks get maximum priority
                urgencyScore ← MAX_DOUBLE
            ELSE IF slack > 0:
                // Inverse of slack: tighter deadlines = higher urgency
                urgencyScore ← 1.0 / slack
            ELSE:
                // Zero slack = maximum urgency
                urgencyScore ← MAX_DOUBLE
        ELSE:
            urgencyScore ← 0.0
        
        // --- CRITICAL PATH SCORE: Based on dependency chain length ---
        chainLength ← task.calcMaxDependencyChainLength()
        chainScore ← chainLength
        
        // --- PARALLELISM SCORE: Prioritize tasks that unlock parallel work ---
        // Only enabled when ready pool is small (< taskLookaheadThreshold)
        IF enableParallelismScore AND readyTaskCount < taskLookaheadThreshold:
            parallelismScore ← task.calculateParallelismScore(parallelismDecayRate)
        ELSE:
            parallelismScore ← 0.0
        
        // --- WEIGHTED COMBINATION ---
        totalScore ← (weightUrgency × urgencyScore) +
                     (weightCriticalDependencyChain × chainScore) +
                     (weightParallelism × parallelismScore)
        
        RETURN totalScore
```

### Key Features

1. **Adaptive Lookahead**: Evaluates up to `taskLookaheadThreshold` tasks to find the best candidate
2. **Multi-Criteria Scoring**: Combines urgency, critical path, and parallelism using configurable weights
3. **Overdue Handling**: Overdue tasks receive maximum priority to minimize deadline violations
4. **Parallelism Awareness**: Optionally prioritizes tasks that enable more parallel execution when the ready pool is small

### Typical Use Cases

- **Urgent workflows** (high `weightUrgency`): Minimize deadline violations
- **Long dependency chains** (high `weightCriticalDependencyChain`): Reduce overall workflow completion time
- **Parallel workloads** (enable `enableParallelismScore`): Maximize resource utilization

---

## Carbon-Aware Workflow Scheduler

### Purpose

The Carbon-Aware Workflow Scheduler delays deferrable tasks during high-carbon periods to reduce operational carbon emissions while maintaining workflow deadlines and dependencies.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `carbonDelayThreshold` | Double | 0.5 | Percentile threshold for "high carbon" (0.5 = median) |
| `maxDelayHours` | Double | 4.0 | Maximum hours a task can be delayed |
| `forecastHorizon` | Int | 24 | Hours to look ahead in carbon forecast |
| `slackThresholdMultiplier` | Double | 1.5 | Safety margin multiplier for slack requirements |
| `prioritizeCriticalPath` | Boolean | true | Apply stricter delays for early/critical tasks |

### Algorithm Pseudocode

```
CLASS CarbonAwareWorkflowScheduler EXTENDS WorkflowAwareScheduler:
    
    ATTRIBUTES:
        carbonDelayThreshold: Double
        maxDelayHours: Double
        forecastHorizon: Integer
        slackThresholdMultiplier: Double
        prioritizeCriticalPath: Boolean
        
        carbonModel: CarbonModel
        currentCarbonIntensity: Double
        lowCarbon: Boolean  // Current carbon regime flag
        
        taskMetadata: Map<TaskID, TaskMetadata>
        totalTasksSeen: Integer
        delayedCount: Integer
        slackSkips: Integer
        criticalPathSkips: Integer
    
    STRUCT TaskMetadata:
        taskId: Integer
        submitTime: Long
        deadline: Long
        deferrable: Boolean
        queuePosition: Integer
    
    FUNCTION selectTask(taskIterator):
        """
        Extends base scheduler with carbon-aware delay logic.
        Delays deferrable tasks during high-carbon periods.
        """
        currentTime ← current_clock_time()
        queuePosition ← 0
        
        // --- METADATA TRACKING PHASE ---
        FOR EACH request IN taskIterator:
            IF NOT request.isCancelled:
                task ← request.task
                
                // Track or update task metadata
                IF task.id NOT IN taskMetadata:
                    totalTasksSeen ← totalTasksSeen + 1
                    taskMetadata[task.id] ← NEW TaskMetadata(
                        taskId = task.id,
                        submitTime = currentTime,
                        deadline = task.deadline,
                        deferrable = task.deferrable,
                        queuePosition = queuePosition
                    )
                ELSE:
                    // Update queue position for existing task
                    taskMetadata[task.id].queuePosition ← queuePosition
                
                queuePosition ← queuePosition + 1
        
        // Reset iterator to beginning
        RESET taskIterator TO START
        
        // --- CARBON-AWARE FILTERING PHASE ---
        WHILE taskIterator.hasNext():
            request ← taskIterator.next()
            
            IF request.isCancelled:
                CONTINUE
            
            task ← request.task
            
            // Check if this task should be delayed for carbon reasons
            IF shouldDelayWorkflowAware(task):
                delayedCount ← delayedCount + 1
                // Skip this task, let iterator continue to next
                CONTINUE
            ELSE:
                // Found a task that should run now
                RETURN request
        
        // No suitable task found
        RETURN NULL
    
    FUNCTION shouldDelayWorkflowAware(task):
        """
        Workflow-aware delay decision logic with adaptive forecast horizon.
        Determines if a task should be delayed based on carbon intensity,
        deadline slack, and workflow position.
        """
        // --- BASIC CHECKS ---
        IF NOT task.deferrable:
            RETURN FALSE  // Cannot delay non-deferrable tasks
        
        currentTime ← current_clock_time()
        slack ← task.deadline - currentTime - task.duration
        
        // --- ADAPTIVE FORECAST HORIZON ---
        // Use shorter horizon if task deadline is sooner than default horizon
        timeUntilDeadlineMs ← task.deadline - currentTime
        timeUntilDeadlineHours ← timeUntilDeadlineMs / 3600000.0
        
        // Use minimum of configured horizon and time until deadline
        // Enforce minimum of 1 hour for stable percentile calculation
        adaptiveHorizonHours ← MIN(forecastHorizon, MAX(1.0, timeUntilDeadlineHours))
        
        // --- CARBON REGIME CHECK ---
        forecast ← carbonModel.getForecast(adaptiveHorizonHours)
        
        IF forecast IS NULL OR forecast IS EMPTY:
            // No forecast available, use global lowCarbon flag as fallback
            IF lowCarbon IS TRUE:
                RETURN FALSE  // Already in low-carbon period
        ELSE:
            // Calculate task-specific carbon threshold using adaptive horizon
            forecastSize ← forecast.size
            quantileIndex ← ROUND(forecastSize × carbonDelayThreshold)
            carbonThreshold ← SORTED(forecast)[quantileIndex]
            
            // If current carbon is already below threshold, don't delay
            IF currentCarbonIntensity < carbonThreshold:
                RETURN FALSE
        
        // --- SLACK REQUIREMENT CALCULATION ---
        baseSlackNeeded ← maxDelayHours × 3600000  // Convert to milliseconds
        minSlackNeeded ← baseSlackNeeded × slackThresholdMultiplier
        
        // --- WORKFLOW-AWARE ADJUSTMENTS ---
        IF prioritizeCriticalPath IS TRUE:
            metadata ← taskMetadata[task.id]
            
            IF metadata IS NOT NULL:
                // Early tasks in queue are likely on or near critical path
                IF metadata.queuePosition < 5:
                    // Require 50% more slack for early tasks
                    minSlackNeeded ← minSlackNeeded × 1.5
                    
                    // If insufficient slack, skip delay immediately
                    IF slack < minSlackNeeded:
                        criticalPathSkips ← criticalPathSkips + 1
                        RETURN FALSE
                
                // During busy periods (many tasks), be more conservative
                queueDepth ← taskMetadata.size
                IF queueDepth > 20:
                    // Require 20% more slack during busy periods
                    minSlackNeeded ← minSlackNeeded × 1.2
        
        // --- FINAL SLACK CHECK ---
        IF slack < minSlackNeeded:
            slackSkips ← slackSkips + 1
            RETURN FALSE
        
        // Safe to delay this task
        RETURN TRUE
    
    FUNCTION updateCarbonIntensity(newCarbonIntensity):
        """
        Called periodically to update carbon intensity and regime flag.
        """
        currentCarbonIntensity ← newCarbonIntensity
        
        // Determine current carbon regime using forecast
        forecast ← carbonModel.getForecast(forecastHorizon)
        
        IF forecast IS EMPTY:
            lowCarbon ← FALSE
            RETURN
        
        forecastSize ← forecast.size
        quantileIndex ← ROUND(forecastSize × carbonDelayThreshold)
        carbonThreshold ← SORTED(forecast)[quantileIndex]
        
        lowCarbon ← (newCarbonIntensity < carbonThreshold)
    
    FUNCTION removeTask(task, host):
        """
        Clean up metadata when task completes to prevent memory bloat.
        """
        REMOVE taskMetadata[task.id]
```

### Key Features

1. **Threshold-Based Delays**: Uses percentile thresholds (not greedy immediate optimization) to determine high-carbon periods
2. **Adaptive Forecast Horizon**: Automatically adjusts forecast window based on task deadlines
3. **Workflow-Aware Safety**: Requires extra slack for early/critical tasks to prevent cascading delays
4. **Queue Position Tracking**: Prioritizes early tasks in the queue as likely critical path members
5. **Busy Period Detection**: More conservative delays when many tasks are waiting

### Safety Mechanisms

The scheduler includes multiple safety checks to prevent deadline violations:

1. **Slack Multiplier**: Requires `slackThresholdMultiplier × maxDelayHours` of slack (default 1.5×)
2. **Critical Path Protection**: Early tasks (position < 5) require 50% more slack
3. **Busy Period Protection**: High queue depth (> 20 tasks) requires 20% more slack
4. **Non-Deferrable Tasks**: Tasks marked as non-deferrable are never delayed

### Typical Use Cases

- **Carbon-intensive regions**: Delay work during peak grid carbon hours
- **Batch workloads**: Defer non-urgent processing to low-carbon periods
- **Variable deadlines**: Adapt delay decisions based on task-specific slack

---

## Algorithm Comparison

| Feature | Workflow-Aware | Carbon-Aware Workflow |
|---------|----------------|----------------------|
| **Base Strategy** | Priority scoring | Delay filtering + priority scoring |
| **Primary Goal** | Minimize deadline violations | Reduce carbon emissions |
| **Secondary Goal** | Optimize critical path | Maintain workflow deadlines |
| **Delay Mechanism** | None (immediate scheduling) | Conditional delays during high carbon |
| **Urgency Handling** | Inverse slack scoring | Slack-based safety checks |
| **Critical Path** | Chain length scoring | Queue position + slack requirements |
| **Parallelism** | Optional scoring component | Inherited from base scheduler |
| **Carbon Awareness** | None | Adaptive forecast-based thresholds |

### When to Use Each Scheduler

**Use Workflow-Aware when:**
- Carbon emissions are not a concern
- Minimizing workflow completion time is critical
- Deadlines are tight with little slack
- Workload has complex dependencies

**Use Carbon-Aware Workflow when:**
- Carbon reduction is a priority
- Tasks have sufficient slack (hours to days)
- Workload includes deferrable tasks
- Carbon intensity varies significantly over time

### Configuration Tips

**For aggressive carbon reduction:**
```json
{
  "carbonDelayThreshold": 0.3,
  "maxDelayHours": 6.0,
  "slackThresholdMultiplier": 1.3,
  "prioritizeCriticalPath": false
}
```

**For conservative carbon reduction:**
```json
{
  "carbonDelayThreshold": 0.6,
  "maxDelayHours": 2.0,
  "slackThresholdMultiplier": 2.0,
  "prioritizeCriticalPath": true
}
```

**For parallelism-focused workflow scheduling:**
```json
{
  "taskDeadlineScore": true,
  "weightUrgency": 0.3,
  "weightCriticalDependencyChain": 0.2,
  "enableParallelismScore": true,
  "weightParallelism": 0.5,
  "parallelismDecayRate": 0.1
}
```