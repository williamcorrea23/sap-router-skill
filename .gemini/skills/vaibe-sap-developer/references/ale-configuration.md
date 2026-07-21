# ALE Configuration & IDoc Type Definition
Parent skill: vaibe-sap-developer
Load when: the user needs the *setup* side of IDoc/ALE — distribution model, partner profiles, ports, or a new IDoc type/segment — as opposed to retrigger/enhancement logic on an existing IDoc (that's `references/idoc-enhancement.md`).

This is almost entirely Customizing/IMG work, not generatable ABAP — walk through it rather than producing code, except where noted.

## Sequence (On-Premise / Private Edition)
1. **Segment definition (WE31)** — field list for each segment, max 1000 chars per segment.
2. **IDoc type / message type (WE30, WE81/WE82)** — assemble segments into the IDoc type, link to a message type.
3. **Port definition (WE21)** — transactional RFC port (most common) pointing at the receiving system's RFC destination.
4. **Partner profile (WE20)** — per partner (logical system), define inbound/outbound parameters: message type, process code, IDoc type.
5. **Distribution model (BD64)** — which message types flow between which logical systems; generates the model that `MASTER_IDOC_DISTRIBUTE` consults.

Rule: don't generate a custom IDoc type when an existing standard one can be extended with an append/custom segment instead — extension is upgrade-safer and is usually what's actually needed (e.g. adding a Z-segment to `ORDERS05` rather than inventing a whole new IDoc type).

## Outbound IDoc generation (ABAP side, once config above exists)
```abap
DATA: lt_idoc_data TYPE STANDARD TABLE OF edidd,
      lt_communication TYPE STANDARD TABLE OF edidc.

CALL FUNCTION 'MASTER_IDOC_DISTRIBUTE'
  TABLES
    communication_idoc_control = lt_communication
    master_idoc_data           = lt_idoc_data
  EXCEPTIONS
    error_in_idoc_control      = 1
    error_writing_idoc_status  = 2
    error_in_idoc_data         = 3
    sending_logical_system_unknown = 4
    OTHERS                     = 5.
```
Rule: populate `EDIDC-MESTYP`/`IDOCTP`/`RCVPRN` from the partner profile values, not hardcoded literals — a mismatch against WE20 config is the most common reason an outbound IDoc never reaches the partner.

## Edition note
Per `references/edition-legality.md`, ALE/IDoc infrastructure is generally not present in standalone BTP ABAP Environment systems. In Cloud Public Edition, prefer extending an existing released IDoc type/message type over creating a new custom one — confirm with the user whether a standard message type already covers the scenario before designing a new IDoc type there.
