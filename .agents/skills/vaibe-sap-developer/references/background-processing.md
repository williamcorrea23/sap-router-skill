# Background Processing & Parallelization
Parent skill: vaibe-sap-developer
Load when: the user needs a background job (scheduled report, batch processing) or parallel/async processing of a large data set.

This is a released-API capability available across all editions — unlike most of the legacy-UI categories in this skill, job scheduling itself isn't blocked by Clean Core/ABAP Cloud restrictions.

## Scheduling a background job
```abap
DATA: lv_jobname  TYPE tbtcjob-jobname VALUE 'Z_PO_APPROVAL_BATCH',
      lv_jobcount TYPE tbtcjob-jobcount.

CALL FUNCTION 'JOB_OPEN'
  EXPORTING
    jobname          = lv_jobname
  IMPORTING
    jobcount         = lv_jobcount
  EXCEPTIONS
    cant_create_job  = 1
    invalid_job_data = 2
    jobname_missing  = 3
    OTHERS           = 4.

SUBMIT zpo_approval_batch
  VIA JOB lv_jobname NUMBER lv_jobcount
  AND RETURN.

CALL FUNCTION 'JOB_CLOSE'
  EXPORTING
    jobcount             = lv_jobcount
    jobname              = lv_jobname
    strtimmed             = abap_true
  EXCEPTIONS
    cant_start_immediate = 1
    invalid_startdate    = 2
    jobname_missing      = 3
    job_close_failed     = 4
    job_nosteps          = 5
    job_notex            = 6
    lock_failed           = 7
    OTHERS               = 8.
```
Rule: always check `sy-subrc` after `JOB_OPEN` before the `SUBMIT ... VIA JOB`, and after `JOB_CLOSE` — a job that fails to close cleanly stays in "scheduled" state forever and never runs.

## Polling for completion (when the caller needs to wait)
```abap
DO.
  SELECT SINGLE status FROM tbtco
    INTO lv_status
    WHERE jobname  = lv_jobname
      AND jobcount = lv_jobcount.
  IF lv_status = 'F' OR lv_status = 'A'.   " finished or aborted
    EXIT.
  ENDIF.
  WAIT UP TO 2 SECONDS.
ENDDO.
```
Rule: always cap the poll loop (max iterations or elapsed-time check) — an unbounded `DO ... ENDDO` polling loop can hang a dialog work process indefinitely if the job never finishes.

## Parallel processing (asynchronous RFC)
```abap
DO lv_package_count TIMES.
  CALL FUNCTION 'Z_PROCESS_PACKAGE'
    STARTING NEW TASK lv_task_id
    PERFORMING handle_result ON END OF TASK
    EXPORTING
      it_package = lt_package.
ENDDO.
```
Rule: cap the number of parallel tasks (check `cl_abap_parallel` or a fixed work-process budget) rather than firing one task per record — uncapped `STARTING NEW TASK` calls can exhaust the RFC work-process pool.

## Anti-patterns
- Don't `COMMIT WORK` inside a tight per-record loop in a batch job — batch the commits (e.g. every N records) to avoid excessive DB log generation.
- Don't schedule a job without a defined recovery/restart approach for partial failure — note this explicitly if the user's requirement doesn't mention it.
